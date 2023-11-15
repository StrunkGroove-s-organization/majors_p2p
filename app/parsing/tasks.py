from main.celery import app
from .models import TotalCoin, Kucoin
from .services import TotalcoinParsing, KucoinParsing


@app.task
def totalcoin():
    dict = {
        'url': 'https://totalcoin.io/ru/offers/ajax-offers-list?type={site}&currency=rub&crypto={currency}&pm=&pro=0',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        },
        'path': ['data'],
        'class_db': TotalCoin,
        'currencies': ['BTC', 'USDT', 'ETH', 'LTC'],
        'trade_types': ["buy", "sell"],
        'timeout': 0.5,
    }

    totalcoin = TotalcoinParsing(dict)
    return totalcoin.main()


@app.task
def kucoin():
    dict = {
        'url': 'https://www.kucoin.com/_api/otc/ad/list?currency={currency}&side={site}&payTypeCodes={pay_type}&legal=RUB&page=1&pageSize=10&status=PUTUP&lang=nl_NL',
        'headers': {
            'Host': 'www.kucoin.com',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://www.kucoin.com/nl/otc/buy/BTC-RUB',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Te': 'trailers'
        },
        'path': ['items'],
        'class_db': Kucoin,
        'currencies':  ['USDT', 'BTC', 'ETH', 'USDC'],
        'trade_types': ['SELL', 'BUY'],
        'pay_types': ['BANK_TRANSFER', 'SBP'],
        'exchange': 'Kucoin',
        'timeout': 0.5,
    }

    kucoin = KucoinParsing(dict)
    return kucoin.main()