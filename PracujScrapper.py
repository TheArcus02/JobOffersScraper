import json
import os
import re
import time

import requests
from dotenv import load_dotenv

from constants import LOGIN_URL, USER_AGENT, JSON_PATTERN, OFFERS_URL
from database import Database
from utils import save_to_file


class PracujScrapper:
    def __init__(self):
        load_dotenv()
        self.db = Database()

    def login(self):
        url = LOGIN_URL
        headers = {
            'accept': '*/*',
            'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json; charset=utf-8',
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
        for offer in offers:
            if not self.db.offer_exists_from_json(offer):
                self.db.save_offer_from_json(offer)
                full_offer_details = self.get_offer_details(offer)
                offer_details = self.extract_offer_details(full_offer_details)
                time.sleep(5)

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
        id = offer['offers'][0]['partitionId']
        if uri is None:
            print('URI not found')
            return None
        html = self.scrape_page(uri)
        save_to_file(html, 'offer_details.html', encoding='utf-8')
        offer_details_json = self.get_json_from_html(html)
        save_to_file(json.dumps(offer_details_json, indent=4), f'full_offer_details/{id}.json')
        return offer_details_json['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']

    def check_if_offer_fits(self, offer):
        pass

    def extract_offer_details(self, offer_json):
        offer_details = {
            "publicationDetails": {
                "isActive": offer_json.get("publicationDetails", {}).get("isActive")
            },
            "attributes": {
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
        save_to_file(json.dumps(offer_details, indent=4), f'offer_details/{offer_json.get('jobOfferWebId', {})}.json')
        return offer_details
