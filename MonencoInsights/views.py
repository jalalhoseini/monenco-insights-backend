from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
)
from rest_framework.response import Response
from rest_framework.views import APIView


class VersionCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            version = request.query_params['version']
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if str(version) != "1":
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            data = dict()
            data['isSupported'] = True
            data['newVersionAvailable'] = False
            data['newVersionLink'] = None
            return Response(data=data, status=status.HTTP_200_OK)

    def post(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
