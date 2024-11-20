from tortoise import fields
from tortoise.models import Model
import json

class UserModel(Model):
    id = fields.IntField(pk=True)
    gmail = fields.CharField(max_length=100)
    password = fields.CharField(max_length=255)
    
    class Meta:
        table = "users"

    def as_dict(self):
        return {
            "id": self.id,
            "gmail": self.gmail,
            "password": self.password,
        }

    def as_json(self):
        return json.dumps(self.as_dict())

    @staticmethod
    def parse_dict(data: dict):
        return UserModel(
            gmail=data["gmail"],
            password=data["password"],
        )

class TemperaturaModel(Model):
    id = fields.IntField(pk=True)
    