from base.models import BaseExchange

class ExchangeBybit(BaseExchange):
    class Meta:
        db_table = 'exchange_bybit'