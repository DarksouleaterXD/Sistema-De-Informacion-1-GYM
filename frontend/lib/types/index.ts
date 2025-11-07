/**
 * Tipos TypeScript que coinciden con los modelos del backend Django
 */

// Usuario
export interface User {
  id: number;
  email: string;
  nombre: string;
  apellido: string;
  is_active: boolean;
  is_superuser: boolean;
  fecha_registro?: string;
  ultimo_acceso?: string;
  roles?: Role[];
  permissions?: string[]; // Lista de códigos de permisos
}

// Instructor (Usuario con rol de Instructor)
export interface Instructor {
  id: number;
  usuario: number | User;
  usuario_info?: User; // Información del usuario relacionado
  especialidades: string[]; // Lista de especialidades (disciplinas)
  certificaciones?: string; // Certificaciones del instructor
  biografia?: string; // Biografía breve
  foto_perfil?: string; // URL de la foto
  activo: boolean;
  fecha_ingreso: string;
  created_at: string;
  updated_at: string;
}

// Cliente
export interface Client {
  id: number;
  nombre: string;
  apellido: string;
  ci: string;
  telefono: string;
  celular?: string; // Campo adicional opcional
  email: string;
  fecha_registro: string;
  peso: string; // DecimalField
  altura: string; // DecimalField
  experiencia: "principiante" | "intermedio" | "avanzado";
  nombre_completo?: string;
  created_at: string;
  updated_at: string;
}

// Rol
export interface Role {
  id: number;
  nombre: string;
  descripcion: string;
  permisos?: Permiso[];
  created_at: string;
  updated_at: string;
}

// Permiso
export interface Permiso {
  id: number;
  nombre: string;
  codigo: string;
  descripcion: string;
  created_at: string;
  updated_at: string;
}

// Plan de Membresía
export interface PlanMembresia {
  id: number;
  nombre: string;
  duracion: number; // días
  precio_base: string; // DecimalField
  descripcion: string;
  created_at: string;
  updated_at: string;
}

// Inscripción Membresía
export interface InscripcionMembresia {
  id: number;
  cliente: number | Client;
  monto: string;
  metodo_de_pago: string;
  metodo_de_pago_display?: string;
  created_at: string;
  updated_at: string;
}

// Membresía
export interface Membresia {
  id: number;
  inscripcion: number | InscripcionMembresia;
  inscripcion_info?: InscripcionMembresia & {
    cliente_info?: Client;
  };
  usuario_registro: number | User;
  usuario_registro_nombre?: string;
  plan: number | PlanMembresia; // Nueva relación FK
  plan_info?: PlanMembresia;
  promociones?: number[] | Promocion[]; // Nueva relación M2M
  estado: "activo" | "inactivo" | "vencido" | "suspendido"; // ✅ CORREGIDO: minúsculas
  estado_display?: string;
  fecha_inicio: string;
  fecha_fin: string;
  dias_restantes?: number;
  esta_activa?: boolean;
  duracion_dias?: number;
  created_at: string;
  updated_at: string;
}

// Membresía-Promoción (tabla intermedia M2M)
export interface MembresiaPromocion {
  id: number;
  membresia: number | Membresia;
  promocion: number | Promocion;
  fecha_aplicacion: string;
  descuento_aplicado: string;
  created_at: string;
  updated_at: string;
}

// Promoción
export interface Promocion {
  id: number;
  nombre: string;
  meses: number; // Duración en meses
  descuento: string; // DecimalField (porcentaje)
  fecha_inicio: string;
  fecha_fin: string;
  estado: "ACTIVA" | "INACTIVA" | "VENCIDA"; // ✅ Promociones usan MAYÚSCULAS en backend
  esta_vigente?: boolean; // Calculado en el backend
  created_at: string;
  updated_at: string;
}

// Bitácora/Auditoría
export interface HistorialActividad {
  id: number;
  usuario: number | User;
  accion: string;
  descripcion: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
}

// Respuesta de Login
export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

// Respuesta paginada
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Filtros comunes
export interface BaseFilters {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
}

// Estados (✅ CORREGIDO: membresías minúsculas, promociones MAYÚSCULAS)
export type EstadoMembresia = "activo" | "inactivo" | "vencido" | "suspendido";
export type EstadoPromocion = "ACTIVA" | "INACTIVA" | "VENCIDA";
export type ExperienciaCliente = "principiante" | "intermedio" | "avanzado";
export type MetodoPago = "efectivo" | "tarjeta" | "transferencia" | "qr";
