from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import P2PSerializer
from .services import BinaryP2PServices, TriangularP2PServices, BestPricesP2PServices


class BinaryP2PView(APIView):
    def post(self, request):
        p2p = BinaryP2PServices(request.data)
        response = p2p.get_ads()
        return Response(response)


class TriangularP2PView(APIView):
    def post(self, request):
        p2p = TriangularP2PServices(request.data)
        response = p2p.get_ads()
        return Response(response)


class BestPricesP2PView(APIView):
    def post(self, request):
        best_prices = BestPricesP2PServices(request.data)
        response = best_prices.get_ads()
        return Response(response)