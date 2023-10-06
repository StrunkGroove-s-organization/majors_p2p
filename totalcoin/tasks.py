import time
import requests

from myproject.celery import app
from base.views import update_payment_methods
from .models import ExchangeTotalCoin

exchange = 'TotalCoin'
url = 'https://totalcoin.io/ru/offers/ajax-offers-list?type={site}&currency=rub&crypto={currency}&pm=&pro=0'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
}
max_ads = 30

@app.task
def main(currencies, buy_sell, timeout):

    def fetches(all_ads, currencies, buy_sell, timeout):

        def fetch(currency, site):
            constructed_url = url.format(
                site=site,
                currency=currency,
            )

            response = requests.get(constructed_url, headers=headers)

            status_code = response.status_code

            if status_code == 200:
                data = response.json()
                return data
            else:
                print(status_code)
                return False

        def pars(all_ads, data):

            ads = data['data'] # [:max_ads]

            for ad in ads:
                name = ad['user']['nickname']
                pay = ad['paymentMethod']['name']
                payments = update_payment_methods([pay])
                price = float(ad['price'])
                buy_sell = 'BUY' if ad['type'] == 'SELL' else 'SELL'
                token = ad['cryptocurrency'].upper()

                if not name or not payments or not price or not token:
                    continue

                existing_object = next((ad for ad in all_ads 
                    if ad.name == name and 
                    ad.price == price and 
                    ad.buy_sell == buy_sell and 
                    ad.token == token
                ), None)
                    
                if existing_object is None:
                    record = ExchangeTotalCoin()
                    available = ad['limitMax']

                    record.name = name
                    record.order_q = float(ad['user']['okReviewCount'])
                    record.order_p = 50
                    record.payments = payments
                    record.buy_sell = buy_sell
                    record.price = price
                    record.lim_min = float(ad['limitMin'])
                    record.lim_max = float(ad['limitMax'])
                    record.token = token
                    record.fiat = ad['user']['currency']['id'].upper()
                    record.available = round(available / price, 4)
                    record.available_rub = available * price
                    record.adv_no = ad['id']
                    record.exchange = exchange

                    all_ads.append(record)
                else:
                    existing_object.payments = list(set(existing_object.payments).union(payments))

        for currency in currencies:
            for site in buy_sell:
                time.sleep(timeout)
                
                data = fetch(currency, site)
                if data:
                    pars(all_ads, data)

    all_ads = []
    fetches(all_ads, currencies, buy_sell, timeout)

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
            'adv_no',
            'available',
            'available_rub',
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

    save_db(all_ads, ExchangeTotalCoin)
    return len(all_ads)