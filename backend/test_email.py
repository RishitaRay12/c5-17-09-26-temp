import os
import sys
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", ""))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("APPLICATION_EMAIL")
EMAIL_TO = os.getenv("SUPPORT_EMAIL")

print(f"SMTP_HOST: {SMTP_HOST}")
print(f"SMTP_PORT: {SMTP_PORT}")
print(f"SMTP_USERNAME: {SMTP_USERNAME}")
print(f"EMAIL_FROM: {EMAIL_FROM}")
print(f"EMAIL_TO: {EMAIL_TO}")
print(f"SMTP_PASSWORD present: {bool(SMTP_PASSWORD)}")

if not all([SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO]):
    print("ERROR: Missing email configuration!")
    sys.exit(1)

try:
    print("\nAttempting SMTP connection...")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        print("[OK] Connected to SMTP server")
        server.starttls()
        print("[OK] STARTTLS enabled")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        print("[OK] Authentication successful")
        
        # Send test email
        msg = MIMEText("This is a test email for handoff verification.")
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        msg["Subject"] = "[TEST] Human Handoff Email Configuration"
        
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print("[OK] Test email sent successfully!")
        print(f"\nCheck your inbox at {EMAIL_TO}")
        
except smtplib.SMTPAuthenticationError as e:
    print(f"[ERROR] Authentication failed: {e}")
    print("Check your SMTP_USERNAME and SMTP_PASSWORD in .env")
except smtplib.SMTPException as e:
    print(f"[ERROR] SMTP error: {e}")
# except Exception as e:
#     print(f"[ERROR] Error: {e}")
