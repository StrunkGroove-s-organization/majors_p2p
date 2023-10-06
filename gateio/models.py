from base.models import BaseExchange

class ExchangeGateIo(BaseExchange):
    class Meta:
        db_table = 'exchange_gateio'