/**
 * Servicio API para Ventas
 */

import { httpClient } from "@/lib/config/http-client";

export interface DetalleVenta {
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

export interface Venta {
  id: number;
  numero_venta: string;
  fecha_venta: string;
  cliente: number;
  cliente_nombre: string;
  cliente_ci: string;
  cliente_telefono?: string;
  cliente_email?: string;
  metodo_pago: "efectivo" | "tarjeta" | "transferencia" | "qr";
  estado: "pendiente" | "completada" | "cancelada";
  subtotal: string;
  descuento: string;
  total: string;
  observaciones?: string;
  vendedor?: number;
  vendedor_nombre?: string;
  detalles?: DetalleVenta[];
  cantidad_items?: number;
  created_at: string;
  updated_at: string;
}

export interface DetalleVentaCreate {
  producto: number;
  cantidad: number;
  precio_unitario: number;
  descuento?: number;
}

export interface CreateVentaDTO {
  cliente: number;
  metodo_pago: "efectivo" | "tarjeta" | "transferencia" | "qr";
  descuento?: number;
  observaciones?: string;
  detalles: DetalleVentaCreate[];
}

export interface UpdateVentaDTO {
  metodo_pago?: "efectivo" | "tarjeta" | "transferencia" | "qr";
  descuento?: number;
  observaciones?: string;
  estado?: "pendiente" | "completada" | "cancelada";
}

export interface PaginatedVentaResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Venta[];
}

class VentaService {
  private baseUrl = "/api/ventas";

  /**
   * Obtener lista de ventas con paginación y filtros
   */
  async getAll(params?: {
    page?: number;
    search?: string;
    estado?: string;
    metodo_pago?: string;
    cliente?: number;
    fecha_desde?: string;
    fecha_hasta?: string;
  }): Promise<PaginatedVentaResponse> {
    const queryParams = new URLSearchParams();

    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.search) queryParams.append("search", params.search);
    if (params?.estado) queryParams.append("estado", params.estado);
    if (params?.metodo_pago) queryParams.append("metodo_pago", params.metodo_pago);
    if (params?.cliente) queryParams.append("cliente", params.cliente.toString());
    if (params?.fecha_desde) queryParams.append("fecha_desde", params.fecha_desde);
    if (params?.fecha_hasta) queryParams.append("fecha_hasta", params.fecha_hasta);

    const url = `${this.baseUrl}/${queryParams.toString() ? `?${queryParams.toString()}` : ""}`;
    return httpClient.get<PaginatedVentaResponse>(url);
  }

  /**
   * Obtener detalle de una venta
   */
  async getById(id: number): Promise<Venta> {
    return httpClient.get<Venta>(`${this.baseUrl}/${id}/`);
  }

  /**
   * Crear una nueva venta
   */
  async create(data: CreateVentaDTO): Promise<Venta> {
    return httpClient.post<Venta>(`${this.baseUrl}/`, data);
  }

  /**
   * Actualizar una venta
   */
  async update(id: number, data: UpdateVentaDTO): Promise<Venta> {
    return httpClient.patch<Venta>(`${this.baseUrl}/${id}/`, data);
  }

  /**
   * Cancelar una venta
   */
  async cancelar(id: number): Promise<Venta> {
    return httpClient.post<Venta>(`${this.baseUrl}/${id}/cancelar/`, {});
  }

  /**
   * Generar PDF de la venta
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
    link.download = `venta_${id}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }

  /**
   * Obtener estadísticas de ventas
   */
  async getEstadisticas(params?: {
    fecha_desde?: string;
    fecha_hasta?: string;
  }): Promise<{
    total_ventas: number;
    total_ingresos: number;
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

export const ventaService = new VentaService();

