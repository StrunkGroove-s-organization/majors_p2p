from django.urls import path
from . import views

urlpatterns = [
    path('binary-arbitrage/',
         views.BinaryP2PView.as_view(), name='binary-arbitrage'),
    path('triangular-arbitrage/', 
         views.TriangularP2PView.as_view(), name='triangular-arbitrage'),
]
