from django.urls import reverse
from django.test import TransactionTestCase
from rest_framework import status


payment_methods = ["Sber", "Tinkoff", "SBP", "Raiffeisenbank", "Bank Transfer"]

trade_type = ["Maker - Maker", "Taker - Taker", "Maker - Taker", 
              "Taker - Maker"]

exchanges = ["Huobi", "TotalCoin", "Kucoin", "HodlHodl", "Gateio", "Garantex",
             "Bybit"]

crypto = ["USDT", "BTC", "ETH", "USDC", "LTC", "DAI","HT", "TRX"]

payload = { "payment_methods": payment_methods,
            "exchanges": exchanges,
            "crypto": crypto[0],
            "trade_type": trade_type[1]}

class P2PApiTests(TransactionTestCase):
    def test_access(self):
        url = reverse('binary-arbitrage')
        response = self.client.post(url, data=payload)
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_payment_methods(self):
    #     url = reverse('binary-arbitrage')
        
    #     response = self.client.post(url, data=payload)
    #     print(response.content)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)