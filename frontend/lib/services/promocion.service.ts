// lib/services/promocion.service.ts
import { httpClient } from "../config/http-client";

export interface Promocion {
  id: number;
  nombre: string;
  descripcion?: string;
  tipo_descuento: "PORCENTAJE" | "MONTO_FIJO";
  valor_descuento: number;
  fecha_inicio: string;
  fecha_fin: string;
  activo: boolean;
  codigo?: string;
  esta_vigente: boolean;
  created_at: string;
  updated_at: string;
}

export interface PromocionCreate {
  nombre: string;
  descripcion?: string;
  tipo_descuento: "PORCENTAJE" | "MONTO_FIJO";
  valor_descuento: number;
  fecha_inicio: string;
  fecha_fin: string;
  activo: boolean;
  codigo?: string;
}

export interface PromocionUpdate {
  nombre?: string;
  descripcion?: string;
  tipo_descuento?: "PORCENTAJE" | "MONTO_FIJO";
  valor_descuento?: number;
  fecha_inicio?: string;
  fecha_fin?: string;
  activo?: boolean;
  codigo?: string;
}

class PromocionService {
  private baseUrl = "/api/promociones";

  async getAll(): Promise<Promocion[]> {
    return await httpClient.get<Promocion[]>(this.baseUrl + "/");
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
}

export const promocionService = new PromocionService();
