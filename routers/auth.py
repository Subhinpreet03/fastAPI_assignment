import uuid

import requests
from authlib.oauth2 import OAuth2Error
from fastapi import APIRouter, Depends, HTTPException, status, Request
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from routers.users import oauth2_scheme
from services.auth_service import authenticate_user, create_user, create_access_token, blacklist_token
from models.user import User
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
import os
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])
with open("google_client_secret.json") as f:
    google_creds = json.load(f)["web"]

oauth = OAuth()

# Register Google OAuth using JSON credentials
oauth.register(
    name="google",
    client_id=google_creds["client_id"],
    client_secret=google_creds["client_secret"],
    authorize_url=google_creds["auth_uri"],
    access_token_url=google_creds["token_uri"],
    client_kwargs={"scope": "openid email profile", 'redirect_uri': 'http://localhost:8000/auth/google/callback'},
    redirect_uri="http://localhost:8000/auth/google/callback",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    authorize_params={"scope": "openid email profile"},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',

)

oauth.register(
    name="facebook",
    client_id="YOUR_FACEBOOK_CLIENT_ID",
    client_secret="YOUR_FACEBOOK_CLIENT_SECRET",
    authorize_url="https://www.facebook.com/dialog/oauth",
    access_token_url="https://graph.facebook.com/oauth/access_token",
    client_kwargs={"scope": "email public_profile"},
)


class UserRegister(BaseModel):
    username: str
    password: str
    email: str
    full_name: str = None
    bio: str = None
    phone: str = None
    photo_url: str = None


@router.post("/register")
async def register(user: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    existing_user = await db.execute(select(User).where(User.username == user.username))
    if existing_user.scalars().first():
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = await create_user(db, user.model_dump())  # Use `model_dump()` in Pydantic v2
    return {"message": "User registered successfully", "user_id": new_user.id}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT token"""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token({"username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Logout user by blacklisting token"""
    blacklist_token(token)
    return {"message": "Logged out successfully"}


@router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = "http://localhost:8000/auth/google/callback"
    url = request.url_for('auth_google_callback')  # Use the route name here
    return await oauth.google.authorize_redirect(request, redirect_uri, prompt="consent")


@router.get("/google/callback")
async def auth_google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)  # Get Google OAuth token
        user_info = token.get('userinfo')  # Extract user info
    except OAuth2Error as error:
        print(error)
        raise HTTPException(status_code=400, detail="OAuth2 Authorization failed")

    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to retrieve user info")

    # 🔹 Create user in the database
    user = await create_user_if_not_exists(db, user_info)

    # 🔹 Create your own JWT token for API authentication
    jwt_token = create_access_token({"username": user.username})

    return {
        "access_token": jwt_token,  # Your JWT
        "token_type": "bearer",
        "google_token": token.get("id_token"),  # Include Google's ID token
    }


async def create_user_if_not_exists(db: AsyncSession, user_info: dict):
    result = await db.execute(select(User).where(User.email == user_info["email"]))
    user = result.scalars().first()

    if not user:
        user = User(
            username=user_info["email"].split("@")[0],
            email=user_info["email"],
            full_name=user_info.get("name"),
            photo_url=user_info.get("picture"),
            password="",  # No password for OAuth users
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
