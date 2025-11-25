from rest_framework import serializers
from apps.audit.models import HistorialActividad as Bitacora

class BitacoraSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()
    usuario_email = serializers.SerializerMethodField()
    usuario_completo = serializers.SerializerMethodField()
    tipo_accion_display = serializers.CharField(source="get_tipo_accion_display", read_only=True)
    nivel_display = serializers.CharField(source="get_nivel_display", read_only=True)
    fecha_formateada = serializers.SerializerMethodField()

    class Meta:
        model = Bitacora
        fields = [
            "id", "usuario", "usuario_nombre", "usuario_email", "usuario_completo",
            "tipo_accion", "tipo_accion_display",
            "accion", "descripcion", "nivel", "nivel_display",
            "ip_address", "user_agent", "fecha_hora", "fecha_formateada",
            "datos_adicionales",
        ]
        read_only_fields = ["id", "fecha_hora"]

    def get_usuario_nombre(self, obj):
        """Retorna el nombre completo del usuario o 'Sistema'"""
        if obj.usuario:
            nombre = obj.usuario.get_full_name()
            return nombre if nombre.strip() else obj.usuario.username
        return "Sistema"
    
    def get_usuario_email(self, obj):
        """Retorna el email del usuario o None"""
        return obj.usuario.email if obj.usuario else None
    
    def get_usuario_completo(self, obj):
        """Retorna nombre completo y email, o 'Sistema'"""
        if obj.usuario:
            nombre = obj.usuario.get_full_name()
            nombre = nombre if nombre.strip() else obj.usuario.username
            return f"{nombre} ({obj.usuario.email})"
        return "Sistema"

    def get_fecha_formateada(self, obj):
        return obj.fecha_hora.strftime("%d/%m/%Y %H:%M:%S")
