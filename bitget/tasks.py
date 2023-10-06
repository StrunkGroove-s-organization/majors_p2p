import time

from myproject.celery import app
from base.views import update_payment_methods
from .models import ExchangeBitget

exchange = 'bitget'
url = 'https://www.bitget.com/v1/p2p/pub/adv/queryAdvList'
headers = {
    'Host': 'www.bitget.com',
    'Cookie': '__cf_bm=4eEhQ7IR7XNSnSz5Z__k.v3km3xtEWV9K6XLpJPYTgg-1693514222-0-Ac8cyv+GtMlqYjQqd/sgzkHgpX8jIrYPEE5s0ZlZXZbK2FX5TDF8mQupiMm60NLGqdgxc0BzYwUXsPuyxzzBhxs=; path=/; expires=Thu, 31-Aug-23 21:07:02 GMT; domain=.bitget.com; HttpOnly; Secure; SameSite=None',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'https://www.bitget.com/p2p-trade?fiatName=RUB',
    'Content-Type': 'application/json;charset=utf-8',
    'Content-Length': '105'
}

# @app.task
def main(currencies, buy_sell, pay_types, timeout):

    def fetches(all_ads, currencies, buy_sell, pay_types, timeout):

        def fetch(currency, site, pay_type):
            data = {
                "side": site,
                "pageNo": 1,
                "pageSize": 10,
                "coinCode": currency,
                "fiatCode": "RUB",
                "paymethodId": pay_type,
                "languageType": 6
            }

            # scraper = cloudscraper.create_scraper()
            
            response = scraper.post(url, headers=headers, json=data)
            status_code = response.status_code

            if status_code == 200:
                data = response.json()
                return data
            else:
                print(response.text)
                return False


        def pars(all_ads, data):

            ads = data['data']['dataList']

            for ad in ads:
                name = ad['nickName']
                payments = [paymethod['paymethodName'] for paymethod in ad['paymethodInfo']]
                price = float(ad['price'])
                buy_sell = 'BUY' if ad['adType'] == 1 else 'Sell'

                if not name or not payments or not price:
                    return

                existing_object = next((ad for ad in all_ads if ad.name == name and ad.price == price and ad.buy_sell == buy_sell), None)

                if existing_object is None:
                    record = ExchangeBitget()

                    record.name = name
                    record.order_q = float(ad['turnoverNum'])
                    record.order_p = float(ad['turnoverRateNum'])
                    record.payments = update_payment_methods(payments)
                    record.buy_sell = buy_sell
                    record.price = price
                    record.lim_min = float(ad['minAmount'])
                    record.lim_max = float(ad['maxAmount'])
                    record.token = ad['coinCode'].upper()
                    record.fiat = ad['fiatCode'].upper()
                    record.available = ad['editAmount']
                    record.adv_no = ad['adNo']
                    record.exchange = exchange

                    all_ads.append(record)
                else:
                    existing_object.payments = list(set(existing_object.payments).union(payments))

        for currency in currencies:
            for site in buy_sell:
                for pay_type in pay_types:
                    time.sleep(timeout)
                    
                    data = fetch(currency, site, pay_type)
                    if data:
                        pars(all_ads, data)

    all_ads = []
    fetches(all_ads, currencies, buy_sell, pay_types, timeout)

    for index, record in enumerate(all_ads, start=1):
        record.id = index

    def save_db(ads, classDB):
        column_update = [
            'name',
            'order_q',
            'order_p',
            'price',
            'lim_min',
            'lim_max',
            'fiat',
            'token',
            'buy_sell',
            'exchange',
            'payments',
        ]

        num_ads_to_update = len(ads)
        num_existing_ads = classDB.objects.count()
        classDB.objects.bulk_update(ads, column_update)

        if num_ads_to_update < num_existing_ads:
            classDB.objects.filter(id__gt=num_ads_to_update).delete()
        elif num_ads_to_update == num_existing_ads:
            pass
        else:
            another_ads = ads[num_existing_ads:]
            classDB.objects.bulk_create(another_ads)

    save_db(all_ads, ExchangeBitget)
    return len(all_ads)