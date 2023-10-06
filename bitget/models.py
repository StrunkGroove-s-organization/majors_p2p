from django.db import models
from base.models import BaseExchange

class ExchangeBitget(BaseExchange):
    class Meta:
        db_table = 'exchange_bitget'