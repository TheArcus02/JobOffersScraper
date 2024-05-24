from PracujScrapper import PracujScrapper


def scrapePracuj():
    pass
    scrapper = PracujScrapper()
    print('logging in...')
    token = scrapper.login()
    print('scrapping offers...')
    offers_json = scrapper.get_offers()
    print(f'Found {len(offers_json)} offers.')
    print('validating offers...')
    validated_offers = scrapper.validate_offers(offers_json)
    if not validated_offers:
        print('No new offers found.')
        return
    print(f'Validated {len(validated_offers)} offers.')
    print('sending email...')
    scrapper.send_email_with_offers(validated_offers)


if __name__ == '__main__':
    pass
    scrapePracuj()
