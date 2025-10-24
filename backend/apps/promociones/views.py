from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.promociones.models import Promocion
from apps.promociones.serializers import PromocionSerializer
from apps.roles.views import HasRoleSuperUser
from apps.audit.models import HistorialActividad as Bitacora


def _ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0] if xff else request.META.get("REMOTE_ADDR", "")


def _ua(request):
    return request.META.get("HTTP_USER_AGENT", "")


class PromocionListCreateView(APIView):
    """
    GET: Lista todas las promociones
    POST: Crea una nueva promoción
    """
    permission_classes = [IsAuthenticated, HasRoleSuperUser]

    def get(self, request):
        promociones = Promocion.objects.all()
        serializer = PromocionSerializer(promociones, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PromocionSerializer(data=request.data)
        if serializer.is_valid():
            promocion = serializer.save()
            
            # Registrar en bitácora
            Bitacora.log_activity(
                request=request,
                tipo_accion="create_promocion",
                accion="Crear Promoción",
                descripcion=f"Promoción creada: {promocion.nombre}",
                nivel="info",
                datos_adicionales={"promocion_id": promocion.id}
            
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PromocionDetailView(APIView):
    """
    GET: Obtiene una promoción por ID
    PUT: Actualiza una promoción
    PATCH: Actualiza parcialmente una promoción
    DELETE: Elimina una promoción
    """
    permission_classes = [IsAuthenticated, HasRoleSuperUser]

    def get(self, request, pk):
        promocion = get_object_or_404(Promocion, pk=pk)
        serializer = PromocionSerializer(promocion)
        return Response(serializer.data)

    def put(self, request, pk):
        promocion = get_object_or_404(Promocion, pk=pk)
        serializer = PromocionSerializer(promocion, data=request.data)
        if serializer.is_valid():
            promocion_updated = serializer.save()
            
            # Registrar en bitácora
            Bitacora.log_activity(
                request=request,
                tipo_accion="update_promocion",
                accion="Actualizar Promoción",
                descripcion=f"Promoción actualizada: {promocion_updated.nombre}",
                nivel="info",
                datos_adicionales={"promocion_id": promocion_updated.id}
            
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        promocion = get_object_or_404(Promocion, pk=pk)
        serializer = PromocionSerializer(promocion, data=request.data, partial=True)
        if serializer.is_valid():
            promocion_updated = serializer.save()
            
            # Registrar en bitácora
            Bitacora.log_activity(
                request=request,
                tipo_accion="update_promocion",
                accion="Actualizar Promoción",
                descripcion=f"Promoción actualizada parcialmente: {promocion_updated.nombre}",
                nivel="info",
                datos_adicionales={"promocion_id": promocion_updated.id}
            
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        promocion = get_object_or_404(Promocion, pk=pk)
        nombre = promocion.nombre
        promocion_id = promocion.id
        promocion.delete()
        
        # Registrar en bitácora
        Bitacora.log_activity(
                request=request,
                tipo_accion="delete_promocion",
                accion="Eliminar Promoción",
                descripcion=f"Promoción eliminada: {nombre}",
                nivel="warning",
                datos_adicionales={"promocion_id": promocion_id}
        
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
