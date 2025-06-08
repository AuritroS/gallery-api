import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from mongoengine import connect, get_db
import certifi

load_dotenv()
app = Flask(__name__)


# ─── Mongo
def _mongo_tls_enabled() -> bool:
    return os.getenv("MONGO_TLS", "true").lower() == "true"


connect(
    host=os.getenv("MONGO_URI"),
    uuidRepresentation="standard",
    tls=_mongo_tls_enabled(),
tlsCAFile=certifi.where() if _mongo_tls_enabled() else None,

)

# ─── JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

# ─── Basic Swagger info
app.config.update(
    API_TITLE="Aboriginal Art API",
    API_VERSION="1.0",
    OPENAPI_VERSION="3.0.2",
    OPENAPI_URL_PREFIX="",
    OPENAPI_JSON_PATH="openapi.json",
    OPENAPI_SWAGGER_UI_PATH="docs",
    OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.18.0/",
)

# ─── BearerAuth scheme & global requirement
security_schemes = {
    "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
}
global_security = [{"BearerAuth": []}]

api = Api(
    app,
    spec_kwargs={
        "components": {"securitySchemes": security_schemes},
        "security": global_security,
    },
)

# ─── Blueprint registration
from resources.auth_resource import blp as AuthBlueprint
from resources.tribe_resource import blp as TribeBlueprint
from resources.artist_resource import blp as ArtistBlueprint
from resources.artifact_resource import blp as ArtifactBlueprint

api.register_blueprint(AuthBlueprint)
api.register_blueprint(TribeBlueprint)
api.register_blueprint(ArtistBlueprint)
api.register_blueprint(ArtifactBlueprint)


# ─── Simple health & root
@app.get("/")
def index():
    return jsonify(status="OK", message="Server is running")


@app.get("/health/db")
def db_health():
    try:
        return jsonify(db_status="OK", collections=get_db().list_collection_names())
    except Exception as e:
        return jsonify(db_status="ERROR", error=str(e)), 500


if __name__ == "__main__":
    app.run(port=5001, debug=True)
