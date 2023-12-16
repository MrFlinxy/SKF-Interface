<div align="center">
<h1>SKF-I</h1>
<h2>Server Kimia Fisik Interface</h2>
<p>SKF-Interface an Interface to Submit Computatational Chemistry Job.<br>
<a href="https://orcaforum.kofo.mpg.de/">ORCA v5.0.4</a> | <a href="https://gaussian.com/">Gaussian 09</a> 
</p>
<h3>Contents</h3>
<a href="https://github.com/MrFlinxy/SKF-Interface/tree/main?tab=readme-ov-file#pre-requisites">Pre-requisites</a> <br>
<a href="https://github.com/MrFlinxy/SKF-Interface/tree/main?tab=readme-ov-file#how-to-use">How to use</a> <br>
<a href="https://github.com/MrFlinxy/SKF-Interface/tree/main?tab=readme-ov-file#tech-used-for-this-project">Tech used for this project</a>
</div>

## Pre-requisites

## How to use

Clone the repository

```console
git clone https://github.com/MrFlinxy/SKF-Interface.git
```

Create python virtual environment

```console
python3 -m venv skf_interface
```

Activate python virtual environment (Linux)

```console
source skf_interface/bin/activate
```

Install the required python packages from requirements.txt

```console
pip install -r requirements.txt
```

Creating .env file

```console
cd SKF-Interface; touch .env
```

Put the following into the .env file

```
cat > .env <<EOF
# FIREBASE Configuration
firebase_apiKey = "<apiKey>"
firebase_authDomain = "<authDomain>"
firebase_projectId = "<projectId>"
firebase_storageBucket = "<storageBucker>"
firebase_messagingSenderId = "<messagingSenderId>"
firebase_appId = "<appId>"
firebase_measurementId = "<measurementId>"
firebase_databaseURL ="<databaseURL>"

# FLASK Configuration
secretKey = '<secretKey>'

# Software paths
orca_fullPath = '<orca_fullPath>'
orca_cpus_per_job= '<orca_cpu>'
gaussian_fullPath = '<gaussian_fullPath>'
gaussian_cpus_per_job= '<gaussian_cpu>'
GAUSS_EXEDIR='<GAUSS_EXEDIR>'
GAUSS_SCRDIR='<GAUSS_SCRDIR>'
EOF
```

## Tech used for this project

<div align="center">
<p>
  <a href="https://www.python.org/">
    <img alt="Python Logo" src="./images/python-logo.svg" width="50"><h3>Python</h3>
  </a>
</p>
<h2>・</h2>

<p>
  <a href="https://flask.palletsprojects.com/">
    <img alt="Flask Logo" src="./images/flask-logo.svg" width="50"><h3>Python Flask</h3>
  </a>
</p>
<h2>・</h2>

<p>
  <a href="/">
    <img alt="Gunicorn Logo" src="./images/gunicorn-logo.svg" width="50">
  </a>
  <a href="/">
    <img alt="Nginx Logo" src="./images/nginx-logo.svg" width="50">
  </a> <h3>Gunicorn・Nginx</h3>
</p>
<h2>・</h2>

<p>
  <a href="https://github.com/thisbejim/Pyrebase/">
    <img alt="Pyrebase Logo" src="./images/pyrebase-logo.svg" width="50"><h3>Pyrebase</h3>
  </a>
</p>
<h2>・</h2>

<p>
  <a href="https://www.schedmd.com/">
    <img alt="Slurm Logo" src="./images/slurm-logo.png" width="50"><h3>Slurm Workload Manager</h3>
  </a>
</p>
<h2>・</h2>

<p>
  <a href="/">
    <img alt="HTML Logo" src="./images/html-logo.svg" width="50">
  </a>
  <a href="/">
    <img alt="CSS Logo" src="./images/css-logo.svg" width="50">
  </a>
  <a href="/">
    <img alt="JS Logo" src="./images/javascript-logo.svg" width="50">
  </a> <h3>HTML・CSS・JavaScript</h3>
</p>
<h2>・</h2>

<p>
  <a href="https://tailwindcss.com/">
    <img alt="TailwindCSS Logo" src="./images/tailwindcss-logo.svg" width="50"><h3>TailwindCSS</h3>
  </a>
</p>
<h2>・</h2>

<p>
  <a href="https://jsme-editor.github.io/">
    <h3>JSME Molecule Editor</h3>
  </a>
</p>
<h2>・</h2>
</div>
