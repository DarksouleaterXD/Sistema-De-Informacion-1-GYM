// lib/services/plan-membresia.service.ts
import { httpClient } from "../config/http-client";
import { PlanMembresia } from "../types";

export interface PlanMembresiaCreate {
  nombre: string;
  duracion: number; // días
  precio_base: number | string;
  descripcion?: string;
}

export interface PlanMembresiaUpdate extends Partial<PlanMembresiaCreate> {}

export interface PaginatedPlanMembresiaResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: PlanMembresia[];
}

class PlanMembresiaService {
  private baseUrl = "/api/planes-membresia";

  async getAll(params?: { page?: number; search?: string }): Promise<PaginatedPlanMembresiaResponse> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.search) queryParams.append('search', params.search);
    
    const url = `${this.baseUrl}/?${queryParams.toString()}`;
    return await httpClient.get<PaginatedPlanMembresiaResponse>(url);
  }

  async getById(id: number): Promise<PlanMembresia> {
    return await httpClient.get<PlanMembresia>(`${this.baseUrl}/${id}/`);
  }

  async create(data: PlanMembresiaCreate): Promise<PlanMembresia> {
    return await httpClient.post<PlanMembresia>(this.baseUrl + "/", data);
  }

  async update(id: number, data: PlanMembresiaUpdate): Promise<PlanMembresia> {
    return await httpClient.put<PlanMembresia>(`${this.baseUrl}/${id}/`, data);
  }

  async patch(id: number, data: Partial<PlanMembresiaUpdate>): Promise<PlanMembresia> {
    return await httpClient.patch<PlanMembresia>(`${this.baseUrl}/${id}/`, data);
  }

  async delete(id: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/${id}/`);
  }

  /**
   * Obtener todos los planes sin paginación (para dropdowns)
   */
  async getAllPlansSimple(): Promise<PlanMembresia[]> {
    // Obtener la primera página con todos los resultados
    const response = await this.getAll({ page: 1 });
    return response.results;
  }

  /**
   * Obtener planes activos (ordenados por duración)
   */
  async getActivePlans(): Promise<PlanMembresia[]> {
    const response = await this.getAllPlansSimple();
    return response.sort((a, b) => a.duracion - b.duracion);
  }
}

export const planMembresiaService = new PlanMembresiaService();
export default planMembresiaService;
