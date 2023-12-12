from flask import Blueprint, render_template, redirect, request, session
from .pyrebase_init import (
    create_new_user,
    login_firebase,
    reset_password,
    verify_status,
    update_verify_status_db,
)

main = Blueprint("main", __name__)


@main.route("/")
def index():
    if "user" in session and "akun" in session:
        return redirect("home")
    else:
        return redirect("login")


@main.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session and "akun" in session:
        return redirect("home")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        session["akun"], session["user"] = login_firebase(email, password)
        try:
            if verify_status(session["akun"]) == True:
                update_verify_status_db(email, session["akun"])
                return redirect("home")
            else:
                session.pop("user")
                session.pop("akun")
                return render_template("auth.html", error="Verify your email")
        except:
            return render_template("auth.html", error="Wrong Email or Password")
    return render_template("auth.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if "user" in session and "akun" in session:
        return redirect("home")
    if request.method == "POST":
        reg_email = request.form.get("registration_email")
        reg_pass = request.form.get("password")
        reg_rep_pass = request.form.get("repeat_password")
        try:
            if reg_pass == reg_rep_pass:
                create_new_user(reg_email, reg_pass)
                return redirect("login")
            else:
                return render_template("register.html", error="Passwords do not match")
        except:
            return render_template("register.html", error="Account already exists")
    return render_template("register.html")


@main.route("/resetpassword", methods=["GET", "POST"])
def resetpassword():
    if "user" in session:
        return redirect("home")
    if request.method == "POST":
        email_to_reset = request.form.get("email")
        reset_password(email_to_reset)
        return redirect("login")
    return render_template("reset.html")


@main.route("/home", methods=["GET"])
def home():
    return render_template("home.html")


@main.route("/submit/<software>", methods=["GET", "POST"])
def submit(software):
    return redirect("login")


@main.route("/jsme/<software>", methods=["POST"])
def jsme(software):
    return redirect("auth")


@main.route("/queue")
def queue():
    return redirect("login")


@main.route("/result")
def result():
    return redirect("login")


@main.route("/result/<folder_name>", methods=["GET"])
def result_folder(folder_name):
    return redirect("login")


@main.route("/download/<folder>/<name>", methods=["GET"])
def download(folder, name):
    return redirect("login")


@main.route("/profile")
def profile():
    return redirect("login")


@main.route("/logout", methods=["GET"])
def logout():
    if "user" not in session and "akun" not in session:
        return redirect("login")
    else:
        session.pop("akun")
        session.pop("user")
        return redirect("login")


@main.errorhandler(404)
def page_not_exist(e):
    return redirect("/")


@main.errorhandler(405)
def page_not_found(e):
    return redirect("/")
