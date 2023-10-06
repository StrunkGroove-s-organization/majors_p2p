from django.db import models
from base.models import BaseExchange

class ExchangeBitpapa(BaseExchange):
    class Meta:
        db_table = 'exchange_bitpapa'