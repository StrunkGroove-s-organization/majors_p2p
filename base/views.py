from django.shortcuts import render

def update_payment_methods(payment_methods):
    updated_methods = []
    for method in payment_methods:
        if method in [
                'B8',
                '97',
                '186',
                '64',
                'Raiffeisen Bank',
                'Райффайзенбанк',
                'Raiffeisenbank'
            ]:
            updated_methods.append('Raiffeisenbank')

        elif method in ['B47', 'B21']: # ???
            updated_methods.append('Tinkoff')

        elif method in ['B3', '13', '75', 'Тинькофф', 'Tinkoff', '581']:
            updated_methods.append('Tinkoff')

        elif method in ['B39', 'Россельхозбанк']:
            updated_methods.append('RosBank')

        elif method in ['B44', '44', 'MTS Bank', 'MTS-Bank']:
            updated_methods.append('MTS-Bank')

        elif method in ['B2', '1', 'Alfa-Bank', 'Альфа-банк', 'Alfa Bank']:
            updated_methods.append('Alfa-Bank')

        elif method in [
                'B1',
                '12',
                'RosBank',
                '185',
                'Sberbank',
                'СберБанк',
                'Sber',
                '582',
            ]:
            updated_methods.append('Sber')

        elif method in ['B7', 'Газпромбанк', 'Gazprom']:
            updated_methods.append('Gazprom')

        elif method in ['31', '22', '62', 'QiWi', 'QIWI']:
            updated_methods.append('QIWI')

        elif method in [
                '274',
                'YM',
                'Yandex',
                'YooMoney',
                'Юmoney',
                'ЮMoney',
                '574'
            ]:
            updated_methods.append('ЮMoney')

        elif method in ['14', 'BANK_TRANSFER']:
            updated_methods.append('Bank Transfer')

        elif method in ['CASH', '90']:
            updated_methods.append('Cash')

        elif method in ['B13', 'Pochta Bank', 'Post Bank', '357']:
            updated_methods.append('Post-Bank')

        elif method in [
                'Home Credit Bank (Russia)',
                '102',
                'Банк Хоум Кредит',
                'Home Credit Bank  (Russia)',
                'Home Credit Bank'
            ]:
            updated_methods.append('Home Credit Bank')

        elif method in [
                'B80',
                '23',
                '74',
                'SBP - Fast Bank Transfer',
                'SBP System of fast payments',
                'СБП',
                'SBP',
            ]:
            updated_methods.append('SBP')

        elif method in ['B5', 'VTB', 'ВТБ']:
            updated_methods.append('VTB')

        elif method in ['73', 'Russia Standart Bank', '533']:
            updated_methods.append('Russia-Standart-Bank')

        elif method in ['70', 'AK Bars Bank']:
            updated_methods.append('AK Bars Bank')

        elif method in ['2', 'Банковская карта']:
            updated_methods.append('Банковская карта')

        # elif method in ['B23', 'B15', 'B41', 'B22', 'B16', 'B14', 'USDT', 'Advanced cash RUB', 'Mobile Recharge', 'Payeer RUB', 'BTC Bitcoin']:
            # pass
        
        else:
            pass
            # updated_methods.append(method)

    return updated_methods
