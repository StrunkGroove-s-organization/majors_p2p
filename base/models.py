from django.db import models

class BaseExchange(models.Model):
    
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=100)
    order_q = models.IntegerField()
    order_p = models.FloatField(default=0)

    price = models.FloatField(default=0)

    lim_min = models.FloatField(default=0)
    lim_max = models.FloatField(default=0)

    fiat = models.CharField(max_length=10)
    token = models.CharField(max_length=10)
    buy_sell = models.CharField(default=10)

    exchange = models.CharField(max_length=20)

    adv_no = models.CharField(max_length=50,default='#')

    payments = models.JSONField()
    best_payment = models.CharField(max_length=20, blank=True, null=True)

    available = models.FloatField(max_length=30, default=0)
    available_rub = models.FloatField(max_length=30, default=0)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['id']),
        ]

