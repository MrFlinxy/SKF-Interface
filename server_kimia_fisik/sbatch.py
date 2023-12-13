from os import environ, path
from dotenv import load_dotenv
from .email_preprocess import email_at_to_underscore_and_remove_dot
from .pyrebase_init import user_folder_name

load_dotenv(".env")

orca_full_path = environ.get("orca_fullPath")
gaussian_full_path = environ.get("gaussian_fullPath")
orca_cpus_per_job = environ.get("orca_cpus_per_job")
gaussian_cpus_per_job = environ.get("gaussian_cpus_per_job")

sbatch_header = f"""#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={orca_cpus_per_job}"""

orca_export = """export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export PATH=/usr/local/bin/:$PATH
export OMP_NUM_THREADS=1"""

gaussian_export = """"""


def orca_submit(folder_path, filename, email, session):
    # Creating sbatch shell script file
    file_path = path.join(folder_path, user_folder_name(email, session), filename)
    orca_cmd = f"{orca_full_path} {file_path}_.inp > {file_path}.out --oversubscribe"
    sbatch_content = f"""{sbatch_header}\n\n{orca_export}\n\n{orca_cmd}"""

    folder_name = user_folder_name(email, session)
    email_sbatch = email_at_to_underscore_and_remove_dot(email)[0:4]
    sbatch_file = path.join(file_path, email_sbatch)
    print(sbatch_file)
    with open(
        f"user_data/{folder_name}/{filename}/{email_sbatch}***.sh",
        "w",
    ) as sbatch:
        sbatch.write(sbatch_content)
    # Running sbatch


def orca_jsme(orca_path):
    pass


def gaussian_submit():
    pass


def gaussian_jsme():
    pass
