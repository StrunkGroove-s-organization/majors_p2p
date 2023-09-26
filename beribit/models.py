from django.db import models
from base.models import BaseExchange

class ExchangeBeribit(BaseExchange):
    class Meta:
        db_table = 'exchange_beribit'