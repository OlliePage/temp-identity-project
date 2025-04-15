"""
Provider package for TempIdentity.
This package contains email and SMS provider implementations.
"""

def get_registry():
    """
    Get the provider registry.
    
    Returns:
        ProviderRegistry: The provider registry instance.
    """
    from tempidentity.providers.registry import registry
    return registry