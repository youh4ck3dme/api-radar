# backend/app/monitoring/tasks.py

import ssl
import socket
from datetime import datetime, timezone

def check_ssl_expiry(domain: str):
    """
    Check the SSL certificate expiration date for a given domain.
    Returns (expiry_date, days_remaining) or (None, error_message).
    """
    context = ssl.create_default_context()
    try:
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                # Získame dátum expirácie z certifikátu
                expiry_str = cert['notAfter']
                # Formát: 'Mar 15 17:00:00 2026 GMT'
                expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z').replace(tzinfo=timezone.utc)
                days_remaining = (expiry_date - datetime.now(timezone.utc)).days
                return {"status": "success", "expiry_date": expiry_date.isoformat(), "days_remaining": days_remaining}
    except Exception as e:
        return {"status": "error", "message": f"Could not check SSL: {str(e)}"}


def dns_health_check(domain: str):
    """
    Check if the domain resolves to an IP address.
    """
    try:
        ip_address = socket.gethostbyname(domain)
        return {"status": "success", "ip": ip_address}
    except socket.gaierror as e:
        return {"status": "error", "message": f"DNS resolution failed: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

