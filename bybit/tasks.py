import time
import requests

from myproject.celery import app
from base.views import update_payment_methods
from .models import ExchangeBybit

exchange = 'Bybit'
url = 'https://api2.bybit.com/fiat/otc/item/online'
headers = {
    'Host': 'api2.bybit.com',
    'Cookie': 'Cookie: _abck=995368C4453BEA56F04C2A541133E07C~-1~YAAQ+9MXAjbeREmKAQAAJXGVTArxv1MTqfroLeVK+qCPhtQm5KajmbLEw9KnuLIjFGIq+vOOQwEQJGfqDOOLD6vyguswV7CkQIZYIPt5HKifoSzGRRjed2Jgwb4u2LIccuH1blJtpy/r0TWO5o89bdH+eT37osvJqzfzh8xiwaFHFBTx0Jwtc0VoZptCPjZj+P74ZxowZUGMhE1PDLevEj9mqtVzzBgn+JPwjEChzOePrBPD+6hjrtuHfYdUsstwlP6631WIlwxvfh5GoP8SQSAj8x3jHurNTQElyu0Z/FQdjOOekOFHDGNCT6rbH2GqLADNoVKM26LNt2AT92Kd7IfPnoTPIoLRwI8A2SJa5RSRKnAhRWQ/IVLwARdXjRmdvmAnvNvp+2yoj+gNgXxjpRqxkxhmGNps~-1~-1~-1; deviceId=fdc27152-4751-93d6-43d4-647dc7ca0690; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%220%22%2C%22first_id%22%3A%2218976c94a2340-0388ac7e2389ba4-47380724-2073600-18976c94a2427d%22%2C%22props%22%3A%7B%22_a_u_v%22%3A%220.0.5%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTg5NzZjOTRhMjM0MC0wMzg4YWM3ZTIzODliYTQtNDczODA3MjQtMjA3MzYwMC0xODk3NmM5NGEyNDI3ZCIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjAifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%220%22%7D%2C%22%24device_id%22%3A%2218976c94a2340-0388ac7e2389ba4-47380724-2073600-18976c94a2427d%22%7D; _by_l_g_d=6f946d57-3cde-2072-7de2-4b43630870b7; _gcl_au=1.1.433292213.1689915065; _ga_SPS4ND2MGC=GS1.1.1693501975.9.1.1693502158.0.0.0; _ga=GA1.1.1271123862.1689915065; _fbp=fb.1.1689915066729.1720802841; BYBIT_REG_REF_prod={"lang":"en-US","g":"6f946d57-3cde-2072-7de2-4b43630870b7","referrer":"www.bybit.com/","source":"bybit.com","medium":"other","url":"https://www.bybit.com/nl-NL/"}; b_t_c_k=; ak_bmsc=E30EFA0F36AAFC7ABD4F84B6E6580BA8~000000000000000000000000000000~YAAQ+9MXAtHlREmKAQAAxlWWTBShhU0YcFrZGi3Xe9VQWJqPuPYRHWb5BytbOS9UQAEuB4LmLoV39sp2wYIf1MeHuFVUJZGop6rAcidhesW6s+C7wPc0g1kRycObBKhR3iwnjmN2tqe5TLESqCzU2c23fbWAXVPEuUp8P0slAP2lWkBPF3HZYGXqY2XgN3SEzwGuBvX8h8BTQCH/XXiWMW+bSf+gv1zyM7epA8KgZfJdzWTZW6Y0WCVJ6DTTG6aOalUOdZ06Yc4fTg3sNaiNkwFxJ7wAeTxJmHwQ6WDy3o/cdWCxjUjTOB/0wXWKnnnxK3PcFUIxAnj2KfHfE2TlIoJPqvl6KSF7klDWhbcZC7oZ46/x4jP5JW47TL/aIHua31KHA9+mUGJwfPJEfaijHCk2IC4xqAJ4CUnzm6wcg/sD9cx68mRTI4W+iBmivGwb+BCG/pK1rrJspUDr5mDhHia7fwi0JqvFLnWqsuTrBjZNWo9tJhfn5R55QBwOLDY9t/uS+BiPfLuRDYUG6cTOzb5c3YafFc9uxxk83G4=; bm_sz=1EDB73D5AA79E38CA39CECF910D4E4AC~YAAQ+9MXAivbREmKAQAAozCVTBSqptsOZHwnxyrjuUHi0q5zW/r5sDtStsch/8ODqVFxeAF4EbLen2YqE7ssJ9Aucrwh6A7Bb1rljMCwYyoWdgHGLP/bvuCVT3x+r4L3J3DC2AVFTamixUfynPXZVMJF9yOS/9MGtaDceXCrZpZjJGqX8dbIp/OCjjdkttLFRaOPkVMGWTwB/PlMbKq5IK1qz8tZzkKXrwm2aEkq5MabrDo1WXiE0F5qy6cYxfGbuiOe5pOEg0lbzsQ9HXtZngjdGiGujM/KsrIk4VHuJykrZA==~3618357~4599874; bm_mi=B20147F89871BDFEF11B4014DA3692BA~YAAQ+9MXAsHlREmKAQAAz1GWTBSbhjwU6op4jJJW7BPYayzd6oB6/TroqZlJaTSKo5l2YZWFtyEo/ApOzMf+8dP6ID2FTgO5YaRGNHuIN55kF5TWxWIECP+5qVLQgH8lVCPrMi7xm/bkYj3WNvuB8Ac1PIp0udKg3r1PVrJ6DN4ZNMEcZUORNSi05AUwNRrLzOBS7kyp3maDwloXttY767jrLEAAGYhom0Hahqn/8b5UzpPuPDbPpE7euIm2hkN98T8O6lSPb/e4618gslKmvMfEb/tlAbT8umYoxPOz2ycMhretpgI150ZIC9VHk+2v9SD7MLiTys5ux+s=~1; bm_sv=0FE96CBA46CBCEA7D16CB4541D9A46F9~YAAQfP1zPlALF0uKAQAA/9CXTBQ4e1FoL4AIG7qAMrUEUlLvlS5l0DDVwIAnLR166tSS1TnIIFfyPCnHIld29nDeSQcBFC2MDQOQhfM79eznBM7nwkk0Mpo5nuvebPjRNi59Rd+AIQKF8t8kEA2hpvmMINw0imeL60yWZ8x25HwCoJWI27s+P9OcZcPITrrUNvvP/6tAERtw8OxOaYlAZiQq4ymvFXvP+dvde9LpoWWEPSIPK9AoxLTQbZPgCoqg~1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0',
    'Accept': 'application/json',
    'Referer': 'https://www.bybit.com/',
    'Guid': '6f946d57-3cde-2072-7de2-4b43630870b7',
    'Content-Type': 'application/json;charset=UTF-8',
}

@app.task
def main(currencies, buy_sell, pay_types, timeout):

    def fetches(all_ads, currencies, buy_sell, pay_types, timeout):

        def fetch(currency, site, pay_type):
            data = {
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

            response = requests.post(url=url, json=data, headers=headers)
            status_code = response.status_code

            if status_code == 200:
                data = response.json()
                return data
            else:
                return False

        def pars(all_ads, data):

            ads = data['result']['items']

            for ad in ads:
                name = ad['nickName']
                payments = update_payment_methods(ad['payments'])
                price = float(ad['price'])
                buy_sell = 'SELL' if ad['side'] == 0 else 'BUY'
                token = ad['symbolInfo']['tokenId'].upper()

                if not name or not payments or not price or not token:
                    continue

                existing_object = next((ad for ad in all_ads 
                    if ad.name == name and 
                    ad.price == price and 
                    ad.buy_sell == buy_sell and 
                    ad.token == token
                ), None)

                if existing_object is None:
                    record = ExchangeBybit()
                    available = float(ad['lastQuantity'])

                    record.name = name
                    record.order_q = float(ad['recentOrderNum'])
                    record.order_p = float(ad['recentExecuteRate'])
                    record.payments = payments
                    record.buy_sell = buy_sell
                    record.price = price
                    record.lim_min = float(ad['minAmount'])
                    record.lim_max = float(ad['maxAmount'])
                    record.token = token
                    record.fiat = ad['symbolInfo']['currencyId'].upper()
                    record.available = round(available, 4)
                    record.available_rub = available * price
                    record.adv_no = ad['userId']
                    record.exchange = exchange

                    all_ads.append(record)
                else:
                    existing_object.payments = list(set(existing_object.payments).union(payments))

        for currency in currencies:
            for site in buy_sell:
                for pay_type in pay_types:
                    time.sleep(timeout)
                    
                    data = fetch(currency, site, pay_type)
                    if data:
                        pars(all_ads, data)

    all_ads = []
    fetches(all_ads, currencies, buy_sell, pay_types, timeout)

    for index, record in enumerate(all_ads, start=1):
        record.id = index

    def save_db(ads, classDB):
        column_update = [
            'name',
            'order_q',
            'order_p',
            'price',
            'lim_min',
            'lim_max',
            'fiat',
            'token',
            'buy_sell',
            'adv_no',
            'exchange',
            'available',
            'payments',
        ]

        num_ads_to_update = len(ads)
        num_existing_ads = classDB.objects.count()
        classDB.objects.bulk_update(ads, column_update)

        if num_ads_to_update < num_existing_ads:
            classDB.objects.filter(id__gt=num_ads_to_update).delete()
        elif num_ads_to_update == num_existing_ads:
            pass
        else:
            another_ads = ads[num_existing_ads:]
            classDB.objects.bulk_create(another_ads)

    save_db(all_ads, ExchangeBybit)
    return len(all_ads)