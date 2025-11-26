import { httpClient } from "../config/http-client";

export interface CategoriaProducto {
  id: number;
  nombre: string;
  codigo: string;
  descripcion: string;
  activo: boolean;
  total_productos?: number;
  created_at: string;
  updated_at: string;
}

export interface CategoriaProductoCreate {
  nombre: string;
  codigo: string;
  descripcion?: string;
  activo?: boolean;
}

export interface CategoriaProductoUpdate {
  nombre?: string;
  codigo?: string;
  descripcion?: string;
  activo?: boolean;
}

export interface CategoriaProductoListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: CategoriaProducto[];
}

const categoriaService = {
  /**
   * Obtener listado de categorías con paginación, búsqueda y filtro
   */
  async getCategorias(params?: {
    page?: number;
    search?: string;
    activo?: boolean;
    ordering?: string;
  }): Promise<CategoriaProductoListResponse> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.search) queryParams.append("search", params.search);
    if (params?.activo !== undefined)
      queryParams.append("activo", params.activo.toString());
    if (params?.ordering) queryParams.append("ordering", params.ordering);

    const queryString = queryParams.toString();
    const url = queryString
      ? `/api/categorias-producto/?${queryString}`
      : `/api/categorias-producto/`;

    return httpClient.get<CategoriaProductoListResponse>(url);
  },

  /**
   * Obtener detalle de una categoría
   */
  async getCategoriaById(id: number): Promise<CategoriaProducto> {
    return httpClient.get<CategoriaProducto>(`/api/categorias-producto/${id}/`);
  },

  /**
   * Crear nueva categoría
   */
  async createCategoria(
    data: CategoriaProductoCreate
  ): Promise<CategoriaProducto> {
    return httpClient.post<CategoriaProducto>("/api/categorias-producto/", data);
  },

  /**
   * Actualizar categoría completa (PUT)
   */
  async updateCategoria(
    id: number,
    data: CategoriaProductoCreate
  ): Promise<CategoriaProducto> {
    return httpClient.put<CategoriaProducto>(
      `/api/categorias-producto/${id}/`,
      data
    );
  },

  /**
   * Actualizar categoría parcial (PATCH)
   */
  async patchCategoria(
    id: number,
    data: CategoriaProductoUpdate
  ): Promise<CategoriaProducto> {
    return httpClient.patch<CategoriaProducto>(
      `/api/categorias-producto/${id}/`,
      data
    );
  },

  /**
   * Eliminar categoría
   */
  async deleteCategoria(id: number): Promise<void> {
    await httpClient.delete(`/api/categorias-producto/${id}/`);
  },
};

export default categoriaService;

