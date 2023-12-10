from dotenv import load_dotenv
from flask import Flask
from os import environ
from .routes import main

load_dotenv("../.env")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = environ.get("secretKey")
    app.register_blueprint(main)
    return app
