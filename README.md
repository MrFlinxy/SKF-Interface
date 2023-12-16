<div align="center">
<h1>SKF-I</h1>
<h2>Server Kimia Fisik Interface</h2>
<p>SKF-Interface an Interface to Submit Computatational Chemistry Job.<br>
<a href="https://orcaforum.kofo.mpg.de/">ORCA v5.0.4</a> | <a href="https://gaussian.com/">Gaussian 09</a> 
</p>
</div>

## Pre-requisites

## Tech used for this project

## How to use

Clone the repository

```
git clone https://github.com/MrFlinxy/SKF-Interface.git
```

Creating .env file

```console
cd SKF-Interface
touch .env
```

put the following into the .env file

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
