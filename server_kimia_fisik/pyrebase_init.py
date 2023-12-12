import pyrebase
from dotenv import load_dotenv
from os import environ
from .email_preprocess import email_dot_to_comma

load_dotenv(".env")

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

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()


def create_new_user(email, password):
    user = auth.create_user_with_email_and_password(email, password)
    auth.send_email_verification(user["idToken"])
    data = {
        "admin": False,
        "email": email,
        "verified": False,
    }
    db.child("user_data").child(f"{email_dot_to_comma(email)}").set(data)


def login_firebase(email, password):
    user = auth.sign_in_with_email_and_password(email, password)
    return user, email


def account_info(session_akun):
    account_info = auth.get_account_info(session_akun["idToken"])
    return account_info


def reset_password(email):
    auth.send_password_reset_email(email)
