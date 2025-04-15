"""
Implementation for Mail.gw email service.
"""

import json
import time
import random
import string
import requests
from typing import Dict, List, Tuple

from tempidentity.providers.email.base import EmailProvider

class MailGwProvider(EmailProvider):
    """Implementation for Mail.gw service."""
    
    name = "mail.gw"
    display_name = "Mail.gw"
    description = "Free temporary email service"
    requires_api_key = False
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.base_url = "https://api.mail.gw"
        self.token = None
        self.domain = None
    
    def _generate_random_credentials(self, length=12):
        """Generate a random username and password."""
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _get_domains(self):
        """Get available domains from Mail.gw."""
        response = requests.get(f"{self.base_url}/domains")
        if response.status_code == 200:
            domains = response.json().get("hydra:member", [])
            if domains:
                return domains[0].get("domain")
        return None
    
    def create_email(self) -> Tuple[bool, str, str]:
        """Create a temporary email address."""
        # Get available domains
        self.domain = self._get_domains()
        if not self.domain:
            return False, "", ""
        
        # Generate random credentials
        username = self._generate_random_credentials()
        self.password = self._generate_random_credentials()
        self.email = f"{username}@{self.domain}"
        
        # Create the account
        payload = {
            "address": self.email,
            "password": self.password
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{self.base_url}/accounts", 
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 201:
            # Login immediately
            if self._login():
                return True, self.email, self.password
            else:
                return False, self.email, self.password
        else:
            return False, "", ""
    
    def _login(self) -> bool:
        """Login to the temporary email account and get token."""
        payload = {
            "address": self.email,
            "password": self.password
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{self.base_url}/token", 
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            self.token = response.json().get("token")
            return True
        else:
            return False
    
    def check_messages(self) -> List[Dict]:
        """Check for messages in the inbox."""
        if not self.token:
            if not self._login():
                return []
        
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        response = requests.get(
            f"{self.base_url}/messages", 
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json().get("hydra:member", [])
        else:
            return []
    
    def get_message_content(self, message_id: str) -> Dict:
        """Get the content of a specific message."""
        if not self.token:
            if not self._login():
                return {}
        
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        response = requests.get(
            f"{self.base_url}/messages/{message_id}", 
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {}
            
    def wait_for_messages(self, timeout: int = 60, check_interval: int = 5) -> List[Dict]:
        """Wait for new messages to arrive."""
        # Use the default implementation from the base class
        return super().wait_for_messages(timeout, check_interval)