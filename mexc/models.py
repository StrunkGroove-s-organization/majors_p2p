from django.db import models
from base.models import BaseExchange

class ExchangeMexc(BaseExchange):
    class Meta:
        db_table = 'exchange_mexc'