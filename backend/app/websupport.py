"""
Websupport REST API v2 integration module
Docs: https://rest.websupport.sk/v2/docs/intro

Auth: HTTP Basic with HMAC-SHA1 signature
  - Username: API identifier
  - Password: HMAC-SHA1(secret, "{METHOD} {path+query} {unix_timestamp}")
  - X-Date:   ISO8601 UTC timestamp (e.g. 20230101T120000Z)
"""

import hmac
import hashlib
import logging
import time
from datetime import datetime, timezone

import requests
from fastapi import HTTPException

from .config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://rest.websupport.sk"
DYNDNS_BASE_URL = "https://dyndns.websupport.sk"


# ---------------------------------------------------------------------------
# Signature
# ---------------------------------------------------------------------------

def generate_websupport_signature(
    api_key: str, secret: str, method: str, path: str, query: str = ""
) -> tuple[str, str, int]:
    """
    Compute HMAC-SHA1 signature for Websupport REST API v2.

    Canonical request: "{METHOD} {path}{query} {unix_timestamp}"
    Returns: (signature_hex, x_date_iso8601, unix_timestamp)
    """
    timestamp = int(time.time())
    canonical = f"{method} {path}{query} {timestamp}"
    signature = hmac.new(
        bytes(secret, "UTF-8"),
        bytes(canonical, "UTF-8"),
        hashlib.sha1,
    ).hexdigest()
    x_date = datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return signature, x_date, timestamp


# ---------------------------------------------------------------------------
# Low-level request helper
# ---------------------------------------------------------------------------

def make_websupport_request(
    api_key: str,
    secret: str,
    method: str,
    path: str,
    query: str = "",
    data: dict = None,
) -> dict:
    """
    Make an authenticated request to Websupport REST API v2.

    Raises HTTPException on auth errors, rate-limit, and network failures.
    Returns parsed JSON dict (empty dict for empty 204 responses).
    """
    signature, x_date, _ = generate_websupport_signature(api_key, secret, method, path, query)
    url = f"{BASE_URL}{path}{query}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Date": x_date,
    }

    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            auth=(api_key, signature),
            json=data,
            timeout=30,
        )
        response.raise_for_status()

        if response.text:
            return response.json()
        return {}

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else 500
        body = e.response.text if e.response is not None else ""
        logger.error("Websupport HTTP %s on %s %s: %s", status, method, path, body)
        if status == 401:
            raise HTTPException(status_code=401, detail="Invalid Websupport API credentials")
        if status == 403:
            raise HTTPException(status_code=403, detail="Access forbidden to Websupport API")
        if status == 429:
            raise HTTPException(status_code=429, detail="Rate limit exceeded for Websupport API")
        raise HTTPException(status_code=status, detail=f"Websupport API error {status}: {body}")

    except requests.exceptions.RequestException as e:
        logger.error("Websupport network error on %s %s: %s", method, path, e)
        raise HTTPException(status_code=500, detail=f"Network error contacting Websupport: {e}")


# ---------------------------------------------------------------------------
# Service class — maps to actual v2 endpoints
# ---------------------------------------------------------------------------

class WebsupportService:
    """
    Thin wrapper around Websupport REST API v2.

    Endpoints used:
      GET  /v2/check                                  – auth verify
      GET  /v2/service/{service}/dns/record           – list DNS records
      POST /v2/service/{service}/dns/record           – create DNS record
      PUT  /v2/service/{service}/dns/record/{id}      – update DNS record
      DELETE /v2/service/{service}/dns/record/{id}    – delete DNS record
      GET  /v2/service/{service}/ftp-account          – list FTP accounts
    """

    @staticmethod
    def _call(method: str, path: str, query: str = "", data: dict = None) -> dict:
        return make_websupport_request(
            settings.WEBSUPPORT_API_KEY,
            settings.WEBSUPPORT_SECRET,
            method,
            path,
            query,
            data,
        )

    # -- Auth ----------------------------------------------------------------

    @staticmethod
    def verify_connection() -> dict:
        """Verify API credentials. Returns {verified: true} on success."""
        return WebsupportService._call("GET", "/v2/check")

    # -- DNS records ---------------------------------------------------------

    @staticmethod
    def get_dns_records(service: str, page: int = 1, rows_per_page: int = 100) -> dict:
        """
        List DNS records for a service (domain name, e.g. 'example.sk').
        Returns paginated response with 'data' list.
        """
        query = f"?page={page}&rowsPerPage={rows_per_page}"
        return WebsupportService._call("GET", f"/v2/service/{service}/dns/record", query)

    @staticmethod
    def create_dns_record(service: str, record: dict) -> dict:
        """
        Create a DNS record.
        record = {type, name, content, ttl, priority?, port?, weight?}
        """
        return WebsupportService._call("POST", f"/v2/service/{service}/dns/record", data=record)

    @staticmethod
    def update_dns_record(service: str, record_id: int, record: dict) -> dict:
        """Update an existing DNS record by its numeric ID."""
        return WebsupportService._call(
            "PUT", f"/v2/service/{service}/dns/record/{record_id}", data=record
        )

    @staticmethod
    def delete_dns_record(service: str, record_id: int) -> dict:
        """Delete a DNS record by its numeric ID."""
        return WebsupportService._call(
            "DELETE", f"/v2/service/{service}/dns/record/{record_id}"
        )

    # -- FTP accounts --------------------------------------------------------

    @staticmethod
    def get_ftp_accounts(service: str, page: int = 1, rows_per_page: int = 100) -> dict:
        """List FTP accounts for a service."""
        query = f"?page={page}&rowsPerPage={rows_per_page}"
        return WebsupportService._call("GET", f"/v2/service/{service}/ftp-account", query)

    # -- Compatibility shims (keep old callers working) ----------------------

    @staticmethod
    def get_domains() -> dict:
        """
        Compatibility shim — v2 API has no domain-list endpoint.
        Returns empty structure; use get_dns_records(service) instead.
        """
        logger.warning(
            "WebsupportService.get_domains() called — v2 API has no domain-list endpoint. "
            "Use get_dns_records(service) with a specific service name."
        )
        return {"items": [], "status": "ok", "note": "Use get_dns_records(service) for v2 API"}

    @staticmethod
    def get_user_info() -> dict:
        """Compatibility shim — v2 has no /user/me. Uses /v2/check instead."""
        return WebsupportService.verify_connection()

    # -- DynDNS -------------------------------------------------------------

    @staticmethod
    def dyndns_update(hostname: str, ip: str) -> str:
        """
        Update a DynDNS record via dyndns.websupport.sk (DynDNS2 protocol).
        Uses plain HTTP Basic auth: DYNDNS_KEY:DYNDNS_SECRET (no HMAC).
        Returns the raw response text (e.g. "good", "nochg", "nohost").
        """
        url = f"{DYNDNS_BASE_URL}/nic/update?hostname={hostname}&myip={ip}"
        try:
            response = requests.get(
                url,
                headers={"Accept": "text/plain"},
                auth=(settings.WEBSUPPORT_DYNDNS_KEY, settings.WEBSUPPORT_DYNDNS_SECRET),
                timeout=15,
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error("DynDNS update error for %s: %s", hostname, e)
            raise HTTPException(status_code=500, detail=f"DynDNS update failed: {e}")

    @staticmethod
    def create_domain(payload: dict) -> dict:
        """Compatibility shim — v2 API manages DNS records, not domains directly."""
        logger.warning(
            "WebsupportService.create_domain() called — not supported in v2 API. "
            "Use create_dns_record(service, record) instead."
        )
        return {"items": [], "status": "ok", "note": "Use create_dns_record(service, record) for v2 API"}

    @staticmethod
    def get_domain_details(domain_id) -> dict:
        """Compatibility shim — v2 API manages DNS records, not domains directly."""
        logger.warning(
            "WebsupportService.get_domain_details() called — not supported in v2 API. "
            "Use get_dns_records(service) instead."
        )
        return {"items": [], "status": "ok", "note": "Use get_dns_records(service) for v2 API"}

    @staticmethod
    def delete_domain(domain_id) -> dict:
        """Compatibility shim — v2 API manages DNS records, not domains directly."""
        logger.warning(
            "WebsupportService.delete_domain() called — not supported in v2 API. "
            "Use delete_dns_record(service, record_id) instead."
        )
        return {"items": [], "status": "ok", "note": "Use delete_dns_record(service, record_id) for v2 API"}
