/**
 * Servicio para gestionar asistencias a clases
 * CU22: Control de asistencias
 */

import { httpClient } from "../config/http-client";
import { BaseFilters, PaginatedResponse } from "../types";

// ================== INTERFACES ==================

export interface AsistenciaClase {
  id: number;
  inscripcion: number;
  clase: number;
  cliente: number;
  cliente_nombre: string;
  estado: "presente" | "ausente" | "justificado" | "tardanza";
  estado_display: string;
  fecha_registro: string;
  hora_llegada?: string;
  observaciones?: string;
  registrado_por: number;
  registrado_por_nombre: string;
  clase_info: {
    id: number;
    disciplina: string;
    fecha: string;
    hora_inicio: string;
    hora_fin: string;
    salon: string;
  };
  es_tardia: boolean;
  minutos_retraso?: number;
  created_at: string;
  updated_at: string;
}

export interface AsistenciaClaseList {
  id: number;
  cliente: number;
  cliente_nombre: string;
  cliente_ci: string;
  estado: string;
  estado_display: string;
  hora_llegada?: string;
  fecha_registro: string;
  disciplina: string;
  es_tardia: boolean;
  observaciones?: string;
}

export interface RegistrarAsistenciaDTO {
  inscripcion_id: number;
  estado: "presente" | "ausente" | "justificado" | "tardanza";
  hora_llegada?: string;
  observaciones?: string;
}

export interface RegistrarAsistenciasMasivasDTO {
  clase_id: number;
  asistencias: Array<{
    inscripcion_id: number;
    estado: "presente" | "ausente" | "justificado" | "tardanza";
    hora_llegada?: string;
    observaciones?: string;
  }>;
}

export interface InscritoClase {
  inscripcion_id: number;
  cliente_id: number;
  cliente_nombre: string;
  cliente_ci: string;
  tiene_asistencia: boolean;
  asistencia_id?: number;
  estado?: string;
  estado_display?: string;
  hora_llegada?: string;
  es_tardia: boolean;
  observaciones?: string;
}

export interface InscritosClaseResponse {
  clase_id: number;
  clase_info: {
    disciplina: string;
    fecha: string;
    hora_inicio: string;
    hora_fin: string;
    salon: string;
  };
  total_inscritos: number;
  con_asistencia: number;
  inscritos: InscritoClase[];
}

export interface EstadisticasClase {
  clase_id: number;
  disciplina: string;
  fecha: string;
  total_inscritos: number;
  total_registros: number;
  presentes: number;
  ausentes: number;
  justificados: number;
  tardanzas: number;
  porcentaje_asistencia: number;
  sin_registrar: number;
}

export interface EstadisticasCliente {
  cliente_id: number;
  cliente_nombre: string;
  periodo: {
    desde: string;
    hasta: string;
  };
  total_inscripciones: number;
  total_asistencias_registradas: number;
  presentes: number;
  ausentes: number;
  justificados: number;
  tardanzas: number;
  porcentaje_asistencia: number;
}

export interface AsistenciaFilters extends BaseFilters {
  clase_id?: number;
  cliente_id?: number;
  estado?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
}

// ================== SERVICIO ==================

class AsistenciaService {
  private readonly baseUrl = "/api/asistencias";

  /**
   * Obtener lista de asistencias con filtros
   */
  async getAsistencias(
    page: number = 1,
    filters?: AsistenciaFilters
  ): Promise<PaginatedResponse<AsistenciaClaseList>> {
    const params = new URLSearchParams();
    params.append("page", page.toString());

    if (filters?.clase_id) params.append("clase_id", filters.clase_id.toString());
    if (filters?.cliente_id) params.append("cliente_id", filters.cliente_id.toString());
    if (filters?.estado) params.append("estado", filters.estado);
    if (filters?.fecha_desde) params.append("fecha_desde", filters.fecha_desde);
    if (filters?.fecha_hasta) params.append("fecha_hasta", filters.fecha_hasta);
    if (filters?.search) params.append("search", filters.search);
    if (filters?.ordering) params.append("ordering", filters.ordering);

    const url = `${this.baseUrl}/?${params.toString()}`;
    return httpClient.get<PaginatedResponse<AsistenciaClaseList>>(url);
  }

  /**
   * Obtener asistencia por ID
   */
  async getById(id: number): Promise<AsistenciaClase> {
    return httpClient.get<AsistenciaClase>(`${this.baseUrl}/${id}/`);
  }

  /**
   * Registrar asistencia individual
   */
  async registrarAsistencia(data: RegistrarAsistenciaDTO): Promise<AsistenciaClase> {
    return httpClient.post<AsistenciaClase>(`${this.baseUrl}/registrar/`, data);
  }

  /**
   * Registrar asistencias masivas
   */
  async registrarAsistenciasMasivas(
    data: RegistrarAsistenciasMasivasDTO
  ): Promise<{
    message: string;
    creadas: number;
    errores: string[];
    asistencias: AsistenciaClaseList[];
  }> {
    return httpClient.post(`${this.baseUrl}/registrar-masivo/`, data);
  }

  /**
   * Actualizar asistencia
   */
  async update(
    id: number,
    data: Partial<RegistrarAsistenciaDTO>
  ): Promise<AsistenciaClase> {
    return httpClient.patch<AsistenciaClase>(`${this.baseUrl}/${id}/`, data);
  }

  /**
   * Eliminar asistencia
   */
  async delete(id: number): Promise<void> {
    return httpClient.delete(`${this.baseUrl}/${id}/`);
  }

  /**
   * Obtener lista de inscritos a una clase para tomar asistencia
   */
  async getInscritosClase(claseId: number): Promise<InscritosClaseResponse> {
    return httpClient.get<InscritosClaseResponse>(
      `${this.baseUrl}/inscritos/${claseId}/`
    );
  }

  /**
   * Obtener estadísticas de asistencia de una clase
   */
  async getEstadisticasClase(claseId: number): Promise<EstadisticasClase> {
    return httpClient.get<EstadisticasClase>(
      `${this.baseUrl}/estadisticas/clase/${claseId}/`
    );
  }

  /**
   * Obtener estadísticas de asistencia de un cliente
   */
  async getEstadisticasCliente(
    clienteId: number,
    fechaDesde?: string,
    fechaHasta?: string
  ): Promise<EstadisticasCliente> {
    let url = `${this.baseUrl}/estadisticas/cliente/${clienteId}/`;

    if (fechaDesde || fechaHasta) {
      const params = new URLSearchParams();
      if (fechaDesde) params.append("fecha_desde", fechaDesde);
      if (fechaHasta) params.append("fecha_hasta", fechaHasta);
      url += `?${params.toString()}`;
    }

    return httpClient.get<EstadisticasCliente>(url);
  }
}

// Exportar instancia única (Singleton)
const asistenciaService = new AsistenciaService();
export default asistenciaService;
