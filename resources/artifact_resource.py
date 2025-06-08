from flask.views import MethodView
from flask_smorest import Blueprint, abort
from resources.auth_utils import admin_required
from models.artifact import Artifact
from models.artist import Artist
from schemas.artifact_schema import (
    ArtifactInSchema,
    ArtifactPatchSchema,
    ArtifactOutSchema,
)
from mongoengine.errors import ValidationError
from bson.errors import InvalidId

blp = Blueprint(
    "Artifacts",
    "artifacts",
    url_prefix="/api/v1/artifacts",
    description="Operations on Artifacts",
)


@blp.route("/")
class ArtifactsList(MethodView):
    @blp.response(200, ArtifactOutSchema(many=True))
    def get(self):
        return list(Artifact.objects.all())

    @admin_required
    @blp.arguments(ArtifactInSchema)
    @blp.response(201, ArtifactOutSchema)
    def post(self, data):
        try:
            artist = Artist.objects.get(id=data["artist"])
        except (Artist.DoesNotExist, ValidationError, InvalidId):
            abort(404, message="Artist not found.")
        artifact = Artifact(
            title=data["title"],
            description=data.get("description", ""),
            image_url=data.get("image_url", ""),
            artist=artist,
            era=data.get("era", ""),
            created_date=data.get("created_date"),
        ).save()
        return artifact


@blp.route("/<string:artifact_id>")
class ArtifactDetail(MethodView):
    @blp.response(200, ArtifactOutSchema)
    def get(self, artifact_id):
        try:
            return Artifact.objects.get(id=artifact_id)
        except (Artifact.DoesNotExist, ValidationError, InvalidId):
            abort(404, message="Artifact not found.")

    @admin_required
    @blp.arguments(ArtifactPatchSchema)
    @blp.response(200, ArtifactOutSchema)
    def put(self, data, artifact_id):
        try:
            art = Artifact.objects.get(id=artifact_id)
        except (Artifact.DoesNotExist, ValidationError, InvalidId):
            abort(404, message="Artifact not found.")
        if "artist" in data:
            try:
                data["artist"] = Artist.objects.get(id=data["artist"])
            except (Artist.DoesNotExist, ValidationError, InvalidId):
                abort(404, message="Artist not found.")
        art.update(**data)
        return Artifact.objects.get(id=artifact_id)

    @admin_required
    @blp.response(204)
    def delete(self, artifact_id):
        try:
            art = Artifact.objects.get(id=artifact_id)
        except (Artifact.DoesNotExist, ValidationError, InvalidId):
            abort(404, message="Artifact not found.")
        art.delete()
        return "", 204
