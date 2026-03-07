# backend/app/ssl/services.py

import subprocess
from pathlib import Path
from ..config import settings


class SSLService:
    @staticmethod
    def generate_ssl_certificate(domain: str, email: str):
        """
        Generate SSL certificate using certbot. 
        Supports dry-run mode for development environments.
        """
        # Check for dry-run mode (local development without root or certbot)
        if settings.ENV == "development":
            print(f"DEBUG: Dry-run SSL generation for {domain} ({email})")
            return {
                "status": "success", 
                "domain": domain, 
                "mode": "dry-run",
                "message": "Certificate generation simulated in development environment."
            }

        certbot_cmd = [
            "certbot", "certonly", "--standalone",
            "--non-interactive", "--agree-tos",
            "--email", email,
            "--domains", domain
        ]
        try:
            # Note: This usually requires root privileges
            result = subprocess.run(certbot_cmd, check=True, capture_output=True, text=True)
            return {
                "status": "success", 
                "domain": domain,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            return {
                "status": "error", 
                "message": f"Certbot failed: {e.stderr or str(e)}",
                "code": e.returncode
            }
        except FileNotFoundError:
            return {
                "status": "error", 
                "message": "Certbot not found on system. Please install it or use development mode."
            }

