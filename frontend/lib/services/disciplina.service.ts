import { httpClient } from "../config/http-client";

export interface Disciplina {
  id: number;
  nombre: string;
  descripcion: string;
  activa: boolean;
  created_at: string;
  updated_at: string;
}

export interface DisciplinaList {
  nombre: string;
  activa: boolean;
}

export interface DisciplinaCreate {
  nombre: string;
  descripcion: string;
  activa?: boolean;
}

export interface DisciplinaUpdate {
  nombre?: string;
  descripcion?: string;
  activa?: boolean;
}

export interface DisciplinaListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Disciplina[];
}

const disciplinaService = {
  /**
   * CU19: Obtener listado de disciplinas con paginación, búsqueda y filtro
   */
  async getDisciplinas(params?: {
    page?: number;
    search?: string;
    activa?: boolean;
  }): Promise<DisciplinaListResponse> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.search) queryParams.append("search", params.search);
    if (params?.activa !== undefined)
      queryParams.append("activa", params.activa.toString());

    return httpClient.get<DisciplinaListResponse>(
      `/api/disciplinas/?${queryParams.toString()}`
    );
  },

  /**
   * CU19: Obtener detalle de una disciplina
   */
  async getDisciplinaById(id: number): Promise<Disciplina> {
    return httpClient.get<Disciplina>(`/api/disciplinas/${id}/`);
  },

  /**
   * CU19: Crear nueva disciplina
   */
  async createDisciplina(data: DisciplinaCreate): Promise<Disciplina> {
    return httpClient.post<Disciplina>("/api/disciplinas/", data);
  },

  /**
   * CU19: Actualizar disciplina completa (PUT)
   */
  async updateDisciplina(
    id: number,
    data: DisciplinaCreate
  ): Promise<Disciplina> {
    return httpClient.put<Disciplina>(`/api/disciplinas/${id}/`, data);
  },

  /**
   * CU19: Actualizar disciplina parcial (PATCH)
   */
  async patchDisciplina(
    id: number,
    data: DisciplinaUpdate
  ): Promise<Disciplina> {
    return httpClient.patch<Disciplina>(`/api/disciplinas/${id}/`, data);
  },

  /**
   * CU19: Eliminar disciplina
   */
  async deleteDisciplina(id: number): Promise<void> {
    await httpClient.delete(`/api/disciplinas/${id}/`);
  },
};

export default disciplinaService;
