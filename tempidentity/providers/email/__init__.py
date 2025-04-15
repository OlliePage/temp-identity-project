"""
Email provider implementations for TempIdentity.
"""

from tempidentity.providers.email.base import EmailProvider
from tempidentity.providers.email.mailgw import MailGwProvider
from tempidentity.providers.email.mailgw_improved import MailGwImprovedProvider
from tempidentity.providers.email.secmail import SecMailProvider
from tempidentity.providers.email.tempmail import TempMailProvider
from tempidentity.providers.email.emailjs import EmailJSProvider
from tempidentity.providers.email.tenminutemail import TenMinuteMailProvider

__all__ = [
    "EmailProvider", 
    "MailGwProvider", 
    "MailGwImprovedProvider",
    "SecMailProvider", 
    "TempMailProvider", 
    "EmailJSProvider", 
    "TenMinuteMailProvider"
]
