import { httpClient } from "../config/http-client";
import { API_ENDPOINTS } from "../config/api";
import { Client, ExperienciaCliente } from "../types";

export interface CreateClientDTO {
  nombre: string;
  apellido: string;
  ci: string;
  telefono?: string;
  email?: string;
  peso?: string | number; // Nuevo campo
  altura?: string | number; // Nuevo campo
  experiencia?: ExperienciaCliente; // Nuevo campo
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
    con_membresia_activa?: boolean;
  }): Promise<ClientListResponse> {
    const queryParams = new URLSearchParams();

    if (params?.search) queryParams.append("search", params.search);
    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.page_size)
      queryParams.append("page_size", params.page_size.toString());
    if (params?.con_membresia_activa)
      queryParams.append("con_membresia_activa", "true");

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

  /**
   * Obtener todos los clientes (sin paginación) para dropdowns/selects
   */
  async getClients(): Promise<Client[]> {
    try {
      const response = await this.getAll({ page_size: 1000 });
      return response.results || [];
    } catch (error) {
      console.error('Error obteniendo clientes:', error);
      return [];
    }
  }

  /**
   * Obtener clientes con membresía activa (para inscripciones)
   */
  async getClientesConMembresia(): Promise<Client[]> {
    try {
      const response = await this.getAll({ 
        page_size: 1000,
        con_membresia_activa: true 
      });
      return response.results || [];
    } catch (error) {
      console.error('Error obteniendo clientes con membresía:', error);
      return [];
    }
  }
}

export const clientService = new ClientService();
export default clientService;
