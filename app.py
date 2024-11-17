import asyncio
from sanic import Sanic
from dotenv import load_dotenv
import os
from sanic_cors import CORS
from loguru import logger
from database.ConnectToDatabase import connectToDatabase
from routers.UserRouter import UserRouter
import sys
from myWebsockets import WebsocketsConfig
from sanic.server.protocols.websocket_protocol import WebSocketProtocol

load_dotenv()

app = Sanic("vitalGuard-server")

CORS(app, resources={
    r"/*": {
        "origins": [os.getenv("DOMAIN_ALLOWED")],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        "allow_headers": ["Content-Type", "authorization"],
        "supports_credentials": True
    }
})

db = connectToDatabase()

if db is None:
    logger.error("closing app without database connection")
    sys.exit(1)
    
app.blueprint(UserRouter(db).blueprint)

WebsocketsConfig(app)

if __name__ == "__main__":
    app.run(
        host=os.getenv("API_HOST"),
        port=int(os.getenv("API_PORT")),
        protocol=WebSocketProtocol,
        dev=True,
    )
