import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv


class EmailConfig:
    def __init__(self):
        load_dotenv()
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 465))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        self.receiver_email = os.getenv("RECEIVER_EMAIL")


class EmailSender:
    def __init__(self, config: EmailConfig = EmailConfig()):
        self.config = config

    def send_email(self, subject: str, body: str):
        message = MIMEMultipart()
        message['From'] = self.config.sender_email
        message['To'] = self.config.receiver_email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'html'))

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port, context=context) as server:
                server.login(self.config.sender_email, self.config.sender_password)
                server.send_message(message)
            print('Email sent successfully!')
        except Exception as e:
            print(f'Failed to send email: {e}')
