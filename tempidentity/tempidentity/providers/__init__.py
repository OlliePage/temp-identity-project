"""Provider package for TempIdentity."""

def get_registry():
    """Get the provider registry."""
    from tempidentity.tempidentity.providers.registry import registry
    return registry