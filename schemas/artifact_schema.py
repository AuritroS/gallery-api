from marshmallow import Schema, fields
from schemas.artist_schema import ArtistOutSchema


class ArtifactInSchema(Schema):
    class Meta:
        name = "ArtifactIn"

    title = fields.String(required=True)
    description = fields.String()
    image_url = fields.String()
    artist = fields.String(required=True, metadata={"description": "Artist ID"})
    era = fields.String()
    created_date = fields.DateTime()


class ArtifactPatchSchema(Schema):
    class Meta:
        name = "ArtifactPatch"

    title = fields.String()
    description = fields.String()
    image_url = fields.String()
    artist = fields.String(metadata={"description": "Artist ID"})
    era = fields.String()
    created_date = fields.DateTime()


class ArtifactOutSchema(Schema):
    class Meta:
        name = "Artifact"

    id = fields.String(dump_only=True, data_key="id")
    title = fields.String()
    description = fields.String()
    image_url = fields.String()
    era = fields.String()
    created_date = fields.DateTime()
    artist_info = fields.Nested(ArtistOutSchema, dump_only=True, attribute="artist")
