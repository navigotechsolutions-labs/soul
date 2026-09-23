"""Email delivery service for Email OTP authentication and system notifications."""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Optional

logger = logging.getLogger("soul.auth.email_service")


class EmailService:
    """Handles sending transactional emails and verification codes."""

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        use_tls: Optional[bool] = None,
    ):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "").strip()
        port_env = os.getenv("SMTP_PORT", "587").strip()
        self.smtp_port = smtp_port or (int(port_env) if port_env.isdigit() else 587)
        self.smtp_user = smtp_user or os.getenv("SMTP_USER", "").strip()
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "").strip()
        self.from_email = (
            from_email
            or os.getenv("SMTP_FROM_EMAIL", "").strip()
            or self.smtp_user
            or "auth@navigotechsolutions.com"
        )
        self.use_tls = use_tls if use_tls is not None else (os.getenv("SMTP_USE_TLS", "1") in ("1", "true", "True"))

    @property
    def is_smtp_configured(self) -> bool:
        """Returns True if SMTP host and credentials are provided."""
        return bool(self.smtp_host and (self.smtp_user or self.smtp_host == "localhost"))

    def send_otp_email(
        self,
        to_email: str,
        code: str,
        expires_in_minutes: int = 10,
    ) -> dict[str, Any]:
        """Sends a 6-digit OTP verification code via SMTP or local dev log fallback.
        
        Args:
            to_email: Recipient's destination email address.
            code: 6-digit numeric verification string.
            expires_in_minutes: Expiration window for this OTP.

        Returns:
            Dict containing delivery status and method.
        """
        to_email = to_email.strip().lower()

        # Subject and email body
        subject = f"Your Soul Engine Verification Code: {code}"
        text_body = (
            f"Hello,\n\n"
            f"Your Soul Engine one-time verification code is:\n\n"
            f"    {code}\n\n"
            f"This code will expire in {expires_in_minutes} minutes.\n"
            f"If you did not request this verification code, please ignore this email.\n\n"
            f"— The Soul Engine Team\n"
            f"https://soul.navigotechsolutions.com"
        )

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #090d14; color: #f8fafc; margin: 0; padding: 24px; }}
            .container {{ max-width: 500px; margin: 0 auto; background: #0f1523; border: 1px solid #1f2942; border-radius: 16px; padding: 32px; }}
            .header {{ text-align: center; margin-bottom: 24px; }}
            .logo {{ font-size: 24px; font-weight: 800; color: #10b981; letter-spacing: -0.5px; }}
            .badge {{ display: inline-block; font-size: 11px; font-family: monospace; background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 6px; padding: 3px 8px; margin-top: 4px; }}
            .otp-box {{ background: #090d14; border: 2px dashed #10b981; border-radius: 12px; text-align: center; padding: 20px; margin: 24px 0; }}
            .otp-code {{ font-size: 36px; font-weight: 800; font-family: monospace; letter-spacing: 8px; color: #10b981; }}
            .info {{ font-size: 13px; color: #94a3b8; line-height: 1.6; text-align: center; }}
            .footer {{ text-align: center; margin-top: 28px; font-size: 11px; color: #64748b; border-top: 1px solid #1f2942; padding-top: 16px; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <div class="logo">Ψ Soul Engine</div>
              <div class="badge">Affective AI & Anti-Slop Studio</div>
            </div>
            <p style="font-size: 15px; color: #e2e8f0; text-align: center; margin: 0;">Use the verification code below to complete your login:</p>
            <div class="otp-box">
              <div class="otp-code">{code}</div>
            </div>
            <p class="info">This code is valid for <strong>{expires_in_minutes} minutes</strong>. Never share this code with anyone.</p>
            <div class="footer">
              Soul Engine — Human-POV AI Cognitive Architecture<br>
              Navigo Tech Solutions • <a href="https://soul.navigotechsolutions.com" style="color: #10b981; text-decoration: none;">soul.navigotechsolutions.com</a>
            </div>
          </div>
        </body>
        </html>
        """

        if self.is_smtp_configured:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"Soul Engine <{self.from_email}>"
                msg["To"] = to_email

                msg.attach(MIMEText(text_body, "plain", "utf-8"))
                msg.attach(MIMEText(html_body, "html", "utf-8"))

                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    if self.use_tls:
                        server.ehlo()
                        server.starttls()
                        server.ehlo()
                    if self.smtp_user and self.smtp_password:
                        server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)

                logger.info(f"Successfully dispatched OTP email to {to_email}")
                return {
                    "sent": True,
                    "method": "smtp",
                    "recipient": to_email,
                }
            except Exception as e:
                logger.error(f"Failed to send email via SMTP to {to_email}: {e}")
                # Fallback to local log so login is never blocked
                return {
                    "sent": False,
                    "method": "smtp_failed",
                    "recipient": to_email,
                    "error": str(e),
                    "dev_otp": code,
                }

        # Local development / Demo mode fallback
        logger.info(f"[SOUL OTP DEV] Generated OTP code for {to_email}: {code} (expires in {expires_in_minutes}m)")
        print(f"\n[SOUL OTP CODE] --> Email: {to_email} | Code: {code} <--\n")
        return {
            "sent": True,
            "method": "dev_mode",
            "recipient": to_email,
            "dev_otp": code,
        }


# Global singleton instance
default_email_service = EmailService()
