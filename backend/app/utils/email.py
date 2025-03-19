import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import emails
from emails.template import JinjaTemplate
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

from app.core.config import settings

def send_email(
    email_to: str,
    subject: str,
    html_template: str,
    environment: Dict[str, Any]
) -> bool:
    """
    Send an email using the emails library.
    
    Args:
        email_to: Recipient email address
        subject: Email subject
        html_template: HTML template string
        environment: Dictionary with variables to be passed to the template
        
    Returns:
        True if the email was sent successfully, False otherwise
    """
    if not settings.EMAILS_ENABLED:
        logging.warning("Email sending is disabled. Would have sent email to %s", email_to)
        return False
    
    # Render the template with the provided environment
    template = Template(html_template)
    html_content = template.render(**environment)
    
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL)
    )
    
    smtp_options = {
        "host": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
    }
    
    if settings.SMTP_USER and settings.SMTP_PASSWORD:
        smtp_options["user"] = settings.SMTP_USER
        smtp_options["password"] = settings.SMTP_PASSWORD
        
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    
    try:
        response = message.send(to=email_to, smtp=smtp_options)
        if response.status_code not in [250, 200]:
            logging.error(
                "Error sending email to %s, status code: %s",
                email_to, response.status_code
            )
            return False
        return True
    except Exception as e:
        logging.exception("Error sending email to %s: %s", email_to, str(e))
        return False

def send_verification_email(email_to: str, user_id: int = None, username: str = None, verification_token: str = None) -> bool:
    """
    Send an email verification link to a user.
    
    Args:
        email_to: User's email address
        user_id: User's ID for generating the verification token (not used if verification_token is provided)
        username: User's username (optional)
        verification_token: Email verification token (if already generated)
        
    Returns:
        True if the email was sent successfully, False otherwise
    """
    # Create verification link using the provided token
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
    
    # Greeting text
    greeting = f"Hi {username}," if username else "Hello,"
    
    # Email template
    html_template = f"""
    <html>
    <body>
        <h1>Verify Your Email Address</h1>
        <p>{greeting}</p>
        <p>Thank you for registering with Library Pulse. Please verify your email address by clicking the link below:</p>
        <p><a href="{{{{ verification_link }}}}">Verify Email</a></p>
        <p>If you did not register for Library Pulse, please ignore this email.</p>
        <p>This link will expire in 24 hours.</p>
    </body>
    </html>
    """
    
    # Send the email
    return send_email(
        email_to=email_to,
        subject="Verify Your Email Address - Library Pulse",
        html_template=html_template,
        environment={"verification_link": verification_link}
    )

def send_password_reset_email(email_to: str, token: str) -> bool:
    """
    Send a password reset link to a user.
    
    Args:
        email_to: User's email address
        token: Password reset token
        
    Returns:
        True if the email was sent successfully, False otherwise
    """
    # Create reset link
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    # Email template
    html_template = """
    <html>
    <body>
        <h1>Reset Your Password</h1>
        <p>You have requested to reset your password for Library Pulse. Please click the link below to set a new password:</p>
        <p><a href="{{ reset_link }}">Reset Password</a></p>
        <p>If you did not request a password reset, please ignore this email.</p>
        <p>This link will expire in 24 hours.</p>
    </body>
    </html>
    """
    
    # Send the email
    return send_email(
        email_to=email_to,
        subject="Reset Your Password - Library Pulse",
        html_template=html_template,
        environment={"reset_link": reset_link}
    ) 