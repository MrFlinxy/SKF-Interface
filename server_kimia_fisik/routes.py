from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, request, send_file, session
from json import load
from os import mkdir, getcwd, listdir, path, system
from re import search
from .pyrebase_init import (
    create_new_user,
    extend_token,
    login_firebase,
    reset_password,
    verify_status,
    update_verify_status_db,
    user_folder_name,
)
from .sbatch import orca_submit, orca_jsme


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
            orca_submit(
                request.files["file"],
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
            smiles = request.form.get("smiles")
            jsme_nama = request.form.get("nama_file")
            calc_type = request.form.get("calc_type")
            basis_set = request.form.get("basis_set")
            teori = request.form.get("teori")
            muatan = request.form.get("muatan")
            multiplisitas = request.form.get("multiplisitas")
            orbital = request.form.get("orbital")
            folder_name = user_folder_name(session["user"], session["akun"])
            orca_jsme(
                smiles,
                jsme_nama,
                calc_type,
                basis_set,
                teori,
                muatan,
                multiplisitas,
                orbital,
                folder_name,
                session["user"],
                session["akun"],
            )
            return render_template("submit_ORCA.html")
        if request.method == "POST" and software == "Gaussian":
            return render_template("submit_Gaussian.html")
    else:
        return redirect("login")


@main.route("/queue")
def queue():
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        system(f"squeue --json > squeue.json")
        with open("squeue.json", "r") as f:
            data = load(f)
            result = []
            queues_len = 0
            if data["jobs"] == []:
                return render_template(
                    "queue.html",
                    message="Tidak ada antrian komputasi",
                    queues=result,
                    queues_len=range(queues_len),
                )
            else:
                for i in range(len(data["jobs"])):
                    # Extracting the data from json
                    job_name = data["jobs"][i]["name"][:-3]
                    job_status = data["jobs"][i]["job_state"]
                    job_submit_time = data["jobs"][i]["submit_time"]

                    # Converting the data into human-readable format
                    job_submit_time_hms = datetime.fromtimestamp(
                        job_submit_time
                    ).strftime("%d-%m-%Y %H:%M:%S")

                    # Collecting time data at now
                    now_time = datetime.now().timestamp()

                    # Subtracting the now with job submitted to get the job time
                    job_runtime_epoch = int(now_time - job_submit_time)

                    # Formatting the job time in HH:MM:SS
                    job_runtime_hms = str(timedelta(seconds=job_runtime_epoch))

                    # Result list
                    result_i = [
                        job_name,
                        job_status,
                        job_submit_time_hms,
                        job_runtime_hms,
                    ]
                    result.append(result_i)
                    queues_len = len(result)
        return render_template(
            "queue.html", queues=result, queues_len=range(queues_len)
        )
    else:
        return redirect("login")


@main.route("/result")
def result():
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        user_folder = user_folder_name(session["user"], session["akun"])
        listdir_user_data = listdir(f"user_data/{user_folder}")
        if len(listdir_user_data) != 0:
            return render_template("result.html", hasil=listdir_user_data)
        else:
            return render_template(
                "result.html", error="Tidak ada hasil Komputasi", show="."
            )
    else:
        return redirect("login")


@main.route("/result/<folder_name>", methods=["GET"])
def result_folder(folder_name):
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        user_folder = user_folder_name(session["user"], session["akun"])
        folder = f"user_data/{user_folder}/{folder_name}"
        result = listdir(folder)
        # Filtering
        res = []
        for i in result:
            tmp = search("\.tmp$", i)
            sh = search("\.sh$", i)
            smi = search("\.smi$", i)
            smix = search("_smi\.xyz$", i)
            if sh == None and tmp == None and smi == None and smix == None:
                res.append(i)
        return render_template("result_files.html", hasil=res, nama_folder=folder_name)
    else:
        return redirect("login")


@main.route("/download/<folder>/<name>", methods=["GET"])
def download(folder, name):
    if "user" in session and "akun" in session:
        session["akun"] = extend_token(session["akun"])
        user_folder = user_folder_name(session["user"], session["akun"])
        file_path = f"../user_data/{user_folder}/{folder}/{name}"
        return send_file(file_path, as_attachment=True)
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
