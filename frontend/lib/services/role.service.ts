// lib/services/role.service.ts
import { httpClient } from "../config/http-client";

export interface Permiso {
  id: number;
  codigo: string;
  nombre: string;
  descripcion?: string;
}

export interface Role {
  id: number;
  nombre: string;
  descripcion?: string;
  created_at: string;
  permisos: Permiso[];
  usuarios_count: number;
}

export interface RoleCreate {
  nombre: string;
  descripcion?: string;
  permisos_ids?: number[];
}

export interface RoleUpdate {
  nombre?: string;
  descripcion?: string;
  permisos_ids?: number[];
}

class RoleService {
  private baseUrl = "/api/roles";
  private permisosUrl = "/api/permissions";

  async getAll(): Promise<Role[]> {
    // Handle paginated response from backend
    const response = await httpClient.get<{
      count: number;
      next: string | null;
      previous: string | null;
      results: Role[];
    }>(this.baseUrl + "/?page_size=100");
    
    return response.results || [];
  }

  async getById(id: number): Promise<Role> {
    return await httpClient.get<Role>(`${this.baseUrl}/${id}/`);
  }

  async getAllPermisos(): Promise<Permiso[]> {
    // Handle paginated response from backend
    const response = await httpClient.get<{
      count: number;
      next: string | null;
      previous: string | null;
      results: Permiso[];
    }>(this.permisosUrl + "/?page_size=100");
    
    return response.results || [];
  }

  async create(data: RoleCreate): Promise<Role> {
    return await httpClient.post<Role>(this.baseUrl + "/", data);
  }

  async update(id: number, data: RoleUpdate): Promise<Role> {
    return await httpClient.put<Role>(`${this.baseUrl}/${id}/`, data);
  }

  async patch(id: number, data: Partial<RoleUpdate>): Promise<Role> {
    return await httpClient.patch<Role>(`${this.baseUrl}/${id}/`, data);
  }

  async delete(id: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/${id}/`);
  }
}

export const roleService = new RoleService();
