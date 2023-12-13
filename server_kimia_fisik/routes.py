from flask import Blueprint, render_template, redirect, request, session
from os import mkdir, getcwd, path
from re import sub
from .pyrebase_init import (
    create_new_user,
    extend_token,
    login_firebase,
    reset_password,
    verify_status,
    update_verify_status_db,
    user_folder_name,
)
from .sbatch import orca_submit


main = Blueprint("main", __name__)


def pop_session():
    session.pop("user")
    session.pop("akun")


@main.route("/")
def index():
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        return redirect("home")
    else:
        return redirect("login")


@main.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        return redirect("home")
    if request.method == "GET":
        return render_template("auth.html")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        session["akun"], session["user"] = login_firebase(email, password)
        try:
            if verify_status(session["akun"]) == True:
                update_verify_status_db(email, session["akun"])
                folder_path = path.join(getcwd(), "user_data")
                user_folder = path.join(
                    folder_path, user_folder_name(email, session["akun"])
                )
                try:
                    try:
                        mkdir(folder_path)
                        mkdir(user_folder)
                    except OSError:
                        pass
                    return redirect("home")
                except:
                    pop_session()
                    return render_template("auth.html", error="Try again")
            else:
                pop_session()
                return render_template("auth.html", error="Verify your email")
        except:
            pop_session()
            return render_template("auth.html", error="Try again")
    else:
        return render_template("auth.html", error="Wrong Email or Password")


@main.route("/register", methods=["GET", "POST"])
def register():
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
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
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        return redirect("home")
    if request.method == "POST":
        email_to_reset = request.form.get("email")
        reset_password(email_to_reset)
        return redirect("login")
    return render_template("reset.html")


@main.route("/home", methods=["GET"])
def home():
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        return render_template("home.html")
    else:
        return redirect("login")


@main.route("/submit/<software>", methods=["GET", "POST"])
def submit(software):
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        if request.method == "GET" and software == "menu":
            return render_template("submit_software.html")

        if request.method == "GET" and software == "ORCA":
            return render_template("submit_ORCA.html")
        if request.method == "POST" and software == "ORCA":
            # Upload file and create file folder
            file = request.files["file"]
            filename = file.filename
            folder_path = path.join(getcwd(), "user_data")
            user_folder = path.join(
                folder_path, user_folder_name(session["user"], session["akun"])
            )
            try:
                file_folder = path.join(user_folder, filename[:-4])
                mkdir(file_folder)
            except FileExistsError:
                pass
            file.save(path.join(file_folder, filename))

            # File content edit
            file_edit = path.join(file_folder, filename)
            new_file = path.join(file_folder, f"{filename[:-4]}_.inp")
            with open(new_file, "w") as f:
                for line in open(str(file_edit), "r").readlines():
                    line = sub(r"nprocs.+", r"nprocs 4", line)
                    line = sub(r"%maxcore.+", r"%maxcore 2048", line)
                    f.write(line)
            orca_submit(
                folder_path,
                filename[:-4],
                session["user"],
                session["akun"],
            )
            return redirect("ORCA")

        if request.method == "GET" and software == "Gaussian":
            return render_template("submit_Gaussian.html")
        if request.method == "POST" and software == "Gaussian":
            return redirect("Gaussian")
    else:
        return redirect("login")


@main.route("/jsme/<software>", methods=["POST"])
def jsme(software):
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        if request.method == "POST" and software == "ORCA":
            return render_template("submit_ORCA.html")
        if request.method == "POST" and software == "Gaussian":
            return render_template("submit_Gaussian.html")
    else:
        return redirect("login")


@main.route("/queue")
def queue():
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        return render_template("queue.html")
    else:
        return redirect("login")


@main.route("/result")
def result():
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        return render_template("result.html")
    else:
        return redirect("login")


@main.route("/result/<folder_name>", methods=["GET"])
def result_folder(folder_name):
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        return render_template("result_files.html")
    else:
        return redirect("login")


@main.route("/download/<folder>/<name>", methods=["GET"])
def download(folder, name):
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        return render_template("home.html")
    else:
        return redirect("login")


@main.route("/profile")
def profile():
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        return render_template("profile.html")
    else:
        return redirect("login")


@main.route("/logout", methods=["GET"])
def logout():
    if "user" not in session and "akun" not in session:
        session["akun"] = extend_token(session["akun"])
        return redirect("login")
    else:
        pop_session()
        return redirect("login")


@main.errorhandler(404)
def page_not_exist(e):
    return redirect("/")


@main.errorhandler(405)
def page_not_found(e):
    return redirect("/")
