import time
import requests

from myproject.celery import app
from base.views import update_payment_methods
from .models import ExchangeHodlHodl

exchange = 'Hodl Hodl'
url = 'https://hodlhodl.com/api/frontend/offers?filters%5Bpayment_method_name%5D={pay_type}&filters%5Bcurrency_code%5D=RUB&pagination%5Boffset%5D=0&filters%5Bside%5D={site}&facets%5Bshow_empty_rest%5D=true&facets%5Bonly%5D=false&pagination%5Blimit%5D=50'
headers = {
  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
}

@app.task
def main(buy_sell, pay_types, timeout):

    def fetches(all_ads, buy_sell, pay_types, timeout):

        def fetch(site, pay_type):
            constructed_url = url.format(
                site=site,
                pay_type=pay_type,
            )

            response = requests.get(constructed_url, headers=headers)
            status_code = response.status_code

            if status_code == 200:
                data = response.json()
                return data
            else:
                return False

        def pars(all_ads, data):

            ads = data['offers']

            for ad in ads:
                name = ad['trader']['login']
                price = float(ad['price'])
                buy_sell = 'SELL' if ad['side'] == 'buy' else 'BUY'
                
                if buy_sell == 'SELL':
                    pay = ad['payment_methods']
                    payments = [paymethod['name'] for paymethod in pay]
                else:
                    pay = ad['payment_method_instructions']
                    payments = [paymethod['payment_method_name'] for paymethod in pay]
                payments = update_payment_methods(payments)
                token = ad['asset_code'].upper()

                if not name or not payments or not price or not token:
                    continue

                existing_object = next((ad for ad in all_ads 
                    if ad.name == name and 
                    ad.price == price and 
                    ad.buy_sell == buy_sell and 
                    ad.token == token
                ), None)

                if existing_object is None:
                    record = ExchangeHodlHodl()
                    available = float(ad['max_amount'])

                    record.name = name
                    rating = ad['trader']['rating']
                    record.order_q = float(rating if rating else 0)
                    record.order_p = float(ad['trader']['trades_count'])
                    record.payments = payments
                    record.buy_sell = buy_sell
                    record.price = price
                    record.lim_min = float(ad['min_amount'])
                    record.lim_max = float(ad['max_amount'])
                    record.token = token
                    record.fiat = ad['currency_code'].upper()
                    record.adv_no = ad['id']
                    record.available = round(available / price, 4) 
                    record.available_rub = available
                    record.exchange = exchange

                    all_ads.append(record)
                else:
                    existing_object.payments = list(set(existing_object.payments).union(payments))

        for site in buy_sell:
            for pay_type in pay_types:
                time.sleep(timeout)
                
                data = fetch(site, pay_type)
                if data:
                    pars(all_ads, data)

    all_ads = []
    fetches(all_ads, buy_sell, pay_types, timeout)

    for index, record in enumerate(all_ads, start=1):
        record.id = index

    def save_db(ads, classDB):
        column_update = [
            'name',
            'order_q',
            'order_p',
            'payments',
            'buy_sell',
            'price',
            'lim_min',
            'lim_max',
            'token',
            'fiat',
            'adv_no',
            'available',
            'available_rub',
            'exchange',
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

    save_db(all_ads, ExchangeHodlHodl)
    return len(all_ads)