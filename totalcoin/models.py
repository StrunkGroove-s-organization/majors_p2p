from base.models import BaseExchange

class ExchangeTotalCoin(BaseExchange):
    class Meta:
        db_table = 'exchange_totalcoin'