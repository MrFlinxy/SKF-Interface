from os import environ, getcwd, mkdir, path
from sre_parse import FLAGS
from dotenv import load_dotenv
from re import I, sub, IGNORECASE
from subprocess import Popen
from time import sleep
from pathlib import Path
from .email_preprocess import email_at_to_underscore_and_remove_dot
from .openbabel_python import smi_xyz
from .pyrebase_init import user_folder_name
from werkzeug.utils import secure_filename

load_dotenv(".env")

orca_full_path = environ.get("orca_fullPath")
gaussian_full_path = environ.get("gaussian_fullPath")
orca_cpus_per_job = environ.get("orca_cpus_per_job")
gaussian_cpus_per_job = environ.get("gaussian_cpus_per_job")
GAUSS_EXEDIR = environ.get("GAUSS_EXEDIR")
GAUSS_SCRDIR = environ.get("GAUSS_SCRDIR")


sbatch_header = f"""#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={orca_cpus_per_job}"""

orca_export = """export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export PATH=/usr/local/bin/:$PATH
export OMP_NUM_THREADS=1"""

gaussian_export = f"""export GAUSS_EXEDIR={GAUSS_EXEDIR}
export GAUSS_SCRDIR={GAUSS_SCRDIR}"""


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
            line = sub(
                r"nprocs.+", rf"nprocs {orca_cpus_per_job}", line, flags=IGNORECASE
            )
            line = sub(r"%maxcore.+", r"%maxcore 2048", line, flags=IGNORECASE)
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
    return Popen(
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

    smi_xyz(smiles, folder_name, jsme_nama)

    while not path.exists(f"user_data/{folder_name}/{jsme_nama}/{jsme_nama}_smi.xyz"):
        sleep(2)

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
    return Popen(
        [
            "sbatch",
            "--output=/dev/null",
            "--error=/dev/null",
            f"user_data/{folder_name}/{jsme_nama}/{email_sbatch}***.sh",
        ]
    )


def orca_nebts_submit(
    file_reactant,
    file_product,
    calculation_name,
    email,
    session,
    teori,
    basis_set,
    muatan,
    multiplisitas,
):
    # Upload file
    filename_reactant = secure_filename(file_reactant.filename)
    filename_product = secure_filename(file_product.filename)
    folder_path = path.join(getcwd(), "user_data")
    user_folder = path.join(folder_path, user_folder_name(email, session))

    try:
        file_folder = path.join(user_folder, calculation_name)
        mkdir(file_folder)
    except FileExistsError:
        pass

    file_reactant.save(path.join(file_folder, filename_reactant))
    file_product.save(path.join(file_folder, filename_product))
    new_file = path.join(file_folder, f"{calculation_name}.inp")

    orca_nebts_inp = f"""# Input File Orca NEB-TS | Server Kimia Fisik
#
! NEB-TS FREQ {teori} {basis_set} 

%maxcore 2048

%pal
   nprocs 4
end

%NEB 
 NEB_END_XYZFILE "{path.join(user_folder, calculation_name)}/{filename_product}" 
END

* XYZFILE {muatan} {multiplisitas} {path.join(user_folder, calculation_name)}/{filename_reactant} *
"""
    print(orca_nebts_inp)
    with open(new_file, "w") as f:
        f.write(orca_nebts_inp)

    # Creating sbatch contents
    file_path = path.join(
        folder_path, user_folder_name(email, session), calculation_name
    )
    orca_cmd = f"{orca_full_path} {file_path}/{calculation_name}.inp > {file_path}/{calculation_name}.out --oversubscribe"
    sbatch_content = f"""{sbatch_header}\n\n{orca_export}\n\n{orca_cmd}"""

    # Creating sbatch shell script file
    folder_name = user_folder_name(email, session)
    email_sbatch = email_at_to_underscore_and_remove_dot(email)[0:4]

    with open(
        Path(f"user_data/{folder_name}/{calculation_name}/{email_sbatch}***.sh"),
        "w+",
    ) as sbatch:
        sbatch.write(sbatch_content)

    # Running sbatch
    return Popen(
        [
            "sbatch",
            "--output=/dev/null",
            "--error=/dev/null",
            f"user_data/{folder_name}/{calculation_name}/{email_sbatch}***.sh",
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
                r"%NProcShared=.+",
                rf"%NProcShared={gaussian_cpus_per_job}",
                line,
                flags=IGNORECASE,
            )
            line = sub(r"%mem=.+", r"%mem=2GB", line, flags=IGNORECASE)
            line = sub(
                r"%Chk=.+",
                rf"%chk={get_cwd}/user_data/{folder_name}/{filename[:-4]}/{filename[:-4]}.chk\n%RWF={getcwd()}/user_data/{folder_name}/{filename[:-4]}/{filename[:-4]}.rwf",
                line,
                flags=IGNORECASE,
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
    return Popen(
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

    smi_xyz(smiles, folder_name, jsme_nama)

    while not path.exists(f"user_data/{folder_name}/{jsme_nama}/{jsme_nama}_smi.xyz"):
        sleep(2)

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
    return Popen(
        [
            "sbatch",
            "--output=/dev/null",
            "--error=/dev/null",
            f"user_data/{folder_name}/{jsme_nama}/{email_sbatch}***.sh",
        ]
    )
