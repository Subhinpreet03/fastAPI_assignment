from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from routers import auth, users, coins, weather
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🔹 Add Session Middleware (REQUIRED for OAuth)
app.add_middleware(SessionMiddleware, secret_key="secret_key")


ALLOWED_HOSTS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(coins.router)
app.include_router(weather.router)

@app.get("/")
def home():
    return {"message": "Welcome to FastAPI"}
