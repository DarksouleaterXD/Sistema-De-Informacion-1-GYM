/**
 * Servicio API para Proveedores (CU29)
 */

import { httpClient } from "@/lib/config/http-client";

export interface Proveedor {
  id: number;
  razon_social: string;
  nit: string;
  telefono: string;
  email: string;
  direccion: string;
  contacto_nombre: string;
  notas: string;
  estado: "A" | "I" | "S";
  estado_display: string;
  esta_activo: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateProveedorDTO {
  razon_social: string;
  nit: string;
  telefono?: string;
  email?: string;
  direccion?: string;
  contacto_nombre?: string;
  notas?: string;
}

export interface UpdateProveedorDTO {
  razon_social?: string;
  telefono?: string;
  email?: string;
  direccion?: string;
  contacto_nombre?: string;
  notas?: string;
  estado?: "A" | "I" | "S";
}

export interface GetProveedoresParams {
  search?: string;
  estado?: string;
  page?: number;
  page_size?: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

class ProveedorService {
  private baseUrl = "/api/proveedores";

  /**
   * Obtener todos los proveedores con filtros
   */
  async getAll(params?: GetProveedoresParams): Promise<PaginatedResponse<Proveedor>> {
    // Construir query params
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.append("search", params.search);
    if (params?.estado) queryParams.append("estado", params.estado);
    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.page_size) queryParams.append("page_size", params.page_size.toString());

    const queryString = queryParams.toString();
    const url = queryString ? `${this.baseUrl}/?${queryString}` : `${this.baseUrl}/`;
    
    return await httpClient.get<PaginatedResponse<Proveedor>>(url);
  }

  /**
   * Obtener un proveedor por ID
   */
  async getById(id: number): Promise<Proveedor> {
    return await httpClient.get<Proveedor>(`${this.baseUrl}/${id}/`);
  }

  /**
   * Crear un nuevo proveedor (CU29)
   */
  async create(data: CreateProveedorDTO): Promise<Proveedor> {
    return await httpClient.post<Proveedor>(`${this.baseUrl}/`, data);
  }

  /**
   * Actualizar un proveedor
   */
  async update(id: number, data: UpdateProveedorDTO): Promise<Proveedor> {
    return await httpClient.patch<Proveedor>(`${this.baseUrl}/${id}/`, data);
  }

  /**
   * Desactivar un proveedor (soft delete)
   */
  async deactivate(id: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/${id}/`);
  }

  /**
   * Eliminar permanentemente un proveedor (hard delete)
   */
  async deletePermanent(id: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/${id}/?permanent=true`);
  }

  /**
   * Activar un proveedor inactivo
   */
  async activate(id: number): Promise<Proveedor> {
    return await httpClient.post<Proveedor>(`${this.baseUrl}/${id}/activate/`, {});
  }
}

export const proveedorService = new ProveedorService();
