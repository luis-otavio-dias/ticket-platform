from typing import TYPE_CHECKING

from rest_framework.response import Response
from rest_framework.views import APIView

if TYPE_CHECKING:
    from rest_framework.request import Request


class HealthCheckView(APIView):
    def get(self, request: Request) -> Response:
        return Response({"status": "ok"})
