import os
import time
import json

import requests
import websocket


class BaseP2P:
    def __init__(self):
        self.payments = {
            'tinkoff': 'Tinkoff',
            'sber': 'Sber',
            'sbp': 'SBP',
            'raiffeisen': 'Raiffeisenbank',
            'bank': 'Bank Transfer',
            'post': 'Post Bank',
            'russian': 'Russian Standart',

            'alfa': 'Alfa',
            'mir': 'MIR',
            'balance_mob': 'Balance Mobile',
            'ymoney': 'ЮMoney',
            'visa_master': 'Visa / MasterCard',
            'qiwi': 'QIWI',
            'sovkom': 'Совкомбанк',
            'uralsiib': 'Уралсиб',
            'mts': 'MTS',
            'gazprom': 'Gazprom',
            'promsvyazbank': 'Промсвязьбанк',
            'webmoney': 'WebMoney',
            'home': 'Банк Хоум Кредит',
            'vtb': 'VTB',
        }


class BaseParsingP2P(BaseP2P):
    def __init__(self, dict: dict):
        super().__init__()

        self.session = requests.Session()
        self.url = dict['url']  
        self.headers = dict.get('headers')  
        self.timeout = dict.get('timeout')  

        self.trade_types = dict.get('trade_types')
        self.currencies = dict.get('currencies')
        self.pay_types = dict.get('pay_types')
        self.path_list = dict.get('path')

        self.index = 1
        self.class_db = dict['class_db']  

    def fetch(self, url_params: dict) -> dict:
        url = self.url.format(**url_params)
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            return None
        return response.json()

    def update_payment_methods(self, payment_methods: list) -> None:
        updated_methods = []
        for method in payment_methods:
            new_method = self.switch(method)
            if new_method is None: continue
            updated_methods.append(new_method)
        return updated_methods

    def unpack(self, data: dict, path_list: list) -> dict:
        """
        Return flat list
        """
        if path_list:
            for path in path_list:
                data = data[path]
        return data

    def pars(self, ads_list: list, data: dict, currency: str) -> None:

        ads = self.unpack(data, self.path_list)

        for ad in ads:
            dict = self.require_info(ad)

            if dict is None \
            or not dict['name'] or not dict['payments'] \
            or not dict['price'] or not dict['token']:
                continue
    
            existing = next((ad for ad in ads_list 
                if ad.name == dict['name'] and 
                ad.price == dict['price'] and 
                ad.buy_sell == dict['buy_sell'] and 
                ad.token == dict['token']
            ), None)

            if existing is None:
                record = self.create_record(ad, dict)
                self.index += 1
                ads_list.append(record)
            else:
                existing.payments = list(set(existing.payments) \
                                         .union(dict['payments']))

    def save_db(self, ads: list) -> None:
        column_update = [
            'name', 'order_q', 'order_p', 'price', 'lim_min', 'lim_max',
            'fiat',  'token', 'buy_sell', 'exchange', 'adv_no', 'available',
            'available_rub', 'payments',
        ]
 
        num_to_update = len(ads)
        num_existing = self.class_db.objects.count()

        self.class_db.objects.bulk_update(ads, column_update)

        if num_to_update < num_existing:
            self.class_db.objects.filter(id__gt=num_to_update).delete()
        elif num_to_update == num_existing:
            pass
        else:
            another_ads = ads[num_existing:]
            self.class_db.objects.bulk_create(another_ads)

    
class TotalcoinParsing(BaseParsingP2P):
    def switch(self, method: str) -> str:
        match method:
            case 'Тинькофф':
                return self.payments['tinkoff']
            case 'СберБанк':
                return self.payments['sber']
            case 'Райффайзенбанк':
                return self.payments['raiffeisen']
            case 'СБП':
                return self.payments['sbp']
            case _:
                return None

    def require_info(self, ad: dict) -> tuple:
        name = ad['user']['nickname']
        pay = ad['paymentMethod']['name']
        payments = self.update_payment_methods([pay])
        price = float(ad['price'])
        buy_sell = 'BUY' if ad['type'] == 'SELL' else 'SELL'
        token = ad['cryptocurrency'].upper()

        dict = {
            'name': name,
            'payments': payments,
            'price': price,
            'token': token,
            'buy_sell': buy_sell,
        }

        return dict

    def create_record(self, ad: dict, dict: dict) -> tuple:
        record = self.class_db()
        record.id = self.index
        record.name = dict['name']
        record.payments = dict['payments']
        record.buy_sell = dict['buy_sell']
        record.token = dict['token']

        record.order_q = float(ad['user']['okReviewCount'])
        record.order_p = 50
        record.price = dict['price']
        record.lim_min = float(ad['limitMin'])
        record.lim_max = float(ad['limitMax'])
        record.fiat = ad['user']['currency']['id'].upper()

        available = ad['limitMax']
        record.available = round(available / dict['price'], 4)
        record.available_rub = available * dict['price']
        record.adv_no = ad['id']
        return record
    
    def main(self) -> int:
        ads_list = []

        for currency in self.currencies:
            for site in self.trade_types:
                url_params = {'currency': currency, 'site': site}
                data = self.fetch(url_params)
                if data is None: continue
                self.pars(ads_list, data, currency)
                time.sleep(self.timeout)

        self.save_db(ads_list)
        return len(ads_list)
    

class KucoinParsing(BaseParsingP2P):
    def switch(self, method: str) -> str:
        match method:
            case 'BANK_TRANSFER':
                return self.payments['bank']
            case 'BANK':
                return self.payments['bank']
            case 'SBP':
                return self.payments['sbp']
            case _:
                return None

    def require_info(self, ad: dict) -> tuple:
        name = ad['nickName']
        payments = []
        for pay in ad['adPayTypes']:
            pay = pay['payTypeCode']
            payments.append(pay)
        payments = self.update_payment_methods(payments)
        price = ad.get('floatPrice')
        if price:
            price = float(price)
        buy_sell = 'BUY' if ad['side'] == 'SELL' else 'SELL'
        token = ad['currency'].upper()
        
        dict = {
            'name': name,
            'payments': payments,
            'price': price,
            'token': token,
            'buy_sell': buy_sell,
        }

        return dict

    def create_record(self, ad: dict, dict: dict):
        record = self.class_db()
        record.id = self.index
        record.name = dict['name']
        record.payments = dict['payments']
        record.buy_sell = dict['buy_sell']
        record.token = dict['token']
        record.price = dict['price']
        record.order_q = float(ad.get('dealOrderNum', 0)) if ad.get('dealOrderNum', 0) else 0
        record.order_p = float(ad.get('dealOrderNum').replace('%', '')) if ad.get('dealOrderNum') else 0
        record.lim_min = float(ad['limitMinQuote'])
        record.lim_max = float(ad['limitMaxQuote'])
        record.fiat = ad['legal'].upper()
        record.adv_no = ad['id']
        available = float(ad['currencyBalanceQuantity'])
        record.available = round(available, 4)
        record.available_rub = available * dict['price']
        return record

    def main(self) -> int:
        ads_list = []

        for currency in self.currencies:
            for site in self.trade_types:
                for pay_type in self.pay_types:

                    url_params = {
                        'currency': currency,
                        'site': site,
                        'pay_type': pay_type,
                    }

                    data = self.fetch(url_params)
                    if data is None: continue
                    self.pars(ads_list, data, currency)
                    time.sleep(self.timeout)

        self.save_db(ads_list)
        return len(ads_list)


class GarantexParsing(BaseParsingP2P):
    def __init__(self, dict: dict):
        super().__init__(dict)
        self.ads_list = []
        self.number_ads = 2

    def fetch(self) -> dict:
        response = requests.get(self.url)

        if response.status_code != 200:
            return None
    
        response_data = response.text

        data_start = response_data.find('window.gon = ')
        data_end = response_data.find(';', data_start)
        data_str = response_data[data_start + len('window.gon = '):data_end]
        
        json_data = json.loads(data_str)
        data = json_data['exchangers']

        return data

    def create_record(self, entry, token, site):
        record = self.class_db()
        record.id = self.index
        record.name = 'Биржевой стакан'
        record.order_q = 100
        record.order_p = 100
        record.payments = ['Tinkoff', 'Sber']
        record.buy_sell = 'SELL' if site == 'bid' else 'BUY'
        record.price = float(entry['price'])
        record.lim_min = 500
        record.lim_max = float(entry['amount'])
        record.token = token
        record.fiat = 'RUB'
        record.available = float(entry['volume'])
        
        return record

    def main(self) -> int:
        data = self.fetch()

        if not data:
            return 
        
        for token, symbol in self.currencies.items():
            for site in self.trade_types:
                ads = data[symbol][site][:self.number_ads]

                for entry in ads:
                    record = self.create_record(entry, token, site)
                    self.ads_list.append(record)
                    self.index += 1

        self.save_db(self.ads_list)
        return len(self.ads_list)
    

class GateioParsing(BaseParsingP2P):
    def fetch(self, constructed_data: dict) -> dict:
        response = requests.post(url=self.url,
                                 data=constructed_data, headers=self.headers)
        
        if response.status_code != 200:
            return None
        return response.json()

    def require_info(self, ad: dict) -> tuple:
        name = ad['username']
        payments = ad['pay_type_num'].split(',')
        payments = self.update_payment_methods(payments)
        price = float(ad['rate'])
        buy_sell = 'BUY' if ad['type'] == 'sell' else 'SELL'
        token = ad['curr_a'].upper()
        
        dict = {
            'name': name,
            'payments': payments,
            'price': price,
            'token': token,
            'buy_sell': buy_sell,
        }
        
        return dict

    def create_record(self, ad: dict, dict: dict):
        record = self.class_db()
        record.id = self.index
        record.name = dict['name']
        record.payments = dict['payments']
        record.buy_sell = dict['buy_sell']
        record.token = dict['token']
        record.price = dict['price']

        record.order_q = float(ad['complete_number'])
        record.order_p = float(ad['complete_rate_month'])
        record.lim_min = round(float(ad['limit_total'].split('~')[0]) * dict['price'], 2)
        record.lim_max = round(float(ad['limit_total'].split('~')[1]) * dict['price'], 2)
        record.fiat = ad['curr_b'].upper()
        record.adv_no = ad['uid']
        available = float(ad['total'].replace(',', ''))
        record.available = round(available, 4)
        record.available_rub = available * dict['price']
        return record

    def switch(self, method: str) -> str:
        match method:
            case '22':
                return self.payments['qiwi']
            case '186':
                return self.payments['raiffeisen']
            case _:
                return None

    def main(self) -> int:
        ads_list = []

        for currency in self.currencies:
            for pay_type in self.pay_types:

                constructed_data = f'type=push_order_list&symbol={currency}&big_trade=0&amount=&pay_type={pay_type}&is_blue='

                data = self.fetch(constructed_data)
                if data is None: continue
                self.pars(ads_list, data, currency)
                time.sleep(self.timeout)

        self.save_db(ads_list)
        return len(ads_list)
    

class HodlHodlParsing(BaseParsingP2P):
    def __init__(self, dict: dict):
        super().__init__(dict)
        self.ads_list = []

    def fetch(self, constructed_url: str) -> dict:
        response = requests.get(constructed_url, headers=self.headers)

        if response.status_code != 200:
            return None
        return response.json()

    def require_info(self, ad: dict) -> tuple:
        name = ad['trader']['login']
        price = float(ad['price'])
        buy_sell = 'SELL' if ad['side'] == 'buy' else 'BUY'
        
        if buy_sell == 'SELL':
            pay = ad['payment_methods']
            payments = [paymethod['name'] for paymethod in pay]
        else:
            pay = ad['payment_method_instructions']
            payments = [paymethod['payment_method_name'] for paymethod in pay]
        payments = self.update_payment_methods(payments)
        token = ad['asset_code'].upper()
        
        dict = {
            'name': name,
            'payments': payments,
            'price': price,
            'token': token,
            'buy_sell': buy_sell,
        }

        return dict

    def create_record(self, ad: dict, dict: dict):
        record = self.class_db()
        record.id = self.index
        record.name = dict['name']
        record.payments = dict['payments']
        record.buy_sell = dict['buy_sell']
        record.token = dict['token']
        record.price = dict['price']

        rating = ad['trader']['rating']
        record.order_p = float(rating if rating else 0) * 100
        record.order_q = float(ad['trader']['trades_count'])
        record.lim_min = float(ad['min_amount'])
        record.lim_max = float(ad['max_amount'])
        record.fiat = ad['currency_code'].upper()
        record.adv_no = ad['id']
        available = float(ad['max_amount'])
        record.available = round(available / dict['price'], 4) 
        record.available_rub = available
        return record

    def switch(self, method: str) -> str:
        match method:
            case 'Sberbank':
                return self.payments['sber']
            case 'Tinkoff':
                return self.payments['tinkoff']
            case _:
                return None

    def main(self) -> int:
        for site in self.trade_types:
            for pay_type in self.pay_types:
                constructed_url = self.url.format(
                    site=site,
                    pay_type=pay_type,
                )

                data = self.fetch(constructed_url)
                if data is None: continue
                self.pars(self.ads_list, data, 'BTC')
                time.sleep(self.timeout)

        self.save_db(self.ads_list)
        return len(self.ads_list)
    

class HuobiParsing(BaseParsingP2P):
    def __init__(self, dict: dict):
        super().__init__(dict)
        self.ads_list = []
        self.tokens = {
            1: 'BTC', 2: 'USDT', 3: 'ETH', 4: 'HT', 5: 'EOS', 7: 'XRP', 
            8: 'LTC', 22: 'TRX', 62: 'USDD',
        }

    def fetch(self, url: dict) -> dict:
        response = requests.get(url)

        if response.status_code != 200:
            return None
        return response.json()

    def require_info(self, ad: dict) -> tuple:
        if ad['isOnline'] == False:
            return None

        name = ad['userName']

        payments = []
        payments_dicts = ad['payMethods']
        for pay in payments_dicts:
            payments.append(pay['name'])
        payments = self.update_payment_methods(payments)

        price = float(ad['price'])
        buy_sell = 'SELL' if ad['tradeType'] == 0 else 'BUY'
        token = self.tokens[ad['coinId']].upper()
        
        dict = {
            'name': name,
            'payments': payments,
            'price': price,
            'token': token,
            'buy_sell': buy_sell,
        }

        return dict

    def create_record(self, ad: dict, dict: dict):
        record = self.class_db()
        record.id = self.index
        record.name = dict['name']
        record.payments = dict['payments']
        record.buy_sell = dict['buy_sell']
        record.token = dict['token']
        record.price = dict['price']

        record.order_q = float(ad.get('tradeMonthTimes', 0))
        record.order_p = float(ad.get('orderCompleteRate', 0))
        record.lim_min = float(ad['minTradeLimit'])
        record.lim_max = float(ad['maxTradeLimit'])
        record.fiat = 'RUB' if ad['currency'] == 11 else 'ERROR'
        record.adv_no = ad['uid']
        available = float(ad['tradeCount'])
        record.available = round(available, 4)
        record.available_rub = available * dict['price']
        return record

    def switch(self, method: str) -> str:
        match method:
            case 'Raiffeisenbank':
                return self.payments['raiffeisen']
            case 'QIWI':
                return self.payments['qiwi']
            case 'Yandex':
                return self.payments['ymoney']
            case 'Tinkoff':
                return self.payments['tinkoff']
            case 'Sberbank':
                return self.payments['sber']
            case 'SBP - Fast Bank Transfer':
                return self.payments['sbp']
            case 'MTS-Bank':
                return self.payments['mts']
            case 'Post Bank':
                return self.payments['post']
            case _:
                return None

    def main(self):
        for currency in self.currencies:
            for site in self.trade_types:
                for pay_type in self.pay_types:
                    constructed_url = self.url.format(
                        currency=currency,
                        site=site,
                        pay_type=pay_type,
                    )

                data = self.fetch(constructed_url)
                if data is None: continue
                self.pars(self.ads_list, data, 'BTC')
                time.sleep(self.timeout)

        self.save_db(self.ads_list)
        return len(self.ads_list)
    

class BybitParsing(BaseParsingP2P):
    def __init__(self, dict: dict):
        super().__init__(dict)
        self.ads_list = []

    def fetch(self, currency: str, site: str, pay_type: str) -> dict:
        payload = {
            'userId':"",
            'tokenId': currency,
            'currencyId': "RUB",
            'payment': pay_type,
            'side': site,
            'size': "10",
            'page': "1",
            'amount': "",
            'authMaker': False,
            'canTrade': False,
        }
        response = requests.post(url=self.url, json=payload, headers=self.headers)

        if response.status_code != 200:
            return None
        return response.json()

    def require_info(self, ad: dict) -> tuple:
        name = ad['nickName']
        payments = self.update_payment_methods(ad['payments'])
        price = float(ad['price'])
        buy_sell = 'SELL' if ad['side'] == 0 else 'BUY'
        token = ad['symbolInfo']['tokenId'].upper()
        
        dict = {
            'name': name,
            'payments': payments,
            'price': price,
            'token': token,
            'buy_sell': buy_sell,
        }

        return dict

    def create_record(self, ad: dict, dict: dict):
        record = self.class_db()
        record.id = self.index
        record.name = dict['name']
        record.payments = dict['payments']
        record.buy_sell = dict['buy_sell']
        record.token = dict['token']
        record.price = dict['price']

        record.order_q = float(ad['recentOrderNum'])
        record.order_p = float(ad['recentExecuteRate'])
        record.lim_min = float(ad['minAmount'])
        record.lim_max = float(ad['maxAmount'])
        record.fiat = ad['symbolInfo']['currencyId'].upper()
        available = float(ad['lastQuantity'])
        record.available = round(available, 4)
        record.available_rub = available * dict['price']
        record.adv_no = ad['userId']
        return record

    def switch(self, method: str) -> str:
        match method:
            case '64':
                return self.payments['raiffeisen']
            case '533':
                return self.payments['russian']
            case '574':
                return self.payments['ymoney']
            case '581':
                return self.payments['tinkoff']
            case '582':
                return self.payments['sber']
            case _:
                return None

    def main(self):
        for currency in self.currencies:
            for site in self.trade_types:
                for pay_type in self.pay_types:
                    data = self.fetch(currency, site, pay_type)
                    if data is None: continue
                    self.pars(self.ads_list, data, currency)
                    time.sleep(self.timeout)

        self.save_db(self.ads_list)
        return len(self.ads_list)
    

class BitpapaParsing(BaseParsingP2P):
    def __init__(self, dict: dict):
        super().__init__(dict)
        self.api_token_buy = os.getenv('TOKEN_FIRST')
        self.api_token_sell = os.getenv('TOKEN_SECOND')
        self.ads_list = []

    def switch(self, method: str) -> str:
        match method:
            # case 'BANK_TRANSFER':
            #     return self.payments['bank']
            case _:
                return method

    def fetch(self, url_params: dict, headers: dict) -> dict:
        url = self.url.format(**url_params)
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return None
        return response.json()

    def require_info(self, ad: dict) -> tuple:
        name = ad['user_name']
        pay = ad['payment_method_code']
        code = ad['payment_method_bank_code']
        payment = code if pay == 'SPECIFIC_BANK' else pay
        payments = self.update_payment_methods([payment])
        price = float(ad['price'])
        buy_sell = 'SELL' if ad['type'] == 'buy' else 'BUY'
        token = ad['crypto_currency_code'].upper()

        dict = {
            'name': name,
            'payments': payments,
            'price': price,
            'token': token,
            'buy_sell': buy_sell,
        }

        return dict
    
    def create_record(self, ad: dict, dict: dict):
        record = self.class_db()
        record.id = self.index
        record.name = dict['name']
        record.payments = dict['payments']
        record.buy_sell = dict['buy_sell']
        record.token = dict['token']
        record.price = dict['price']

        record.order_q = float(ad.get('tradeMonthTimes', 0))
        record.order_p = float(ad.get('orderCompleteRate', 0))
        record.lim_min = float(ad['limit_min'])
        record.lim_max = float(ad['limit_max'])
        record.fiat = ad['currency_code']
        record.adv_no = ad['user_name']
        available = float(ad['limit_max'])
        record.available = round(available / dict['price'], 4)
        record.available_rub = available
        return record
    
    def main(self) -> int:
        ads_list = []

        for currency in self.currencies:
            for site in self.trade_types:

                sort = 'price' if site == 'SELL' else '-price'
                token = self.api_token_sell if site == 'SELL' else self.api_token_buy

                url_params = {
                    'currency': currency,
                    'site': site,
                    'sort': sort,
                }
                headers = {
                    'Accept': 'application/json',
                    'X-Access-Token': token,
                }

                data = self.fetch(url_params, headers)
                if data is None: continue
                self.pars(ads_list, data, currency)
                time.sleep(self.timeout)

        self.save_db(ads_list)
        return len(ads_list)
    

class BeribitParsing(BaseParsingP2P):
    def __init__(self, dict) -> None:
        super().__init__(dict)
        self.ws = websocket.WebSocket()
        self.request = {
            'event': 'subscribe',
            'channel': 'depth',
            'symbol': 'usdtrub',
        }
        self.all_ads = []
        self.max_ads = dict.get('max_ads')

    def create_record(self, ad: dict, trade_type: str) -> None:
        record = self.class_db()

        price = float(ad['ExchangeRate'])
        size = float(ad['Size'])

        record.id = self.index
        record.name = 'Биржевой стакан'
        record.payments = [self.payments['tinkoff'], self.payments['sber']]
        record.buy_sell = trade_type
        record.token = 'USDT'
        record.price = price
        record.order_q = 100
        record.order_p = 100
        record.lim_min = 500
        record.lim_max = size
        record.fiat = 'RUB'
        record.adv_no = '#'
        record.available = round(size, 4)
        record.available_rub = size * price

        self.all_ads.append(record)

    def ws_connect(self) -> None:
        self.ws.connect(self.url, header=self.headers)
        self.ws.send(json.dumps(self.request))

    def wait_message(self) -> dict:
        while True:
            message = self.ws.recv()
            data = json.loads(message)
            return data
    
    def parsing(self, message) -> None:
        data = message['Depth']
        for trade_type in self.trade_types: 
            items = data[trade_type][:self.max_ads]
            for item in items:
                self.create_record(item, trade_type)
                self.index += 1

        self.ws.close()

    def main(self) -> int:
        self.ws_connect()
        message = self.wait_message()
        self.parsing(message)
        self.save_db(self.all_ads)
        return len(self.all_ads)


class MexcParsing(BaseParsingP2P):
    def switch(self, method: str) -> str:
        match method:
            case '12':
                return self.payments['sber']
            case '13':
                return self.payments['tinkoff']
            case _:
                return None

    def require_info(self, ad: dict) -> tuple:
        name = ad['merchant']['nickName']
        payments = self.update_payment_methods(ad['payMethod'].split(','))
        price = float(ad['price'])
        buy_sell = 'BUY' if ad['tradeType'] == 1 else 'SELL'
        token = ad['coinName'].upper()
        
        dict = {
            'name': name,
            'payments': payments,
            'price': price,
            'token': token,
            'buy_sell': buy_sell,
        }

        return dict

    def create_record(self, ad: dict, dict: dict):
        record = self.class_db()
        record.id = self.index
        record.name = dict['name']
        record.payments = dict['payments']
        record.buy_sell = dict['buy_sell']
        record.token = dict['token']
        record.price = dict['price']
        record.order_q = float(ad['merchantStatistics']['doneLastMonthCount'])
        record.order_p = float(ad['merchantStatistics']['lastMonthCompleteRate']) * 100
        record.lim_min = float(ad['minTradeLimit'])
        record.lim_max = float(ad['maxTradeLimit'])
        record.fiat = ad['currency'].upper()
        available = ad['availableQuantity']
        record.available = round(available, 4)
        record.available_rub = available * dict['price']
        return record

    def main(self) -> int:
        ads_list = []

        for currency in self.currencies:
            for site in self.trade_types:
                for pay_type in self.pay_types:

                    url_params = {
                        'currency': currency,
                        'site': site,
                        'pay_type': pay_type,
                    }

                    data = self.fetch(url_params)
                    if data is None: continue
                    self.pars(ads_list, data, currency)
                    time.sleep(self.timeout)

        self.save_db(ads_list)
        return len(ads_list)