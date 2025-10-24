// lib/services/role.service.ts
import { httpClient } from "../config/http-client";

export interface Permiso {
  id: number;
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
}

export interface RoleUpdate {
  nombre?: string;
  descripcion?: string;
}

class RoleService {
  private baseUrl = "/api/roles";

  async getAll(): Promise<Role[]> {
    return await httpClient.get<Role[]>(this.baseUrl + "/");
  }

  async getById(id: number): Promise<Role> {
    return await httpClient.get<Role>(`${this.baseUrl}/${id}/`);
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
