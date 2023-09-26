import time
import requests

from myproject.celery import app
from base.views import update_payment_methods
from .models import ExchangeKucoin

exchange = 'kucoin'
url = 'https://www.kucoin.com/_api/otc/ad/list?currency={currency}&side={site}&payTypeCodes={pay_type}&legal=RUB&page=1&pageSize=10&status=PUTUP&lang=nl_NL'

headers = {
    'Host': 'www.kucoin.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'https://www.kucoin.com/nl/otc/buy/BTC-RUB',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Te': 'trailers'
  }

@app.task
def main(currencies, buy_sell, pay_types, timeout):

    def fetches(all_ads, currencies, buy_sell, pay_types, timeout):

        def fetch(currency, site, pay_type):
            constructed_url = url.format(
                currency=currency,
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

            ads = data['items']

            for ad in ads:
                name = ad['nickName']
                
                payments = []
                for pay in ad['adPayTypes']:
                    pay = pay['payTypeCode']
                    payments.append(pay)

                price = float(ad['floatPrice'])
                buy_sell = 'BUY' if ad['side'] == 'SELL' else 'SELL'
                token = ad['currency'].upper()

                if not name or not payments or not price or not token:
                    continue

                existing_object = next((ad for ad in all_ads 
                    if ad.name == name and 
                    ad.price == price and 
                    ad.buy_sell == buy_sell and 
                    ad.token == token
                ), None)

                if existing_object is None:
                    record = ExchangeKucoin()
                    available = float(ad['currencyBalanceQuantity'])

                    record.name = name
                    record.order_q = float(ad.get('completedOrderQuantity', 0))
                    record.order_p = float(ad.get('completedRate', 0)) * 100
                    record.payments = update_payment_methods(payments)
                    record.buy_sell = buy_sell
                    record.price = price
                    record.lim_min = float(ad['limitMinQuote'])
                    record.lim_max = float(ad['limitMaxQuote'])
                    record.token = token
                    record.fiat = ad['legal'].upper()
                    record.adv_no = ad['id']
                    record.available = round(available, 4)
                    record.available_rub = available * price
                    record.exchange = exchange

                    all_ads.append(record)
                else:
                    existing_object.payments = list(
                        set(existing_object.payments).union(payments)
                    )

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

    save_db(all_ads, ExchangeKucoin)
    return len(all_ads)