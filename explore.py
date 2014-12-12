from pymongo import MongoClient
import pickle
import sys

DATABASE_NAME = 'movie_cliches'
COLLECTION_NAME = 'scripts'


def connect_to_db(db=DATABASE_NAME, 
                  coll=COLLECTION_NAME):
    """ Keep this modular in case in the future I want to
    use a remote db, etc."""
    return MongoClient()[db][coll]


if __name__ == '__main__':

    db = connect_to_db()
    script = db.find_one()
    print script['genres']

    


