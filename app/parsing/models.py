from django.db import models


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


class TotalCoin(BaseExchange):
    exchange = models.CharField(default='TotalCoin')
    class Meta:
        db_table = 'exchange_totalcoin'


class Kucoin(BaseExchange):
    exchange = models.CharField(default='Kucoin')
    class Meta:
        db_table = 'exchange_kucoin'