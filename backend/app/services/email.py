from typing import Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.core.config import settings

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>",
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=settings.SMTP_TLS,
    MAIL_SSL_TLS=not settings.SMTP_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

async def send_email(
    email_to: EmailStr,
    subject: str,
    html_content: str
) -> bool:
    """
    Send an email using FastAPI-Mail.
    
    Args:
        email_to: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not settings.EMAILS_ENABLED:
        print("Email sending is disabled")
        return False
        
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=html_content,
            subtype="html"
        )
        
        fm = FastMail(conf)
        await fm.send_message(message)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

async def send_verification_email(
    email_to: EmailStr,
    username: str,
    verification_token: str
) -> bool:
    """
    Send verification email to new user.
    
    Args:
        email_to: User's email address
        username: User's username
        verification_token: Email verification token
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
    
    html_content = f"""
    <html>
        <body>
            <h2>Welcome to Library Pulse!</h2>
            <p>Hi {username},</p>
            <p>Thank you for registering with Library Pulse. Please verify your email address by clicking the link below:</p>
            <p><a href="{verification_url}">Verify Email Address</a></p>
            <p>If you didn't create an account with Library Pulse, you can safely ignore this email.</p>
            <p>Best regards,<br>The Library Pulse Team</p>
        </body>
    </html>
    """
    
    return await send_email(
        email_to=email_to,
        subject="Verify your Library Pulse account",
        html_content=html_content
    )

async def send_password_reset_email(
    email_to: EmailStr,
    username: str,
    reset_token: str
) -> bool:
    """
    Send password reset email to user.
    
    Args:
        email_to: User's email address
        username: User's username
        reset_token: Password reset token
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    
    html_content = f"""
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hi {username},</p>
            <p>We received a request to reset your password. Click the link below to create a new password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't request a password reset, you can safely ignore this email.</p>
            <p>Best regards,<br>The Library Pulse Team</p>
        </body>
    </html>
    """
    
    return await send_email(
        email_to=email_to,
        subject="Reset your Library Pulse password",
        html_content=html_content
    ) 