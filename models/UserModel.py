from models.PyObjectId import PyObjectId
import json

class UserModel:
    _id: PyObjectId
    def __init__(self, username : str, gmail : str, password : str):
        self.username : str = username
        self.gmail = gmail
        self.password : str | bytes = password
        
    def as_dict(self):
        return {
            "username": self.username,
            "gmail": self.gmail,
            "password": self.password.decode('utf-8') if isinstance(self.password, bytes) else self.password
        }
    
    def as_json(self):
        return json.dumps(self.as_dict())
    
    @staticmethod
    def parse_dict(dict):
        return UserModel(dict["username"], dict["gmail"], dict["password"])