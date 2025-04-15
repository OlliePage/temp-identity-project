"""
Implementation for TextVerified SMS service.
"""

import json
import requests
from typing import Dict, List, Tuple, Optional

from tempidentity.providers.sms.base import SMSProvider

class TextVerifiedProvider(SMSProvider):
    """Implementation for TextVerified service."""
    
    name = "textverified"
    display_name = "TextVerified"
    description = "Paid temporary phone number service"
    requires_api_key = True
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.base_url = "https://www.textverified.com/api"
        self.api_key = self.config.get('api_key', '')
        self.service = None
    
    def get_available_services(self) -> List[Dict]:
        """Get available services for verification."""
        headers = {
            "X-SIMPLE-API-ACCESS-TOKEN": self.api_key
        }
        
        response = requests.get(
            f"{self.base_url}/Services", 
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
    
    def create_number(self, service_name: str) -> Tuple[bool, str]:
        """Create a temporary phone number for a service."""
        headers = {
            "X-SIMPLE-API-ACCESS-TOKEN": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "id": service_name
        }
        
        response = requests.post(
            f"{self.base_url}/Verifications", 
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            data = response.json()
            self.verification_id = data.get("id")
            self.phone_number = data.get("number")
            self.service = service_name
            
            return True, self.phone_number
        else:
            return False, ""
    
    def check_sms(self) -> Optional[str]:
        """Check for received SMS."""
        if not self.verification_id:
            return None
        
        headers = {
            "X-SIMPLE-API-ACCESS-TOKEN": self.api_key
        }
        
        response = requests.get(
            f"{self.base_url}/Verifications/{self.verification_id}", 
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("code")
        else:
            return None
    
    def wait_for_sms(self, timeout: int = 300, check_interval: int = 10) -> Optional[str]:
        """Wait for an SMS to arrive."""
        # Use the default implementation from the base class
        return super().wait_for_sms(timeout, check_interval)
    
    def cancel_number(self) -> bool:
        """Cancel the current phone number."""
        if not self.verification_id:
            return False
        
        headers = {
            "X-SIMPLE-API-ACCESS-TOKEN": self.api_key
        }
        
        response = requests.delete(
            f"{self.base_url}/Verifications/{self.verification_id}", 
            headers=headers
        )
        
        if response.status_code == 200:
            self.verification_id = None
            self.phone_number = None
            self.service = None
            return True
        else:
            return False