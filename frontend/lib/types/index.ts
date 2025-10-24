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
}

// Cliente
export interface Client {
  id: number;
  nombre: string;
  apellido: string;
  ci: string;
  telefono: string;
  email: string;
  fecha_registro: string;
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

// Inscripción Membresía
export interface InscripcionMembresia {
  id: number;
  cliente: number | Client;
  monto: string;
  metodo_de_pago: string;
  created_at: string;
  updated_at: string;
}

// Membresía
export interface Membresia {
  id: number;
  inscripcion: number | InscripcionMembresia;
  usuario_registro: number | User;
  estado: "activo" | "inactivo" | "vencido" | "suspendido";
  fecha_inicio: string;
  fecha_fin: string;
  dias_restantes?: number;
  esta_activa?: boolean;
  duracion_dias?: number;
  created_at: string;
  updated_at: string;
}

// Promoción
export interface Promocion {
  id: number;
  nombre: string;
  descripcion: string;
  descuento: string;
  fecha_inicio: string;
  fecha_fin: string;
  activo: boolean;
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

// Estados
export type EstadoMembresia = "activo" | "inactivo" | "vencido" | "suspendido";
export type MetodoPago = "efectivo" | "tarjeta" | "transferencia" | "qr";
