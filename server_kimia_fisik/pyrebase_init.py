import pyrebase
from dotenv import load_dotenv
from os import environ

config = {
    "apiKey": environ.get("firebase_apiKey"),
    "authDomain": environ.get("firebase_authDomain"),
    "projectId": environ.get("firebase_projectId"),
    "storageBucket": environ.get("firebase_storageBucket"),
    "messagingSenderId": environ.get("firebase_messagingSenderId"),
    "appId": environ.get("firebase_appId"),
    "measurementId": environ.get("firebase_measurementId"),
    "databaseURL": environ.get("firebase_databaseURL"),
}

load_dotenv("../.env")


def initialize_firebase():
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    db = firebase.database()
    return firebase, auth, db
