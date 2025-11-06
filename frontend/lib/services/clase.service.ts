import { httpClient } from '@/lib/config/http-client';

export interface Salon {
  id: number;
  nombre: string;
  capacidad: number;
  descripcion?: string;
  activo: boolean;
}

export interface Clase {
  id: number;
  disciplina: number;
  disciplina_nombre?: string;
  instructor: number;
  instructor_nombre?: string;
  salon: number;
  salon_nombre?: string;
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  cupo_maximo: number;
  cupos_disponibles?: number;
  esta_llena?: boolean;
  estado: 'programada' | 'en_progreso' | 'completada' | 'cancelada';
  estado_display?: string;
  observaciones?: string;
  created_at?: string;
  updated_at?: string;
}

export interface InscripcionClase {
  id: number;
  clase: number;
  cliente: number;
  cliente_nombre?: string;
  estado: 'confirmada' | 'en_lista_espera' | 'cancelada';
  fecha_inscripcion: string;
}

export interface ClaseFormData {
  disciplina: number;
  instructor: number;
  salon: number;
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  cupo_maximo: number;
  estado?: 'programada' | 'en_progreso' | 'completada' | 'cancelada';
  observaciones?: string;
}

export interface SalonFormData {
  nombre: string;
  capacidad: number;
  descripcion?: string;
  activo?: boolean;
}

export interface InscripcionFormData {
  clase: number;
  cliente: number;
  estado?: 'confirmada' | 'en_lista_espera' | 'cancelada';
}

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Servicios para Salones
export const getSalones = async (
  page = 1,
  search = '',
  activo?: boolean
): Promise<PaginatedResponse<Salon>> => {
  const params = new URLSearchParams({
    page: page.toString(),
  });

  if (search) params.append('search', search);
  if (activo !== undefined) params.append('activo', activo.toString());

  return httpClient.get<PaginatedResponse<Salon>>(`/api/salones/?${params.toString()}`);
};

export const getSalonById = async (id: number): Promise<Salon> => {
  return httpClient.get<Salon>(`/api/salones/${id}/`);
};

export const createSalon = async (data: SalonFormData): Promise<Salon> => {
  return httpClient.post<Salon>('/api/salones/', data);
};

export const updateSalon = async (id: number, data: SalonFormData): Promise<Salon> => {
  return httpClient.put<Salon>(`/api/salones/${id}/`, data);
};

export const deleteSalon = async (id: number): Promise<void> => {
  await httpClient.delete(`/api/salones/${id}/`);
};

// Servicios para Clases
export const getClases = async (
  page = 1,
  search = '',
  estado?: string,
  fecha?: string,
  disciplina?: number,
  instructor?: number
): Promise<PaginatedResponse<Clase>> => {
  const params = new URLSearchParams({
    page: page.toString(),
  });

  if (search) params.append('search', search);
  if (estado) params.append('estado', estado);
  if (fecha) params.append('fecha', fecha);
  if (disciplina) params.append('disciplina', disciplina.toString());
  if (instructor) params.append('instructor', instructor.toString());

  return httpClient.get<PaginatedResponse<Clase>>(`/api/clases/?${params.toString()}`);
};

export const getClaseById = async (id: number): Promise<Clase> => {
  return httpClient.get<Clase>(`/api/clases/${id}/`);
};

export const createClase = async (data: ClaseFormData): Promise<Clase> => {
  return httpClient.post<Clase>('/api/clases/', data);
};

export const updateClase = async (id: number, data: ClaseFormData): Promise<Clase> => {
  return httpClient.put<Clase>(`/api/clases/${id}/`, data);
};

export const deleteClase = async (id: number): Promise<void> => {
  await httpClient.delete(`/api/clases/${id}/`);
};

// Servicios para Inscripciones a Clases
export const getInscripciones = async (
  page = 1,
  clase?: number,
  cliente?: number,
  estado?: string
): Promise<PaginatedResponse<InscripcionClase>> => {
  const params = new URLSearchParams({
    page: page.toString(),
  });

  if (clase) params.append('clase', clase.toString());
  if (cliente) params.append('cliente', cliente.toString());
  if (estado) params.append('estado', estado);

  return httpClient.get<PaginatedResponse<InscripcionClase>>(`/api/inscripciones-clase/?${params.toString()}`);
};

export const getInscripcionById = async (id: number): Promise<InscripcionClase> => {
  return httpClient.get<InscripcionClase>(`/api/inscripciones-clase/${id}/`);
};

export const createInscripcion = async (data: InscripcionFormData): Promise<InscripcionClase> => {
  return httpClient.post<InscripcionClase>('/api/inscripciones-clase/', data);
};

export const updateInscripcion = async (
  id: number,
  data: InscripcionFormData
): Promise<InscripcionClase> => {
  return httpClient.put<InscripcionClase>(`/api/inscripciones-clase/${id}/`, data);
};

export const deleteInscripcion = async (id: number): Promise<void> => {
  await httpClient.delete(`/api/inscripciones-clase/${id}/`);
};
