from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.user import User
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import httpx
import os

from services.auth_service import is_token_blacklisted

GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"

router = APIRouter(prefix="/users", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = "e$6Xr!Z9w*qNmP*VeH2v7kLq#8DbzqGh2aLbI4HnQFvX6cKoV7V8J$YrHhF7#8@c"
ALGORITHM = "HS256"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")  # Ensure you load this in your environment
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


# async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
#     if is_token_blacklisted(token):
#         raise HTTPException(status_code=401, detail="Token has been revoked")
#
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#
#         result = await db.execute(select(User).where(User.username == username))
#         user = result.scalars().first()
#         if not user:
#             raise HTTPException(status_code=401, detail="User not found")
#         return user
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Could not validate credentials")


async def verify_google_token(token: str):
    """Verify Google OAuth token using Google's userinfo endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid or expired Google token")

        payload = response.json()

    # Ensure the token's audience matches your Google Client ID
    if payload.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=401, detail="Invalid token audience")

    return payload


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """Authenticate user using either Google token or local JWT"""
    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    try:
        # 🔹 Try decoding as a local JWT first
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username", 'None')
    except JWTError:
        # 🔹 If decoding fails, check if it's a Google token
        payload = await verify_google_token(token)
        username = payload.get("email")  # Google tokens use email as the identifier

    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 🔹 Fetch user from the database
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Fetch the profile of the logged-in user"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "photo_url": current_user.photo_url,
        "bio": current_user.bio,
        "phone": current_user.phone,
        "is_google_user": current_user.password == "",  # Google users don't have passwords
    }


@router.put("/profile")
async def update_profile(updated_user: dict, current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    """Update user profile"""
    for key, value in updated_user.items():
        if hasattr(current_user, key):
            setattr(current_user, key, value)

    await db.commit()
    await db.refresh(current_user)
    return {"message": "Profile updated successfully"}
