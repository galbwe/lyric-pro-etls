from abc import ABC

from pymongo import MongoClient

from lyric_pro_etls.models import Song


MONGO_DATABASE = "lyric_pro_etls"

MONGO_COLLECTION = "songs"


def make_connection_string():
    # TODO: add more parameters to this function
    return "mongodb://root:example@localhost:27017"


def make_mongo_client():
    uri = make_connection_string()
    return MongoClient(uri)


def get_collection(database, collection):
    return make_mongo_client()[database][collection]


def insert_song(song):
    songs = get_collection(MONGO_DATABASE, MONGO_COLLECTION)
    result = songs.insert_one(dict(song))
    return result.inserted_id


def get_song_by_slug(slug):
    songs = get_collection(MONGO_DATABASE, MONGO_COLLECTION)
    result = songs.find_one({"slug": slug})
    if result is None:
        return None
    result.pop("_id")
    return Song(**result)
