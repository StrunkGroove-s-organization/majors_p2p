from base.models import BaseExchange

class ExchangeGarantex(BaseExchange):
    class Meta:
        db_table = 'exchange_garantex'