from rest_framework.views import APIView
from rest_framework.response import Response

from .services import (
    BinaryP2PServices, TriangularP2PServices, BestPricesP2PServices
)

class BinaryP2PView(APIView):
    def post(self, request):
        p2p = BinaryP2PServices(request.data)
        ads = p2p.get_ads()
        return Response(ads)


class TriangularP2PView(APIView):
    def post(self, request):
        p2p = TriangularP2PServices(request.data)
        ads = p2p.get_ads()
        return Response(ads)


class BestPricesP2PView(APIView):
    def post(self, request):
        best_prices = BestPricesP2PServices(request.data)
        ads = best_prices.get_ads()
        return Response(ads)