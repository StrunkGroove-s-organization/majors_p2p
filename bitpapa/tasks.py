import time
import requests

from secrets import token_buy, token_sell
from myproject.celery import app
from base.views import update_payment_methods
from .models import ExchangeBitpapa

exchange = 'Bitpapa'
url = 'https://bitpapa.com/api/v1/partners/ads/search?sort={sort}&crypto_currency_code={currency}&currency_code=RUB&limit=100&page=1&type={site}'


@app.task
def main(currencies, buy_sell, timeout):

    def fetches(all_ads, currencies, site, timeout):

        def fetch(currency, site):
            sort = 'price' if site == 'sell' else '-price'
            token = token_sell if site == 'sell' else token_buy
            constructed_url = url.format(
                currency=currency,
                site=site,
                sort=sort,
            )
            headers = {
                'Accept': 'application/json',
                'X-Access-Token': token,
            }
            response = requests.get(constructed_url, headers=headers)
            status_code = response.status_code

            if status_code == 200:
                data = response.json()
                return data
            else:
                return False

        def pars(all_ads, data):

            ads = data['ads']

            for ad in ads:

                name = ad['user_name']

                pay = ad['payment_method_code']
                code = ad['payment_method_bank_code']
                pay = code if pay == 'SPECIFIC_BANK' else pay
                payments = update_payment_methods([pay])
                    
                price = float(ad['price'])
                buy_sell = 'SELL' if ad['type'] == 'buy' else 'BUY'
                token = ad['crypto_currency_code'].upper()

                if not name or not payments or not price or not token:
                    continue

                existing_object = next((ad for ad in all_ads 
                    if ad.name == name and 
                    ad.price == price and 
                    ad.buy_sell == buy_sell and 
                    ad.token == token
                ), None)

                if existing_object is None:
                    record = ExchangeBitpapa()
                    record.name = name
                    record.order_q = float(ad.get('tradeMonthTimes', 0))
                    record.order_p = float(ad.get('orderCompleteRate', 0))
                    record.payments = payments
                    record.buy_sell = buy_sell
                    record.price = price
                    record.lim_min = float(ad['limit_min'])
                    record.lim_max = float(ad['limit_max'])
                    record.token = token
                    record.fiat = ad['currency_code']
                    record.adv_no = ad['user_name']
                    available = float(ad['limit_max'])
                    record.available = round(available / price, 4)
                    record.available_rub = available
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

    save_db(all_ads, ExchangeBitpapa)
    return len(all_ads)