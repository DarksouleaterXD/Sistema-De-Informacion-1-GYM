import { httpClient } from "../config/http-client";

export interface InscripcionMembresia {
  id: number;
  cliente: number;
  cliente_info?: {
    id: number;
    nombre: string;
    apellido: string;
    ci: string;
    email: string;
    celular: string;
  };
  monto: number;
  metodo_de_pago: string;
  metodo_de_pago_display?: string;
  created_at: string;
  updated_at: string;
}

export interface Membresia {
  id: number;
  inscripcion: number;
  inscripcion_info?: InscripcionMembresia;
  usuario_registro: number;
  usuario_registro_nombre?: string;
  estado: string;
  estado_display?: string;
  fecha_inicio: string;
  fecha_fin: string;
  dias_restantes?: number;
  esta_activa?: boolean;
  duracion_dias?: number;
  created_at: string;
  updated_at: string;
}

export interface MembresiaList {
  id: number;
  cliente_nombre: string;
  cliente_ci: string;
  estado: string;
  estado_display: string;
  fecha_inicio: string;
  fecha_fin: string;
  monto: number;
  metodo_pago: string;
  dias_restantes: number;
  esta_activa: boolean;
}

export interface MembresiaCreate {
  cliente: number;
  monto: number;
  metodo_de_pago: string;
  estado: string;
  fecha_inicio: string;
  fecha_fin: string;
}

export interface MembresiaStats {
  total_membresias: number;
  activas: number;
  vencidas: number;
  ingresos_totales: number;
  ingresos_mes_actual: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

class MembresiaService {
  private baseURL = "/api/membresias";

  /**
   * Obtener lista de membresías con paginación
   */
  async getAll(params?: {
    page?: number;
    search?: string;
    estado?: string;
  }): Promise<PaginatedResponse<MembresiaList>> {
    const queryParams = new URLSearchParams();

    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.search) queryParams.append("search", params.search);
    if (params?.estado) queryParams.append("estado", params.estado);

    const url = `${this.baseURL}/${
      queryParams.toString() ? `?${queryParams.toString()}` : ""
    }`;

    return httpClient.get<PaginatedResponse<MembresiaList>>(url);
  }

  /**
   * Obtener detalle de una membresía
   */
  async getById(id: number): Promise<Membresia> {
    return httpClient.get<Membresia>(`${this.baseURL}/${id}/`);
  }

  /**
   * Crear una nueva membresía (con inscripción)
   */
  async create(data: MembresiaCreate): Promise<Membresia> {
    return httpClient.post<Membresia>(this.baseURL + "/", data);
  }

  /**
   * Actualizar una membresía completa
   */
  async update(id: number, data: Partial<Membresia>): Promise<Membresia> {
    return httpClient.put<Membresia>(`${this.baseURL}/${id}/`, data);
  }

  /**
   * Actualizar parcialmente una membresía
   */
  async patch(id: number, data: Partial<Membresia>): Promise<Membresia> {
    return httpClient.patch<Membresia>(`${this.baseURL}/${id}/`, data);
  }

  /**
   * Eliminar una membresía
   */
  async delete(id: number): Promise<void> {
    return httpClient.delete(`${this.baseURL}/${id}/`);
  }

  /**
   * Obtener estadísticas de membresías
   */
  async getStats(): Promise<MembresiaStats> {
    return httpClient.get<MembresiaStats>(`${this.baseURL}/stats/`);
  }
}

export const membresiaService = new MembresiaService();
export default membresiaService;
