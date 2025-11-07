"""
Constantes compartidas en toda la aplicación
"""

# Estados de membresía
ESTADO_ACTIVO = 'activo'
ESTADO_INACTIVO = 'inactivo'
ESTADO_VENCIDO = 'vencido'
ESTADO_SUSPENDIDO = 'suspendido'
ESTADO_CANCELADO = 'cancelado'

ESTADOS_MEMBRESIA = [
    (ESTADO_ACTIVO, 'Activo'),
    (ESTADO_INACTIVO, 'Inactivo'),
    (ESTADO_VENCIDO, 'Vencido'),
    (ESTADO_SUSPENDIDO, 'Suspendido'),
    (ESTADO_CANCELADO, 'Cancelado'),
]

# Estados de clase
CLASE_PROGRAMADA = 'programada'
CLASE_EN_CURSO = 'en_curso'
CLASE_FINALIZADA = 'finalizada'
CLASE_CANCELADA = 'cancelada'

ESTADOS_CLASE = [
    (CLASE_PROGRAMADA, 'Programada'),
    (CLASE_EN_CURSO, 'En Curso'),
    (CLASE_FINALIZADA, 'Finalizada'),
    (CLASE_CANCELADA, 'Cancelada'),
]

# Estados de inscripción a clase
INSCRIPCION_CONFIRMADA = 'confirmada'
INSCRIPCION_CANCELADA_CLASE = 'cancelada'
INSCRIPCION_ASISTIO = 'asistio'
INSCRIPCION_NO_ASISTIO = 'no_asistio'

ESTADOS_INSCRIPCION_CLASE = [
    (INSCRIPCION_CONFIRMADA, 'Confirmada'),
    (INSCRIPCION_CANCELADA_CLASE, 'Cancelada'),
    (INSCRIPCION_ASISTIO, 'Asistió'),
    (INSCRIPCION_NO_ASISTIO, 'No Asistió'),
]

# Métodos de pago
METODO_EFECTIVO = 'efectivo'
METODO_TARJETA = 'tarjeta'
METODO_TRANSFERENCIA = 'transferencia'
METODO_QR = 'qr'

METODOS_PAGO = [
    (METODO_EFECTIVO, 'Efectivo'),
    (METODO_TARJETA, 'Tarjeta de Crédito/Débito'),
    (METODO_TRANSFERENCIA, 'Transferencia Bancaria'),
    (METODO_QR, 'Código QR'),
]

# Tipos de actividad para auditoría
ACTIVIDAD_LOGIN = 'login'
ACTIVIDAD_LOGOUT = 'logout'
ACTIVIDAD_CREAR = 'crear'
ACTIVIDAD_ACTUALIZAR = 'actualizar'
ACTIVIDAD_ELIMINAR = 'eliminar'
ACTIVIDAD_VER = 'ver'
ACTIVIDAD_CONSULTAR = 'consultar'

TIPOS_ACTIVIDAD = [
    (ACTIVIDAD_LOGIN, 'Inicio de Sesión'),
    (ACTIVIDAD_LOGOUT, 'Cierre de Sesión'),
    (ACTIVIDAD_CREAR, 'Crear Registro'),
    (ACTIVIDAD_ACTUALIZAR, 'Actualizar Registro'),
    (ACTIVIDAD_ELIMINAR, 'Eliminar Registro'),
    (ACTIVIDAD_VER, 'Ver Registro'),
    (ACTIVIDAD_CONSULTAR, 'Consultar Registro'),
]

# Niveles de experiencia para clientes
EXPERIENCIA_PRINCIPIANTE = 'principiante'
EXPERIENCIA_INTERMEDIO = 'intermedio'
EXPERIENCIA_AVANZADO = 'avanzado'

NIVELES_EXPERIENCIA = [
    (EXPERIENCIA_PRINCIPIANTE, 'Principiante'),
    (EXPERIENCIA_INTERMEDIO, 'Intermedio'),
    (EXPERIENCIA_AVANZADO, 'Avanzado'),
]

# Duraciones de planes de membresía (en días)
PLAN_MENSUAL = 30
PLAN_TRIMESTRAL = 90
PLAN_SEMESTRAL = 180
PLAN_ANUAL = 365

DURACIONES_PLAN = [
    (PLAN_MENSUAL, 'Mensual (30 días)'),
    (PLAN_TRIMESTRAL, 'Trimestral (90 días)'),
    (PLAN_SEMESTRAL, 'Semestral (180 días)'),
    (PLAN_ANUAL, 'Anual (365 días)'),
]

# Estados de promoción
ESTADO_PROMOCION_ACTIVA = 'ACTIVA'
ESTADO_PROMOCION_INACTIVA = 'INACTIVA'
ESTADO_PROMOCION_VENCIDA = 'VENCIDA'

ESTADOS_PROMOCION = [
    (ESTADO_PROMOCION_ACTIVA, 'Activa'),
    (ESTADO_PROMOCION_INACTIVA, 'Inactiva'),
    (ESTADO_PROMOCION_VENCIDA, 'Vencida'),
]
