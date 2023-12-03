from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import P2PSerializer
from .services import BinaryP2PServices, TriangularP2PServices


class BinaryP2PView(APIView):
    def post(self, request):
        # serializer = P2PSerializer(data=request.data)
        
        # if not serializer.is_valid():
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        p2p = BinaryP2PServices(request.data)
        response = p2p.get_ads()
        return Response(response)


class TriangularP2PView(APIView):
    def post(self, request):
        # serializer = P2PSerializer(data=request.data)
        
        # if serializer.is_valid():
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        p2p = TriangularP2PServices(request.data)
        response = p2p.get_ads()
        return Response(response)
