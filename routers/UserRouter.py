from controllers.UserController import UserController
from sanic import Blueprint, response
from loguru import logger
from routers.middlewares import validateToken

class UserRouter:
    def __init__(self):
        self.blueprint = Blueprint("user", url_prefix = "/users")
        """acts as a route package object"""
        
        @self.blueprint.post("/login")
        async def user_login_request(request):
            return await UserController.login(request)
        
        @self.blueprint.post("/register")
        async def user_register_request(request):
            return await UserController.register(request)
        
        @self.blueprint.put("/edit")
        @validateToken
        async def user_edit_request(request):
            return await UserController.edit_user(request)
        
        logger.info("user routes have been set")