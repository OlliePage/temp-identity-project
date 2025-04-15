"""
Provider registry for TempIdentity.
"""

from typing import Dict, Type, Optional
import importlib
import inspect

from tempidentity.providers.email.base import EmailProvider
from tempidentity.providers.sms.base import SMSProvider

class ProviderRegistry:
    """Registry for email and SMS providers."""
    
    def __init__(self):
        """Initialize empty provider registries."""
        self.email_providers = {}  # name -> class mapping
        self.sms_providers = {}    # name -> class mapping
        self._initialized = False
    
    def register_email_provider(self, provider_class: Type[EmailProvider]):
        """Register an email provider class."""
        self.email_providers[provider_class.name] = provider_class
    
    def register_sms_provider(self, provider_class: Type[SMSProvider]):
        """Register an SMS provider class."""
        self.sms_providers[provider_class.name] = provider_class
    
    def get_email_provider(self, name: str) -> Optional[Type[EmailProvider]]:
        """Get an email provider class by name."""
        self._ensure_initialized()
        return self.email_providers.get(name)
    
    def get_sms_provider(self, name: str) -> Optional[Type[SMSProvider]]:
        """Get an SMS provider class by name."""
        self._ensure_initialized()
        return self.sms_providers.get(name)
    
    def get_all_email_providers(self) -> Dict[str, Type[EmailProvider]]:
        """Get all registered email providers."""
        self._ensure_initialized()
        return self.email_providers.copy()
    
    def get_all_sms_providers(self) -> Dict[str, Type[SMSProvider]]:
        """Get all registered SMS providers."""
        self._ensure_initialized()
        return self.sms_providers.copy()
    
    def create_email_provider(self, name: str, config: Dict = None) -> Optional[EmailProvider]:
        """Create an instance of an email provider by name."""
        self._ensure_initialized()
        provider_class = self.get_email_provider(name)
        if provider_class:
            return provider_class(config)
        return None
    
    def create_sms_provider(self, name: str, config: Dict = None) -> Optional[SMSProvider]:
        """Create an instance of an SMS provider by name."""
        self._ensure_initialized()
        provider_class = self.get_sms_provider(name)
        if provider_class:
            return provider_class(config)
        return None
    
    def _ensure_initialized(self):
        """Ensure the registry is initialized."""
        if not self._initialized:
            self._discover_builtin_providers()
            self._initialized = True
    
    def _discover_builtin_providers(self):
        """Discover built-in providers."""
        try:
            # Import email providers
            import tempidentity.providers.email as email_module
            for name in dir(email_module):
                obj = getattr(email_module, name)
                if (inspect.isclass(obj) and issubclass(obj, EmailProvider) and 
                    obj != EmailProvider and hasattr(obj, 'name')):
                    self.register_email_provider(obj)
            
            # Import SMS providers
            import tempidentity.providers.sms as sms_module
            for name in dir(sms_module):
                obj = getattr(sms_module, name)
                if (inspect.isclass(obj) and issubclass(obj, SMSProvider) and 
                    obj != SMSProvider and hasattr(obj, 'name')):
                    self.register_sms_provider(obj)
        except ImportError:
            # Handle import errors
            pass
    
    def auto_discover_providers(self):
        """
        Discover and register all available providers.
        
        This method can be called to explicitly discover providers,
        including those from external packages.
        """
        self._discover_builtin_providers()
        
        # Try to discover providers from entry points
        try:
            import pkg_resources
            for entry_point in pkg_resources.iter_entry_points('tempidentity.providers'):
                try:
                    provider_module = entry_point.load()
                    if hasattr(provider_module, 'register_providers'):
                        provider_module.register_providers()
                except Exception as e:
                    # Skip providers that fail to load
                    print(f"Error loading provider {entry_point.name}: {e}")
        except ImportError:
            # pkg_resources might not be available
            pass

# Create a singleton instance
registry = ProviderRegistry()