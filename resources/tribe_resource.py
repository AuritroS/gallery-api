from flask.views import MethodView
from flask_smorest import Blueprint, abort
from resources.auth_utils import admin_required
from models.tribe import Tribe
from schemas.tribe_schema import TribeInSchema, TribePatchSchema, TribeOutSchema
from mongoengine.errors import ValidationError
from bson.errors import InvalidId

blp = Blueprint(
    "Tribes",
    "tribes",
    url_prefix="/api/v1/tribes",
    description="Operations on Aboriginal Tribes",
)


@blp.route("/")
class TribesList(MethodView):
    @blp.response(200, TribeOutSchema(many=True))
    def get(self):
        return list(Tribe.objects.all())

    @admin_required
    @blp.arguments(TribeInSchema)
    @blp.response(201, TribeOutSchema)
    def post(self, new_data):
        return Tribe(**new_data).save()


@blp.route("/<string:tribe_id>")
class TribeDetail(MethodView):
    @blp.response(200, TribeOutSchema)
    def get(self, tribe_id):
        try:
            return Tribe.objects.get(id=tribe_id)
        except (Tribe.DoesNotExist, ValidationError, InvalidId):
            abort(404, message="Tribe not found.")

    @admin_required
    @blp.arguments(TribePatchSchema)
    @blp.response(200, TribeOutSchema)
    def put(self, update_data, tribe_id):
        try:
            tribe_obj = Tribe.objects.get(id=tribe_id)
        except (Tribe.DoesNotExist, ValidationError, InvalidId):
            abort(404, message="Tribe not found.")
        tribe_obj.update(**update_data)
        return Tribe.objects.get(id=tribe_id)

    @admin_required
    @blp.response(204)
    def delete(self, tribe_id):
        try:
            tribe_obj = Tribe.objects.get(id=tribe_id)
        except (Tribe.DoesNotExist, ValidationError, InvalidId):
            abort(404, message="Tribe not found.")
        tribe_obj.delete()
        return "", 204
