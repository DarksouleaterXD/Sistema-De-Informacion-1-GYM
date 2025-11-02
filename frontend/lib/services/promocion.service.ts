// lib/services/promocion.service.ts
import { httpClient } from "../config/http-client";
import { Promocion, EstadoPromocion } from "../types";

// Re-exportar tipos para facilitar imports
export type { Promocion, EstadoPromocion };

export interface PromocionCreate {
  nombre: string;
  meses: number; // Duración en meses
  descuento: number | string; // Porcentaje de descuento
  fecha_inicio: string;
  fecha_fin: string;
  estado?: EstadoPromocion;
}

export interface PromocionUpdate {
  nombre?: string;
  meses?: number;
  descuento?: number | string;
  fecha_inicio?: string;
  fecha_fin?: string;
  estado?: EstadoPromocion;
}

class PromocionService {
  private baseUrl = "/api/promociones";

  async getAll(params?: {
    estado?: EstadoPromocion;
    activas?: boolean;
  }): Promise<Promocion[]> {
    const queryParams = new URLSearchParams();

    if (params?.estado) queryParams.append("estado", params.estado);
    if (params?.activas) queryParams.append("activas", "true");

    const url = `${this.baseUrl}/${
      queryParams.toString() ? `?${queryParams.toString()}` : ""
    }`;

    return await httpClient.get<Promocion[]>(url);
  }

  async getById(id: number): Promise<Promocion> {
    return await httpClient.get<Promocion>(`${this.baseUrl}/${id}/`);
  }

  async create(data: PromocionCreate): Promise<Promocion> {
    return await httpClient.post<Promocion>(this.baseUrl + "/", data);
  }

  async update(id: number, data: PromocionUpdate): Promise<Promocion> {
    return await httpClient.put<Promocion>(`${this.baseUrl}/${id}/`, data);
  }

  async patch(id: number, data: Partial<PromocionUpdate>): Promise<Promocion> {
    return await httpClient.patch<Promocion>(`${this.baseUrl}/${id}/`, data);
  }

  async delete(id: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/${id}/`);
  }

  /**
   * Activar una promoción
   */
  async activar(id: number): Promise<Promocion> {
    return await httpClient.patch<Promocion>(`${this.baseUrl}/${id}/`, {
      estado: "ACTIVA",
    });
  }

  /**
   * Desactivar una promoción
   */
  async desactivar(id: number): Promise<Promocion> {
    return await httpClient.patch<Promocion>(`${this.baseUrl}/${id}/`, {
      estado: "INACTIVA",
    });
  }
}

export const promocionService = new PromocionService();
