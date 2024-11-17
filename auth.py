from sanic import Blueprint, response
from routers.middlewares import validateToken

auth_bp = Blueprint("auth", url_prefix="/auth")

@auth_bp.get("/")
@validateToken
async def checkToken(request):
    try:
        return response.json({
            "success": True,
            "message": "user authenticated"
        }, status=200)
    except Exception as e:
        return response.json({
            "success": False,
            "message": "internal server error during token verification"
        }, status=500)