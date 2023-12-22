from django.db import models


### Info parsing ###
# class CryptoParsing(models.Model):
#     name = models.CharField(max_length=100)

# class BanksParsing(models.Model):
#     name = models.CharField(max_length=100)

# class BanksParsingTotalCoin(models.Model):
#     crypto = models.ForeignKey(CryptoParsing, on_delete=models.CASCADE)





### Ads ###
class BaseExchange(models.Model):
    BUY_SELL_CHOICES = (
        ('BUY', 'BUY'),
        ('SELL', 'SELL'),
    )

    id = models.AutoField(primary_key=True)
    price = models.FloatField(default=0.0)
    name = models.CharField(max_length=100)
    payments = models.JSONField()
    fiat = models.CharField(max_length=10)
    token = models.CharField(max_length=10)
    buy_sell = models.CharField(max_length=4, choices=BUY_SELL_CHOICES)
    # best_payment = models.CharField(max_length=20, blank=True, null=True)

    order_q = models.IntegerField(default=0)
    order_p = models.FloatField(default=0.0)
    lim_min = models.FloatField(default=0.0)
    lim_max = models.FloatField(default=0.0)
    adv_no = models.CharField(max_length=50)
    available = models.FloatField(max_length=30, default=0.0)
    available_rub = models.FloatField(max_length=30, default=0.0)

    class Meta:
        abstract = True


class TotalCoinModel(BaseExchange):
    exchange = models.CharField(default='TotalCoin')
    class Meta:
        db_table = 'totalcoin'


class KucoinModel(BaseExchange):
    exchange = models.CharField(default='Kucoin')
    class Meta:
        db_table = 'kucoin'


class GarantexModel(BaseExchange):
    exchange = models.CharField(default='Garantex')
    class Meta:
        db_table = 'garantex'


class GateioModel(BaseExchange):
    exchange = models.CharField(default='Gateio')
    class Meta:
        db_table = 'gateio'


class HodlHodlModel(BaseExchange):
    exchange = models.CharField(default='HodlHodl')
    class Meta:
        db_table = 'hodlhodl'


class HuobiModel(BaseExchange):
    exchange = models.CharField(default='Huobi')
    class Meta:
        db_table = 'huobi'


class BybitModel(BaseExchange):
    exchange = models.CharField(default='Bybit')
    class Meta:
        db_table = 'bybit'


class BitpapaModel(BaseExchange):
    exchange = models.CharField(default='Bitpapa')
    class Meta:
        db_table = 'bitpapa'