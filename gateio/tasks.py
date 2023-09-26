import time
import requests

from myproject.celery import app
from base.views import update_payment_methods
from .models import ExchangeGateIo

exchange = 'Gate.io'
url = 'https://www.gate.io/json_svr/query_push/?u=21&c=388882'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'https://www.gate.io/ru/c2c/market',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://www.gate.io',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Te': 'trailers',
    'Connection': 'close'
  }

@app.task
def main(currencies, pay_types, timeout):

    def fetches(all_ads, currencies, pay_types, timeout):

        def fetch(currency, pay_type):
            data = 'type=push_order_list&symbol={currency}&big_trade=0&amount=&pay_type={pay_type}&is_blue='
            constructed_data = data.format(
                currency=currency,
                pay_type=pay_type,
            )

            response = requests.post(url=url, data=constructed_data, headers=headers)

            status_code = response.status_code

            if status_code == 200:
                data = response.json()
                return data
            else:
                return False

        def pars(all_ads, data):

            ads = data['push_order']

            for ad in ads:
                name = ad['username']
                payments = ad['pay_type_num'].split(',')
                price = float(ad['rate'])
                buy_sell = 'BUY' if ad['type'] == 'sell' else 'SELL'
                token = ad['curr_a'].upper()

                if not name or not payments or not price or not token:
                    continue

                existing_object = next((ad for ad in all_ads 
                    if ad.name == name and 
                    ad.price == price and 
                    ad.buy_sell == buy_sell and 
                    ad.token == token
                ), None)

                if existing_object is None:
                    record = ExchangeGateIo()
                    available = float(ad['total'].replace(',', ''))

                    record.name = name
                    record.order_q = float(ad['complete_number'])
                    record.order_p = float(ad['complete_rate_month'])
                    record.payments = update_payment_methods(payments)
                    record.buy_sell = buy_sell
                    record.price = price
                    record.lim_min = float(ad['limit_total'].split('~')[0])
                    record.lim_max = float(ad['limit_total'].split('~')[1])
                    record.token = token
                    record.fiat = ad['curr_b'].upper()
                    record.available = round(available / price, 4)
                    record.available_rub = available
                    record.adv_no = ad['uid']
                    record.exchange = exchange

                    all_ads.append(record)
                else:
                    existing_object.payments = list(set(existing_object.payments).union(payments))

        for currency in currencies:
            for pay_type in pay_types:
                time.sleep(timeout)
                
                data = fetch(currency, pay_type)
                if data:
                    pars(all_ads, data)

    all_ads = []
    fetches(all_ads, currencies, pay_types, timeout)

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
            'available',
            'available_rub',
            'adv_no',
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

    save_db(all_ads, ExchangeGateIo)
    return len(all_ads)