/**
 * Servicio API para Productos (CU24)
 */

import { httpClient } from "@/lib/config/http-client";

export interface CategoriaProducto {
  id: number;
  nombre: string;
  codigo: string;
  descripcion: string;
  activo: boolean;
  created_at: string;
  updated_at: string;
}

export interface Producto {
  id: number;
  nombre: string;
  codigo: string;
  descripcion: string;
  categoria: number;
  categoria_nombre: string;
  proveedor: number | null;
  proveedor_nombre: string;
  precio: string;
  costo: string;
  stock: number;
  stock_minimo: number;
  unidad_medida: string;
  unidad_medida_display: string;
  promocion: number | null;
  promocion_nombre: string;
  estado: "ACTIVO" | "AGOTADO";
  estado_display: string;
  precio_con_descuento: string;
  necesita_reposicion: boolean;
  margen_ganancia: string;
  imagen?: string | null;
  imagen_url?: string | null;
  creado_por: number;
  creado_por_username: string;
  modificado_por: number | null;
  modificado_por_username: string;
  created_at: string;
  updated_at: string;
}

export interface CreateProductoDTO {
  nombre: string;
  codigo: string;
  descripcion?: string;
  imagen?: File | null;
  categoria: number;
  proveedor?: number | null;
  precio: number;
  costo: number;
  stock: number;
  stock_minimo: number;
  unidad_medida: string;
  promocion?: number | null;
}

export interface UpdateProductoDTO {
  nombre?: string;
  descripcion?: string;
  categoria?: number;
  proveedor?: number | null;
  precio?: number;
  costo?: number;
  stock?: number;
  stock_minimo?: number;
  unidad_medida?: string;
  promocion?: number | null;
}

export interface ActualizarStockDTO {
  cantidad: number;
  tipo_movimiento: "entrada" | "salida";
  motivo?: string;
}

export interface GetProductosParams {
  search?: string;
  categoria?: number;
  proveedor?: number;
  estado?: string;
  bajo_stock?: boolean;
  page?: number;
  page_size?: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ProductoEstadisticas {
  total_productos: number;
  productos_activos: number;
  productos_agotados: number;
  productos_bajo_stock: number;
  valor_inventario: string;
}

class ProductoService {
  private baseUrl = "/api/productos/productos";
  private categoriaUrl = "/api/categorias-producto";

  /**
   * Obtener todos los productos con filtros
   */
  async getAll(params?: GetProductosParams): Promise<PaginatedResponse<Producto>> {
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.append("search", params.search);
    if (params?.categoria) queryParams.append("categoria", params.categoria.toString());
    if (params?.proveedor) queryParams.append("proveedor", params.proveedor.toString());
    if (params?.estado) queryParams.append("estado", params.estado);
    if (params?.bajo_stock !== undefined) queryParams.append("bajo_stock", params.bajo_stock.toString());
    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.page_size) queryParams.append("page_size", params.page_size.toString());

    const queryString = queryParams.toString();
    const url = queryString ? `${this.baseUrl}/?${queryString}` : `${this.baseUrl}/`;
    
    return await httpClient.get<PaginatedResponse<Producto>>(url);
  }

  /**
   * Obtener un producto por ID
   */
  async getById(id: number): Promise<Producto> {
    return await httpClient.get<Producto>(`${this.baseUrl}/${id}/`);
  }

  /**
   * Crear un nuevo producto (CU24)
   */
  async create(data: CreateProductoDTO): Promise<Producto> {
    // Si hay imagen, usar FormData
    if (data.imagen) {
      const formData = new FormData();
      Object.keys(data).forEach((key) => {
        const value = data[key as keyof CreateProductoDTO];
        if (value !== null && value !== undefined) {
          if (key === 'imagen' && value instanceof File) {
            formData.append('imagen', value);
          } else if (key !== 'imagen') {
            formData.append(key, String(value));
          }
        }
      });
      return await httpClient.postFormData<Producto>(`${this.baseUrl}/`, formData);
    }
    return await httpClient.post<Producto>(`${this.baseUrl}/`, data);
  }

  /**
   * Actualizar un producto
   */
  async update(id: number, data: UpdateProductoDTO): Promise<Producto> {
    // Si hay imagen, usar FormData
    if (data.imagen) {
      const formData = new FormData();
      Object.keys(data).forEach((key) => {
        const value = data[key as keyof UpdateProductoDTO];
        if (value !== null && value !== undefined) {
          if (key === 'imagen' && value instanceof File) {
            formData.append('imagen', value);
          } else if (key !== 'imagen') {
            formData.append(key, String(value));
          }
        }
      });
      return await httpClient.patchFormData<Producto>(`${this.baseUrl}/${id}/`, formData);
    }
    return await httpClient.patch<Producto>(`${this.baseUrl}/${id}/`, data);
  }

  /**
   * Eliminar un producto
   */
  async delete(id: number): Promise<void> {
    return await httpClient.delete(`${this.baseUrl}/${id}/`);
  }

  /**
   * Actualizar stock de un producto
   */
  async actualizarStock(id: number, data: ActualizarStockDTO): Promise<Producto> {
    // Mapear tipo_movimiento a operacion según lo que espera el backend
    const payload = {
      cantidad: data.cantidad,
      operacion: data.tipo_movimiento === "entrada" ? "sumar" : "restar",
      motivo: data.motivo || "",
    };
    return await httpClient.post<Producto>(`${this.baseUrl}/${id}/actualizar-stock/`, payload);
  }

  /**
   * Obtener productos con bajo stock
   */
  async getBajoStock(): Promise<Producto[]> {
    return await httpClient.get<Producto[]>(`${this.baseUrl}/bajo_stock/`);
  }

  /**
   * Obtener productos activos
   */
  async getActivos(): Promise<Producto[]> {
    return await httpClient.get<Producto[]>(`${this.baseUrl}/activos/`);
  }

  /**
   * Obtener estadísticas de productos
   */
  async getEstadisticas(): Promise<ProductoEstadisticas> {
    return await httpClient.get<ProductoEstadisticas>(`${this.baseUrl}/estadisticas/`);
  }

  /**
   * Obtener todas las categorías de productos
   * Nota: El endpoint devuelve un objeto paginado, extraemos el array results
   */
  async getCategorias(): Promise<CategoriaProducto[]> {
    const response = await httpClient.get<PaginatedResponse<CategoriaProducto>>(`${this.categoriaUrl}/`);
    // Si la respuesta es un objeto paginado, extraer results
    if (response && 'results' in response && Array.isArray(response.results)) {
      return response.results;
    }
    // Si ya es un array (fallback), retornarlo directamente
    if (Array.isArray(response)) {
      return response;
    }
    // Si no es ninguno de los casos anteriores, retornar array vacío
    return [];
  }

  /**
   * Obtener categorías activas
   */
  async getCategoriasActivas(): Promise<CategoriaProducto[]> {
    const categorias = await this.getCategorias();
    return categorias.filter(c => c.activo);
  }
}

export const productoService = new ProductoService();
