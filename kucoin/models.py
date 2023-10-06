from django.db import models
from base.models import BaseExchange

class ExchangeKucoin(BaseExchange):
    class Meta:
        db_table = 'exchange_kucoin'