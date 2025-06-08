# models/user.py
from mongoengine import Document, StringField
from werkzeug.security import generate_password_hash, check_password_hash


class User(Document):
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    role = StringField(choices=("user", "admin"), default="user")

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)
