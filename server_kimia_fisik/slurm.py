import subprocess
import time
import requests

class SlurmClient:
    BASE_URL = "http://127.0.0.1:6820"

    def __init__(self):
        self.token = None
        self.token_expires_at = 0

    def _get_token(self):
        # Refresh one minute before expiration
        if self.token and time.time() < self.token_expires_at - 60:
            return self.token

        result = subprocess.run(
            ["scontrol", "token"],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout.strip()

        # SLURM_JWT=eyJ...
        self.token = output.split("=", 1)[1]

        # Default Slurm token lifetime = 1800 seconds
        self.token_expires_at = time.time() + 1800

        return self.token

    def _headers(self):
        return {
            "X-SLURM-USER-NAME": "mdmachine",
            "X-SLURM-USER-TOKEN": self._get_token(),
        }
    
    def list_jobs(self):
        response = requests.get(
            f"{self.BASE_URL}/slurm/v0.0.40/jobs",
            headers=self._headers(),
        )

        response.raise_for_status()
        return response.json()