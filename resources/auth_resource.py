from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import jsonify
from flask_jwt_extended import create_access_token
from models.user import User
from schemas.user_schema import UserRegisterSchema, UserOutSchema

blp = Blueprint("Auth", "auth", url_prefix="/auth", description="Authentication")


@blp.route("/register")
class Register(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, UserOutSchema)
    def post(self, data):
        if User.objects(username=data["username"]).first():
            abort(400, message="Username already exists.")
        user = User(username=data["username"])
        user.set_password(data["password"])
        user.save()
        return user


@blp.route("/login")
class Login(MethodView):
    @blp.arguments(UserRegisterSchema)
    def post(self, data):
        user = User.objects(username=data["username"]).first()
        if not user or not user.check_password(data["password"]):
            abort(401, message="Bad credentials")
        token = create_access_token(
            identity=str(user.id), additional_claims={"role": user.role}
        )
        return jsonify(access_token=token)
