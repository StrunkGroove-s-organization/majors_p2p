import requests

from django.db import connection
from django.core.cache import cache
from psycopg2.extensions import AsIs

from parsing.services import BaseP2P
from .models import (
    AdsInTwo, BestLinksInTwoActions,
    AdsInThree, BestLinksInThreeActions,
)


class BaseCount(BaseP2P):
    def __init__(self):
        super().__init__()

        self.time_cash = 60
        self.min_spread = 0.01
        self.buy_sell = ['BUY', 'SELL']
        self.trade_types = {
            'b-b': 'Taker - Maker',
            'b-s': 'Taker - Taker',
            's-b': 'Maker - Maker',
            's-s': 'Maker - Taker',
        }
        self.tokens = [
            "USDT", "BTC", "ETH", "BUSD", "BNB", "DOGE", "TRX", "USDD", "USDC",
            "RUB", "HT", "EOS", "XRP", "LTC", "GMT", "TON", "XMR", "DAI", 
            "TUSD",
        ]
        self.exchanges = {
            'kucoin': {
                'tokens': {
                    'USDT', 'BTC', 'ETH', 'USDC',
                },
                'pay': {
                    self.payments['sbp'], self.payments['bank'],
                }
            }, 
            'totalcoin': {
                'tokens': {
                    'USDT', 'BTC', 'ETH',
                },
                'pay': {
                    self.payments['tinkoff'], self.payments['sber'],
                    self.payments['sbp'], self.payments['raiffeisen'],
                }
            },
            # 'garantex': {
            #     'tokens': {
            #         'USDT', 'BTC', 'ETH', 'USDC', 'DAI'
            #     },
            #     'pay': {
            #         self.payments['tinkoff'], self.payments['sber'],
            #     }
            # },
            
            'mexc': {
                'tokens': {
                    'USDT', 'BTC', 'ETH', 'USDC',
                },
                'pay': {
                    self.payments['tinkoff'], self.payments['sber'],
                }
            },
            'hodlhodl': {
                'tokens': {
                    'BTC'
                },
                'pay': {
                    self.payments['tinkoff'], self.payments['sber'],
                }
            },
            'bitpapa': {
                'tokens': {
                    'USDT', 'BTC', 'ETH', 'TON', 'XMR',
                },
                'pay': {
                    self.payments['tinkoff'], self.payments['sber'],
                    self.payments['raiffeisen'], self.payments['sbp']
                }
            },
            'gateio': {
                'tokens': {
                    'USDT', 'BTC', 'ETH'
                },
                'pay': {
                    self.payments['raiffeisen'], self.payments['qiwi'],
                }
            },
            # 'beribit': {
            #     'tokens': {
            #         'USDT'
            #     },
            #     'pay': {
            #         self.payments['tinkoff'], self.payments['sber'],
            #     }
            # }, 
            'bybit': {
                'tokens': {
                    'USDT', 'BTC', 'ETH', 'USDC'
                },
                'pay': {
                    self.payments['raiffeisen'], self.payments['tinkoff'],
                    self.payments['sber']
                }
            },
            'huobi': {
                'tokens': {
                    'USDT', 'BTC', 'ETH' #, 'USDD', 'HT', 'TRX', 'EOS', 'XRP', 
                    # 'LTC'
                },
                'pay': {
                    self.payments['raiffeisen'], self.payments['sbp'],
                    self.payments['tinkoff'], self.payments['sber'],
                    # self.payments['russian'],
                    # self.payments['post'], self.payments['post'],
                }
            },
        }


    def exchange_query(self, ex: str, site: str, pay: str, limit: int) -> str:
        sort_direction = "ASC" if site == "BUY" else "DESC"
        query = f"""
            (
                SELECT
                    name, order_q, order_p, price, lim_min, lim_max, fiat,
                    token, buy_sell, exchange, adv_no,  '{pay}' as best_payment,
                    available_rub, available
                FROM public.{AsIs(ex)}
                WHERE token = %s
                AND buy_sell = %s
                AND '{pay}' IN (
                    SELECT value::text FROM jsonb_array_elements_text(payments)
                )
                ORDER BY price {sort_direction}
                LIMIT {limit}
            )
        """
        return query
    

    def create_exchange_query(self, limit) -> tuple:
        union_queries = []
        params = []

        for site in self.buy_sell:
            for token in self.tokens:
                for ex in self.exchanges:
                    payments = self.exchanges[ex]['pay']
                    tokens_ex = self.exchanges[ex]['tokens']

                    if token not in tokens_ex: continue

                    for pay in payments:
                        query = self.exchange_query(ex, site, pay, limit=limit)
                        params.extend([token, site])
                        union_queries.append(query)

        full_query = " UNION ".join(union_queries)
        return full_query, params


    def execute_exchange_query(self, limit) -> tuple:
        query, params = self.create_exchange_query(limit)
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
        return result


    def split_and_sort_ads(self, ads: list) -> tuple:
        buy_ads = {}
        sell_ads = {}

        for ad in ads:
            if ad['buy_sell'] == 'BUY':
                token = ad['token']
                if token not in buy_ads: buy_ads[token] = []
                buy_ads[token].append(ad)

            elif ad['buy_sell'] == 'SELL':
                token = ad['token']
                if token not in sell_ads: sell_ads[token] = []
                sell_ads[token].append(ad)

        for ads in buy_ads.values():
            ads.sort(key=lambda x: x['price'], reverse=False)

        for ads in sell_ads.values():
            ads.sort(key=lambda x: x['price'], reverse=True)

        return buy_ads, sell_ads


    def create_response(self, result: list) -> dict:
        response = [
            {
                "name": row[0],
                "order_q": row[1],
                "order_p": row[2],
                "price": row[3],
                "lim_min": row[4],
                "lim_max": row[5],
                "fiat": row[6],
                "token": row[7],
                "buy_sell": row[8],
                "exchange": row[9],
                "adv_no": row[10],
                "best_payment": row[11],
                "available_rub": row[12],
                "available": row[13],
            }
            for row in result
        ]
        return response


    def get_ads(self, limit=3) -> tuple:
        result = self.execute_exchange_query(limit)
        ads = self.create_response(result)
        buy_dict, sell_dict = self.split_and_sort_ads(ads)
        return buy_dict, sell_dict


class CountActionsInTwo(BaseCount):
    def __init__(self):
        super().__init__()
        self.total_links = {}


    def create_answer(self, trade_type: str, total: int) -> str:
        return f'Count in 2 actions: {trade_type} --> {total}\n'


    def count_spread(self, buy_price: float, sell_price: float) -> float:
        spread = ((sell_price / buy_price) - 1) * 100
        spread = round(spread, 2)
        return spread


    def create_key(self, trade_type: str, token: str) -> str:
        return f'{trade_type}--{token}--{2}'
    

    def count(self, buy_ads: dict,
              sell_ads: dict, trade_type: str) -> str:

        for token in self.tokens:
            key = self.create_key(trade_type, token)
            self.total_links[key] = []
            
            buy_ads_by_token = buy_ads.get(token)
            sell_ads_by_token = sell_ads.get(token)
            if not buy_ads_by_token or not sell_ads_by_token: continue

            for buy_ad in buy_ads_by_token:
                buy_price = buy_ad['price']

                for sell_ad in sell_ads_by_token:
                    sell_price = sell_ad['price']

                    spread = self.count_spread(buy_price, sell_price)

                    if spread < self.min_spread: continue
                    self.total_links[key].append({'spread': spread,
                                                '1': buy_ad,
                                                '2': sell_ad})


    def save(self) -> int:
        BestLinksInTwoActions.objects.all().delete()

        n = 0
        for key, values in self.total_links.items():
            if len(values) == 0: continue
            n += len(values)
            cache.set(key, values, self.time_cash)
        return n
            
            # for ad in values:
            #     buy_ad_data = ad['1']
            #     sell_ad_data = ad['2']
            #     spread = ad['spread']

            #     buy_ad = AdsInTwo.objects.create(**buy_ad_data)
            #     sell_ad = AdsInTwo.objects.create(**sell_ad_data)
            #     spread = BestLinksInTwoActions.objects.create(
            #         buy_ad=buy_ad, sell_ad=sell_ad, spread=spread
            #     )


    def count_in_two_actions(self) -> None:
        buy_dict, sell_dict = self.get_ads(limit=15)

        self.count(buy_dict, buy_dict, self.trade_types['b-b'])
        self.count(buy_dict, sell_dict, self.trade_types['b-s'])
        self.count(sell_dict, buy_dict, self.trade_types['s-b'])
        self.count(sell_dict, sell_dict, self.trade_types['s-s'])
        
        number_of_links = self.save()
        return number_of_links
    

class CountActionsInThree(BaseCount):
    def __init__(self):
        super().__init__()
        self.min_spread = 0.3


    def create_key(self, trade_type: str, token: str) -> str:
        return f'{trade_type}--{token}--{3}'
    

    def get_key(self, fiat: str) -> str:
        match fiat:
            case 'BTC':
                return 'BTCUSDT'
            case 'GMT':
                return 'GMTUSDT'
            case 'XMR':
                return 'XMRUSDT'
            case 'DOGE':
                return 'DOGEUSDT'
            case 'TRX':
                return 'TRXUSDT'
            case 'EOS':
                return 'EOSUSDT'
            case 'XRP':
                return 'XRPUSDT'
            case 'LTC':
                return 'LTCUSDT'
            case 'BUSD':
                return 'BUSDUSDT'
            case 'BNB':
                return 'BNBUSDT'
            case 'ETH':
                return 'ETHUSDT'
            case 'RUB':
                return 'USDTRUB'
            case 'SHIB':
                return 'SHIBUSDT'
            case 'USDC':
                return 'USDCUSDT'
            case 'DAI':
                return 'DAIUSDT'
            case 'TON':
                return 'TON_USDT'
            case 'HT':
                return 'HT_USDT'
            case _:
                return None


    def get_price_by_symbol(self, crypto: dict, target_crypto: str) -> float:
        price = crypto.get(target_crypto, None)
        if price is not None: 
            return float(price)
        return price


    def count_spread(self, buy_price: float, sell_price: float, 
                     spot_price: float, reverse=False) -> float:
        if reverse == False:
            spread = ((sell_price / (buy_price * spot_price)) - 1) * 100
        elif reverse == True:
            spot_price = 1 / spot_price
            spread = ((sell_price / (buy_price * spot_price)) - 1) * 100
        spread = round(spread, 2)
        return spread


    def binance_spot(self) -> dict:
        url = "https://api.binance.com/api/v3/ticker/price"
        response = requests.get(url)
        data = response.json()
        
        spot_prices = {}
        for token_info in data:
            symbol = token_info['symbol']
            price = token_info['price']
            spot_prices[symbol] = price
        return spot_prices
    

    def count(self, buy_ads: list, sell_ads: list, spot) -> dict:
        links = {}
        for token in self.tokens:
            links[token] = []

        for buy_token, buy_ads_bu_token in buy_ads.items():
            for buy_ad in buy_ads_bu_token:
            
                for sell_token, sell_ads_bu_token in sell_ads.items():
                    for sell_ad in sell_ads_bu_token:

                        if buy_token == 'USDT' and sell_token != 'USDT':
                            reverse = False
                            token = sell_token
                        elif buy_token != 'USDT' and sell_token == 'USDT':
                            reverse = True
                            token = buy_token
                        else:
                            continue
                        
                        key = self.get_key(token)
                        spot_price = self.get_price_by_symbol(spot, key)

                        if spot_price == None:  continue

                        spread = self.count_spread(buy_ad['price'], 
                                                    sell_ad['price'], 
                                                    spot_price,
                                                    reverse=reverse)
                        
                        if spread < self.min_spread: continue
                        
                        links[token].append({'spread': spread,
                                            'spot': spot_price,
                                            '1': buy_ad,
                                            '2': sell_ad})
        return links
    

    def save(self, total_links: dict) -> int:
        BestLinksInThreeActions.objects.all().delete()

        n = 0
        for trade_type, ads in total_links.items():
            for token, links in ads.items():
                if len(links) == 0: continue
                n += len(links)
                key = self.create_key(trade_type, token)
                cache.set(key, links, self.time_cash)
        return n 
                # for ad in links:
                #     buy_ad_data = ad['1']
                #     sell_ad_data = ad['2']
                #     spread = ad['spread']
                #     spot = ad['spot']

                #     buy_ad = AdsInThree.objects.create(**buy_ad_data)
                #     sell_ad = AdsInThree.objects.create(**sell_ad_data)
                #     spread = BestLinksInThreeActions.objects.create(
                #         buy_ad=buy_ad, sell_ad=sell_ad, spread=spread, spot=spot
                #     )


    def count_in_three_actions(self) -> None:
        buy_dict, sell_dict = self.get_ads(limit=15)
        spot = self.binance_spot()

        data = {
            self.trade_types['b-b']: self.count(buy_dict, buy_dict, spot),
            self.trade_types['b-s']: self.count(buy_dict, sell_dict, spot),
            self.trade_types['s-b']: self.count(sell_dict, buy_dict, spot),
            self.trade_types['s-s']: self.count(sell_dict, sell_dict, spot)
        }

        number_of_links = self.save(data)
        return number_of_links
        

class BestPrices(BaseCount):
    def create_key_best_prices(self, site: str, token: str) -> str:
        return f'best-prices--{site}--{token}'

        
    def save_in_cash(self, site: str, all_ads: dict) -> None:
        for token, ads in all_ads.items():
            key = self.create_key_best_prices(site, token)
            cache.set(key, ads, self.time_cash)


    def create_links(self) -> None:
        buy_dict, sell_dict = self.get_ads(limit=1)
        self.save_in_cash('BUY', buy_dict)
        self.save_in_cash('SELL', sell_dict)