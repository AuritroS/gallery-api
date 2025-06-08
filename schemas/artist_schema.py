from marshmallow import Schema, fields
from schemas.tribe_schema import TribeOutSchema


class ArtistInSchema(Schema):
    class Meta:
        name = "ArtistIn"

    name = fields.String(required=True)
    bio = fields.String()
    tribe = fields.String(required=True, metadata={"description": "Tribe ID"})
    active_years = fields.List(fields.Integer(), required=True)


class ArtistPatchSchema(Schema):
    class Meta:
        name = "ArtistPatch"

    name = fields.String()
    bio = fields.String()
    tribe = fields.String(metadata={"description": "Tribe ID"})
    active_years = fields.List(fields.Integer())


class ArtistOutSchema(Schema):
    class Meta:
        name = "Artist"

    id = fields.String(dump_only=True, data_key="id")
    name = fields.String()
    bio = fields.String()
    active_years = fields.List(fields.Integer())
    tribe_info = fields.Nested(TribeOutSchema, dump_only=True, attribute="tribe")
