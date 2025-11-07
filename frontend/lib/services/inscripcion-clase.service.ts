/**
 * CU21: Inscribir Cliente a Clase
 * Servicio para gestionar inscripciones de clientes a clases programadas
 * 
 * Funcionalidades:
 * - Listar inscripciones con filtros
 * - Crear nueva inscripción (con validaciones)
 * - Actualizar estado de inscripción
 * - Eliminar inscripción
 */

import { httpClient } from '@/lib/config/http-client';
import { API_ENDPOINTS } from '@/lib/config/api';

// ==================== INTERFACES ====================

export interface InscripcionClase {
  id: number;
  clase: number;
  clase_info?: string;
  disciplina_nombre?: string;
  fecha_clase?: string;
  hora_inicio?: string;
  hora_fin?: string;
  cupos_disponibles?: number;
  cliente: number;
  cliente_nombre?: string;
  cliente_ci?: string;
  estado: 'confirmada' | 'cancelada' | 'asistio' | 'no_asistio';
  estado_display?: string;
  fecha_inscripcion: string;
  observaciones?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CreateInscripcionDTO {
  clase: number;
  cliente: number;
  observaciones?: string;
}

export interface UpdateInscripcionDTO {
  estado?: 'confirmada' | 'cancelada' | 'asistio' | 'no_asistio';
  observaciones?: string;
}

export interface InscripcionListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: InscripcionClase[];
}

export interface InscripcionFilters {
  clase?: number;
  cliente?: number;
  estado?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

// ==================== SERVICE CLASS ====================

class InscripcionClaseService {
  private readonly baseUrl = '/api/inscripciones-clase/';

  /**
   * Obtener lista de inscripciones con filtros y paginación
   */
  async getAll(filters?: InscripcionFilters): Promise<InscripcionListResponse> {
    const params = new URLSearchParams();

    if (filters?.clase) params.append('clase', filters.clase.toString());
    if (filters?.cliente) params.append('cliente', filters.cliente.toString());
    if (filters?.estado) params.append('estado', filters.estado);
    if (filters?.fecha_desde) params.append('fecha_desde', filters.fecha_desde);
    if (filters?.fecha_hasta) params.append('fecha_hasta', filters.fecha_hasta);
    if (filters?.search) params.append('search', filters.search);
    if (filters?.page) params.append('page', filters.page.toString());
    if (filters?.page_size) params.append('page_size', filters.page_size.toString());

    const url = `${this.baseUrl}${params.toString() ? '?' + params.toString() : ''}`;
    return httpClient.get<InscripcionListResponse>(url);
  }

  /**
   * Obtener una inscripción por ID
   */
  async getById(id: number): Promise<InscripcionClase> {
    return httpClient.get<InscripcionClase>(`${this.baseUrl}${id}/`);
  }

  /**
   * Crear nueva inscripción
   * CU21: Validaciones en backend:
   * - Cliente debe tener membresía activa
   * - Clase debe tener cupos disponibles
   * - Cliente no puede inscribirse dos veces a la misma clase
   */
  async create(data: CreateInscripcionDTO): Promise<InscripcionClase> {
    return httpClient.post<InscripcionClase>(this.baseUrl, data);
  }

  /**
   * Actualizar inscripción (cambiar estado, observaciones)
   */
  async update(id: number, data: UpdateInscripcionDTO): Promise<InscripcionClase> {
    return httpClient.patch<InscripcionClase>(`${this.baseUrl}${id}/`, data);
  }

  /**
   * Eliminar inscripción
   */
  async delete(id: number): Promise<void> {
    return httpClient.delete<void>(`${this.baseUrl}${id}/`);
  }

  /**
   * Marcar asistencia de un cliente a una clase
   */
  async marcarAsistencia(id: number, asistio: boolean): Promise<InscripcionClase> {
    return this.update(id, {
      estado: asistio ? 'asistio' : 'no_asistio'
    });
  }

  /**
   * Cancelar inscripción
   */
  async cancelar(id: number, observaciones?: string): Promise<InscripcionClase> {
    return this.update(id, {
      estado: 'cancelada',
      observaciones
    });
  }

  /**
   * Obtener inscripciones de un cliente específico
   */
  async getByCliente(clienteId: number): Promise<InscripcionClase[]> {
    const response = await this.getAll({ 
      cliente: clienteId,
      page_size: 1000 
    });
    return response.results;
  }

  /**
   * Obtener inscripciones de una clase específica
   */
  async getByClase(claseId: number): Promise<InscripcionClase[]> {
    const response = await this.getAll({ 
      clase: claseId,
      page_size: 1000 
    });
    return response.results;
  }

  /**
   * Verificar si un cliente está inscrito en una clase
   */
  async isClienteInscrito(claseId: number, clienteId: number): Promise<boolean> {
    try {
      const response = await this.getAll({ 
        clase: claseId,
        cliente: clienteId,
        page_size: 1
      });
      return response.results.length > 0 && 
             response.results[0].estado !== 'cancelada';
    } catch (error) {
      console.error('Error verificando inscripción:', error);
      return false;
    }
  }
}

// ==================== EXPORT ====================

export const inscripcionClaseService = new InscripcionClaseService();
export default inscripcionClaseService;
