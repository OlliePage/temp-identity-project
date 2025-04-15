"""
Email provider implementations for TempIdentity.
"""

from tempidentity.providers.email.base import EmailProvider
from tempidentity.providers.email.mailgw import MailGwProvider

__all__ = ['EmailProvider', 'MailGwProvider']