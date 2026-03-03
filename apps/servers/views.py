from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Server, ServerUser, TerminalSession
from .serializers import ServerSerializer, ServerUserSerializer, TerminalSessionSerializer
import paramiko
import io

class ServerUserViewSet(viewsets.ModelViewSet):
    queryset = ServerUser.objects.all()
    serializer_class = ServerUserSerializer

    def get_queryset(self):
        """Optionally filter by server_id if provided in URL params or query"""
        queryset = super().get_queryset()
        server_id = self.request.query_params.get('server_id')
        if server_id:
            queryset = queryset.filter(server_id=server_id)
        return queryset

    def destroy(self, request, *args, **kwargs):
        """Eliminación suave de usuario"""
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all().order_by('-created_at')
    # ... existing code ...
    serializer_class = ServerSerializer

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        server = self.get_object()
        sessions = TerminalSession.objects.filter(server=server).order_by('-started_at')
        serializer = TerminalSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Eliminación suave de servidor"""
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

