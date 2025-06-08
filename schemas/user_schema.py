from marshmallow import Schema, fields


class UserRegisterSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)


class UserOutSchema(Schema):
    id = fields.String(dump_only=True, data_key="id")
    username = fields.String()
