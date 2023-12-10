from flask import Blueprint, render_template, redirect

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("home.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    return render_template("auth.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")


@main.route("/resetpassword", methods=["GET", "POST"])
def resetpassword():
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
    return redirect("/")


@main.errorhandler(404)
def page_not_exist(e):
    return redirect("/")


@main.errorhandler(405)
def page_not_found(e):
    return redirect("/")
