import { httpClient } from "../config/http-client";
import {
  Membresia,
  PlanMembresia,
  InscripcionMembresia,
  MembresiaPromocion,
} from "../types";

// Re-exportar tipos para facilitar imports
export type {
  Membresia,
  PlanMembresia,
  InscripcionMembresia,
  MembresiaPromocion,
};

export interface MembresiaList {
  id: number;
  cliente_nombre: string;
  cliente_ci: string;
  plan_nombre?: string; // Nuevo campo
  estado: string;
  estado_display: string;
  fecha_inicio: string;
  fecha_fin: string;
  monto: number;
  metodo_pago: string;
  dias_restantes: number;
  esta_activa: boolean;
  promociones_aplicadas?: number; // Cantidad de promociones
}

export interface MembresiaCreate {
  cliente: number;
  plan: number; // Nuevo campo requerido
  promociones?: number[]; // Nuevo campo opcional para M2M
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

  /**
   * Obtener todos los planes de membresía
   */
  async getPlanes(): Promise<PlanMembresia[]> {
    return httpClient.get<PlanMembresia[]>("/api/planes-membresia/");
  }

  /**
   * Aplicar promoción a una membresía
   */
  async aplicarPromocion(
    membresiaId: number,
    promocionId: number
  ): Promise<MembresiaPromocion> {
    return httpClient.post<MembresiaPromocion>(
      `${this.baseURL}/${membresiaId}/aplicar-promocion/`,
      { promocion_id: promocionId }
    );
  }

  /**
   * Remover promoción de una membresía
   */
  async removerPromocion(
    membresiaId: number,
    promocionId: number
  ): Promise<void> {
    return httpClient.delete(
      `${this.baseURL}/${membresiaId}/remover-promocion/${promocionId}/`
    );
  }
}

export const membresiaService = new MembresiaService();
export default membresiaService;
