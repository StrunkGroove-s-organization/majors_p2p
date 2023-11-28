from django.urls import path
from . import views

urlpatterns = [
    path('binary-arbitrage/', views.BinaryP2PView.as_view()),
    path('triangular-arbitrage/', views.TriangularP2PView.as_view()),
]

# {"payment_methods":["Tinkoff","Sber","SBP"],"exchanges":["exchange_bybit","exchange_huobi","exchange_garantex","exchange_bitpapa","exchange_beribit","exchange_hodlhodl","exchange_mexc","exchange_kucoin","exchange_gateio","exchange_totalcoin"],"crypto":"USDT","crypto_multi":"DAI","trade_type":"M-M_SELL-BUY","user_spread":"1100","ord_q":"1","ord_p":"1","deposit":"1","only_stable_coin":false}
