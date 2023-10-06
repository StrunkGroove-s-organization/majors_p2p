from django.db import models
from base.models import BaseExchange

class ExchangeHuobi(BaseExchange):
    class Meta:
        db_table = 'exchange_huobi'