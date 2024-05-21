import datetime
import json
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from constants import OFFERS_HTML_TEMPLATE


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


def build_email_body(offers):
    offer_sections = []
    for offer in offers:
        job_title = offer["attributes"]["jobTitle"]
        location = offer["attributes"]["workplaces"][0]["inlandLocation"]["location"]["name"]
        apply_url = offer["attributes"].get('offerAbsoluteUrl', '#')
        remote_work = "Yes" if offer["attributes"]["employment"][
            "entirelyRemoteWork"] else "No"
        publication_date = offer["publicationDetails"][
            "lastPublishedUtc"] if "publicationDetails" in offer else "Unknown"
        expiration_date = offer["publicationDetails"][
            "expirationDateUtc"] if "publicationDetails" in offer else "Unknown"

        publication_date = datetime.datetime.strptime(publication_date, "%Y-%m-%dT%H:%M:%SZ").strftime(
            "%Y-%m-%d %H:%M:%S")
        expiration_date = datetime.datetime.strptime(expiration_date, "%Y-%m-%dT%H:%M:%SZ").strftime(
            "%Y-%m-%d %H:%M:%S")

        sections = []
        for section in offer["attributes"]["textSections"]:
            section_title = section.get("sectionType", "").replace("-", " ").capitalize()
            section_content = "<br>".join(section["textElements"])
            if section.get("sectionType") in ["technologies-expected", "technologies-optional",
                                              "requirements-expected",
                                              "requirements-optional", "work-organization-work-style",
                                              "work-organization-team-members", "development-practices",
                                              "training-space", "offered", "benefits"]:
                section_content = "<ul>" + "".join(f"<li>{item}</li>" for item in section["textElements"]) + "</ul>"
            sections.append(f"""
                <div class="section">
                    <h3>{section_title}</h3>
                    <p>{section_content}</p>
                </div>
                """)

        sections_html = "".join(sections)
        offer_sections.append(f"""
            <div class="offer">
                <h2>{job_title}</h2>
                <div class="uri">
                    <a href="{apply_url}">Apply here</a>
                </div>
                <p>Location: {location}</p>
                <p>Remote work available: {remote_work}</p>
                <p>Publication Date: {publication_date}</p>
                <p>Expiration Date: {expiration_date}</p>
                {sections_html}
            </div>
            """)

    offers_html = "".join(offer_sections)
    return OFFERS_HTML_TEMPLATE.format(offers=offers_html)


if __name__ == '__main__':
    pass
    config = EmailConfig()
    email_sender = EmailSender(config=config)
    subject = "New Job Offers"
    with open('data/offer_details/1003308306.json', 'r') as offer_file:
        json = json.load(offer_file)
        offers = [json]
        body = build_email_body(offers)
        email_sender.send_email(subject=subject, body=body)
