import datetime
import json
import os
import re
import time

import requests
from dotenv import load_dotenv

from Database import Database
from EmailSender import EmailSender
from constants import LOGIN_URL, USER_AGENT, JSON_PATTERN, OFFERS_URL, OFFERS_HTML_TEMPLATE
from utils import save_to_file


class PracujScrapper:
    def __init__(self):
        load_dotenv()
        self.db = Database()
        self.email_sender = EmailSender()

    def login(self):
        url = LOGIN_URL
        headers = {
            'accept': '*/*',
            'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json; charset=utf-8',
            'cookie': 'gp__cfXfiDZP=78; __cf_bm=JfSolsKxM.2fZpLc4qiJCycNVi6TC3VjHRQRbZLfz9s-1716204820-1.0.1.1-IuXz4_snWY5brRDnMKmeh6KhmkJgzmSm0edOuzNtzTIh.xePb2kf_nZDMKwC8SsBYGvhAaena3CyPNq0eXkWvg; __cfruid=829b5f8620d1324606978f1745f1eb8875bd88eb-1716204820; _cfuvid=3c.0CHBMKZZJw25QaZlQnC2CxbsJEN67DZBqCnhu__w-1716204820272-0.0.1.1-604800000; gptrackCookie=3ee511fe-d63d-416a-ye1a-07b5ef4d0b37; gp_lang=pl; cf_clearance=EDLXiQ.C0fsUSOU_4pXJ4ktYAG..vGrVXCBZGGf5lWQ-1716204821-1.0.1.1-lSjPN9bVWYfDunsTKRW0eVfRW1h2Dpdp00eKsU9QVI4ijSE2I7CwEzHtNQy5I9ogdsRs0i6c.se7k89BNoNWTQ; _gpantiforgery=CfDJ8I6hLzPzDNhHkh1OJJZeYhMNJkHtTme_4Sewxa3pZ86uzv_VMH3IThH1uQ3lB6wB0UoQuYa_adn0-9sJROMN23Wh9coxWA0YKp0RIJ3LMmwAUr8SYw6y95HIU0AyRupWD3zCVOKeWysY-uVzAnp-jYg; gpc_v=1; gpc_analytic=1; gpc_func=1; gpc_ad=1; gpc_audience=1; gpc_social=1; gp_ab__sales__205=B; _gpauthclient=pracuj.pl; XSRF-TOKEN=CfDJ8I6hLzPzDNhHkh1OJJZeYhMpEYSrTiiXQRn4OtNzz4fBkEPmcIk5_IYw-7YHCKVR_Vu9aqjuO_K7C3KN-oZC_rqNtdn7iE3XYgRrgA7a5QrQduzA_IGu6kaHOLvuqH_0247OA7GTPlmPJmigrhj6_Kw; gptrackPVID=f9e51301-bb81-4455-ae18-7214c0fa76cd; x-auth-csrf-token=cb05b2b1fd016dcb4644443a2b6e626eb902aba336a9a29fd2651a6e56abbc16; gptrackPVID=d7ece9a1-ab24-47cd-y81f-2c8edfdb78af',
            'origin': 'https://login.pracuj.pl',
            'priority': 'u=1, i',
            'referer': 'https://login.pracuj.pl/logowanie?aupid=73cf0224-ee40-485a-a875-41adb086d6e7',
            'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': USER_AGENT,
            'x-auth-csrf-hash': '56be1a47db0f21fe7d4cc02f26b5b2c496e15f7a852abaa9ac3b891f24399e4a',
            'x-kl-ajax-request': 'Ajax_Request',
            'User-Agent': USER_AGENT
        }
        data = {
            'login': os.getenv('PRACUJ_LOGIN'),
            'password': os.getenv('PRACUJ_PASSWORD')
        }
        res = requests.post(url, headers=headers, json=data)

        if res.status_code == 200:
            return res.json()
        else:
            print(f'Error: {res.status_code}')
            print(res.text)
            return None

    def scrape_page(self, url):
        headers = {
            'User-Agent': USER_AGENT
        }
        res = requests.get(url, headers=headers)

        if res.status_code == 200:
            return res.text
        else:
            print(f'Error: {res.status_code}')
            print(res.text)
            return None

    def get_json_from_html(self, html):
        match = re.search(JSON_PATTERN, html)
        if match:
            data = match.group(0)
            start_index = data.find('{')
            end_index = data.rfind('}') + 1
            json_data = json.loads(data[start_index:end_index])
            return json_data
        else:
            print(f'No matches found...')
            return None

    def validate_offers(self, offers):
        new_offers = []
        for offer in offers:
            if not self.db.offer_exists_from_json(offer):
                id = offer['offers'][0]['partitionId']

                # Save to DB
                self.db.save_offer_from_json(offer)

                # Get offer details
                full_offer_details = self.get_offer_details(offer)
                # Save full json to file
                save_to_file(json.dumps(full_offer_details, indent=4), f'full_offer_details/{id}.json')
                # Extract usefull offer details
                offer_details = self.extract_offer_details(full_offer_details)
                save_to_file(json.dumps(offer_details, indent=4),
                             f'offer_details/{id}.json')
                new_offers.append(offer_details)

                # Wait before next request to prevent ban
                time.sleep(5)

        return new_offers

    def send_email_with_offers(self, offers):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f'New Job Offers - {current_time}'
        body = self.build_email_body(offers)
        self.email_sender.send_email(subject, body)

    def get_offers(self):
        html = self.scrape_page(OFFERS_URL)
        if html is None:
            print('No offers found')
            return None
        save_to_file(html, 'offers_page.html', encoding='utf-8')
        offers_json = self.get_json_from_html(html)
        save_to_file(json.dumps(offers_json, indent=4), 'offers_page.json')
        return offers_json['props']['pageProps']['data']['jobOffers']['groupedOffers']

    def get_offer_details(self, offer):
        uri = offer['offers'][0]['offerAbsoluteUri']
        if uri is None:
            print('URI not found')
            return None
        html = self.scrape_page(uri)
        save_to_file(html, 'offer_details.html', encoding='utf-8')
        offer_details_json = self.get_json_from_html(html)
        return offer_details_json['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']

    def check_if_offer_fits(self, offer):
        # Implement chatGPT to validate the offer if it fits my needs
        pass

    def extract_offer_details(self, offer_json):
        offer_details = {
            "jobOfferWebId": offer_json.get('jobOfferWebId'),
            "publicationDetails": {
                "lastPublishedUtc": offer_json.get('publicationDetails', {}).get('lastPublishedUtc'),
                "expirationDateUtc": offer_json.get('publicationDetails', {}).get('expirationDateUtc'),
                "isActive": offer_json.get("publicationDetails", {}).get("isActive")
            },
            "attributes": {
                "offerAbsoluteUrl": offer_json.get('attributes', {}).get('offerAbsoluteUrl'),
                "jobTitle": offer_json.get("attributes", {}).get("jobTitle"),
                "applying": {
                    "applyURL": offer_json.get("attributes", {}).get("applying", {}).get("applyURL"),
                    "oneClickApply": offer_json.get("attributes", {}).get("applying", {}).get("oneClickApply")
                },
                "workplaces": [
                    {
                        "inlandLocation": {
                            "location": {
                                "name": workplace.get("inlandLocation", {}).get('location', {}).get("name")
                            }
                        }
                    } for workplace in offer_json.get("attributes", {}).get("workplaces", [])
                ],
                "employment": {
                    "positionLevels": [
                        {"name": level.get("name")} for level in
                        offer_json.get("attributes", {}).get("employment", {}).get("positionLevels", [])
                    ],
                    "entirelyRemoteWork": offer_json.get("attributes", {}).get("employment", {}).get(
                        "entirelyRemoteWork"),
                    "workSchedules": [
                        {"name": schedule.get("name")} for schedule in
                        offer_json.get("attributes", {}).get("employment", {}).get("workSchedules", [])
                    ],
                    "typesOfContracts": [
                        {
                            "name": contract.get("name"),
                            "salary": {
                                "from": contract.get("salary", {}).get("from") if contract.get("salary") else None,
                                "to": contract.get("salary", {}).get("to") if contract.get("salary") else None,
                                "currency": contract.get("salary", {}).get("currency", {}).get("code") if contract.get(
                                    "salary") else None,
                                "salaryKind": contract.get("salary", {}).get("salaryKind", {}).get(
                                    "name") if contract.get("salary") else None
                            }
                        } for contract in
                        offer_json.get("attributes", {}).get("employment", {}).get("typesOfContracts", [])
                    ],
                    "workModes": [
                        {"name": mode.get("name")} for mode in
                        offer_json.get("attributes", {}).get("employment", {}).get("workModes", [])
                    ]
                },
                "textSections": [
                    {
                        "sectionType": section.get("sectionType"),
                        "plainText": section.get("plainText"),
                        "textElements": section.get("textElements", [])
                    } for section in offer_json.get("textSections", [])
                ]
            }
        }
        return offer_details

    @staticmethod
    def build_email_body(offers):
        offer_sections = []
        for offer in offers:
            job_title = offer["attributes"]["jobTitle"]
            location = offer["attributes"]["workplaces"][0]["inlandLocation"]["location"]["name"]
            apply_url = offer["attributes"].get('offerAbsoluteUrl', '#')
            remote_work = "Yes" if offer["attributes"]["employment"][
                "entirelyRemoteWork"] else "No"
            publication_date = PracujScrapper.convert_date(offer["publicationDetails"][
                                                               "lastPublishedUtc"] if "publicationDetails" in offer else "Unknown")
            expiration_date = PracujScrapper.convert_date(offer["publicationDetails"][
                                                              "expirationDateUtc"] if "publicationDetails" in offer else "Unknown")

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

    @staticmethod
    def convert_date(date):
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        if re.search(r'\.\d+Z', date):
            date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        return datetime.datetime.strptime(date, date_format).strftime("%Y-%m-%d %H:%M:%S")
