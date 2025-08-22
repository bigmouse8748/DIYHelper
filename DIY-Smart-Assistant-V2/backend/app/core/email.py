"""
Email Service for sending verification emails
"""

import smtplib
import ssl
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from typing import Optional
import logging

from ..config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email or settings.smtp_user
        
    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return bool(
            self.smtp_host and 
            self.smtp_user and 
            self.smtp_password and 
            self.from_email
        )
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using SMTP"""
        if not self.is_configured():
            logger.warning("Email service not configured, skipping email send")
            return False
            
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"DIY Smart Assistant <{self.from_email}>"
            message["To"] = to_email
            
            # Add headers to improve deliverability
            message["Message-ID"] = f"<{int(time.time())}.{hash(to_email)}@diyassistant.com>"
            message["Date"] = formatdate(localtime=True)
            message["X-Mailer"] = "DIY Smart Assistant v2.0.0"
            message["Reply-To"] = self.from_email
            message["Return-Path"] = self.from_email
            
            # Add anti-spam headers
            message["X-Priority"] = "3"
            message["X-MSMail-Priority"] = "Normal"
            message["Importance"] = "Normal"
            
            # Add text version if provided
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                message.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
                
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def get_verification_email_html(self, username: str, verification_url: str) -> str:
        """Generate HTML content for verification email"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Email - DIY Smart Assistant</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f7fa;
                }}
                .email-container {{
                    background: white;
                    border-radius: 12px;
                    padding: 40px;
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 32px;
                    margin-bottom: 10px;
                }}
                .title {{
                    color: #667eea;
                    font-size: 24px;
                    font-weight: 600;
                    margin-bottom: 20px;
                }}
                .content {{
                    margin-bottom: 30px;
                }}
                .verify-btn {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 16px;
                    margin: 20px 0;
                }}
                .verify-btn:hover {{
                    opacity: 0.9;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 14px;
                    color: #666;
                    text-align: center;
                }}
                .warning {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 6px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #856404;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="logo">🔨</div>
                    <h1 class="title">Welcome to DIY Smart Assistant!</h1>
                </div>
                
                <div class="content">
                    <p>Hi <strong>{username}</strong>,</p>
                    
                    <p>Thank you for registering with DIY Smart Assistant! To complete your account setup and start using our intelligent DIY tools, please verify your email address.</p>
                    
                    <div style="text-align: center;">
                        <a href="{verification_url}" class="verify-btn">Verify My Email</a>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong> This verification link will expire in 24 hours. If you didn't create an account with us, please ignore this email.
                    </div>
                    
                    <p>Once verified, you'll have access to:</p>
                    <ul>
                        <li>🔍 <strong>Tool Identification</strong> - AI-powered tool recognition</li>
                        <li>🔍 <strong>Smart Tool Finder</strong> - Interactive tool recommendations</li>
                        <li>📊 <strong>Project Analysis</strong> - Comprehensive DIY project guidance</li>
                        <li>⭐ <strong>Curated Product Picks</strong> - Expert-selected tools and materials</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #667eea;">{verification_url}</p>
                    <p>Need help? Contact us at support@diyassistant.com</p>
                    <p>&copy; 2025 DIY Smart Assistant. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def get_verification_email_text(self, username: str, verification_url: str) -> str:
        """Generate plain text content for verification email"""
        return f"""
        Welcome to DIY Smart Assistant!
        
        Hi {username},
        
        Thank you for registering with DIY Smart Assistant! To complete your account setup, please verify your email address by clicking the link below:
        
        {verification_url}
        
        This verification link will expire in 24 hours.
        
        Once verified, you'll have access to our intelligent DIY tools:
        - Tool Identification - AI-powered tool recognition
        - Smart Tool Finder - Interactive tool recommendations  
        - Project Analysis - Comprehensive DIY project guidance
        - Curated Product Picks - Expert-selected tools and materials
        
        If you didn't create an account with us, please ignore this email.
        
        Need help? Contact us at support@diyassistant.com
        
        © 2025 DIY Smart Assistant. All rights reserved.
        """
    
    async def send_verification_email(
        self, 
        to_email: str, 
        username: str, 
        verification_token: str,
        base_url: str = "http://localhost:8000"
    ) -> bool:
        """Send email verification email"""
        verification_url = f"{base_url}/api/v1/auth/verify?token={verification_token}"
        
        html_content = self.get_verification_email_html(username, verification_url)
        text_content = self.get_verification_email_text(username, verification_url)
        
        return await self.send_email(
            to_email=to_email,
            subject="Please verify your email address",
            html_content=html_content,
            text_content=text_content
        )


# Global email service instance
email_service = EmailService()