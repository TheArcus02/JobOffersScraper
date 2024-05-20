import json
import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()


def login():
    pass
    url = 'https://login.pracuj.pl/api/public/users/sign-in'
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
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'x-auth-csrf-hash': '56be1a47db0f21fe7d4cc02f26b5b2c496e15f7a852abaa9ac3b891f24399e4a',
        'x-kl-ajax-request': 'Ajax_Request',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
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


def scrapper_get_page():
    pass
    url = 'https://it.pracuj.pl/praca?et=1%2C3%2C17&itth=33%2C34%2C36%2C37%2C42%2C73%2C76%2C213%2C77&pn=1'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        return res.text
    else:
        print(f'Error: {res.status_code}')
        print(res.text)
        return None


def save_to_file(data, filename):
    pass
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(data)


def offers_parser(filename: str):
    pass
    with open(filename, 'r', encoding='utf-8') as file:
        html = file.read()
        pattern = r'<script\s+id="__NEXT_DATA__"\s+type="application\/json">\{.*?\}<\/script>'
        match = re.search(pattern, html)
        if match:
            json_data = match.group(0)
            start_index = json_data.find('{')
            end_index = json_data.rfind('}') + 1
            offers = json.loads(json_data[start_index:end_index])
            return offers['props']['pageProps']['data']['jobOffers']['groupedOffers']
        else:
            print(f'Not found data inside: {filename}')
            return None


if __name__ == '__main__':
    # token = login()
    # print(token)
    # page_html = scrapper_get_page()
    # save_to_file(page_html, 'offers_page.html')
    offers = offers_parser('offers_page.html')
    print(json.dumps(offers, indent=4, ensure_ascii=False))
