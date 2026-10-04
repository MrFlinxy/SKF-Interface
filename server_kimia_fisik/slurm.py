import subprocess
import time
import requests
import re
from datetime import datetime
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")

class SlurmClient:
    BASE_URL = "http://127.0.0.1:6820"
    SLURM_API_VERSION = "v0.0.40"
    SLURM_URL = f"{BASE_URL}/slurm/{SLURM_API_VERSION}"
    SLURMDB_URL = f"{BASE_URL}/slurmdb/{SLURM_API_VERSION}"
    CWD = "/home/mdmachine/SKF-Interface"

    def __init__(self):
        self.token = None
        self.token_expires_at = 0

    def _get_token(self):
        if self.token and time.time() < self.token_expires_at - 60:
            return self.token

        result = subprocess.run(
            ["scontrol", "token"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()
        self.token = output.split("=", 1)[1]
        self.token_expires_at = time.time() + 1800
        return self.token

    def _headers(self):
        return {
            "X-SLURM-USER-NAME": "mdmachine",
            "X-SLURM-USER-TOKEN": self._get_token(),
        }
    
    def _post_headers(self):
        return {
            "Content-Type":"application/json",
            "X-SLURM-USER-NAME": "mdmachine",
            "X-SLURM-USER-TOKEN": self._get_token(),
        }
    
    # slurmdctld
    def list_jobs(self):
        response = requests.get(
            f"{self.SLURM_URL}/jobs",
            headers=self._headers(),
        )

        response.raise_for_status()
        return response.json()
    
    def get_job(self, job_id):
        response = requests.get(
            f"{self.SLURM_URL}/job/{job_id}",
            headers=self._headers(),
        )

        response.raise_for_status()
        return response.json()
    
    def submit_job(
            self,
            reqData,
        ):

        body = {
            "script": reqData["command"],
            "job": {
                    "admin_comment": reqData["admin_comment"],
                    "comment": reqData["comment"],
                    "cpus_per_task": reqData["cpus_per_task"],
                    "current_working_directory": self.CWD,
                    "environment": reqData["environment"],
                    "name": reqData["name"],
                    "nodes": "1",
                    "standard_output": "/dev/null",
                    "standard_error": "/dev/null",
                    "tasks": "1",
                }
        }
        
        response = requests.post(
            f"{self.SLURM_URL}/job/submit",
            headers=self._post_headers(),
            json=body,
        )

        response.raise_for_status()
        return response.json()
    
    def cancel_job(self, job_id):
        response = requests.delete(
            f"{self.SLURM_URL}/job/{job_id}",
            headers=self._headers(),
        )

        response.raise_for_status()
        return response.json()
    
    def suspend_job(self, job_id):
        response = requests.delete(
            f"{self.SLURM_URL}/job/{job_id}?signal=STOP",
            headers=self._headers(),
        )

        response.raise_for_status()
        return response.json()
    
    def resume_job(self, job_id):
        response = requests.delete(
            f"{self.SLURM_URL}/job/{job_id}?signal=CONT",
            headers=self._headers(),
        )

        response.raise_for_status()
        return response.json()
    
    # slurmdbd
    def list_job_history(self, isOwnJob=False, state=None, email=None):
        response = requests.get(
            f"{self.SLURMDB_URL}/jobs",
            headers=self._headers(),
        )

        response.raise_for_status()

        data = response.json()
        jobs = data.get("jobs", [])
        filtered_jobs = []
        for job in jobs:

            # --------------------------------
            # Extract email and job name
            # --------------------------------

            submit_line = job.get("submit_line", "")

            job_email, job_name = parse_submit_line(
                submit_line
            )

            # --------------------------------
            # Filter own jobs
            # --------------------------------

            if isOwnJob:
                if not email:
                    continue

                if job_email != email:
                    continue

            # --------------------------------
            # Filter state
            # --------------------------------

            if state:
                if state != job.get("state", {}).get("current", ["UNKNOWN"])[-1]:
                    continue
            
            displayed_email = censor_email(
                job_email,
                email
            )

            filtered_jobs.append({
                "job_id": job.get("job_id"),
                "job_name": job_name,
                "user_email": displayed_email,
                "cpu": job.get("required", {}).get("CPUs"),
                "state": job.get("state", {}).get("current", ["UNKNOWN"])[-1],
                "submit_time": format_submit_time(
                    job.get("time", {}).get("submission")
                ),
                "elapsed": format_elapsed(
                    job.get("time", {}).get("elapsed")
                )
            })

        filtered_jobs.sort(
            key=lambda job: job["submit_time"],
            reverse=True
        )

        return filtered_jobs
    
    def get_job_history(self, job_id):
        response = requests.get(
            f"{self.SLURMDB_URL}/job/{job_id}",
            headers=self._headers(),
        )

        response.raise_for_status()
        return response.json()

def parse_submit_line(submit_line):
    # Extract email from --comment
    email_match = re.search(
        r'--comment="([^"]+)"',
        submit_line
    )

    # Extract job name from user_data/<user>/<job_name>/<script>
    job_match = re.search(
        r'user_data/[^/]+/([^/]+)/[^/]+\.sh',
        submit_line
    )

    email = email_match.group(1) if email_match else None
    job_name = job_match.group(1) if job_match else None

    return email, job_name

def censor_email(email, own_email):
    if not email:
        return email

    # Don't censor our own email
    if email == own_email:
        return email

    if "@" not in email:
        return email

    local, domain = email.split("@", 1)

    if len(local) <= 2:
        censored_local = local[0] + "*"
    else:
        censored_local = local[:2] + "*" * (len(local) - 2)

    return f"{censored_local}@{domain}"

def format_elapsed(seconds):
    if seconds is None:
        return None

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def format_submit_time(timestamp):
    if not timestamp:
        return None

    return datetime.fromtimestamp(
        timestamp,
        tz=WIB
    ).strftime("%Y-%m-%d %H:%M:%S")