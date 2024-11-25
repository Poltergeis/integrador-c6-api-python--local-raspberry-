import asyncio
from sanic import Sanic
from dotenv import load_dotenv
import os
from sanic_cors import CORS
from loguru import logger
from database.ConnectToDatabase import connectToDatabase
from routers.UserRouter import UserRouter
from auth import auth_bp

load_dotenv()

app = Sanic("vitalGuard-server")

CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        "allow_headers": ["Content-Type", "authorization"],
        "supports_credentials": True
    }
})

connectToDatabase(app)
    
app.blueprint(UserRouter().blueprint)
app.blueprint(auth_bp)

if __name__ == "__main__":
    app.run(
        host=os.getenv("API_HOST"),
        port=int(os.getenv("API_PORT")),
        dev=True,
    )
