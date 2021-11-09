from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class MusicAPI(APIView):

    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        q = request.query_params.get("q")
        if not q:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response({"result": "ok"})
