from peewee import *
from models import Thing


db = SqliteDatabase("data.db")

db.connect()
db.create_tables([Thing])
