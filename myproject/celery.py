import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {

    'count-links-task': {
        'task': 'count_links.tasks.main',
        'schedule': 20,
    },

    'kucoin-task': {
        'task': 'kucoin.tasks.main',
        'schedule': 30,
        'kwargs': {
            'currencies': ['USDT', 'BTC', 'ETH', 'USDC'],
            'buy_sell': ['SELL', 'BUY'],
            'pay_types': ['BANK_TRANSFER', 'SBP'], # 12 - Sber, 13 - Tinkoff
            'timeout': 0.5,
        }
    },

    # 'mexc-task': {
    #     'task': 'mexc.tasks.main',
    #     'schedule': 30,
    #     'kwargs': {
    #         'currencies': ['USDT', 'BTC', 'ETH', 'USDC'],
    #         'buy_sell': ['SELL', 'BUY'],
    #         'pay_types': ['12', '13'], # 12 - Sber, 13 - Tinkoff
    #         'timeout': 0.5,
    #     }
    # }, 

    'hodlhodl-task': {
        'task': 'hodlhodl.tasks.main',
        'schedule': 30,
        'kwargs': {
            'buy_sell': ['SELL', 'BUY'], 
            'pay_types': ['Tinkoff', 'Sberbank'],
            'timeout': 0.5,
        }
    },

    'bitpapa-task': {
        'task': 'bitpapa.tasks.main',
        'schedule': 30,
        'kwargs': {
            'currencies': ['BTC', 'ETH', 'USDT', 'XMR', 'TON'],
            'buy_sell': ['SELL', 'BUY'], 
            'timeout': 0.5,
        }
    },

    'gateio-task': {
        'task': 'gateio.tasks.main',
        'schedule': 30,
        'kwargs': {
            'currencies': ['USDT_RUB', 'BTC_RUB', 'ETH_RUB'],
            'pay_types': ['qiwi', 'raiffe'],
            'timeout': 0.5,
        }
    },

    'totalcoin-task': {
        'task': 'totalcoin.tasks.main',
        'schedule': 30,
        'kwargs': {
            'currencies': ['BTC', 'USDT', 'ETH', 'LTC'],
            'buy_sell': ["buy", "sell"], 
            'timeout': 0.5,
        }
    },

    'beribit-task': {
        'task': 'beribit.tasks.main',
        'schedule': 30,
    },

    'garantex-task': {
        'task': 'garantex.tasks.main',
        'schedule': 30,
    },

    'huobi-task': {
        'task': 'huobi.tasks.main',
        'schedule': 60,
        'kwargs': {
            # 1 - BTC
            # 2 - USDT
            # 3 - ETH
            # 4 - HT
            # 5 - EOS
            # 7 - XRP
            # 8 - LTC
            # 22 - TRX
            # 62 - USDD
            'currencies': [1, 2, 3, 4, 5, 7, 8, 22, 62],
            'buy_sell': ['SELL', 'BUY'],
            # 9 - QIWI
            # 19 - Юmoney
            # 28 - Tinkoff
            # 29 - Sber
            # 36 - Raiff
            # 69 - SBP
            # 356 - MTS
            # 357 - Post bank
            'pay_types': [9, 19, 28, 29, 36, 69, 356, 357],
            'timeout': 0.01,
        }
    },

    'bybit-task': {
        'task': 'bybit.tasks.main',
        'schedule': 60,
        'kwargs': {
            'currencies': ['USDT', 'BTC', 'ETH', 'USDC'], 
            'buy_sell': ["1", "0"], 
            # 64 - Raiff
            # 533 - Russian Standart
            # 574 - ЮMoney
            # 581 - Tinkoff
            # 582 - Sber
            'pay_types': [["64"], ["533"], ["574"], ["581"], ["582"]],
            'timeout': 0.5,
        }
    },















    ### FIXME ###
    # 'bitget-task': {
    #     'task': 'bitget.tasks.main',
    #     'schedule': crontab(),
    #     'kwargs': {
    #         'currencies': ['BTC'], # , 'USDT', 'ETH', 'USDC', 'DAI'
    #         'buy_sell': [1, 0],
    #         'pay_types': ["1", "96", "97", "241", "258", "287", "304"], # 1 - Bank Transfer, 96 - Raiff, 97 - QIWI, 241 - Alfa, 258 - SBP, 287 - MTS, 304 - ЮMoney
    #         'timeout': 0.5,
    #     }
    # },

    # 'binance-task': {
    #     'task': 'binance.tasks.main',
    #     'schedule': crontab(),
    #     'kwargs': {
    #         'currencies': ['USDT', 'BTC', 'ETH', 'USDC', 'DAI', 'TUSD'],
    #         'buy_sell': ['SELL', 'BUY'],
    #         'pay_types': ['QiWi', 'Yandex.Money'],
    #         'timeout': 0.5,
    #     }
    # },

    # 'okx-task': {
    #     'task': 'okx.tasks.main',
    #     'schedule': crontab(),
    #     'kwargs': {
    #         'currencies': ['USDT', 'BTC', 'ETH', 'USDC', 'DAI', 'TUSD'],
    #         'buy_sell': ['SELL', 'BUY'],
    #         'pay_types': ['QiWi', 'Yandex.Money'],
    #         'timeout': 0.5,
    #     }
    # },
}

