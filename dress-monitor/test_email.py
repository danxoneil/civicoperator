#!/usr/bin/env python3
"""
Email Configuration Test Script
Tests email notification settings for the dress monitor
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_email_configuration():
    """Test email notification settings"""

    print("=" * 60)
    print("Email Configuration Test")
    print("=" * 60)
    print()

    # Load environment variables
    send_email = os.getenv('SEND_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
    notification_email = os.getenv('NOTIFICATION_EMAIL', '')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')

    # Check configuration
    print("📋 Current Configuration:")
    print(f"  SEND_EMAIL_NOTIFICATIONS: {send_email}")
    print(f"  NOTIFICATION_EMAIL: {notification_email or '(not set)'}")
    print(f"  SMTP_SERVER: {smtp_server}")
    print(f"  SMTP_PORT: {smtp_port}")
    print(f"  SMTP_USER: {smtp_user or '(not set)'}")
    print(f"  SMTP_PASSWORD: {'*' * len(smtp_password) if smtp_password else '(not set)'}")
    print()

    # Validation
    if not send_email:
        print("⚠️  SEND_EMAIL_NOTIFICATIONS is not set to 'true'")
        print("   Email notifications are disabled.")
        print()
        print("To enable, set: SEND_EMAIL_NOTIFICATIONS=true")
        return False

    if not all([notification_email, smtp_user, smtp_password]):
        print("❌ Missing required configuration:")
        if not notification_email:
            print("   - NOTIFICATION_EMAIL is not set")
        if not smtp_user:
            print("   - SMTP_USER is not set")
        if not smtp_password:
            print("   - SMTP_PASSWORD is not set")
        print()
        print("Please configure these in your .env file or GitHub Secrets.")
        return False

    # Attempt to send test email
    print("📧 Sending test email...")
    print()

    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = notification_email
        msg['Subject'] = "🧪 Test - Emilio Pucci Dress Monitor"

        body = f"""
This is a test email from your Emilio Pucci Dress Monitor.

✅ Your email configuration is working correctly!

Configuration Details:
- SMTP Server: {smtp_server}:{smtp_port}
- Sending From: {smtp_user}
- Sending To: {notification_email}
- Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

When the dress is found, you will receive a notification similar to this one
with the item details, link, and pricing information.

---
This is an automated test message. No action required.
"""

        msg.attach(MIMEText(body, 'plain'))

        # Connect and send
        print(f"Connecting to {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        print("Authenticating...")
        server.login(smtp_user, smtp_password)

        print("Sending message...")
        server.send_message(msg)
        server.quit()

        print()
        print("=" * 60)
        print("✅ SUCCESS! Test email sent successfully!")
        print("=" * 60)
        print()
        print(f"Check your inbox at: {notification_email}")
        print("(It may take a few minutes to arrive)")
        print()
        print("If you don't see it:")
        print("  1. Check your spam/junk folder")
        print("  2. Verify the email address is correct")
        print("  3. For Gmail, ensure you're using an App Password")
        print()
        return True

    except smtplib.SMTPAuthenticationError:
        print()
        print("=" * 60)
        print("❌ Authentication Failed")
        print("=" * 60)
        print()
        print("The SMTP username or password is incorrect.")
        print()
        print("For Gmail users:")
        print("  1. Go to: https://myaccount.google.com/apppasswords")
        print("  2. Generate a new App Password for 'Mail'")
        print("  3. Use that 16-character password (no spaces)")
        print("  4. Update SMTP_PASSWORD with the new App Password")
        print()
        return False

    except smtplib.SMTPException as e:
        print()
        print("=" * 60)
        print("❌ SMTP Error")
        print("=" * 60)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Possible issues:")
        print("  - SMTP server or port is incorrect")
        print("  - Network connection issues")
        print("  - Email provider blocking the connection")
        print()
        return False

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Unexpected Error")
        print("=" * 60)
        print()
        print(f"Error: {str(e)}")
        print()
        return False


if __name__ == "__main__":
    success = test_email_configuration()
    sys.exit(0 if success else 1)
