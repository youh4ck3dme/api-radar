# backend/app/domains/services.py

from ..websupport import WebsupportService


class DomainService:
    @staticmethod
    def list_domains():
        """Get list of domains from Websupport API"""
        return WebsupportService.get_domains()

    @staticmethod
    def create_domain(payload: dict):
        """Create new domain via Websupport API"""
        return WebsupportService.create_domain(payload)

    @staticmethod
    def get_domain_details(domain_id: int):
        """Get domain details from Websupport API"""
        return WebsupportService.get_domain_details(domain_id)

    @staticmethod
    def delete_domain(domain_id: int):
        """Delete domain via Websupport API"""
        return WebsupportService.delete_domain(domain_id)

