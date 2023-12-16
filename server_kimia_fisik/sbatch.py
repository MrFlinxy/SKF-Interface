from os import environ, getcwd, mkdir, path
from dotenv import load_dotenv
from re import sub
from subprocess import PIPE, Popen
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

gaussian_export = """export GAUSS_EXEDIR=$g09root/g09"""


def orca_submit(file, email, session):
    # Upload file
    filename = file.filename
    folder_path = path.join(getcwd(), "user_data")
    user_folder = path.join(folder_path, user_folder_name(email, session))
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
            line = sub(r"nprocs.+", rf"nprocs {orca_cpus_per_job}", line)
            line = sub(r"%maxcore.+", r"%maxcore 2048", line)
            f.write(line)
    # Creating sbatch contents
    file_path = path.join(folder_path, user_folder_name(email, session), filename[:-4])
    orca_cmd = f"{orca_full_path} {file_path}/{filename[:-4]}_.inp > {file_path}/{filename[:-4]}.out --oversubscribe"
    sbatch_content = f"""{sbatch_header}\n\n{orca_export}\n\n{orca_cmd}"""

    # Creating sbatch shell script file
    folder_name = user_folder_name(email, session)
    email_sbatch = email_at_to_underscore_and_remove_dot(email)[0:4]
    with open(
        f"user_data/{folder_name}/{filename[:-4]}/{email_sbatch}***.sh",
        "w",
    ) as sbatch:
        sbatch.write(sbatch_content)

    # Running sbatch
    Popen(
        [
            "sbatch",
            "--output=/dev/null",
            "--error=/dev/null",
            f"user_data/{folder_name}/{filename[:-4]}/{email_sbatch}***.sh",
        ]
    )


def orca_jsme(
    smiles,
    jsme_nama,
    calc_type,
    basis_set,
    teori,
    muatan,
    multiplisitas,
    orbital,
    folder_name,
    email,
    session,
):
    try:
        mkdir(f"user_data/{folder_name}/{jsme_nama}")
    except FileExistsError:
        pass

    with open(f"user_data/{folder_name}/{jsme_nama}/{jsme_nama}.smi", "w") as f:
        f.write(smiles)

    p = (
        Popen(
            [
                "obabel",
                "-ismi",
                f"user_data/{folder_name}/{jsme_nama}/{jsme_nama}.smi",
                "-oxyz",
                f"-Ouser_data/{folder_name}/{jsme_nama}/{jsme_nama}_smi.xyz",
                "--gen3d",
            ],
            stdout=PIPE,
        )
        .communicate()[0]
        .decode("utf-8")
    )

    with open(
        f"user_data/{folder_name}/{jsme_nama}/{jsme_nama}_smi.xyz", "r"
    ) as coord_xyz:
        dummy0 = coord_xyz.readline()
        dummy1 = coord_xyz.readline()
        lines = coord_xyz.read()
        koordinat = lines

    # ORCA Input
    if orbital != None:
        orbital_inp = f"""%output
   print[p_mos] 1
   print[p_basis] 2
end"""
    else:
        orbital_inp = ""

    orca_inp = f"""# Input File Orca | Server Kimia Fisik
#
! {calc_type} {teori} {basis_set} 

%maxcore 2048

{orbital_inp}

%pal
   nprocs {orca_cpus_per_job}
end

* xyz {muatan} {multiplisitas}
{koordinat}
*
"""
    with open(f"user_data/{folder_name}/{jsme_nama}/{jsme_nama}.inp", "w") as f:
        f.write(orca_inp)

    orca_cmd = f"{orca_full_path} user_data/{folder_name}/{jsme_nama}/{jsme_nama}.inp > user_data/{folder_name}/{jsme_nama}/{jsme_nama}.out --oversubscribe"
    sbatch_content = f"""{sbatch_header}\n\n{orca_export}\n\n{orca_cmd}"""

    # Creating sbatch shell script file
    folder_name = user_folder_name(email, session)
    email_sbatch = email_at_to_underscore_and_remove_dot(email)[0:4]
    with open(
        f"user_data/{folder_name}/{jsme_nama}/{email_sbatch}***.sh",
        "w",
    ) as sbatch:
        sbatch.write(sbatch_content)

    # Running sbatch
    Popen(
        [
            "sbatch",
            "--output=/dev/null",
            "--error=/dev/null",
            f"user_data/{folder_name}/{jsme_nama}/{email_sbatch}***.sh",
        ]
    )


def gaussian_submit(file, email, session):
    # Upload file
    filename = file.filename
    folder_path = path.join(getcwd(), "user_data")
    user_folder = path.join(folder_path, user_folder_name(email, session))
    folder_name = user_folder_name(email, session)
    get_cwd = getcwd()
    try:
        file_folder = path.join(user_folder, filename[:-4])
        mkdir(file_folder)
    except FileExistsError:
        pass
    file.save(path.join(file_folder, filename))
    # File content edit
    file_edit = path.join(file_folder, filename)
    new_file = path.join(file_folder, f"{filename[:-4]}_.gjf")
    with open(new_file, "w") as f:
        for line in open(str(file_edit), "r").readlines():
            line = sub(
                r"%NProcShared=.+", rf"%NProcShared={gaussian_cpus_per_job}", line
            )
            line = sub(r"%mem=.+", r"%mem=2GB", line)
            line = sub(
                r"%Chk=.+",
                rf"%chk={get_cwd}/user_data/{folder_name}/{filename[:-4]}/{filename[:-4]}.chk\n%RWF={getcwd()}/user_data/{folder_name}/{filename[:-4]}/{filename[:-4]}.rwf",
                line,
            )
            f.write(line)
    # Creating sbatch contents
    file_path = path.join(folder_path, user_folder_name(email, session), filename[:-4])
    gaussian_cmd = f"{gaussian_full_path} < {file_path}/{filename[:-4]}_.gjf > {file_path}/{filename[:-4]}.out"
    sbatch_content = f"""{sbatch_header}\n{gaussian_export}\n\n{gaussian_cmd}"""

    # Creating sbatch shell script file
    email_sbatch = email_at_to_underscore_and_remove_dot(email)[0:4]
    with open(
        f"user_data/{folder_name}/{filename[:-4]}/{email_sbatch}***.sh",
        "w",
    ) as sbatch:
        sbatch.write(sbatch_content)

    # Running sbatch
    Popen(
        [
            "sbatch",
            "--output=/dev/null",
            "--error=/dev/null",
            f"user_data/{folder_name}/{filename[:-4]}/{email_sbatch}***.sh",
        ]
    )


def gaussian_jsme(
    smiles,
    jsme_nama,
    calc_type,
    basis_set,
    teori,
    muatan,
    multiplisitas,
    folder_name,
    email,
    session,
):
    try:
        mkdir(f"user_data/{folder_name}/{jsme_nama}")
    except FileExistsError:
        pass

    with open(f"user_data/{folder_name}/{jsme_nama}/{jsme_nama}.smi", "w") as f:
        f.write(smiles)
    p = (
        Popen(
            [
                "obabel",
                "-ismi",
                f"user_data/{folder_name}/{jsme_nama}/{jsme_nama}.smi",
                "-oxyz",
                f"-Ouser_data/{folder_name}/{jsme_nama}/{jsme_nama}_smi.xyz",
                "--gen3d",
            ],
            stdout=PIPE,
        )
        .communicate()[0]
        .decode("utf-8")
    )

    with open(
        f"user_data/{folder_name}/{jsme_nama}/{jsme_nama}_smi.xyz", "r"
    ) as coord_xyz:
        dummy0 = coord_xyz.readline()
        dummy1 = coord_xyz.readline()
        lines = coord_xyz.read()
        koordinat = lines

    get_cwd = getcwd()

    gaussian_gjf = f"""%NProcShared={gaussian_cpus_per_job}
%mem=2GB
%chk={get_cwd}/user_data/{folder_name}/{jsme_nama}/{jsme_nama}.chk
%RWF={get_cwd}/user_data/{folder_name}/{jsme_nama}/{jsme_nama}.rwf
# {teori}/{basis_set} {calc_type}  

 {jsme_nama} | {calc_type} | {teori}/{basis_set}

{muatan} {multiplisitas}
{koordinat}

"""
    with open(f"user_data/{folder_name}/{jsme_nama}/{jsme_nama}.gjf", "w") as f:
        f.write(gaussian_gjf)

    gaussian_cmd = f"{gaussian_full_path} < user_data/{folder_name}/{jsme_nama}/{jsme_nama}.gjf > user_data/{folder_name}/{jsme_nama}/{jsme_nama}.out"
    sbatch_content = f"""{sbatch_header}\n{gaussian_export}\n\n{gaussian_cmd}"""

    # Creating sbatch shell script file
    folder_name = user_folder_name(email, session)
    email_sbatch = email_at_to_underscore_and_remove_dot(email)[0:4]
    with open(
        f"user_data/{folder_name}/{jsme_nama}/{email_sbatch}***.sh",
        "w",
    ) as sbatch:
        sbatch.write(sbatch_content)

    # Running sbatch
    Popen(
        [
            "sbatch",
            "--output=/dev/null",
            "--error=/dev/null",
            f"user_data/{folder_name}/{jsme_nama}/{email_sbatch}***.sh",
        ]
    )
