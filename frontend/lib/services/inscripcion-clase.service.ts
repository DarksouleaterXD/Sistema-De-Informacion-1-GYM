/**
 * Servicio para gestión de inscripciones a clases
 * CU21: Inscribir Cliente a Clase
 */

import { httpClient } from "../config/http-client";

export interface InscripcionClase {
  id: number;
  clase: number;
  clase_info: string;
  disciplina_nombre: string;
  instructor_nombre: string;
  fecha_clase: string;
  hora_clase: string;
  cliente: number;
  cliente_nombre: string;
  cliente_ci: string;
  estado: string;
  estado_display: string;
  fecha_inscripcion: string;
  observaciones?: string;
  created_at: string;
  updated_at: string;
}

export interface InscripcionClaseList {
  id: number;
  cliente_nombre: string;
  cliente_ci: string;
  disciplina: string;
  fecha_clase: string;
  hora_inicio: string;
  instructor: string;
  estado: string;
  estado_display: string;
  fecha_inscripcion: string;
}

export interface CreateInscripcionClaseData {
  clase: number;
  cliente: number;
  observaciones?: string;
}

export interface UpdateInscripcionClaseData {
  estado?: string;
  observaciones?: string;
}

/**
 * Obtener todas las inscripciones a clases con filtros opcionales
 */
export const getInscripcionesClase = async (params?: {
  clase?: number;
  cliente?: number;
  estado?: string;
}): Promise<InscripcionClase[]> => {
  let url = "/api/inscripciones-clase/";
  
  if (params) {
    const searchParams = new URLSearchParams();
    if (params.clase) searchParams.append("clase", params.clase.toString());
    if (params.cliente) searchParams.append("cliente", params.cliente.toString());
    if (params.estado) searchParams.append("estado", params.estado);
    
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }
  
  return await httpClient.get<InscripcionClase[]>(url);
};

/**
 * Obtener detalle de una inscripción
 */
export const getInscripcionClaseById = async (
  id: number
): Promise<InscripcionClase> => {
  return await httpClient.get<InscripcionClase>(
    `/api/inscripciones-clase/${id}/`
  );
};

/**
 * Crear nueva inscripción a clase
 * Valida: cupo disponible y membresía activa
 */
export const createInscripcionClase = async (
  data: CreateInscripcionClaseData
): Promise<InscripcionClase> => {
  return await httpClient.post<InscripcionClase>(
    "/api/inscripciones-clase/",
    data
  );
};

/**
 * Actualizar inscripción (cambiar estado)
 */
export const updateInscripcionClase = async (
  id: number,
  data: UpdateInscripcionClaseData
): Promise<InscripcionClase> => {
  return await httpClient.patch<InscripcionClase>(
    `/api/inscripciones-clase/${id}/`,
    data
  );
};

/**
 * Eliminar/Cancelar inscripción
 */
export const deleteInscripcionClase = async (id: number): Promise<void> => {
  await httpClient.delete(`/api/inscripciones-clase/${id}/`);
};

const inscripcionClaseService = {
  getInscripcionesClase,
  getInscripcionClaseById,
  createInscripcionClase,
  updateInscripcionClase,
  deleteInscripcionClase,
};

export default inscripcionClaseService;
