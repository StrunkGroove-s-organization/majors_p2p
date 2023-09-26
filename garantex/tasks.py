import time
import json
import requests

from myproject.celery import app
from base.views import update_payment_methods
from .models import ExchangeGarantex

exchange = 'Garantex'
url = 'https://garantex.org/trading/btcrub'
number_pars_row = 2


@app.task
def main():

    def fetch():

        response = requests.get(url)
        status_code = response.status_code

        if status_code == 200:

            response_data = response.text

            start_index = response_data.find('window.gon = ')
            end_index = response_data.find(';', start_index)
            json_str = response_data[start_index + len('window.gon = '):end_index]
            
            json_data = json.loads(json_str)
            data = json_data['exchangers']

            return data
        else:
            return False

    def pars(data, token, all_ads):

        ask = data['ask'][:number_pars_row]
        bid = data['bid'][:number_pars_row]

        for entry in ask:
            record = ExchangeGarantex()

            record.name = 'Биржевой стакан'
            record.order_q = 100
            record.order_p = 100
            record.payments = ['Tinkoff', 'Sber']
            record.buy_sell = 'BUY'
            record.price = float(entry['price'])
            record.lim_min = 500
            record.lim_max = float(entry['amount'])
            record.token = token
            record.fiat = 'RUB'
            record.available = float(entry['volume'])
            record.exchange = exchange

            all_ads.append(record)

        for entry in bid:
            record = ExchangeGarantex()
            price = float(entry['price'])
            available = float(entry['volume'])

            record.name = 'Биржевой стакан'
            record.order_q = 100
            record.order_p = 100
            record.payments = ['Tinkoff', 'Sber']
            record.buy_sell = 'SELL'
            record.price = price
            record.lim_min = 500
            record.lim_max = float(entry['amount'])
            record.token = token
            record.fiat = 'RUB'
            record.available = round(available, 4)
            record.available_rub = round(available * price, 2)
            record.exchange = exchange

            all_ads.append(record)

    all_ads = []

    data = fetch()
    if data:
        pars(data['usdcrub'], 'USDC', all_ads)
        pars(data['btcrub'], 'BTC', all_ads)
        pars(data['ethrub'], 'ETH', all_ads)
        pars(data['usdtrub'], 'USDT', all_ads)
        pars(data['dairub'], 'DAI', all_ads)
                    
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

    save_db(all_ads, ExchangeGarantex)
    return len(all_ads)