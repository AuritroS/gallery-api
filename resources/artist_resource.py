from flask.views import MethodView
from flask_smorest import Blueprint, abort
from resources.auth_utils import admin_required
from models.artist import Artist
from models.tribe import Tribe
from schemas.artist_schema import ArtistInSchema, ArtistPatchSchema, ArtistOutSchema
from mongoengine.errors import ValidationError
from bson.errors import InvalidId

blp = Blueprint(
    "Artists",
    "artists",
    url_prefix="/api/v1/artists",
    description="Operations on Aboriginal Artists",
)


@blp.route("/")
class ArtistsList(MethodView):
    @blp.response(200, ArtistOutSchema(many=True))
    def get(self):
        return list(Artist.objects.all())

    @admin_required
    @blp.arguments(ArtistInSchema)
    @blp.response(201, ArtistOutSchema)
    def post(self, artist_data):
        try:
            tribe = Tribe.objects.get(id=artist_data["tribe"])
        except (Tribe.DoesNotExist, ValidationError, InvalidId):
            abort(404, message="Tribe not found.")
        artist = Artist(
            name=artist_data["name"],
            bio=artist_data.get("bio", ""),
            tribe=tribe,
            active_years=artist_data["active_years"],
        ).save()
        return artist


@blp.route("/<string:artist_id>")
class ArtistDetail(MethodView):
    @blp.response(200, ArtistOutSchema)
    def get(self, artist_id):
        try:
            return Artist.objects.get(id=artist_id)
        except (Artist.DoesNotExist, ValidationError, InvalidId):
            abort(404, message="Artist not found.")

    @admin_required
    @blp.arguments(ArtistPatchSchema)
    @blp.response(200, ArtistOutSchema)
    def put(self, update_data, artist_id):
        try:
            artist = Artist.objects.get(id=artist_id)
        except (Artist.DoesNotExist, ValidationError, InvalidId):
            abort(404, message="Artist not found.")
        if "tribe" in update_data:
            try:
                update_data["tribe"] = Tribe.objects.get(id=update_data["tribe"])
            except (Tribe.DoesNotExist, ValidationError, InvalidId):
                abort(404, message="Tribe not found.")
        artist.update(**update_data)
        return Artist.objects.get(id=artist_id)

    @admin_required
    @blp.response(204)
    def delete(self, artist_id):
        try:
            artist = Artist.objects.get(id=artist_id)
        except (Artist.DoesNotExist, ValidationError, InvalidId):
            abort(404, message="Artist not found.")
        artist.delete()
        return "", 204
