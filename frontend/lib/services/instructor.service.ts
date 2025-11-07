/**
 * Servicio para gestionar instructores
 */

import { httpClient } from "../config/http-client";
import { BaseFilters, PaginatedResponse } from "../types";

export interface Instructor {
  id: number;
  usuario: number;
  usuario_info: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    is_active: boolean;
  };
  nombre_completo: string;
  email: string;
  especialidades: string;
  certificaciones?: string;
  experiencia_anos: number;
  telefono?: string;
  telefono_emergencia?: string;
  biografia?: string;
  foto_url?: string;
  activo: boolean;
  fecha_ingreso?: string;
  clases_count?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateInstructorDTO {
  usuario_id: number;
  especialidades: string;
  certificaciones?: string;
  experiencia_anos: number;
  telefono?: string;
  telefono_emergencia?: string;
  biografia?: string;
  foto_url?: string;
  activo?: boolean;
  fecha_ingreso?: string;
}

export interface UpdateInstructorDTO {
  especialidades?: string;
  certificaciones?: string;
  experiencia_anos?: number;
  telefono?: string;
  telefono_emergencia?: string;
  biografia?: string;
  foto_url?: string;
  activo?: boolean;
  fecha_ingreso?: string;
}

export interface InstructorFilters extends BaseFilters {
  activo?: boolean;
  experiencia_anos?: number;
}

class InstructorService {
  private readonly baseUrl = "/api/instructores";

  /**
   * Obtiene la lista de instructores
   */
  async getAll(
    filters?: InstructorFilters
  ): Promise<PaginatedResponse<Instructor>> {
    const params = new URLSearchParams();

    if (filters) {
      if (filters.page) params.append("page", filters.page.toString());
      if (filters.page_size)
        params.append("page_size", filters.page_size.toString());
      if (filters.search) params.append("search", filters.search);
      if (filters.ordering) params.append("ordering", filters.ordering);
      if (filters.activo !== undefined)
        params.append("activo", filters.activo.toString());
      if (filters.experiencia_anos)
        params.append("experiencia_anos", filters.experiencia_anos.toString());
    }

    const queryString = params.toString();
    const url = queryString
      ? `${this.baseUrl}/?${queryString}`
      : `${this.baseUrl}/`;

    return httpClient.get<PaginatedResponse<Instructor>>(url);
  }

  /**
   * Obtiene un instructor por ID
   */
  async getById(id: number): Promise<Instructor> {
    return httpClient.get<Instructor>(`${this.baseUrl}/${id}/`);
  }

  /**
   * Crea un nuevo instructor
   */
  async create(data: CreateInstructorDTO): Promise<Instructor> {
    return httpClient.post<Instructor>(`${this.baseUrl}/`, data);
  }

  /**
   * Actualiza un instructor
   */
  async update(id: number, data: UpdateInstructorDTO): Promise<Instructor> {
    return httpClient.patch<Instructor>(`${this.baseUrl}/${id}/`, data);
  }

  /**
   * Elimina (desactiva) un instructor
   */
  async delete(id: number): Promise<void> {
    return httpClient.delete<void>(`${this.baseUrl}/${id}/`);
  }

  /**
   * Activa un instructor desactivado
   */
  async activate(id: number): Promise<Instructor> {
    return httpClient.post<Instructor>(`${this.baseUrl}/${id}/activar/`);
  }

  /**
   * Obtiene las clases de un instructor
   */
  async getClases(id: number): Promise<any[]> {
    return httpClient.get<any[]>(`${this.baseUrl}/${id}/clases/`);
  }
}

export const instructorService = new InstructorService();
