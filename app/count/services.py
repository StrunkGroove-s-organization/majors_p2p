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
                    'USDT', 'BTC', 'ETH', 'LTC',
                },
                'pay': {
                    self.payments['tinkoff'], self.payments['sber'],
                    self.payments['ymoney'], self.payments['mts'], 
                    self.payments['raiffeisen'],
                }
            },
            'garantex': {
                'tokens': {
                    'USDT', 'BTC', 'ETH', 'USDC', 'DAI'
                },
                'pay': {
                    self.payments['tinkoff'], self.payments['sber'],
                }
            },
            
            # 'exchange_mexc': {
            #     'tokens': {
            #         'USDT', 'BTC', 'ETH', 'USDC',
            #     },
            #     'pay': {
            #         'Tinkoff', 'Sber',
            #     }
            # },
            'hodlhodl': {
                'tokens': {
                    'BTC'
                },
                'pay': {
                    self.payments['tinkoff'], self.payments['sber'],
                }
            },
            # 'exchange_bitpapa': {
            #     'tokens': {
            #         'USDT', 'BTC', 'ETH', 'TON', 'XMR',
            #     },
            #     'pay': {
            #         'Tinkoff',
            #         'Sber',
            #         'ЮMoney',
            #         'MTS-Bank',
            #         'Raiffeisenbank',
            #     }
            # },
            'gateio': {
                'tokens': {
                    'USDT', 'BTC', 'ETH'
                },
                'pay': {
                    self.payments['raiffeisen'], self.payments['qiwi'],
                }
            },
            # 'exchange_beribit': {
            #     'tokens': {
            #         'USDT'
            #     },
            #     'pay': {
            #         'Tinkoff', 'Sber',
            #     }
            # }, 
            'bybit': {
                'tokens': {
                    'USDT', 'BTC', 'ETH', 'USDC'
                },
                'pay': {
                    self.payments['raiffeisen'], self.payments['tinkoff'],
                    self.payments['sber'],
                }
            },
            'huobi': {
                'tokens': {
                    'USDT', 'BTC', 'ETH', 'USDD', 'HT', 'TRX', 'EOS', 'XRP', 
                    'LTC'
                },
                'pay': {
                    self.payments['raiffeisen'], self.payments['post'],
                    self.payments['tinkoff'], self.payments['sber'],
                    self.payments['sbp'], self.payments['russian'],
                    self.payments['post'],
                }
            },
        }


    def create_exchange_query(self) -> tuple:
        union_queries = []
        params = []

        for site in self.buy_sell:
            for token in self.tokens:
                for ex in self.exchanges:
                    payments = self.exchanges[ex]['pay']
                    tokens_ex = self.exchanges[ex]['tokens']

                    if token not in tokens_ex: continue

                    for pay in payments:
                        query = self.exchange_query(ex, site, pay)
                        params.extend([token, site])
                        union_queries.append(query)

        full_query = " UNION ".join(union_queries)
        return full_query, params


    def exchange_query(self, ex: str, site: str, pay: str) -> str:
        sort_direction = "ASC" if site == "BUY" else "DESC"
        query = f"""
            (
                SELECT
                    name, order_q, order_p, price, lim_min, lim_max, fiat,
                    token, buy_sell, exchange, adv_no,  '{pay}' as best_payment,
                    available_rub
                FROM public.{AsIs(ex)}
                WHERE price = (
                    SELECT {'MIN' if sort_direction == 'ASC' else 'MAX'}(price)
                    FROM public.{AsIs(ex)}
                    WHERE token = %s
                    AND buy_sell = %s
                    AND '{pay}' IN (
                        SELECT value::text FROM jsonb_array_elements_text(payments)
                    )
                )
                LIMIT 1
            )
        """
        return query


    def execute_exchange_query(self, query: str, params: list) -> tuple:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
        return result


    def split_and_sort_ads(self, exchange_ads: list) -> tuple:
        buy_ads = {token: [] for token in self.tokens}
        sell_ads = {token: [] for token in self.tokens}

        for ad in exchange_ads:
            token = ad['token']
            if ad['buy_sell'] == 'BUY':
                buy_ads[token].append(ad)
            elif ad['buy_sell'] == 'SELL':
                sell_ads[token].append(ad)

        for token, token_ads in buy_ads.items():
            token_ads.sort(key=lambda x: x['price'], reverse=False)

        for token, token_ads in sell_ads.items():
            token_ads.sort(key=lambda x: x['price'], reverse=True)

        return buy_ads, sell_ads


    def create_answer(self, trade_type: str, total: int) -> str:
        return f'Count in 2 actions: {trade_type} --> {total}\n'


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
            }
            for row in result
        ]
        return response


    def get_ads(self) -> dict:
        query, params = self.create_exchange_query()
        result = self.execute_exchange_query(query, params)

        exchange = self.create_response(result)
        buy_dict, sell_dict = self.split_and_sort_ads(exchange)
        data = {
            'buy': buy_dict,
            'sell': sell_dict,
        } 
        return data


class CountActionsInTwo(BaseCount):
    def count_spread(self, buy_price: float, sell_price: float) -> float:
        spread = ((sell_price / buy_price) - 1) * 100
        spread = round(spread, 2)
        return spread


    def create_key(self, trade_type: str, token: str) -> str:
        return f'{trade_type}--{token}--{2}'
    

    def count(self, total_links: dict, buy_data: dict,
              sell_data: dict, trade_type: str) -> str:

        for token in self.tokens:
            key = self.create_key(trade_type, token)
            total_links[key] = []

            buy_ads = buy_data[token]
            sell_ads = sell_data[token]

            for buy_ad in buy_ads:
                buy_price = buy_ad['price']

                for sell_ad in sell_ads:
                    sell_price = sell_ad['price']

                    spread = self.count_spread(buy_price, sell_price)

                    if spread < self.min_spread: continue
                    total_links[key].append({
                        'spread': spread,
                        '1': buy_ad,
                        '2': sell_ad,
                    })


    def save(self, total_links: dict) -> str:
        BestLinksInTwoActions.objects.all().delete()

        for key, values in total_links.items():
            if len(values) == 0: continue
            cache.set(key, values, self.time_cash)
            
            for ad in values:
                buy_ad_data = ad['1']
                sell_ad_data = ad['2']
                spread = ad['spread']

                buy_ad = AdsInTwo.objects.create(**buy_ad_data)
                sell_ad = AdsInTwo.objects.create(**sell_ad_data)
                spread = BestLinksInTwoActions.objects.create(
                    buy_ad=buy_ad, sell_ad=sell_ad, spread=spread
                )


    def count_in_two_actions(self) -> None:
        dict = self.get_ads()

        total_links = {} 

        self.count(total_links, dict['buy'], dict['buy'], self.trade_types['b-b'])
        self.count(total_links, dict['buy'], dict['sell'], self.trade_types['b-s'])
        self.count(total_links, dict['sell'], dict['buy'], self.trade_types['s-b'])
        self.count(total_links, dict['sell'], dict['sell'], self.trade_types['s-s'])
        
        self.save(total_links)
        return
    

class CountActionsInThree(BaseCount):
    def get_key(self, fiat: str) -> str:
        if fiat == 'BTC':
            return 'BTCUSDT'
        elif fiat == 'GMT':
            return 'GMTUSDT'
        elif fiat == 'XMR':
            return 'XMRUSDT'
        elif fiat == 'DOGE':
            return 'DOGEUSDT'
        elif fiat == 'TRX':
            return 'TRXUSDT'
        elif fiat == 'EOS':
            return 'EOSUSDT'
        elif fiat == 'XRP':
            return 'XRPUSDT'
        elif fiat == 'LTC':
            return 'LTCUSDT'
        elif fiat == 'BUSD':
            return 'BUSDUSDT'
        elif fiat == 'BNB':
            return 'BNBUSDT'
        elif fiat == 'ETH':
            return 'ETHUSDT'
        elif fiat == 'RUB':
            return 'USDTRUB'
        elif fiat == 'SHIB':
            return 'SHIBUSDT'
        elif fiat == 'USDC':  
            return 'USDCUSDT' 
        elif fiat == 'TON':
            return 'TON_USDT'
        elif fiat == 'HT':
            return 'HT_USDT'
        else:
            return fiat


    def get_price_by_symbol(self, crypto: dict, target_crypto: str) -> float:
        for crypto_obj in crypto:
            if crypto_obj == target_crypto:
                return float(crypto[target_crypto])
        return None


    def count_spread(self, buy_price: float, 
                     sell_price: float, spot_price: float) -> float:
        
        spread = ((sell_price / (buy_price * spot_price)) - 1) * 100
        spread = round(spread, 2)
        return spread


    def count(self, buy_ads: dict, sell_ads: dict, spot) -> dict:
        links = {}

        for buy_token, buy_ads_by_token in buy_ads.items():
            sub_links = []

            for buy_ad in buy_ads_by_token:
                buy_price = buy_ad['price']
            
                for sell_token, sell_ads_by_token in sell_ads.items():
                    for sell_ad in sell_ads_by_token:
                        sell_price = sell_ad['price']

                        if buy_token == 'USDT' and sell_token != 'USDT':
                            key = self.get_key(sell_token)
                            spot_price = self.get_price_by_symbol(spot, key)

                            if spot_price == None:  continue

                            spread = self.count_spread(buy_price, sell_price, spot_price)

                            if spread < self.min_spread: continue

                            sub_links.append({
                                'spread': spread,
                                'spot': spot_price,
                                '1': buy_ad,
                                '2': sell_ad,
                            })

                        elif buy_token != 'USDT' and sell_token == 'USDT':
                            key = self.get_key(buy_token)
                            spot_price = self.get_price_by_symbol(spot, key)

                            if spot_price == None:  continue

                            spot_price = 1 / spot_price
                            spread = self.count_spread(buy_price, sell_price, spot_price)

                            if spread < self.min_spread: continue

                            sub_links.append({
                                'spread': spread,
                                'spot': spot_price,
                                '1': buy_ad,
                                '2': sell_ad,
                            })
            links[buy_token] = sub_links
        return links


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


    def create_key(self, trade_type: str, token: str) -> str:
        return f'{trade_type}--{token}--{3}'
    

    def save(self, total_links: dict) -> str:
        BestLinksInThreeActions.objects.all().delete()

        for trade_type, ads in total_links.items():
            for token, links in ads.items():
                if len(links) == 0: continue
                key = self.create_key(trade_type, token)
                cache.set(key, links, self.time_cash)

                for ad in links:
                    buy_ad_data = ad['1']
                    sell_ad_data = ad['2']
                    spread = ad['spread']
                    spot = ad['spot']

                    buy_ad = AdsInThree.objects.create(**buy_ad_data)
                    sell_ad = AdsInThree.objects.create(**sell_ad_data)
                    spread = BestLinksInThreeActions.objects.create(
                        buy_ad=buy_ad, sell_ad=sell_ad, spread=spread, spot=spot
                    )


    def count_in_three_actions(self) -> None:
        dict = self.get_ads()
        spot = self.binance_spot()

        data = {
            self.trade_types['b-b']: self.count(dict['buy'], dict['buy'], spot),
            self.trade_types['b-s']: self.count(dict['buy'], dict['sell'], spot),
            self.trade_types['s-b']: self.count(dict['sell'], dict['buy'], spot),
            self.trade_types['s-s']: self.count(dict['sell'], dict['sell'], spot)
        }

        self.save(data)
        return
        

        
