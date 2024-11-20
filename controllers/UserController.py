from sanic.request import Request
from sanic import response
from models.models import UserModel
from controllers import validations
from loguru import logger
import bleach
import bcrypt
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

class UserController:
    
    @staticmethod
    async def login(request : Request):
        try:
            gmail : str = request.json.get("gmail", "")
            password : str = request.json.get("password", "")
            if gmail is None or password is None:
                return response.json({
                    "success": False,
                    "message": "gmail and password cannot be empty"
                }, status=400)
            gmail = gmail.strip()
            password = password.strip()
            safeGmail = bleach.clean(text=gmail, strip=True)
            safePassword = bleach.clean(text=password, strip=False)
            if not validations.validate_email(safeGmail) or not validations.validate_safe_string(safePassword):
                return response.json({
                    "success": False,
                    "message": "request data is invalid or malformed"
                }, status=400)
            foundUser : UserModel = await UserModel.filter(gmail = safeGmail).first()
            if foundUser is None:
                return response.json({
                    "success": False,
                    "message": "user was not found"
                }, status=404)
            if not bcrypt.checkpw(safePassword.encode('utf-8'), foundUser.password.encode('utf-8')):
                return response.json({
                    "success": False,
                    "message": "invalid password"
                }, status=400)
            token = jwt.encode(foundUser.as_dict(), os.getenv("JWT_SECRET"), algorithm="HS256")
            res = response.json({
                "success": True,
                "message": "user found",
            }, status=200)
            res.cookies["authToken"] = token
            res.cookies['authToken']['httponly'] = True
            res.cookies['authToken']['samesite'] = 'strict'
            res.cookies['authToken']["max-age"] = 86400
            return res
        except Exception as e:
            logger.error(f"internal server error.\n{e}")
            return response.json(body={
                "success": False,
                "message": f"internal server error.\n{e}"
            }, status=500)
    
    @staticmethod
    async def register(request : Request):
        try:
            gmail = request.json.get("gmail", "").strip()
            password = request.json.get("password", "").strip()
            if not validations.validate_existing_strings([gmail,password]):
                return response.json({
                    "success": False,
                    "message": "username, email and password cannot be empty"
                }, status=400)
            safeGmail = bleach.clean(text=gmail, strip=True)
            safePassword = bleach.clean(text=password, strip=False)
            if not (validations.validate_email(safeGmail) or validations.validate_safe_string(safePassword)):
                return response.json({
                    "success": False,
                    "message": "request data is invalid or malformed"
                }, status=400)
            hashedPassword = bcrypt.hashpw(safePassword.encode('utf-8'), bcrypt.gensalt())
            newUser = await UserModel.create(gmail = safeGmail, password = hashedPassword.decode())
            if newUser is None:
                return response.json({
                    "success": False,
                    "message": "couldn't create a new user"
                }, status=400)
            return response.json({
                "success": True,
                "message": "new user created and saved",
                "user": newUser.as_dict()
            })
        except Exception as e:
            logger.error(f"internal server error.\n{e}")
            return response.json({
                "success": False,
                "message": f"internal server error.\n{e}"
            }, status=500)
    
    @staticmethod
    async def edit_user(request : Request):
        try:
            id = request.ctx.user.id
            newPassword = request.json.get("newPassword", "")
            if id is None or newPassword is None:
                return response.json({
                    "success": False,
                    "message": "request data incomplete, userId and the new Password cannot be empty"
                }, status=400)
            safe_id = bleach.clean(text=id, strip=True)
            safeNewPassword = bleach.clean(text=safeNewPassword, strip=False)
            if safe_id is None or safeNewPassword is None:
                return response.json({
                    "success": False,
                    "message": "user request is malformed or non secure"
                })
            updatedUser = await UserModel.get(id = id)
            if updatedUser is None:
                return response.json({
                    "success": False,
                    "message": "User not found"
                }, status=404)
            updatedUser.password = bcrypt.hashpw(safeNewPassword.encode("utf-8"), bcrypt.gensalt())
            await updatedUser.save()
            return response.json({
                "success": True,
                "message": "User updated successfully"
            }, status=200)
        except Exception as e:
            logger.error(f"internal server error.\n{e}")
            return response.json({
                "success": False,
                "message": f"internal server error.\n{e}"
            }, status=500)
    
    @staticmethod
    async def delete_user(request : Request):
        return ""