import { httpClient } from "../config/http-client";
import { API_ENDPOINTS } from "../config/api";
import { Client } from "../types";

export interface CreateClientDTO {
  nombre: string;
  apellido: string;
  ci: string;
  telefono?: string;
  email?: string;
}

export interface UpdateClientDTO extends Partial<CreateClientDTO> {}

export interface ClientListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Client[];
}

class ClientService {
  /**
   * Obtener lista de clientes con paginación y búsqueda
   */
  async getAll(params?: {
    search?: string;
    page?: number;
    page_size?: number;
  }): Promise<ClientListResponse> {
    const queryParams = new URLSearchParams();

    if (params?.search) queryParams.append("search", params.search);
    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.page_size)
      queryParams.append("page_size", params.page_size.toString());

    const url = `${API_ENDPOINTS.CLIENTS.BASE}${
      queryParams.toString() ? "?" + queryParams.toString() : ""
    }`;
    return httpClient.get<ClientListResponse>(url);
  }

  /**
   * Obtener un cliente por ID
   */
  async getById(id: number): Promise<Client> {
    return httpClient.get<Client>(API_ENDPOINTS.CLIENTS.DETAIL(id));
  }

  /**
   * Crear un nuevo cliente
   */
  async create(data: CreateClientDTO): Promise<Client> {
    return httpClient.post<Client>(API_ENDPOINTS.CLIENTS.BASE, data);
  }

  /**
   * Actualizar un cliente completamente
   */
  async update(id: number, data: CreateClientDTO): Promise<Client> {
    return httpClient.put<Client>(API_ENDPOINTS.CLIENTS.DETAIL(id), data);
  }

  /**
   * Actualizar parcialmente un cliente
   */
  async partialUpdate(id: number, data: UpdateClientDTO): Promise<Client> {
    return httpClient.patch<Client>(API_ENDPOINTS.CLIENTS.DETAIL(id), data);
  }

  /**
   * Eliminar un cliente
   */
  async delete(id: number): Promise<void> {
    return httpClient.delete<void>(API_ENDPOINTS.CLIENTS.DETAIL(id));
  }
}

export const clientService = new ClientService();
