from marshmallow import Schema, fields


class TribeInSchema(Schema):
    class Meta:
        name = "TribeIn"

    name = fields.String(required=True)
    region = fields.String(required=True)
    description = fields.String()


class TribePatchSchema(Schema):
    class Meta:
        name = "TribePatch"

    name = fields.String()
    region = fields.String()
    description = fields.String()


class TribeOutSchema(Schema):
    class Meta:
        name = "Tribe"

    id = fields.String(dump_only=True, data_key="id")
    name = fields.String()
    region = fields.String()
    description = fields.String()
