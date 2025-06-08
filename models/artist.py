from mongoengine import Document, StringField, ReferenceField, ListField, IntField
from .tribe import Tribe


class Artist(Document):
    meta = {"collection": "artists"}
    name = StringField(required=True)
    bio = StringField()
    tribe = ReferenceField(Tribe, required=True)
    active_years = ListField(
        IntField(), min_length=2, max_length=2
    )  # e.g. [1930, 1960]
