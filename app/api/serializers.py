from rest_framework import serializers


class P2PSerializer(serializers.Serializer):
    PAYMENT_METHODS_CHOICES = [
        'Tinkoff',
        'Sber',
        'Raiffeisenbank',
        'MTS-Bank',
        'QIWI',
        'ЮMmoney',
        'Post-Bank',
        'SBP',
        'Russia-Standart-Bank',
        'bank_transfer',
    ]

    EXCHANGES_CHOICES = [
        'exchange_huobi',
        'exchange_mexc',
        'exchange_gateio',
        'exchange_hodlhodl',
        'exchange_bybit',
        'exchange_kucoin',
        'exchange_garantex',
        'exchange_beribit',
        'exchange_totalcoin',
        'exchange_bitpapa',
    ]

    CRYPTO_CHOICES = [
        'USDT', 'BTC', 'ETH', 'BUSD', 'BNB', 'DOGE', 'TRX', 'USDD', 'USDC',
        'RUB', 'HT', 'EOS', 'XRP', 'LTC', 'GMT', 'TON', 'XMR', 'DAI', 'TUSD'
    ]

    TRADE_TYPE_CHOICES = [
        'M-M_SELL-BUY',
        'M-T_SELL-SELL',
        'T-M_BUY-BUY',
        'T-T_BUY-SELL',
    ]

    payment_methods = serializers.ListField(
        child=serializers.ChoiceField(choices=PAYMENT_METHODS_CHOICES),
        required=True,
    )
    exchanges = serializers.ListField(
        child=serializers.ChoiceField(choices=EXCHANGES_CHOICES),
        required=True
    )
    crypto = serializers.ChoiceField(
        choices=CRYPTO_CHOICES,
        required=True,
    )
    trade_type = serializers.ChoiceField(
        choices=TRADE_TYPE_CHOICES,
        required=True,
    )
    ord_q = serializers.FloatField(required=False)
    ord_p = serializers.FloatField(required=False)
    user_spread = serializers.FloatField(required=False)
    lim_first = serializers.FloatField(required=False)
    lim_second = serializers.FloatField(required=False)
    available_first = serializers.FloatField(required=False)
    available_second = serializers.FloatField(required=False)
    only_stable_coin = serializers.BooleanField(required=False)

    def validate_ord_q(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Order quantity must be a non-negative number."
            )
        return value

    def validate_ord_p(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Order price must be a non-negative number."
            )
        return value

    def validate_user_spread(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Spread max must be a non-negative number."
            )
        return value

    def validate_lim_first(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "Limit sell must be a non-negative number."
            )
        return value

    def validate_lim_second(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "Limit buy must be a non-negative number."
            )
        return value

    def validate_available_first(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Available rub buy must be a non-negative number."
            )
        return value

    def validate_available_second(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Available rub sell must be a non-negative number."
            )
        return value