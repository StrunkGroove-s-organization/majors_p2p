from django.core.cache import cache


class BaseP2P:
    def __init__(self, validated_data):
        self.validated_data = validated_data

    def create_key(self, trade_type, crypto, number):
        return f'{trade_type}--{crypto}--{number}'

    def get_trade_type(self):
        trade_type = self.validated_data['trade_type']
        return trade_type

    def get_crypto(self):
        crypto = self.validated_data['crypto']
        return crypto


class BaseAndFiltersP2P(BaseP2P):
    def delete_ads(self, data, delete_indexes):   
        for index in reversed(delete_indexes):
            data.pop(index)


    def filter_only_stable_coin(self, data):
        only_stable_coin = self.validated_data.get('only_stable_coin')

        if only_stable_coin is not True: return 

        delete_indexes = []

        for index, ad in enumerate(data):
            token = ad['2']['token']

            if token != 'USDT':
                delete_indexes.append(index)
        
        self.delete_ads(data, delete_indexes)


    def filter_required(self, data):
        pay_methods = self.validated_data['payment_methods']

        delete_indexes = []

        for index, ad in enumerate(data):
            buy_pay = ad['1']['best_payment']
            sell_pay = ad['2']['best_payment']

            if buy_pay not in pay_methods or sell_pay not in pay_methods:
                delete_indexes.append(index)
            
        self.delete_ads(data, delete_indexes)


    def filter_required_ex(self, data):
        exchanges = self.validated_data['exchanges']

        delete_indexes = []

        for index, ad in enumerate(data):
            buy_item = ad['1']['exchange']
            sell_item = ad['2']['exchange']

            if buy_item not in exchanges or sell_item not in exchanges:
                delete_indexes.append(index)

        self.delete_ads(data, delete_indexes)


    def filter_spread(self, data):
        user_spread = self.validated_data.get('user_spread')

        if user_spread:
            delete_indexes = []

            for index, ad in enumerate(data):
                spread = ad['spread']

                if spread > user_spread:
                    delete_indexes.append(index)
        
            self.delete_ads(data, delete_indexes)


    def filter_first_lim(self, data):
        lim = self.validated_data.get('lim_first')
    
        if not lim: return 

        delete_indexes = []

        for index, ad in enumerate(data):
            first_lim_min = ad['1']['lim_min']
            first_lim_max = ad['1']['lim_max']

            if first_lim_min > lim or lim > first_lim_max:
                delete_indexes.append(index)

        self.delete_ads(data, delete_indexes)


    def filter_second_lim(self, data):
        lim = self.validated_data.get('lim_second')
    
        if not lim: return

        delete_indexes = []

        for index, ad in enumerate(data):
            first_lim_min = ad['2']['lim_min']
            first_lim_max = ad['2']['lim_max']

            if first_lim_min > lim or lim > first_lim_max:
                delete_indexes.append(index)

        self.delete_ads(data, delete_indexes)


    def filter_ord_q(self, data):
        ord_q = self.validated_data.get('ord_q')
    
        if not ord_q: return

        delete_indexes = []

        for index, ad in enumerate(data):
            first_order_q = ad['1']['order_q']
            second_order_q = ad['2']['order_q']

            if ord_q > first_order_q or ord_q > second_order_q:
                delete_indexes.append(index)

        self.delete_ads(data, delete_indexes)


    def filter_ord_p(self, data):
        ord_p = self.validated_data.get('ord_p')
    
        if not ord_p: return

        delete_indexes = []

        for index, ad in enumerate(data):
            first_order_p = ad['1']['order_p']
            second_order_p = ad['2']['order_p']

            if ord_p > first_order_p or ord_p > second_order_p:
                delete_indexes.append(index)

        self.delete_ads(data, delete_indexes)


    def filter_first_available(self, data):
        available = self.validated_data.get('available_first')
    
        if not available: return

        delete_indexes = []

        for index, ad in enumerate(data):
            first_available = ad['1']['available_rub']

            if available > first_available:
                delete_indexes.append(index)

        self.delete_ads(data, delete_indexes)


    def filter_second_available(self, data):
        available = self.validated_data.get('available_second')
    
        if not available: return
        
        delete_indexes = []

        for index, ad in enumerate(data):
            second_available = ad['2']['available_rub']

            if available > second_available:
                delete_indexes.append(index)

        self.delete_ads(data, delete_indexes)


    def create_unique_record(self, ad: dict):
        buy_exchange = ad['1']['exchange']
        buy_pay = ad['1']['best_payment']
        buy_token = ad['1']['token']

        sell_exchange = ad['2']['exchange']
        sell_pay = ad['2']['best_payment']
        sell_token = ad['2']['token']
        
        buy = f'{buy_exchange}--{buy_pay}--{buy_token}'
        sell = f'{sell_exchange}--{sell_pay}--{sell_token}'

        return f'{buy}--{sell}', 
        

    def filter_best_links(self, data):
        unique_links = {}
        delete_indexes = []

        for index, ad in enumerate(data):
            unique_record = self.create_unique_record(ad)

            if unique_record not in unique_links.keys():
                unique_links[unique_record] = {
                    'index': index,
                    'spread': ad['spread']
                }
            else:
                if ad['spread'] > unique_links[unique_record]['spread']:
                    delete_indexes.append(index)
                else:
                    delete_indexes.append(unique_links[unique_record]['index'])
                    del unique_links[unique_record]

        self.delete_ads(data, delete_indexes)

class TriangularP2PServices(BaseAndFiltersP2P):
    def __init__(self, validated_data):
        super().__init__(validated_data)
        self.number = 3

    def get_ads(self):
        trade_type = self.get_trade_type()
        crypto = self.get_crypto()

        key = self.create_key(trade_type, crypto, self.number)
        values = cache.get(key)
        if not values:
            return 'Values doesnt exists'

        self.filter_required(values)
        self.filter_required_ex(values)
        self.filter_spread(values)
        self.filter_first_lim(values)
        self.filter_second_lim(values)
        self.filter_ord_q(values)
        self.filter_ord_p(values)
        self.filter_first_available(values)
        self.filter_second_available(values)
        self.filter_only_stable_coin(values)
        self.filter_best_links(values)

        values.sort(key=lambda item: item['spread'], reverse=True)

        return values


class BinaryP2PServices(BaseAndFiltersP2P):
    def __init__(self, validated_data):
        super().__init__(validated_data)
        self.number = 2


    def get_ads(self):
        trade_type = self.get_trade_type()
        crypto = self.get_crypto()

        key = self.create_key(trade_type, crypto, self.number)
        values = cache.get(key)
        if not values:
            return 'Values doesnt exists'

        self.filter_required(values)
        self.filter_required_ex(values)
        self.filter_spread(values)
        self.filter_first_lim(values)
        self.filter_second_lim(values)
        self.filter_ord_q(values)
        self.filter_ord_p(values)
        self.filter_first_available(values)
        self.filter_second_available(values)

        values.sort(key=lambda item: item['spread'], reverse=True)

        return values
    

class BestPricesP2PServices:
    pass