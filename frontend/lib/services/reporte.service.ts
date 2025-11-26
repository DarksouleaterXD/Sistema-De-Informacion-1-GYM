/**
 * Servicio para gestión de reportes
 */
import { httpClient } from "../config/http-client";

export type TipoPeriodo = "dia" | "semana" | "mes" | "anio" | "personalizado";
export type TipoReporte =
  | "ventas"
  | "compras"
  | "inventario"
  | "membresias"
  | "financiero";
export type FormatoReporte = "json" | "pdf";

export interface FiltroReporte {
  tipo_periodo?: TipoPeriodo;
  fecha_inicio?: string;
  fecha_fin?: string;
  formato?: FormatoReporte;
}

export interface ReporteVentas {
  total_ventas: number;
  cantidad_ventas: number;
  ventas_por_metodo_pago: Record<string, { total: number; cantidad: number }>;
  ventas_por_dia: Array<{ fecha: string; total: number; cantidad: number }>;
  productos_mas_vendidos: Array<{
    producto: string;
    codigo: string;
    cantidad: number;
    total: number;
  }>;
  clientes_mas_frecuentes: Array<{
    cliente: string;
    ci: string;
    cantidad_compras: number;
    total_gastado: number;
  }>;
  periodo: {
    fecha_inicio: string;
    fecha_fin: string;
  };
}

export interface ReporteCompras {
  total_compras: number;
  cantidad_ordenes: number;
  compras_por_proveedor: Array<{
    proveedor: string;
    nit: string;
    cantidad_ordenes: number;
    total_comprado: number;
  }>;
  compras_por_dia: Array<{ fecha: string; total: number; cantidad: number }>;
  productos_mas_comprados: Array<{
    producto: string;
    codigo: string;
    cantidad: number;
    total: number;
  }>;
  periodo: {
    fecha_inicio: string;
    fecha_fin: string;
  };
}

export interface ReporteInventario {
  total_productos: number;
  productos_activos: number;
  productos_agotados: number;
  productos_bajo_stock: number;
  productos_vencidos: number;
  productos_proximos_vencer: number;
  valor_total_inventario: number;
  movimientos_recientes: Array<{
    id: number;
    producto: string;
    codigo: string;
    tipo: string;
    cantidad: number;
    usuario: string;
    fecha: string;
    motivo: string;
  }>;
  productos: Array<{
    nombre: string;
    codigo: string;
    categoria: string;
    stock: number;
    stock_minimo: number;
    precio: number;
    estado: string;
    unidad_medida: string;
  }>;
}

export interface ReporteMembresias {
  total_membresias: number;
  membresias_activas: number;
  membresias_vencidas: number;
  nuevas_membresias: number;
  renovaciones: number;
  ingresos_membresias: number;
  membresias_por_plan: Array<{ plan: string; cantidad: number }>;
  periodo: {
    fecha_inicio: string;
    fecha_fin: string;
  };
}

export interface ReporteFinanciero {
  ingresos_totales: number;
  egresos_totales: number;
  ganancia_neta: number;
  ingresos_por_fuente: Record<string, number>;
  egresos_por_categoria: Record<string, number>;
  periodo: {
    fecha_inicio: string;
    fecha_fin: string;
  };
}

class ReporteService {
  private baseUrl = "/api/reportes";

  /**
   * Generar reporte de ventas
   */
  async generarReporteVentas(
    filtros: FiltroReporte
  ): Promise<ReporteVentas | Blob> {
    const queryString = this.buildQueryString(filtros);
    const url = `${this.baseUrl}/ventas/${
      queryString ? `?${queryString}` : ""
    }`;

    if (filtros.formato === "pdf") {
      return await httpClient.getBlob(url);
    }
    return await httpClient.get<ReporteVentas>(url);
  }

  /**
   * Generar reporte de compras
   */
  async generarReporteCompras(
    filtros: FiltroReporte
  ): Promise<ReporteCompras | Blob> {
    const queryString = this.buildQueryString(filtros);
    const url = `${this.baseUrl}/compras/${
      queryString ? `?${queryString}` : ""
    }`;

    if (filtros.formato === "pdf") {
      return await httpClient.getBlob(url);
    }
    return await httpClient.get<ReporteCompras>(url);
  }

  /**
   * Generar reporte de inventario
   */
  async generarReporteInventario(
    formato: FormatoReporte = "json"
  ): Promise<ReporteInventario | Blob> {
    if (formato === "pdf") {
      return await httpClient.getBlob(
        `${this.baseUrl}/inventario/?formato=pdf`
      );
    }
    return await httpClient.get<ReporteInventario>(
      `${this.baseUrl}/inventario/`
    );
  }

  /**
   * Generar reporte de membresías
   */
  async generarReporteMembresias(
    filtros: FiltroReporte
  ): Promise<ReporteMembresias | Blob> {
    const queryString = this.buildQueryString(filtros);
    const url = `${this.baseUrl}/membresias/${
      queryString ? `?${queryString}` : ""
    }`;

    if (filtros.formato === "pdf") {
      return await httpClient.getBlob(url);
    }
    return await httpClient.get<ReporteMembresias>(url);
  }

  /**
   * Generar reporte financiero
   */
  async generarReporteFinanciero(
    filtros: FiltroReporte
  ): Promise<ReporteFinanciero | Blob> {
    const queryString = this.buildQueryString(filtros);
    const url = `${this.baseUrl}/financiero/${
      queryString ? `?${queryString}` : ""
    }`;

    if (filtros.formato === "pdf") {
      return await httpClient.getBlob(url);
    }
    return await httpClient.get<ReporteFinanciero>(url);
  }

  /**
   * Construir query string a partir de filtros
   */
  private buildQueryString(filtros: FiltroReporte): string {
    const params = new URLSearchParams();
    if (filtros.tipo_periodo) {
      params.append("tipo_periodo", filtros.tipo_periodo);
    }
    if (filtros.fecha_inicio) {
      params.append("fecha_inicio", filtros.fecha_inicio);
    }
    if (filtros.fecha_fin) {
      params.append("fecha_fin", filtros.fecha_fin);
    }
    if (filtros.formato) {
      params.append("formato", filtros.formato);
    }
    return params.toString();
  }

  /**
   * Descargar PDF
   */
  descargarPDF(blob: Blob, nombreArchivo: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = nombreArchivo;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}

export default new ReporteService();
