from mongoengine import Document, StringField, ReferenceField, DateTimeField
from .artist import Artist


class Artifact(Document):
    meta = {"collection": "artifacts"}
    title = StringField(required=True)
    description = StringField()
    image_url = StringField()
    artist = ReferenceField(Artist, required=True)
    era = StringField()  # e.g. "Contemporary"
    created_date = DateTimeField()  # e.g. datetime.datetime(2024, 5, 1)
