"""
Test suite for Websupport API integration
Tests API authentication, domain operations, and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from requests.exceptions import RequestException, HTTPError

from tests import TEST_CONFIG
from app.websupport import (
    generate_websupport_signature,
    make_websupport_request,
    WebsupportService
)


class TestWebsupportSignature:
    """Test Websupport API signature generation"""
    
    def test_signature_generation(self):
        """Test signature generation according to Websupport spec"""
        api_key = "test_api_key"
        secret = "test_secret"
        method = "GET"
        path = "/v2/service/domains"
        
        signature, x_date, timestamp = generate_websupport_signature(api_key, secret, method, path)
        
        assert isinstance(signature, str)
        assert len(signature) > 0
        assert isinstance(x_date, str)
        assert isinstance(timestamp, int)
        
        # Verify signature format (SHA1 hex digest)
        assert len(signature) == 40  # SHA1 hex is 40 characters
    
    def test_signature_with_query(self):
        """Test signature generation with query parameters"""
        api_key = "test_api_key"
        secret = "test_secret"
        method = "GET"
        path = "/v2/service/domains"
        query = "?page=1&limit=10"
        
        # Note: query is not included in canonical request for signature
        signature, x_date, timestamp = generate_websupport_signature(api_key, secret, method, path)
        
        assert isinstance(signature, str)
        assert len(signature) > 0
    
    def test_signature_different_methods(self):
        """Test signature generation with different HTTP methods"""
        api_key = "test_api_key"
        secret = "test_secret"
        path = "/v2/service/domains"
        
        methods = ["GET", "POST", "PUT", "DELETE"]
        signatures = []
        
        for method in methods:
            signature, _, _ = generate_websupport_signature(api_key, secret, method, path)
            signatures.append(signature)
        
        # Each method should produce different signature
        assert len(set(signatures)) == len(methods)
    
    def test_signature_different_paths(self):
        """Test signature generation with different paths"""
        api_key = "test_api_key"
        secret = "test_secret"
        method = "GET"
        
        paths = ["/v2/service/domains", "/v2/user/me", "/v2/service/domains/123"]
        signatures = []
        
        for path in paths:
            signature, _, _ = generate_websupport_signature(api_key, secret, method, path)
            signatures.append(signature)
        
        # Each path should produce different signature
        assert len(set(signatures)) == len(paths)


class TestWebsupportRequest:
    """Test Websupport API request handling"""
    
    @patch('app.websupport.requests.request')
    def test_successful_request(self, mock_request):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"success": True, "data": []}'
        mock_response.json.return_value = {"success": True, "data": []}
        mock_request.return_value = mock_response
        
        result = make_websupport_request(
            "test_key", "test_secret", "GET", "/v2/service/domains"
        )
        
        assert result == {"success": True, "data": []}
        mock_request.assert_called_once()
    
    @patch('app.websupport.requests.request')
    def test_empty_response(self, mock_request):
        """Test request with empty response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_request.return_value = mock_response
        
        result = make_websupport_request(
            "test_key", "test_secret", "GET", "/v2/service/domains"
        )
        
        assert result == {}
    
    @patch('app.websupport.requests.request')
    def test_401_error(self, mock_request):
        """Test 401 Unauthorized error"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_request.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            make_websupport_request(
                "test_key", "test_secret", "GET", "/v2/service/domains"
            )

        assert exc_info.value.status_code == 401
        assert "Invalid Websupport API credentials" in str(exc_info.value.detail)

    @patch('app.websupport.requests.request')
    def test_403_error(self, mock_request):
        """Test 403 Forbidden error"""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_request.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            make_websupport_request(
                "test_key", "test_secret", "GET", "/v2/service/domains"
            )

        assert exc_info.value.status_code == 403
        assert "Access forbidden to Websupport API" in str(exc_info.value.detail)

    @patch('app.websupport.requests.request')
    def test_429_error(self, mock_request):
        """Test 429 Too Many Requests error"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_request.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            make_websupport_request(
                "test_key", "test_secret", "GET", "/v2/service/domains"
            )

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded for Websupport API" in str(exc_info.value.detail)
    
    @patch('app.websupport.requests.request')
    def test_network_error(self, mock_request):
        """Test network error handling"""
        mock_request.side_effect = RequestException("Connection failed")
        
        with pytest.raises(HTTPException) as exc_info:
            make_websupport_request(
                "test_key", "test_secret", "GET", "/v2/service/domains"
            )
        
        assert exc_info.value.status_code == 500
        assert "Network error" in str(exc_info.value.detail)
    
    @patch('app.websupport.requests.request')
    def test_other_http_error(self, mock_request):
        """Test other HTTP errors"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_request.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            make_websupport_request(
                "test_key", "test_secret", "GET", "/v2/service/domains"
            )

        assert exc_info.value.status_code == 500
        assert "Websupport API error" in str(exc_info.value.detail)
    
    @patch('app.websupport.requests.request')
    def test_request_parameters(self, mock_request):
        """Test that request is called with correct parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"success": True}'
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response
        
        make_websupport_request(
            "test_key", "test_secret", "GET", "/v2/service/domains"
        )
        
        # Verify request parameters (method and url are positional args)
        call_args = mock_request.call_args
        assert call_args[0][0] == "GET"
        assert call_args[0][1] == "https://rest.websupport.sk/v2/service/domains"
        assert "Content-Type" in call_args[1]["headers"]
        assert "Accept" in call_args[1]["headers"]
        assert "X-Date" in call_args[1]["headers"]
        assert call_args[1]["auth"][0] == "test_key"  # api_key is auth username
        assert isinstance(call_args[1]["auth"][1], str)  # signature (HMAC) is auth password
        assert call_args[1]["timeout"] == 30


class TestWebsupportService:
    """Test WebsupportService class methods — v2 API"""

    # -- Compatibility shims (no network call) --------------------------------

    def test_get_domains_shim(self):
        """get_domains() is a shim in v2 — returns status ok without network call"""
        result = WebsupportService.get_domains()
        assert result["status"] == "ok"
        assert "items" in result

    def test_create_domain_shim(self):
        """create_domain() is a shim in v2"""
        result = WebsupportService.create_domain({"name": "test.sk"})
        assert result["status"] == "ok"

    def test_get_domain_details_shim(self):
        """get_domain_details() is a shim in v2"""
        result = WebsupportService.get_domain_details(123)
        assert result["status"] == "ok"

    def test_delete_domain_shim(self):
        """delete_domain() is a shim in v2"""
        result = WebsupportService.delete_domain(123)
        assert result["status"] == "ok"

    # -- Real v2 methods ------------------------------------------------------

    @patch('app.websupport.make_websupport_request')
    def test_verify_connection(self, mock_request):
        """verify_connection() calls GET /v2/check"""
        mock_request.return_value = {"verified": True}

        result = WebsupportService.verify_connection()

        assert result["verified"] is True
        mock_request.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "GET",
            "/v2/check",
            "",
            None,
        )

    @patch('app.websupport.make_websupport_request')
    def test_get_user_info_calls_verify(self, mock_request):
        """get_user_info() compatibility shim calls verify_connection()"""
        mock_request.return_value = {"verified": True}

        result = WebsupportService.get_user_info()

        assert result["verified"] is True
        mock_request.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "GET",
            "/v2/check",
            "",
            None,
        )

    @patch('app.websupport.make_websupport_request')
    def test_get_dns_records(self, mock_request):
        """get_dns_records() calls GET /v2/service/{service}/dns/record"""
        mock_request.return_value = {
            "currentPage": 1, "totalRecords": 2,
            "data": [{"id": 1, "name": "www", "content": "1.2.3.4", "ttl": 600}]
        }

        result = WebsupportService.get_dns_records("example.sk")

        assert result["totalRecords"] == 2
        assert len(result["data"]) == 1
        mock_request.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "GET",
            "/v2/service/example.sk/dns/record",
            "?page=1&rowsPerPage=100",
            None,
        )

    @patch('app.websupport.make_websupport_request')
    def test_create_dns_record(self, mock_request):
        """create_dns_record() calls POST /v2/service/{service}/dns/record"""
        record = {"type": "A", "name": "www", "content": "1.2.3.4", "ttl": 600}
        mock_request.return_value = {}

        WebsupportService.create_dns_record("example.sk", record)

        mock_request.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "POST",
            "/v2/service/example.sk/dns/record",
            "",
            record,
        )

    @patch('app.websupport.make_websupport_request')
    def test_update_dns_record(self, mock_request):
        """update_dns_record() calls PUT /v2/service/{service}/dns/record/{id}"""
        record = {"content": "5.6.7.8", "ttl": 300}
        mock_request.return_value = {}

        WebsupportService.update_dns_record("example.sk", 42, record)

        mock_request.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "PUT",
            "/v2/service/example.sk/dns/record/42",
            "",
            record,
        )

    @patch('app.websupport.make_websupport_request')
    def test_delete_dns_record(self, mock_request):
        """delete_dns_record() calls DELETE /v2/service/{service}/dns/record/{id}"""
        mock_request.return_value = {}

        WebsupportService.delete_dns_record("example.sk", 42)

        mock_request.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "DELETE",
            "/v2/service/example.sk/dns/record/42",
            "",
            None,
        )


class TestWebsupportIntegration:
    """Integration tests for Websupport API"""

    @patch('app.websupport.make_websupport_request')
    def test_full_dns_lifecycle(self, mock_request):
        """Test complete DNS record lifecycle via v2 API"""
        mock_request.side_effect = [
            {"currentPage": 1, "totalRecords": 0, "data": []},  # get_dns_records
            {},  # create_dns_record (204 → {})
            {},  # update_dns_record
            {},  # delete_dns_record
        ]

        records = WebsupportService.get_dns_records("example.sk")
        assert records["totalRecords"] == 0

        WebsupportService.create_dns_record("example.sk", {"type": "A", "name": "test", "content": "1.1.1.1", "ttl": 600})
        WebsupportService.update_dns_record("example.sk", 1, {"content": "2.2.2.2"})
        WebsupportService.delete_dns_record("example.sk", 1)

        assert mock_request.call_count == 4

    @patch('app.websupport.make_websupport_request')
    def test_error_handling_consistency(self, mock_request):
        """Test consistent error handling across real v2 methods"""
        mock_request.side_effect = HTTPException(status_code=401, detail="Unauthorized")

        with pytest.raises(HTTPException) as exc_info:
            WebsupportService.verify_connection()
        assert exc_info.value.status_code == 401

        with pytest.raises(HTTPException) as exc_info:
            WebsupportService.get_dns_records("example.sk")
        assert exc_info.value.status_code == 401

        with pytest.raises(HTTPException) as exc_info:
            WebsupportService.create_dns_record("example.sk", {})
        assert exc_info.value.status_code == 401

        with pytest.raises(HTTPException) as exc_info:
            WebsupportService.delete_dns_record("example.sk", 1)
        assert exc_info.value.status_code == 401

    @patch('app.websupport.generate_websupport_signature')
    @patch('app.websupport.requests.request')
    def test_signature_in_request_headers(self, mock_request, mock_signature):
        """Test that signature is properly included in request headers"""
        mock_signature.return_value = ("test_signature", "20230101T120000Z", 1234567890)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"verified": true}'
        mock_response.json.return_value = {"verified": True}
        mock_request.return_value = mock_response

        WebsupportService.verify_connection()

        mock_signature.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "GET",
            "/v2/check",
            "",
        )

        call_args = mock_request.call_args
        assert call_args[1]["auth"][1] == "test_signature"