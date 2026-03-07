"""
Neon Auth integration module
Handles authentication with Neon Auth for trial period
"""

import json
import jwt
import requests
from datetime import datetime, timezone
from fastapi import HTTPException, status
from .config import settings

class NeonAuthService:
    """Service for Neon Auth integration"""
    
    def __init__(self):
        self.auth_url = "https://ep-square-union-aeczbg2r.neonauth.c-2.us-east-2.aws.neon.tech/neondb/auth"
        self.jwks_url = "https://ep-square-union-aeczbg2r.neonauth.c-2.us-east-2.aws.neon.tech/neondb/auth/.well-known/jwks.json"
        self.jwks_cache = None
        self.jwks_cache_time = None
    
    def get_jwks(self):
        """Get and cache JWKS keys from Neon Auth"""
        current_time = datetime.now(timezone.utc)
        
        # Cache for 1 hour
        if self.jwks_cache and self.jwks_cache_time and (current_time - self.jwks_cache_time).seconds < 3600:
            return self.jwks_cache
        
        try:
            response = requests.get(self.jwks_url, timeout=10)
            response.raise_for_status()
            self.jwks_cache = response.json()
            self.jwks_cache_time = current_time
            return self.jwks_cache
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch JWKS: {str(e)}")
    
    def verify_neon_token(self, token: str) -> dict:
        """Verify JWT token from Neon Auth"""
        try:
            # Get JWKS keys
            jwks = self.get_jwks()
            
            # Decode token header to get kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            if not kid:
                raise HTTPException(status_code=401, detail="Invalid token format")
            
            # Find matching key
            key = None
            for jwk in jwks.get("keys", []):
                if jwk.get("kid") == kid:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
                    break
            
            if not key:
                raise HTTPException(status_code=401, detail="Unable to find matching key")
            
            # Verify token
            payload = jwt.decode(
                token, 
                key, 
                algorithms=["RS256"],
                audience="api-centrum",  # Your API identifier
                options={"verify_exp": True}
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
    
    def get_user_info_from_token(self, token: str) -> dict:
        """Extract user info from Neon Auth token"""
        payload = self.verify_neon_token(token)
        
        return {
            "email": payload.get("email"),
            "name": payload.get("name"),
            "sub": payload.get("sub"),  # User ID
            "roles": payload.get("roles", []),
            "organizations": payload.get("organizations", [])
        }
    
    def is_trial_active(self) -> bool:
        """Check if trial is still active (basic check)"""
        try:
            # Try to fetch JWKS as a basic health check
            self.get_jwks()
            return True
        except:
            return False
    
    def get_login_url(self, redirect_uri: str = None) -> str:
        """Get Neon Auth login URL"""
        base_url = self.auth_url
        client_id = "api-centrum"  # You would register this in Neon Auth
        
        if redirect_uri:
            return f"{base_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        else:
            return f"{base_url}?client_id={client_id}&response_type=code"

# Global instance
neon_auth_service = NeonAuthService()

def verify_neon_auth_token(token: str) -> dict:
    """Verify Neon Auth token and return user info"""
    return neon_auth_service.get_user_info_from_token(token)

def is_neon_trial_active() -> bool:
    """Check if Neon Auth trial is active"""
    return neon_auth_service.is_trial_active()

def get_login_url() -> str:
    """Get Neon Auth login URL"""
    return neon_auth_service.get_login_url()
