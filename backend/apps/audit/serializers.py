from rest_framework import serializers
from apps.audit.models import HistorialActividad as Bitacora

class BitacoraSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()
    tipo_accion_display = serializers.CharField(source="get_tipo_accion_display", read_only=True)
    nivel_display = serializers.CharField(source="get_nivel_display", read_only=True)
    fecha_formateada = serializers.SerializerMethodField()

    class Meta:
        model = Bitacora
        fields = [
            "id", "usuario", "usuario_nombre", "tipo_accion", "tipo_accion_display",
            "accion", "descripcion", "nivel", "nivel_display",
            "ip_address", "user_agent", "fecha_hora", "fecha_formateada",
            "datos_adicionales",
        ]
        read_only_fields = ["id", "fecha_hora"]

    def get_usuario_nombre(self, obj):
        return obj.usuario.username if obj.usuario else "Sistema"

    def get_fecha_formateada(self, obj):
        return obj.fecha_hora.strftime("%d/%m/%Y %H:%M:%S")
