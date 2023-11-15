import time

import requests


class BaseParsingP2P:
    def __init__(self, dict: dict):
        self.session = requests.Session()
        self.url = dict['url']  
        self.headers = dict['headers']  
        self.timeout = dict['timeout']  

        self.trade_types = dict.get('trade_types')
        self.currencies = dict.get('currencies')
        self.pay_types = dict.get('pay_types')
        self.path_list = dict.get('path')

        self.index = 1
        self.class_db = dict['class_db']  
        self.path_list = dict.get('path')
        self.payments = {
            'tinkoff': 'Tinkoff',
            'sber': 'Sber',
            'sbp': 'SBP',
            'raiffeisen': 'Raiffeisen',
            'bank': 'bank_transfer',

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


    def fetch(self, url_params: dict) -> dict:
        url = self.url.format(**url_params)
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            return None
        return response.json()
    

    def switch(self, method: str) -> str: # FIXME
        if method in [
                'B8', '97', '186', '64', 'Raiffeisen Bank', 'Райффайзенбанк',
                'Raiffeisenbank'
            ]:
            return 'Raiffeisenbank'

        elif method in ['B47', 'B21']: # ???
            return 'Tinkoff'

        elif method in ['B3', '13', '75', 'Тинькофф', 'Tinkoff', '581']:
            return 'Tinkoff'

        elif method in ['B39', 'Россельхозбанк']:
            return 'RosBank'

        elif method in ['B44', '44', 'MTS Bank', 'MTS-Bank']:
            return 'MTS-Bank'

        elif method in ['B2', '1', 'Alfa-Bank', 'Альфа-банк', 'Alfa Bank']:
            return 'Alfa-Bank'

        elif method in [
                'B1', '12', 'RosBank', '185', 'Sberbank', 'СберБанк', 'Sber','582',
            ]:
            return 'Sber'

        elif method in ['B7', 'Газпромбанк', 'Gazprom']:
            return 'Gazprom'

        elif method in ['31', '22', '62', 'QiWi', 'QIWI']:
            return 'QIWI'

        elif method in [
                '274', 'YM', 'Yandex', 'YooMoney', 'Юmoney', 'ЮMoney', '574'
            ]:
            return 'ЮMoney'

        elif method in ['14', 'BANK_TRANSFER']:
            return 'BANK'

        elif method in ['CASH', '90']:
            return 'Cash'

        elif method in ['B13', 'Pochta Bank', 'Post Bank', '357']:
            return 'Post-Bank'

        elif method in [
                'Home Credit Bank (Russia)', '102', 'Банк Хоум Кредит',
                'Home Credit Bank  (Russia)', 'Home Credit Bank'
            ]:
            return 'Home Credit Bank'

        elif method in [
                'B80', '23', '74', 'SBP - Fast Bank Transfer',
                'SBP System of fast payments', 'СБП', 'SBP',
            ]:
            return 'SBP'

        elif method in ['B5', 'VTB', 'ВТБ']:
            return 'VTB'

        elif method in ['73', 'Russia Standart Bank', '533']:
            return 'Russia-Standart-Bank'

        elif method in ['70', 'AK Bars Bank']:
            return 'AK Bars Bank'

        elif method in ['2', 'Банковская карта']:
            return 'Банковская карта'

        # elif method in ['B23', 'B15', 'B41', 'B22', 'B16', 'B14', 'USDT', 'Advanced cash RUB', 'Mobile Recharge', 'Payeer RUB', 'BTC Bitcoin']:
            # pass
        
        else:
            return None


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

            if not dict['name'] or not dict['payments'] \
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
                existing.payments = list(set(existing.payments).union(dict['payments']))


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
            case 'SBP':
                return self.payments['sbp']
            
            case _:
                return None


    def create_record(self, ad: dict, dict: dict):
        record = self.class_db()
        record.id = self.index
        record.name = dict['name']
        record.payments = dict['payments']
        record.buy_sell = dict['buy_sell']
        record.token = dict['token']
        record.price = dict['price']

        record.order_q = float(ad.get('completedOrderQuantity', 0))
        record.order_p = float(ad.get('completedRate', 0)) * 100
        record.lim_min = float(ad['limitMinQuote'])
        record.lim_max = float(ad['limitMaxQuote'])
        record.fiat = ad['legal'].upper()
        record.adv_no = ad['id']
        available = float(ad['currencyBalanceQuantity'])
        record.available = round(available, 4)
        record.available_rub = available * dict['price']
        return record
    

    def require_info(self, ad: dict) -> tuple:
        name = ad['nickName']
        payments = []
        for pay in ad['adPayTypes']:
            pay = pay['payTypeCode']
            payments.append(pay)
        payments = self.update_payment_methods(payments)
        price = float(ad['floatPrice'])
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


class KucoinParsing(BaseParsingP2P):
    def switch(self, method: str) -> str:
        match method:
            case 'BANK_TRANSFER':
                return self.payments['bank']
            case 'SBP':
                return self.payments['sbp']
            
            case _:
                return None


    def create_record(self, ad: dict, dict: dict):
        record = self.class_db()
        record.id = self.index
        record.name = dict['name']
        record.payments = dict['payments']
        record.buy_sell = dict['buy_sell']
        record.token = dict['token']
        record.price = dict['price']

        record.order_q = float(ad.get('completedOrderQuantity', 0))
        record.order_p = float(ad.get('completedRate', 0)) * 100
        record.lim_min = float(ad['limitMinQuote'])
        record.lim_max = float(ad['limitMaxQuote'])
        record.fiat = ad['legal'].upper()
        record.adv_no = ad['id']
        available = float(ad['currencyBalanceQuantity'])
        record.available = round(available, 4)
        record.available_rub = available * dict['price']
        return record
    

    def require_info(self, ad: dict) -> tuple:
        name = ad['nickName']
        payments = []
        for pay in ad['adPayTypes']:
            pay = pay['payTypeCode']
            payments.append(pay)
        payments = self.update_payment_methods(payments)
        price = float(ad['floatPrice'])
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
