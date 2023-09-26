import requests

from myproject.celery import app
from base.info import tokens, buy_sell, exchanges, time_cash

from django.db import connection
from django.core.cache import cache
from psycopg2.extensions import AsIs


def create_exchange_dict(result):
    exchange_ads = [
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
            "available": row[12],
        }
        for row in result
    ]
    return exchange_ads


def create_exchange_query(buy_sell, tokens, exchanges):
    union_queries = []
    params = []

    for site in buy_sell:
        for token in tokens:
            for ex in exchanges:
                payments = exchanges[ex]['pay']
                tokens_ex = exchanges[ex]['tokens']
                if token not in tokens_ex:
                    continue

                for pay in payments:
                    query = get_exchange_query(ex, site, pay)
                    params.extend([token, site])
                    union_queries.append(query)

    full_query = " UNION ".join(union_queries)
    return full_query, params


def execute_exchange_query(full_query, params):
    with connection.cursor() as cursor:
        cursor.execute(full_query, params)
        result = cursor.fetchall()
    return result


def split_and_sort_ads(exchange_ads, tokens):
    buy_ads = {token: [] for token in tokens}
    sell_ads = {token: [] for token in tokens}

    for ad in exchange_ads:
        token = ad['token']
        if ad['buy_sell'] == 'BUY':
            buy_ads[token].append(ad)
        elif ad['buy_sell'] == 'SELL':
            sell_ads[token].append(ad)

    for token, token_ads in buy_ads.items():
        token_ads.sort(key=lambda x: x['price'])
        key = f'BUY--{token}'
        cache.set(key, token_ads, time_cash)

    for token, token_ads in sell_ads.items():
        token_ads.sort(key=lambda x: x['price'], reverse=True)
        key = f'SELL--{token}'
        cache.set(key, token_ads, time_cash)

    return buy_ads, sell_ads


def get_exchange_query(ex, site, pay):
    sort_direction = "ASC" if site == "BUY" else "DESC"
    query = f"""
        (
            SELECT
                name, order_q, order_p, price, 
                lim_min, lim_max, fiat, token, 
                buy_sell, exchange, adv_no, 
                '{pay}' as best_payment, available
            FROM public.{AsIs(ex)}
            WHERE price = (
                SELECT {'MIN' if sort_direction == 'ASC' else 'MAX'}(price)
                FROM public.{AsIs(ex)}
                WHERE token = %s
                AND buy_sell = %s
                AND '{pay}' IN (SELECT value::text FROM jsonb_array_elements_text(payments))
            )
            LIMIT 1
        )
    """
    return query


def count_2_actions(first_dict, second_dict, trade_type):

    def count_spread(first_price, second_price):
        spread = ((second_price / first_price) - 1) * 100
        spread = round(spread, 2)
        return spread

    total = 0
    for token in tokens:
        fisrt_ads = first_dict[token]
        second_ads = second_dict[token]

        best_links = []
        for first_ad in fisrt_ads:
            first_price = first_ad['price']

            for second_ad in second_ads:
                second_price = second_ad['price']

                spread = count_spread(first_price, second_price)

                if spread < 0.01:
                    continue
                
                total += 1
                item = {
                    'spread': spread,
                    '1': first_ad,
                    '2': second_ad,
                }
                best_links.append(item)

        if len(best_links) != 0:
            key = f'{trade_type}--{token}--{2}'
            cache.set(key, best_links, time_cash)
    
    answer = f'{trade_type}: {total}\n'
    return answer


def count_3_actions(first_dict, second_dict, spot, trade_type):

    def count_spread(first_price, second_price, spot_price):
        spread = ((second_price / (first_price * spot_price)) - 1) * 100
        spread = round(spread, 2)
        return spread

    def get_key(fiat):
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

    def get_price_by_symbol(crypto_list, target_crypto):
        for crypto_obj in crypto_list:
            if crypto_obj == target_crypto:
                return float(crypto_list[target_crypto])
        return None

    total = 0
    best_links = []
    for first_token, first_ads in first_dict.items():
        for first_ad in first_ads:
            first_price = first_ad['price']
    
        for second_token, second_ads in second_dict.items():
            for second_ad in second_ads:
                second_price = second_ad['price']

                if first_token == 'USDT' and second_token != 'USDT':
                    key = get_key(second_token)
                    spot_price = get_price_by_symbol(spot, key)
                    if spot_price == None: 
                        continue
                    spread = count_spread(first_price, second_price, spot_price)

                    if spread < 0.01:
                        continue

                    total += 1
                    item = {
                        'spread': spread,
                        'spot': spot_price,
                        '1': first_ad,
                        '2': second_ad,
                    }
                    best_links.append(item)

                elif first_token != 'USDT' and second_token == 'USDT':
                    key = get_key(first_token)
                    spot_price = get_price_by_symbol(spot, key)
                    if spot_price == None: 
                        continue
                    spot_price = 1 / spot_price
                    spread = count_spread(first_price, second_price, spot_price)

                    if spread < 0.01:
                        continue

                    total += 1
                    item = {
                        'spread': spread,
                        'spot': spot_price,
                        '1': first_ad,
                        '2': second_ad,
                    }
                    best_links.append(item)

        if len(best_links) != 0:
            key = f'{trade_type}--{first_token}--{3}'
            cache.set(key, best_links, time_cash)

    answer = f'{trade_type}: {total}\n'
    return answer


def binance_spot():
    url = "https://api.binance.com/api/v3/ticker/price"
    response = requests.get(url)
    data = response.json()
    
    spot_prices = {}
    for token_info in data:
        symbol = token_info['symbol']
        price = token_info['price']
        spot_prices[symbol] = price
    return spot_prices


@app.task
def main():

    query, params = create_exchange_query(buy_sell, tokens, exchanges)
    result = execute_exchange_query(query, params)
    exchange_dict = create_exchange_dict(result)
    buy_dict, sell_dict = split_and_sort_ads(exchange_dict, tokens)

    answer = count_2_actions(buy_dict, buy_dict, 'BUY-BUY')
    answer += count_2_actions(buy_dict, sell_dict, 'BUY-SELL')
    answer += count_2_actions(sell_dict, buy_dict, 'SELL-BUY')
    answer += count_2_actions(sell_dict, sell_dict, 'SELL-SELL')

    spot = binance_spot()
    answer += count_3_actions(buy_dict, buy_dict, spot, 'BUY-BUY')
    answer += count_3_actions(buy_dict, sell_dict, spot, 'BUY-SELL')
    answer += count_3_actions(sell_dict, buy_dict, spot, 'SELL-BUY')
    answer += count_3_actions(sell_dict, sell_dict, spot, 'SELL-SELL')
    answer = f'\n{answer}'
    return answer