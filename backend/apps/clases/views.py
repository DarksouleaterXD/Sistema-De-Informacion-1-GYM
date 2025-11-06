from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Salon, Clase, InscripcionClase
from .serializers import (
    SalonSerializer, ClaseSerializer, ClaseListSerializer,
    InscripcionClaseSerializer
)
from apps.audit.helpers import registrar_bitacora
from apps.core.permissions import HasPermission, PermissionCodes


# ==========================================
# SALONES
# ==========================================

class SalonListCreateView(generics.ListCreateAPIView):
    """
    GET: Listar salones con búsqueda y filtros
    POST: Crear nuevo salón
    """
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = [PermissionCodes.SALON_VIEW]
    serializer_class = SalonSerializer

    def get_queryset(self):
        queryset = Salon.objects.all()
        
        # Búsqueda
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | 
                Q(descripcion__icontains=search)
            )
        
        # Filtro por estado
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            activo_bool = activo.lower() == 'true'
            queryset = queryset.filter(activo=activo_bool)
        
        return queryset.order_by('nombre')

    def perform_create(self, serializer):
        salon = serializer.save()
        
        # Auditoría
        registrar_bitacora(
            usuario=self.request.user,
            modulo="SALONES",
            actividad="CREAR",
            descripcion=f"Creó el salón: {salon.nombre}",
            dato_modificado=f"Salón ID: {salon.id}"
        )


class SalonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Obtener detalle de un salón
    PUT/PATCH: Actualizar salón
    DELETE: Eliminar salón
    """
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = [PermissionCodes.SALON_VIEW]
    queryset = Salon.objects.all()
    serializer_class = SalonSerializer

    def perform_update(self, serializer):
        salon = serializer.save()
        
        # Auditoría
        registrar_bitacora(
            usuario=self.request.user,
            modulo="SALONES",
            actividad="ACTUALIZAR",
            descripcion=f"Actualizó el salón: {salon.nombre}",
            dato_modificado=f"Salón ID: {salon.id}"
        )

    def perform_destroy(self, instance):
        nombre = instance.nombre
        
        # Auditoría
        registrar_bitacora(
            usuario=self.request.user,
            modulo="SALONES",
            actividad="ELIMINAR",
            descripcion=f"Eliminó el salón: {nombre}",
            dato_modificado=f"Salón ID: {instance.id}"
        )
        
        instance.delete()


# ==========================================
# CLASES (CU20)
# ==========================================

class ClaseListCreateView(generics.ListCreateAPIView):
    """
    CU20: Programar Clase
    GET: Listar clases con búsqueda y filtros
    POST: Crear nueva clase programada
    """
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = [PermissionCodes.CLASE_VIEW]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ClaseListSerializer
        return ClaseSerializer

    def get_queryset(self):
        queryset = Clase.objects.select_related('disciplina', 'instructor', 'salon').all()
        
        # Búsqueda
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(disciplina__nombre__icontains=search) |
                Q(instructor__first_name__icontains=search) |
                Q(instructor__last_name__icontains=search) |
                Q(salon__nombre__icontains=search)
            )
        
        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtro por fecha
        fecha = self.request.query_params.get('fecha', None)
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        
        # Filtro por disciplina
        disciplina_id = self.request.query_params.get('disciplina', None)
        if disciplina_id:
            queryset = queryset.filter(disciplina_id=disciplina_id)
        
        # Filtro por instructor
        instructor_id = self.request.query_params.get('instructor', None)
        if instructor_id:
            queryset = queryset.filter(instructor_id=instructor_id)
        
        return queryset.order_by('-fecha', '-hora_inicio')

    def perform_create(self, serializer):
        clase = serializer.save()
        
        # Auditoría
        registrar_bitacora(
            usuario=self.request.user,
            modulo="CLASES",
            actividad="PROGRAMAR",
            descripcion=f"Programó clase de {clase.disciplina.nombre} para {clase.fecha} {clase.hora_inicio}",
            dato_modificado=f"Clase ID: {clase.id}, Instructor: {clase.instructor.get_full_name()}, Salón: {clase.salon.nombre}"
        )


class ClaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Obtener detalle de una clase
    PUT/PATCH: Actualizar clase
    DELETE: Eliminar clase
    """
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = [PermissionCodes.CLASE_VIEW]
    queryset = Clase.objects.select_related('disciplina', 'instructor', 'salon').all()
    serializer_class = ClaseSerializer

    def perform_update(self, serializer):
        clase = serializer.save()
        
        # Auditoría
        registrar_bitacora(
            usuario=self.request.user,
            modulo="CLASES",
            actividad="EDITAR",
            descripcion=f"Editó clase de {clase.disciplina.nombre} del {clase.fecha}",
            dato_modificado=f"Clase ID: {clase.id}"
        )

    def perform_destroy(self, instance):
        descripcion_clase = f"{instance.disciplina.nombre} - {instance.fecha} {instance.hora_inicio}"
        
        # Auditoría
        registrar_bitacora(
            usuario=self.request.user,
            modulo="CLASES",
            actividad="ELIMINAR",
            descripcion=f"Eliminó clase: {descripcion_clase}",
            dato_modificado=f"Clase ID: {instance.id}"
        )
        
        instance.delete()


# ==========================================
# INSCRIPCIONES A CLASES
# ==========================================

class InscripcionClaseListCreateView(generics.ListCreateAPIView):
    """
    GET: Listar inscripciones a clases
    POST: Inscribir cliente a clase
    """
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = [PermissionCodes.INSCRIPCION_CLASE_VIEW]
    serializer_class = InscripcionClaseSerializer

    def get_queryset(self):
        queryset = InscripcionClase.objects.select_related('clase', 'cliente').all()
        
        # Filtro por clase
        clase_id = self.request.query_params.get('clase', None)
        if clase_id:
            queryset = queryset.filter(clase_id=clase_id)
        
        # Filtro por cliente
        cliente_id = self.request.query_params.get('cliente', None)
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        
        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset.order_by('-fecha_inscripcion')

    def perform_create(self, serializer):
        inscripcion = serializer.save()
        
        # Auditoría
        registrar_bitacora(
            usuario=self.request.user,
            modulo="INSCRIPCIONES_CLASE",
            actividad="INSCRIBIR",
            descripcion=f"Inscribió a {inscripcion.cliente.nombre_completo} en clase de {inscripcion.clase.disciplina.nombre}",
            dato_modificado=f"Inscripción ID: {inscripcion.id}, Clase: {inscripcion.clase.fecha} {inscripcion.clase.hora_inicio}"
        )


class InscripcionClaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Obtener detalle de inscripción
    PUT/PATCH: Actualizar inscripción (cambiar estado)
    DELETE: Eliminar inscripción
    """
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = [PermissionCodes.INSCRIPCION_CLASE_VIEW]
    queryset = InscripcionClase.objects.select_related('clase', 'cliente').all()
    serializer_class = InscripcionClaseSerializer

    def perform_update(self, serializer):
        inscripcion = serializer.save()
        
        # Auditoría
        registrar_bitacora(
            usuario=self.request.user,
            modulo="INSCRIPCIONES_CLASE",
            actividad="ACTUALIZAR",
            descripcion=f"Actualizó inscripción de {inscripcion.cliente.nombre_completo} - Estado: {inscripcion.get_estado_display()}",
            dato_modificado=f"Inscripción ID: {inscripcion.id}"
        )

    def perform_destroy(self, instance):
        cliente_nombre = instance.cliente.nombre_completo
        clase_info = f"{instance.clase.disciplina.nombre} - {instance.clase.fecha}"
        
        # Auditoría
        registrar_bitacora(
            usuario=self.request.user,
            modulo="INSCRIPCIONES_CLASE",
            actividad="CANCELAR",
            descripcion=f"Canceló inscripción de {cliente_nombre} en {clase_info}",
            dato_modificado=f"Inscripción ID: {instance.id}"
        )
        
        instance.delete()
