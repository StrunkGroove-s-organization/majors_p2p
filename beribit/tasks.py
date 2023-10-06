import json
import websocket

from myproject.celery import app
from base.views import update_payment_methods
from .models import ExchangeBeribit

number_max_ads = 2
exchange = 'Beribit'
ws_url = 'wss://beribit.com/ws/depth/usdtrub'
headers = {
    'Content-Type': 'application/json;charset=utf-8',
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
}


def ws_connect(ws_url, headers, all_ads):

    def subscribe():
        request = {
            'event': 'subscribe',
            'channel': 'depth',
            'symbol': 'usdtrub',
        }
        ws.send(json.dumps(request))

    def pars(data, all_ads):

        def pars_table(items, all_ads, buy_sell):
            for i in items:
                record = ExchangeBeribit()
                price = float(i['ExchangeRate'])

                record.name = 'Биржевой стакан'
                record.order_q = 100
                record.order_p = 100
                record.payments = ['Tinkoff', 'Sber']
                record.buy_sell = buy_sell
                record.price = price
                record.lim_min = 500
                record.lim_max = float(i['Price'])
                record.token = 'USDT'
                record.fiat = 'RUB'
                record.adv_no = '#'
                available = float(i['Size'])
                record.available = round(available, 4)
                record.available_rub = available * price
                record.exchange = exchange

                all_ads.append(record)

        ask_items = data['Asks'][:number_max_ads]
        pars_table(ask_items, all_ads, 'SELL')

        bid_items = data['Bids'][:number_max_ads]
        pars_table(bid_items, all_ads, 'BUY')

    ws = websocket.WebSocket()
    ws.connect(ws_url, header=headers)

    subscribe()

    while True:
        message = ws.recv()
        data = json.loads(message)
        pars(data['Depth'], all_ads)

        if len(all_ads) == 4:
            ws.close()
            return
        else:
            all_ads = []

@app.task
def main():

    all_ads = []
    ws_connect(ws_url, headers, all_ads)

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

    save_db(all_ads, ExchangeBeribit)
    return len(all_ads)