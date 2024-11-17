from sanic import response, Blueprint
from sanic.request import Request
import jwt
import os
from dotenv import load_dotenv
from typing import Callable

load_dotenv()

# Middleware decorator for specific routes
def validateToken(handler: Callable) -> Callable:
    async def middleware(request: Request, *args, **kwargs):
        token = request.cookies.get("authToken")
        if not token:
            return response.json({
                "success": False,
                "message": "invalid or non existant token"
            }, status=401)
        try:
            decoded_payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            request.ctx.user = decoded_payload
        except jwt.ExpiredSignatureError:
            return response.json({
                "success": False,
                "message": "invalid request with expired token"
            }, status=401)
        except jwt.InvalidTokenError:
            return response.json({
                "success": False,
                "message": "invalid token"
            }, status=401)
        
        response = await handler(request, *args, **kwargs)
        return response

    return middleware
