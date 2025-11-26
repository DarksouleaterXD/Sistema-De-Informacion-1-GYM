/**
 * Servicio para gestión de inventario y ajustes de stock
 */
import { httpClient } from '../config/http-client';
import {
  Producto,
  MovimientoInventario,
  AjustarStockRequest,
  AjustarStockResponse,
  PaginatedResponse,
} from '../types';

/**
 * Construye query string a partir de parámetros
 */
const buildQueryString = (params?: Record<string, any>): string => {
  if (!params) return '';
  const query = Object.entries(params)
    .filter(([_, value]) => value !== undefined && value !== null && value !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');
  return query ? `?${query}` : '';
};

class InventarioService {
  /**
   * Obtener lista de productos con filtros
   */
  async getProductos(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    categoria?: number;
    proveedor?: number;
    estado?: string;
    stock_bajo?: boolean;
    ordering?: string;
  }): Promise<PaginatedResponse<Producto>> {
    const query = buildQueryString(params);
    console.log('📡 GET /api/productos/productos/' + query);
    return await httpClient.get<PaginatedResponse<Producto>>(`/api/productos/productos/${query}`);
  }

  /**
   * Obtener detalle de un producto
   */
  async getProducto(id: number): Promise<Producto> {
    return await httpClient.get<Producto>(`/api/productos/productos/${id}/`);
  }

  /**
   * Ajustar stock de un producto
   */
  async ajustarStock(data: AjustarStockRequest): Promise<AjustarStockResponse> {
    console.log('📡 POST /api/productos/productos/ajustar-stock/', data);
    return await httpClient.post<AjustarStockResponse>('/api/productos/productos/ajustar-stock/', data);
  }

  /**
   * Obtener movimientos de inventario
   */
  async getMovimientos(params?: {
    page?: number;
    page_size?: number;
    producto?: number;
    tipo?: 'ENTRADA' | 'SALIDA' | 'AJUSTE';
    fecha_desde?: string;
    fecha_hasta?: string;
    search?: string;
    ordering?: string;
  }): Promise<PaginatedResponse<MovimientoInventario>> {
    const query = buildQueryString(params);
    return await httpClient.get<PaginatedResponse<MovimientoInventario>>(`/api/productos/movimientos-inventario/${query}`);
  }

  /**
   * Obtener detalle de un movimiento
   */
  async getMovimiento(id: number): Promise<MovimientoInventario> {
    return await httpClient.get<MovimientoInventario>(`/api/productos/movimientos-inventario/${id}/`);
  }

  /**
   * Obtener productos con stock bajo
   */
  async getProductosBajoStock(params?: {
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Producto>> {
    const query = buildQueryString(params);
    return await httpClient.get<PaginatedResponse<Producto>>(`/api/productos/productos/bajo-stock/${query}`);
  }

  /**
   * Obtener estadísticas de inventario
   */
  async getEstadisticas(): Promise<{
    total_productos: number;
    productos_activos: number;
    productos_agotados: number;
    productos_bajo_stock: number;
    valor_total_inventario: number;
    stock_total: number;
    precio_promedio: number;
  }> {
    return await httpClient.get('/api/productos/productos/estadisticas/');
  }
}

export default new InventarioService();
