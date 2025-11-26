/**
 * Servicio API para Compras (Órdenes de Compra)
 */

import { httpClient } from "@/lib/config/http-client";

export interface ItemOrdenCompra {
  id: number;
  producto: number;
  producto_nombre: string;
  producto_codigo: string;
  cantidad: number;
  precio_unitario: string;
  descuento: string;
  subtotal: string;
  created_at: string;
  updated_at: string;
}

export interface OrdenCompra {
  id: number;
  numero_orden: string;
  fecha_orden: string;
  fecha_esperada?: string;
  proveedor: number;
  proveedor_nombre: string;
  proveedor_nit: string;
  proveedor_telefono?: string;
  proveedor_email?: string;
  proveedor_direccion?: string;
  estado: "pendiente" | "confirmada" | "recibida" | "cancelada";
  subtotal: string;
  descuento: string;
  total: string;
  observaciones?: string;
  creado_por?: number;
  creado_por_nombre?: string;
  items?: ItemOrdenCompra[];
  cantidad_items?: number;
  created_at: string;
  updated_at: string;
}

export interface ItemOrdenCompraCreate {
  producto: number;
  cantidad: number;
  precio_unitario: number;
  descuento?: number;
}

export interface CreateOrdenCompraDTO {
  proveedor: number;
  fecha_esperada?: string;
  descuento?: number;
  observaciones?: string;
  items: ItemOrdenCompraCreate[];
}

export interface UpdateOrdenCompraDTO {
  fecha_esperada?: string;
  descuento?: number;
  observaciones?: string;
  estado?: "pendiente" | "confirmada" | "recibida" | "cancelada";
}

export interface PaginatedOrdenCompraResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: OrdenCompra[];
}

class CompraService {
  private baseUrl = "/api/compras";

  /**
   * Obtener lista de órdenes de compra con paginación y filtros
   */
  async getAll(params?: {
    page?: number;
    search?: string;
    estado?: string;
    proveedor?: number;
    fecha_desde?: string;
    fecha_hasta?: string;
  }): Promise<PaginatedOrdenCompraResponse> {
    const queryParams = new URLSearchParams();

    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.search) queryParams.append("search", params.search);
    if (params?.estado) queryParams.append("estado", params.estado);
    if (params?.proveedor) queryParams.append("proveedor", params.proveedor.toString());
    if (params?.fecha_desde) queryParams.append("fecha_desde", params.fecha_desde);
    if (params?.fecha_hasta) queryParams.append("fecha_hasta", params.fecha_hasta);

    const url = `${this.baseUrl}/${queryParams.toString() ? `?${queryParams.toString()}` : ""}`;
    return httpClient.get<PaginatedOrdenCompraResponse>(url);
  }

  /**
   * Obtener detalle de una orden de compra
   */
  async getById(id: number): Promise<OrdenCompra> {
    return httpClient.get<OrdenCompra>(`${this.baseUrl}/${id}/`);
  }

  /**
   * Crear una nueva orden de compra
   */
  async create(data: CreateOrdenCompraDTO): Promise<OrdenCompra> {
    return httpClient.post<OrdenCompra>(`${this.baseUrl}/`, data);
  }

  /**
   * Actualizar una orden de compra
   */
  async update(id: number, data: UpdateOrdenCompraDTO): Promise<OrdenCompra> {
    return httpClient.patch<OrdenCompra>(`${this.baseUrl}/${id}/`, data);
  }

  /**
   * Confirmar una orden de compra
   */
  async confirmar(id: number): Promise<OrdenCompra> {
    return httpClient.post<OrdenCompra>(`${this.baseUrl}/${id}/confirmar/`, {});
  }

  /**
   * Recibir una orden de compra (actualiza stock)
   */
  async recibir(id: number): Promise<OrdenCompra> {
    return httpClient.post<OrdenCompra>(`${this.baseUrl}/${id}/recibir/`, {});
  }

  /**
   * Cancelar una orden de compra
   */
  async cancelar(id: number): Promise<OrdenCompra> {
    return httpClient.post<OrdenCompra>(`${this.baseUrl}/${id}/cancelar/`, {});
  }

  /**
   * Generar PDF de la orden de compra
   */
  async generarPDF(id: number): Promise<void> {
    if (typeof window === "undefined") return;
    
    const token = localStorage.getItem("access_token");
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const url = apiUrl.startsWith("/") 
      ? `${apiUrl}${this.baseUrl}/${id}/generar_pdf/`
      : `${apiUrl}${this.baseUrl}/${id}/generar_pdf/`;
    
    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Error al generar PDF");
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = `orden_${id}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }

  /**
   * Obtener estadísticas de compras
   */
  async getEstadisticas(params?: {
    fecha_desde?: string;
    fecha_hasta?: string;
  }): Promise<{
    total_ordenes: number;
    total_gastos: number;
    fecha_desde?: string;
    fecha_hasta?: string;
  }> {
    const queryParams = new URLSearchParams();
    if (params?.fecha_desde) queryParams.append("fecha_desde", params.fecha_desde);
    if (params?.fecha_hasta) queryParams.append("fecha_hasta", params.fecha_hasta);

    const url = `${this.baseUrl}/estadisticas/${queryParams.toString() ? `?${queryParams.toString()}` : ""}`;
    return httpClient.get(url);
  }
}

export const compraService = new CompraService();

