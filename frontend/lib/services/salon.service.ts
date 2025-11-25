/**
 * Servicio para gestión de Salones del Gimnasio
 * Los salones son espacios físicos donde se realizan las clases
 * Cada salón tiene una capacidad máxima que determina el cupo de las clases
 */

import { httpClient } from '@/lib/config/http-client';

// ==================== INTERFACES ====================

export interface Salon {
  id: number;
  nombre: string;
  capacidad: number;
  descripcion?: string;
  activo: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CreateSalonDTO {
  nombre: string;
  capacidad: number;
  descripcion?: string;
  activo?: boolean;
}

export interface UpdateSalonDTO extends Partial<CreateSalonDTO> {}

export interface SalonListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Salon[];
}

export interface SalonFilters {
  activo?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
}

// ==================== SERVICE CLASS ====================

class SalonService {
  private readonly baseUrl = '/api/salones/';

  /**
   * Obtener lista de salones con filtros y paginación
   */
  async getAll(filters?: SalonFilters): Promise<SalonListResponse> {
    const params = new URLSearchParams();

    if (filters?.activo !== undefined) {
      params.append('activo', filters.activo.toString());
    }
    if (filters?.search) params.append('search', filters.search);
    if (filters?.page) params.append('page', filters.page.toString());
    if (filters?.page_size) params.append('page_size', filters.page_size.toString());

    const url = `${this.baseUrl}${params.toString() ? '?' + params.toString() : ''}`;
    return httpClient.get<SalonListResponse>(url);
  }

  /**
   * Obtener un salón por ID
   */
  async getById(id: number): Promise<Salon> {
    return httpClient.get<Salon>(`${this.baseUrl}${id}/`);
  }

  /**
   * Crear un nuevo salón
   */
  async create(data: CreateSalonDTO): Promise<Salon> {
    return httpClient.post<Salon>(this.baseUrl, data);
  }

  /**
   * Actualizar un salón completamente
   */
  async update(id: number, data: CreateSalonDTO): Promise<Salon> {
    return httpClient.put<Salon>(`${this.baseUrl}${id}/`, data);
  }

  /**
   * Actualizar parcialmente un salón
   */
  async partialUpdate(id: number, data: UpdateSalonDTO): Promise<Salon> {
    return httpClient.patch<Salon>(`${this.baseUrl}${id}/`, data);
  }

  /**
   * Eliminar un salón
   */
  async delete(id: number): Promise<void> {
    return httpClient.delete<void>(`${this.baseUrl}${id}/`);
  }

  /**
   * Obtener todos los salones activos (sin paginación) para dropdowns
   */
  async getSalonesActivos(): Promise<Salon[]> {
    try {
      const response = await this.getAll({ 
        activo: true,
        page_size: 1000 
      });
      return response.results || [];
    } catch (error) {
      console.error('Error obteniendo salones activos:', error);
      return [];
    }
  }

  /**
   * Activar/Desactivar un salón
   */
  async toggleActivo(id: number, activo: boolean): Promise<Salon> {
    return this.partialUpdate(id, { activo });
  }

  /**
   * Verificar si un nombre de salón ya existe
   */
  async existeNombre(nombre: string, excludeId?: number): Promise<boolean> {
    try {
      const response = await this.getAll({ 
        search: nombre,
        page_size: 100
      });
      
      const salones = response.results.filter(s => 
        s.nombre.toLowerCase() === nombre.toLowerCase() &&
        (!excludeId || s.id !== excludeId)
      );
      
      return salones.length > 0;
    } catch (error) {
      console.error('Error verificando nombre:', error);
      return false;
    }
  }
}

// ==================== EXPORT ====================

export const salonService = new SalonService();
export default salonService;
