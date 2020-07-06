from peewee import *
import datetime


db = SqliteDatabase("data.db")


class BaseModel(Model):
    class Meta:
        database = db


class Thing(BaseModel):
    id = IntegerField(primary_key=True)
    name = TextField(null=True)
    ingested_at = DateTimeField(default=datetime.datetime.now)
    created_at = DateTimeField(null=True)
    state = TextField(null=False)
