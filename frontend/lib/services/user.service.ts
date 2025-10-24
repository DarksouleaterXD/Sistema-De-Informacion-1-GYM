import { httpClient } from "../config/http-client";

export interface Role {
  id: number;
  nombre: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined: string;
  roles: Role[];
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  roles?: number[];
}

export interface UserUpdate {
  first_name?: string;
  last_name?: string;
  is_active?: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
  roles?: number[];
  change_password?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

class UserService {
  private baseURL = "/api/users";

  /**
   * Obtener lista de usuarios con paginación
   */
  async getAll(params?: {
    page?: number;
    search?: string;
    is_active?: boolean;
  }): Promise<PaginatedResponse<User>> {
    const queryParams = new URLSearchParams();

    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.search) queryParams.append("search", params.search);
    if (params?.is_active !== undefined)
      queryParams.append("is_active", params.is_active.toString());

    const url = `${this.baseURL}/${
      queryParams.toString() ? `?${queryParams.toString()}` : ""
    }`;

    return httpClient.get<PaginatedResponse<User>>(url);
  }

  /**
   * Obtener detalle de un usuario
   */
  async getById(id: number): Promise<User> {
    return httpClient.get<User>(`${this.baseURL}/${id}/`);
  }

  /**
   * Crear un nuevo usuario
   */
  async create(data: UserCreate): Promise<User> {
    return httpClient.post<User>(this.baseURL + "/", data);
  }

  /**
   * Actualizar un usuario completo
   */
  async update(id: number, data: UserUpdate): Promise<User> {
    return httpClient.put<User>(`${this.baseURL}/${id}/`, data);
  }

  /**
   * Actualizar parcialmente un usuario
   */
  async patch(id: number, data: UserUpdate): Promise<User> {
    return httpClient.patch<User>(`${this.baseURL}/${id}/`, data);
  }

  /**
   * Eliminar un usuario
   */
  async delete(id: number): Promise<void> {
    return httpClient.delete(`${this.baseURL}/${id}/`);
  }
}

export const userService = new UserService();
export default userService;
