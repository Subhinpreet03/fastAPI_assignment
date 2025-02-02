from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
TOKEN_BLACKLIST = set()  # Store blacklisted tokens in memory (Consider using Redis for production)


async def authenticate_user(db: AsyncSession, username: str, password: str):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user and pwd_context.verify(password, user.password):
        return user
    return None


async def create_user(db: AsyncSession, user_data: dict):
    password = user_data.pop("password")  # Remove the 'password' key from user_data
    hashed_password = pwd_context.hash(password)  # Hash the password
    user = User(**user_data, password=hashed_password)  # Pass the rest of the data, with hashed password
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Generate JWT token"""
    if not isinstance(data, dict):
        raise ValueError("data must be a dictionary")

    to_encode = data.copy()  # ✅ Now safe to copy
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def blacklist_token(token: str):
    """Add token to blacklist"""
    TOKEN_BLACKLIST.add(token)


def is_token_blacklisted(token: str):
    """Check if token is blacklisted"""
    return token in TOKEN_BLACKLIST
