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

class PlanMembresiaService {
  private baseUrl = "/api/planes-membresia";

  async getAll(): Promise<PlanMembresia[]> {
    return await httpClient.get<PlanMembresia[]>(this.baseUrl + "/");
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
   * Obtener planes activos (ordenados por duración)
   */
  async getActivePlans(): Promise<PlanMembresia[]> {
    const plans = await this.getAll();
    return plans.sort((a, b) => a.duracion - b.duracion);
  }
}

export const planMembresiaService = new PlanMembresiaService();
export default planMembresiaService;
