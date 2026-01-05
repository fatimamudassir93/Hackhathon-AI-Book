"""
Authentication utilities - JWT, password hashing, user management
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os

from database import get_db
from models import User, UserProfile

# Security configuration
SECRET_KEY = os.getenv("AUTH_SECRET", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer for JWT
security = HTTPBearer()

# Pydantic models
class TokenData(BaseModel):
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    technical_level: str  # beginner, intermediate, advanced
    programming_experience: list[str] = []
    robotics_background: str = "none"
    learning_goals: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    profile: Optional[dict]

    class Config:
        from_attributes = True


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    # Truncate to 72 bytes for bcrypt compatibility (same as hashing)
    password_bytes = plain_password.encode('utf-8')[:72]
    plain_password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password_truncated, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password (truncates to 72 bytes for bcrypt compatibility)"""
    # Bcrypt has a 72 byte limit, truncate the password if needed
    password_bytes = password.encode('utf-8')[:72]
    return pwd_context.hash(password_bytes.decode('utf-8', errors='ignore'))


# JWT utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> TokenData:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return TokenData(email=email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


# User management
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_user(db: Session, user_create: UserCreate) -> User:
    """Create a new user with profile"""
    # Check if user already exists
    existing_user = get_user_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        email=user_create.email,
        password_hash=hashed_password,
        name=user_create.name
    )
    db.add(db_user)
    db.flush()  # Get the user ID without committing

    # Create user profile
    db_profile = UserProfile(
        user_id=db_user.id,
        technical_level=user_create.technical_level,
        programming_experience=user_create.programming_experience,
        robotics_background=user_create.robotics_background,
        learning_goals=user_create.learning_goals
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_user)

    return db_user


# Dependency for protected routes
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token
    Use this as a dependency in protected routes
    """
    token = credentials.credentials
    token_data = decode_access_token(token)

    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# Optional authentication (for endpoints that work with or without auth)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if authenticated, None otherwise
    Use this for endpoints that provide different functionality based on auth status
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        token_data = decode_access_token(token)
        user = get_user_by_email(db, email=token_data.email)
        return user
    except HTTPException:
        return None
