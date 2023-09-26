import time
import requests

from myproject.celery import app
from base.views import update_payment_methods
from .models import ExchangeHuobi

exchange = 'huobi'
url = 'https://www.huobi.com/-/x/otc/v1/data/trade-market?coinId={currency}&currency=11&tradeType={site}&currPage=1&payMethod={pay_type}&acceptOrder=0&country=&blockType=general&online=1&range=0&amount=&onlyTradable=false&isFollowed=false'
tokens = {
    1: 'BTC',
    2: 'USDT',
    3: 'ETH',
    4: 'HT',
    5: 'EOS',
    7: 'XRP',
    8: 'LTC',
    22: 'TRX',
    62: 'USDD',
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

            response = requests.get(constructed_url)
            status_code = response.status_code

            if status_code == 200:
                data = response.json()
                return data
            else:
                return False

        def pars(all_ads, data):

            ads = data['data']

            for ad in ads:
                if ad['isOnline'] == False:
                    continue

                name = ad['userName']

                payments = []
                payments_dicts = ad['payMethods']
                for pay in payments_dicts:
                    payments.append(pay['name'])
                    
                price = float(ad['price'])
                buy_sell = 'SELL' if ad['tradeType'] == 0 else 'BUY'
                token_id = ad['coinId']
                token = tokens[token_id].upper()

                if not name or not payments or not price or not token:
                    continue

                existing_object = next((ad for ad in all_ads 
                    if ad.name == name and 
                    ad.price == price and 
                    ad.buy_sell == buy_sell and 
                    ad.token == token
                ), None)

                if existing_object is None:
                    record = ExchangeHuobi()
                    available = float(ad['tradeCount'])

                    record.name = name
                    record.order_q = float(ad.get('tradeMonthTimes', 0))
                    record.order_p = float(ad.get('orderCompleteRate', 0))
                    record.payments = update_payment_methods(payments)
                    record.buy_sell = buy_sell
                    record.price = price
                    record.lim_min = float(ad['minTradeLimit'])
                    record.lim_max = float(ad['maxTradeLimit'])
                    record.token = token
                    record.fiat = 'RUB' if ad['currency'] == 11 else 'ERROR'
                    record.adv_no = ad['uid']
                    record.available = round(available, 4)
                    record.available_rub = available * price
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
            'available',
            'adv_no',
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

    save_db(all_ads, ExchangeHuobi)
    return len(all_ads)