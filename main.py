import json

from PracujScrapper import PracujScrapper


def scrapePracuj():
    pass
    scrapper = PracujScrapper()
    print('logging in...')
    token = scrapper.login()
    print('scrapping offers...')
    offers_json = scrapper.get_offers()
    print('validating offers...')
    scrapper.validate_and_save_offers(offers_json)


def testing_scrape():
    pass
    scrapper = PracujScrapper()

    with open('data/offers_page.html', 'r', encoding='utf-8') as offers_file:
        offers_html = offers_file.read()
        offers_json = scrapper.get_json_from_html(offers_html)
        # print(offers_json)
        with open('data/offer_details.html', 'r', encoding='utf-8') as details_file:
            offer_details_html = details_file.read()
            full_offer_details_json = scrapper.get_json_from_html(offer_details_html)
            print(json.dumps(full_offer_details_json, indent=4),
                  open('data/full_offer_details.json', 'w', encoding='utf-8'))
            offer_details = scrapper.extract_offer_details(full_offer_details_json)
            print(offer_details)


if __name__ == '__main__':
    pass
    scrapePracuj()
    # testing_scrape()
