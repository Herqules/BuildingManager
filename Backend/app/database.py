from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from fastapi import HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL with fallback
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Ensure URL is PostgreSQL compatible
if not DATABASE_URL.startswith("postgresql"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    # Create engine with PostgreSQL-specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"options": "-c timezone=utc"},  # ✓ Good: Timezone handling
        pool_size=10,                                 # ✓ Good: Larger pool
        max_overflow=20,                             # ✓ Good: More overflow
        pool_timeout=30,                             # = Same as current
        pool_pre_ping=True                           # ✓ Good: Connection verification
    )
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Define base class for models
    Base = declarative_base()
    
except SQLAlchemyError as e:
    logger.error(f"Database connection error: {str(e)}")
    raise

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def get_db_with_retry():
    """
    Attempts to connect to database with retries
    """
    db = SessionLocal()
    try:
        db.execute("SELECT 1")
        return db
    except SQLAlchemyError as e:
        logger.error(f"Database connection attempt failed: {e}")
        db.close()
        raise

def verify_database_connection():
    """
    Verify database connection is working.
    Returns True if connection is successful, False otherwise.
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection verification failed: {str(e)}")
        return False
    finally:
        db.close()

def get_db():
    """
    Dependency function to get database session with better error handling
    """
    db = SessionLocal()
    try:
        # Test connection
        db.execute("SELECT 1")
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database service temporarily unavailable. Please try again later."
        )
    finally:
        db.close()

# Cache frequently accessed data
@cache(expire=60)  # Cache for 60 seconds
async def get_common_data():
    return db.query(CommonData).all()
