from mongoengine import Document, StringField


class Tribe(Document):
    meta = {"collection": "tribes"}
    name = StringField(required=True, unique=True)
    region = StringField(required=True)
    description = StringField()
