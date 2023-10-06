buy_sell = ['BUY', 'SELL']
tokens = [
    "USDT",
    "BTC",
    "ETH",
    "BUSD",
    "BNB",
    "DOGE",
    "TRX",
    "USDD",
    "USDC",
    "RUB",
    "HT",
    "EOS",
    "XRP",
    "LTC",
    "GMT",
    "TON",
    "XMR",
    "DAI",
    "TUSD",
]
exchanges = {
    'exchange_kucoin': {
        'tokens': {
            'USDT', 'BTC', 'ETH', 'USDC',
        },
        'pay': {
            'SBP', 'Bank Transfer',
        }
    }, 
    'exchange_mexc': {
        'tokens': {
            'USDT', 'BTC', 'ETH', 'USDC',
        },
        'pay': {
            'Tinkoff', 'Sber',
        }
    },
    'exchange_hodlhodl': {
        'tokens': {
            'BTC'
        },
        'pay': {
            'Tinkoff', 'Sber',
        }
    },
    'exchange_bitpapa': {
        'tokens': {
            'USDT', 'BTC', 'ETH', 'TON', 'XMR',
        },
        'pay': {
            'Tinkoff',
            'Sber',
            'ЮMoney',
            'MTS-Bank',
            'Raiffeisenbank',
        }
    },
    'exchange_gateio': {
        'tokens': {
            'USDT', 'BTC', 'ETH'
        },
        'pay': {
            'Raiffeisenbank', 'QIWI',
        }
    },
    'exchange_totalcoin': {
        'tokens': {
            'USDT', 'BTC', 'ETH', 'LTC',
        },
        'pay': {
            'Tinkoff',
            'Sber',
            'ЮMoney',
            'MTS-Bank',
            'Raiffeisenbank',
        }
    },
    'exchange_beribit': {
        'tokens': {
            'USDT'
        },
        'pay': {
            'Tinkoff', 'Sber',
        }
    }, 
    'exchange_garantex': {
        'tokens': {
            'USDT', 'BTC', 'ETH', 'USDC', 'DAI'
        },
        'pay': {
            'Tinkoff', 'Sber',
        }
    },
    'exchange_bybit': {
        'tokens': {
            'USDT', 'BTC', 'ETH', 'USDC'
        },
        'pay': {
            'Raiffeisenbank',
            'Russia-Standart-Bank',
            'ЮMoney',
            'Tinkoff',
            'Sber',
        }
    },
    'exchange_huobi': {
        'tokens': {
            'USDT', 'BTC', 'ETH', 'USDD', 'HT', 'TRX', 'EOS', 'XRP', 'LTC'
        },
        'pay': {
            'Tinkoff',
            'Sber',
            'ЮMoney',
            'MTS-Bank',
            'Raiffeisenbank',
            'Post-Bank',
            'SBP',
        }
    },
}
time_cash = 50