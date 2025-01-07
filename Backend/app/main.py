from fastapi import FastAPI, Depends, HTTPException, status, Request, Response, APIRouter
from sqlalchemy.orm import Session
from .database import engine, SessionLocal
from . import models, schemas, crud
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from pydantic import BaseModel, validator
import bleach
import logging
from fastapi.responses import JSONResponse
from typing import Any
import time
import json
from .models import TicketStatus
from .validators import TicketValidator
from typing import List, Optional, Dict
from .auth import get_current_user, oauth2_scheme

print("Available schemas:", dir(schemas))  # Temporary debug line

# Initialize FastAPI app
app = FastAPI()

# Get allowed origins from environment variables
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
ALLOWED_HEADERS = ["Authorization", "Content-Type"]

# Replace the existing CORS middleware with this more secure version
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check route
@app.get("/")
def read_root():
    return {"message": "BuildingManager API is running"}

class SanitizedOrganizationCreate(schemas.OrganizationCreate):
    @validator('name', 'type', 'address')
    def sanitize_strings(cls, v):
        return bleach.clean(v)

# Example CRUD routes
@app.post("/organizations/", response_model=schemas.Organization)
async def create_organization(
    organization: SanitizedOrganizationCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.create_organization(db=db, organization=organization)

@app.get("/organizations/{organization_id}", response_model=schemas.Organization)
def get_organization(organization_id: int, db: Session = Depends(get_db)):
    db_organization = crud.get_organization(db=db, organization_id=organization_id)
    if not db_organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=username)
    if user is None:
        raise credentials_exception
    return user

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> Any:
    logger.error(f"Global error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url} took {duration:.2f}s")
    return response

@app.middleware("http")
async def validation_middleware(request: Request, call_next):
    # Validate request
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            # Ensure JSON is valid
            await request.json()
        except json.JSONDecodeError:
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid JSON format"}
            )
    
    response = await call_next(request)
    
    # Validate response
    if response.status_code >= 500:
        logger.error(f"Server error occurred: {response.status_code}")
        
    return response

# Create versioned routers
v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")

# Version 1 endpoints (basic features)
@v1_router.get("/tickets/")
async def get_tickets_v1(db: Session = Depends(get_db)):
    # Basic ticket listing
    return crud.get_tickets_basic(db)

# Version 2 endpoints (advanced features)
@v2_router.get("/tickets/")
async def get_tickets_v2(
    db: Session = Depends(get_db),
    include_followups: bool = False,
    include_severity: bool = False
):
    # Advanced ticket listing with optional related data
    return crud.get_tickets_advanced(db, include_followups, include_severity)

# Include routers in main app
app.include_router(v1_router)
app.include_router(v2_router)
