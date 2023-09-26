from django.db import models
from base.models import BaseExchange

class ExchangeOkx(BaseExchange):
    class Meta:
        db_table = 'exchange_okx'