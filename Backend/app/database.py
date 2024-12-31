from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from fastapi import HTTPException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL with fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://buildingmanager:superuser@localhost:5432/buildingmanager"
)

#temporary passowrd: superuser

# Ensure URL is PostgreSQL compatible
if not DATABASE_URL.startswith("postgresql"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Retry configuration for database operations
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry_error_cls=SQLAlchemyError
)
async def get_db_connection():
    """Attempt to establish database connection with retry logic"""
    try:
        # Test connection
        connection = engine.connect()
        connection.close()
        logger.info("Database connection successful")
        return engine
    except SQLAlchemyError as e:
        logger.error(f"Database connection attempt failed: {str(e)}")
        raise

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

# Database session dependency
def get_db():
    """Dependency for getting database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check function
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def check_db_health():
    """Check database health with retry logic"""
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable"
        )

# Connection management
async def init_db():
    """Initialize database connections and verify setup"""
    try:
        await get_db_connection()
        await check_db_health()
        logger.info("Database initialization successful")
    except SQLAlchemyError as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

# Cleanup function
async def close_db_connections():
    """Gracefully close all database connections"""
    try:
        engine.dispose()
        logger.info("Database connections closed successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error closing database connections: {str(e)}")
        raise
