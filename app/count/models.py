from django.db import models


class AdsAbstract(models.Model):
    BUY_SELL_CHOICES = (
        ('BUY', 'BUY'),
        ('SELL', 'SELL'),
    )

    id = models.AutoField(primary_key=True)
    price = models.FloatField(default=0.0)
    name = models.CharField(max_length=100)
    fiat = models.CharField(max_length=10)
    token = models.CharField(max_length=10)
    buy_sell = models.CharField(max_length=4, choices=BUY_SELL_CHOICES)
    order_q = models.IntegerField(default=0)
    order_p = models.FloatField(default=0.0)
    lim_min = models.FloatField(default=0.0)
    lim_max = models.FloatField(default=0.0)
    adv_no = models.CharField(max_length=50)
    available = models.FloatField(max_length=30, default=0.0)
    exchange = models.CharField(max_length=50)
    best_payment = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        abstract = True


class AdsInTwo(AdsAbstract):
    class Meta:
        verbose_name = 'Ads in two actions'
        verbose_name_plural = 'Buy Ads'


class AdsInThree(AdsAbstract):
    class Meta:
        verbose_name = 'Ads in three actions'
        verbose_name_plural = 'Sell Ads'


class BestLinksInTwoActions(models.Model):
    buy_ad = models.OneToOneField(AdsInTwo, related_name='buy_ad', on_delete=models.CASCADE)
    sell_ad = models.OneToOneField(AdsInTwo, related_name='sell_ad', on_delete=models.CASCADE)
    spread = models.FloatField()


class BestLinksInThreeActions(models.Model):
    buy_ad = models.OneToOneField(AdsInThree, related_name='buy_ad', on_delete=models.CASCADE)
    sell_ad = models.OneToOneField(AdsInThree, related_name='sell_ad', on_delete=models.CASCADE)
    spread = models.FloatField()
    spot = models.FloatField()