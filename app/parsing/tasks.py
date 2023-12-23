from main.celery import app
from .models import (
    TotalCoinModel, KucoinModel, GarantexModel, GateioModel, HodlHodlModel,
    HuobiModel, BybitModel, BitpapaModel, BeribitModel, MexcModel
)
from .services import (
    TotalcoinParsing, KucoinParsing, GarantexParsing, GateioParsing, 
    HodlHodlParsing, HuobiParsing, BybitParsing, BitpapaParsing, BeribitParsing,
    MexcParsing
)

@app.task
def totalcoin():
    dict = {
        'url': 'https://totalcoin.io/ru/offers/ajax-offers-list?type={site}&currency=rub&crypto={currency}&pm=&pro=0',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        },
        'path': ['data'],
        'class_db': TotalCoinModel,
        'currencies': ['BTC', 'USDT', 'ETH'],
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
        'class_db': KucoinModel,
        'currencies':  ['USDT', 'BTC', 'ETH', 'USDC'],
        'trade_types': ['SELL', 'BUY'],
        'pay_types': ['BANK_TRANSFER', 'SBP', 'BANK'],
        'exchange': 'Kucoin',
        'timeout': 0.5,
    }

    kucoin = KucoinParsing(dict)
    return kucoin.main()


@app.task
def garantex():
    dict = {
        'url': 'https://garantex.org/trading/btcrub',
        'class_db': GarantexModel,
        'currencies':  {'USDC': 'usdcrub', 'BTC': 'btcrub', 'ETH': 'ethrub',
                        'USDT': 'usdtrub', 'DAI': 'dairub'},
        'trade_types': ['bid', 'ask'],
        'exchange': 'Garantex',
    }

    garantex = GarantexParsing(dict)
    return garantex.main()


@app.task
def gateio():
    dict = {
        'url': 'https://www.gate.io/json_svr/query_push/?u=21&c=388882',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Cookie': 'cf_clearance=WVgJZwsvRLJtvCSBMPzARZC8.lLilHcbjP1iMW8JNpY-1701898388-0-1-47b97e73.bf996eac.10b82193-160.0.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://www.gate.io/ru/c2c/market',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.gate.io',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Te': 'trailers',
            'Connection': 'close'
        },
        'path': ['push_order'],
        'class_db': GateioModel,
        'currencies':  ['USDT_RUB', 'BTC_RUB', 'ETH_RUB'],
        # SBP, BANK transfer
        'pay_types': ['qiwi', 'raiffe'],
        'exchange': 'Gateio',
        'timeout': 0.5,
    }

    gateio = GateioParsing(dict)
    return gateio.main()


@app.task
def hodlhodl():
    dict = {
        'url': 'https://hodlhodl.com/api/frontend/offers?filters%5Bpayment_method_name%5D={pay_type}&filters%5Bcurrency_code%5D=RUB&pagination%5Boffset%5D=0&filters%5Bside%5D={site}&facets%5Bshow_empty_rest%5D=true&facets%5Bonly%5D=false&pagination%5Blimit%5D=50',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        },
        'path': ['offers'],
        'class_db': HodlHodlModel,
        'trade_types': ['SELL', 'BUY'], 
        'pay_types': ['Tinkoff', 'Sberbank'],
        'exchange': 'Hodl Hodl',
        'timeout': 0.5,
    }

    hodlhodl = HodlHodlParsing(dict)
    return hodlhodl.main()


@app.task
def huobi():
    dict = {
        'url': 'https://www.huobi.com/-/x/otc/v1/data/trade-market?coinId={currency}&currency=11&tradeType={site}&currPage=1&payMethod={pay_type}&acceptOrder=0&country=&blockType=general&online=1&range=0&amount=&onlyTradable=false&isFollowed=false',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        },
        'path': ['data'],
        'class_db': HuobiModel,
        # 1 - BTC, 2 - USDT, 3 - ETH, 4 - HT, 5 - EOS, 7 - XRP, 8 - LTC
        # 22 - TRX, 62 - USDD
        'currencies':  [1, 2, 3],
        'trade_types': ['SELL', 'BUY'],
        # 9 - QIWI, 19 - Юmoney, 28 - Tinkoff, 29 - Sber, 36 - Raiff, 69 - SBP
        # 356 - MTS, 357 - Post bank
        'pay_types': [28, 29, 36, 69],
        'exchange': 'Houbi',
        'timeout': 0.01,
    }

    huobi = HuobiParsing(dict)
    return huobi.main()


@app.task
def bybit():
    dict = {
        'url': 'https://api2.bybit.com/fiat/otc/item/online',
        'headers': {
            'Host': 'api2.bybit.com',
            'Cookie': 'Cookie: _abck=995368C4453BEA56F04C2A541133E07C~-1~YAAQ+9MXAjbeREmKAQAAJXGVTArxv1MTqfroLeVK+qCPhtQm5KajmbLEw9KnuLIjFGIq+vOOQwEQJGfqDOOLD6vyguswV7CkQIZYIPt5HKifoSzGRRjed2Jgwb4u2LIccuH1blJtpy/r0TWO5o89bdH+eT37osvJqzfzh8xiwaFHFBTx0Jwtc0VoZptCPjZj+P74ZxowZUGMhE1PDLevEj9mqtVzzBgn+JPwjEChzOePrBPD+6hjrtuHfYdUsstwlP6631WIlwxvfh5GoP8SQSAj8x3jHurNTQElyu0Z/FQdjOOekOFHDGNCT6rbH2GqLADNoVKM26LNt2AT92Kd7IfPnoTPIoLRwI8A2SJa5RSRKnAhRWQ/IVLwARdXjRmdvmAnvNvp+2yoj+gNgXxjpRqxkxhmGNps~-1~-1~-1; deviceId=fdc27152-4751-93d6-43d4-647dc7ca0690; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%220%22%2C%22first_id%22%3A%2218976c94a2340-0388ac7e2389ba4-47380724-2073600-18976c94a2427d%22%2C%22props%22%3A%7B%22_a_u_v%22%3A%220.0.5%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTg5NzZjOTRhMjM0MC0wMzg4YWM3ZTIzODliYTQtNDczODA3MjQtMjA3MzYwMC0xODk3NmM5NGEyNDI3ZCIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjAifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%220%22%7D%2C%22%24device_id%22%3A%2218976c94a2340-0388ac7e2389ba4-47380724-2073600-18976c94a2427d%22%7D; _by_l_g_d=6f946d57-3cde-2072-7de2-4b43630870b7; _gcl_au=1.1.433292213.1689915065; _ga_SPS4ND2MGC=GS1.1.1693501975.9.1.1693502158.0.0.0; _ga=GA1.1.1271123862.1689915065; _fbp=fb.1.1689915066729.1720802841; BYBIT_REG_REF_prod={"lang":"en-US","g":"6f946d57-3cde-2072-7de2-4b43630870b7","referrer":"www.bybit.com/","source":"bybit.com","medium":"other","url":"https://www.bybit.com/nl-NL/"}; b_t_c_k=; ak_bmsc=E30EFA0F36AAFC7ABD4F84B6E6580BA8~000000000000000000000000000000~YAAQ+9MXAtHlREmKAQAAxlWWTBShhU0YcFrZGi3Xe9VQWJqPuPYRHWb5BytbOS9UQAEuB4LmLoV39sp2wYIf1MeHuFVUJZGop6rAcidhesW6s+C7wPc0g1kRycObBKhR3iwnjmN2tqe5TLESqCzU2c23fbWAXVPEuUp8P0slAP2lWkBPF3HZYGXqY2XgN3SEzwGuBvX8h8BTQCH/XXiWMW+bSf+gv1zyM7epA8KgZfJdzWTZW6Y0WCVJ6DTTG6aOalUOdZ06Yc4fTg3sNaiNkwFxJ7wAeTxJmHwQ6WDy3o/cdWCxjUjTOB/0wXWKnnnxK3PcFUIxAnj2KfHfE2TlIoJPqvl6KSF7klDWhbcZC7oZ46/x4jP5JW47TL/aIHua31KHA9+mUGJwfPJEfaijHCk2IC4xqAJ4CUnzm6wcg/sD9cx68mRTI4W+iBmivGwb+BCG/pK1rrJspUDr5mDhHia7fwi0JqvFLnWqsuTrBjZNWo9tJhfn5R55QBwOLDY9t/uS+BiPfLuRDYUG6cTOzb5c3YafFc9uxxk83G4=; bm_sz=1EDB73D5AA79E38CA39CECF910D4E4AC~YAAQ+9MXAivbREmKAQAAozCVTBSqptsOZHwnxyrjuUHi0q5zW/r5sDtStsch/8ODqVFxeAF4EbLen2YqE7ssJ9Aucrwh6A7Bb1rljMCwYyoWdgHGLP/bvuCVT3x+r4L3J3DC2AVFTamixUfynPXZVMJF9yOS/9MGtaDceXCrZpZjJGqX8dbIp/OCjjdkttLFRaOPkVMGWTwB/PlMbKq5IK1qz8tZzkKXrwm2aEkq5MabrDo1WXiE0F5qy6cYxfGbuiOe5pOEg0lbzsQ9HXtZngjdGiGujM/KsrIk4VHuJykrZA==~3618357~4599874; bm_mi=B20147F89871BDFEF11B4014DA3692BA~YAAQ+9MXAsHlREmKAQAAz1GWTBSbhjwU6op4jJJW7BPYayzd6oB6/TroqZlJaTSKo5l2YZWFtyEo/ApOzMf+8dP6ID2FTgO5YaRGNHuIN55kF5TWxWIECP+5qVLQgH8lVCPrMi7xm/bkYj3WNvuB8Ac1PIp0udKg3r1PVrJ6DN4ZNMEcZUORNSi05AUwNRrLzOBS7kyp3maDwloXttY767jrLEAAGYhom0Hahqn/8b5UzpPuPDbPpE7euIm2hkN98T8O6lSPb/e4618gslKmvMfEb/tlAbT8umYoxPOz2ycMhretpgI150ZIC9VHk+2v9SD7MLiTys5ux+s=~1; bm_sv=0FE96CBA46CBCEA7D16CB4541D9A46F9~YAAQfP1zPlALF0uKAQAA/9CXTBQ4e1FoL4AIG7qAMrUEUlLvlS5l0DDVwIAnLR166tSS1TnIIFfyPCnHIld29nDeSQcBFC2MDQOQhfM79eznBM7nwkk0Mpo5nuvebPjRNi59Rd+AIQKF8t8kEA2hpvmMINw0imeL60yWZ8x25HwCoJWI27s+P9OcZcPITrrUNvvP/6tAERtw8OxOaYlAZiQq4ymvFXvP+dvde9LpoWWEPSIPK9AoxLTQbZPgCoqg~1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0',
            'Accept': 'application/json',
            'Referer': 'https://www.bybit.com/',
            'Guid': '6f946d57-3cde-2072-7de2-4b43630870b7',
            'Content-Type': 'application/json;charset=UTF-8',
        },
        'path': ['result', 'items'],
        'class_db': BybitModel,
        'currencies': ['USDT', 'BTC', 'ETH', 'USDC'],
        'trade_types': ['1', '0'],
        # 64 - Raiff, 533 - Russian Standart, 574 - ЮMoney, 581 - Tinkoff
        # 582 - Sber
        'pay_types': [["64"], ["581"], ["582"]],
        'exchange': 'Bybit',
        'timeout': 0.01,
    }

    bybit = BybitParsing(dict)
    return bybit.main()


@app.task
def bitpapa():
    dict = {
        'url': 'https://bitpapa.com/api/v1/partners/ads/search?sort={sort}&crypto_currency_code={currency}&currency_code=RUB&limit=100&page=1&type={site}',
        'path': ['ads'],
        'class_db': BitpapaModel,
        'currencies':  ['BTC', 'ETH', 'USDT', 'XMR', 'TON'],
        'trade_types': ['SELL', 'BUY'],
        'exchange': 'Bitpapa',
        'timeout': 0.5,
    }

    bitpapa = BitpapaParsing(dict)
    return bitpapa.main()


@app.task
def bitpapa():
    dict = {
        'url': 'https://bitpapa.com/api/v1/partners/ads/search?sort={sort}&crypto_currency_code={currency}&currency_code=RUB&limit=100&page=1&type={site}',
        'path': ['ads'],
        'class_db': BitpapaModel,
        'currencies':  ['BTC', 'ETH', 'USDT', 'XMR', 'TON'],
        'trade_types': ['SELL', 'BUY'],
        'exchange': 'Bitpapa',
        'timeout': 0.5,
    }

    bitpapa = BitpapaParsing(dict)
    return bitpapa.main()


@app.task
def beribit():
    dict = {
        'url': 'wss://beribit.com/ws/depth/usdtrub',
        'headers': {
            'Content-Type': 'application/json;charset=utf-8',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        },
        'max_ads': 2,
        'path': ['Depth'],
        'class_db': BeribitModel,
        'trade_types': ['Asks', 'Bids'],
        'exchange': 'Beribit',
        'timeout': 0.5,
    }

    beribit = BeribitParsing(dict)
    return beribit.main()


@app.task
def mexc():
    dict = {
        'url': 'https://p2p.mexc.com/api/market?allowTrade=false&amount=&blockTrade=false&coinId={currency}&countryCode=&currency=RUB&follow=false&haveTrade=false&page=1&payMethod={pay_type}&tradeType={site}',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://otc.mexc.com/',
            'Language': 'en-US',
            'Version': '3.3.7',
            'Origin': 'https://otc.mexc.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Te': 'trailers',
        },
        'path': ['data'],
        'currencies':  [
            '34309140878b4ae99f195ac091d49bab', # USDC
            'febc9973be4d4d53bb374476239eb219', # BTC
            '128f589271cb4951b03e71e6323eb7be', # USDT
            '93c38b0169214f8689763ce9a63a73ff', # ETH
            ],
        'class_db': MexcModel,
        'trade_types': ['SELL', 'BUY'],
        'pay_types': ['12', '13'], # 12 - Sber, 13 - Tinkoff
        'exchange': 'Mexc',
        'timeout': 0.5,
    }

    mexc = MexcParsing(dict)
    return mexc.main()