"use client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import {
  Search,
  Package,
  Edit,
  Loader2,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Archive,
  Download,
} from "lucide-react";
import { Card, Button, Input } from "@/components/ui";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PermissionCodes } from "@/lib/utils/permissions";
import AjustarStockModal from "@/components/productos/AjustarStockModal";
import inventarioService from "@/lib/services/inventario.service";
import reporteService from "@/lib/services/reporte.service";
import { httpClient } from "@/lib/config/http-client";
import { Producto, AjustarStockResponse } from "@/lib/types";

type ModalMode = "ajustar" | null;

function InventarioPageContent() {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [estadoFilter, setEstadoFilter] = useState<string>("");
  const [stockBajoFilter, setStockBajoFilter] = useState(false);
  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const [selectedProducto, setSelectedProducto] = useState<Producto | null>(
    null
  );
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    total: 0,
  });
  const [estadisticas, setEstadisticas] = useState<any>(null);
  const [downloadingPDF, setDownloadingPDF] = useState(false);

  useEffect(() => {
    loadProductos();
    loadEstadisticas();
  }, [searchTerm, estadoFilter, stockBajoFilter, pagination.page]);

  const loadProductos = async () => {
    try {
      setLoading(true);
      console.log("🔍 Cargando productos con filtros:", {
        searchTerm,
        estadoFilter,
        stockBajoFilter,
        page: pagination.page,
        pageSize: pagination.pageSize,
      });

      const response = stockBajoFilter
        ? await inventarioService.getProductosBajoStock({
            page: pagination.page,
            page_size: pagination.pageSize,
          })
        : await inventarioService.getProductos({
            search: searchTerm,
            estado: estadoFilter,
            page: pagination.page,
            page_size: pagination.pageSize,
            ordering: "-created_at",
          });

      console.log("✅ Respuesta recibida:", {
        count: response?.count,
        results: response?.results?.length,
        productos: response?.results,
      });

      setProductos(response?.results || []);
      setPagination((prev) => ({ ...prev, total: response?.count || 0 }));
    } catch (error: any) {
      console.error("❌ Error al cargar productos:", error);
      console.error(
        "Detalles del error:",
        error.response?.data || error.message
      );
      setProductos([]);
    } finally {
      setLoading(false);
    }
  };

  const loadEstadisticas = async () => {
    try {
      const stats = await inventarioService.getEstadisticas();
      setEstadisticas(stats);
    } catch (error) {
      console.error("Error al cargar estadísticas:", error);
    }
  };

  const handleAjustar = (producto: Producto) => {
    setModalMode("ajustar");
    setSelectedProducto(producto);
  };

  const handleAjusteSuccess = async (response: AjustarStockResponse) => {
    if (!response || !response.producto || !response.ajuste) {
      console.error("Respuesta inválida del servidor:", response);
      alert("Error: Respuesta inválida del servidor");
      return;
    }

    alert(
      `✓ Ajuste realizado exitosamente\n\nProducto: ${
        response.producto.nombre
      }\nStock anterior: ${response.ajuste.stock_anterior}\nStock actual: ${
        response.ajuste.stock_actual
      }\nDiferencia: ${response.ajuste.diferencia > 0 ? "+" : ""}${
        response.ajuste.diferencia
      }`
    );
    setModalMode(null);
    setSelectedProducto(null);
    loadProductos();
    loadEstadisticas();
  };

  const handleDescargarPDF = async () => {
    try {
      setDownloadingPDF(true);

      // Construir query string con los filtros actuales
      const params = new URLSearchParams();
      params.append("formato", "pdf");
      if (searchTerm) {
        params.append("search", searchTerm);
      }
      if (estadoFilter) {
        params.append("estado", estadoFilter);
      }
      if (stockBajoFilter) {
        params.append("stock_bajo", "true");
      }

      const queryString = params.toString();
      const url = `/api/reportes/inventario/${
        queryString ? `?${queryString}` : ""
      }`;

      const blob = await httpClient.getBlob(url);
      const nombreArchivo = `inventario_${
        new Date().toISOString().split("T")[0]
      }.pdf`;
      reporteService.descargarPDF(blob, nombreArchivo);
    } catch (error: any) {
      console.error("Error al descargar PDF:", error);
      alert(
        "Error al descargar el PDF: " + (error.message || "Error desconocido")
      );
    } finally {
      setDownloadingPDF(false);
    }
  };

  const getEstadoBadge = (estado: string) => {
    const badges: Record<string, { label: string; color: string; icon: any }> =
      {
        ACTIVO: {
          label: "Activo",
          color: "bg-green-100 text-green-800",
          icon: CheckCircle,
        },
        INACTIVO: {
          label: "Inactivo",
          color: "bg-gray-100 text-gray-800",
          icon: XCircle,
        },
        AGOTADO: {
          label: "Agotado",
          color: "bg-red-100 text-red-800",
          icon: AlertTriangle,
        },
        DESCONTINUADO: {
          label: "Descontinuado",
          color: "bg-orange-100 text-orange-800",
          icon: Archive,
        },
      };
    const badge = badges[estado] || badges.ACTIVO;
    const Icon = badge.icon;
    return (
      <span
        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${badge.color}`}
      >
        <Icon className="w-3 h-3" />
        {badge.label}
      </span>
    );
  };

  const totalPages = Math.ceil(pagination.total / pagination.pageSize);

  return (
    <div className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8 flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Gestión de Inventario
          </h1>
          <p className="text-gray-600">
            Ajuste de stock y control de inventario de productos
          </p>
        </div>
        <Button
          onClick={handleDescargarPDF}
          disabled={downloadingPDF}
          variant="outline"
          className="flex items-center gap-2"
        >
          {downloadingPDF ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Download className="w-4 h-4" />
          )}
          Descargar PDF
        </Button>
      </div>

      {/* Estadísticas */}
      {estadisticas && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Total Productos
                </p>
                <p className="text-3xl font-bold text-gray-800 mt-1">
                  {estadisticas.total_productos}
                </p>
              </div>
              <div className="bg-blue-100 p-3 rounded-lg">
                <Package className="w-8 h-8 text-blue-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Activos</p>
                <p className="text-3xl font-bold text-green-600 mt-1">
                  {estadisticas.productos_activos}
                </p>
              </div>
              <div className="bg-green-100 p-3 rounded-lg">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Stock Bajo</p>
                <p className="text-3xl font-bold text-yellow-600 mt-1">
                  {estadisticas.productos_bajo_stock}
                </p>
              </div>
              <div className="bg-yellow-100 p-3 rounded-lg">
                <AlertTriangle className="w-8 h-8 text-yellow-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Agotados</p>
                <p className="text-3xl font-bold text-red-600 mt-1">
                  {estadisticas.productos_agotados}
                </p>
              </div>
              <div className="bg-red-100 p-3 rounded-lg">
                <XCircle className="w-8 h-8 text-red-600" />
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Filtros y búsqueda */}
      <Card className="p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="lg:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Buscar Producto
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Buscar por nombre o código..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Seleccionar Producto
            </label>
            <select
              value=""
              onChange={(e) => {
                const productoId = parseInt(e.target.value);
                if (productoId) {
                  const producto = productos.find((p) => p.id === productoId);
                  if (producto) {
                    handleAjustar(producto);
                  }
                }
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 bg-white"
            >
              <option value="">Seleccione para ajustar...</option>
              {productos.map((producto) => (
                <option key={producto.id} value={producto.id}>
                  {producto.codigo} - {producto.nombre} (Stock: {producto.stock}
                  )
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estado
            </label>
            <select
              value={estadoFilter}
              onChange={(e) => setEstadoFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 bg-white"
            >
              <option value="">Todos los estados</option>
              <option value="ACTIVO">Activo</option>
              <option value="INACTIVO">Inactivo</option>
              <option value="AGOTADO">Agotado</option>
              <option value="DESCONTINUADO">Descontinuado</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filtros
            </label>
            <label className="flex items-center gap-2 cursor-pointer h-10 px-3 py-2 border border-gray-300 rounded-lg">
              <input
                type="checkbox"
                checked={stockBajoFilter}
                onChange={(e) => setStockBajoFilter(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Solo stock bajo</span>
            </label>
          </div>
        </div>
      </Card>

      {/* Tabla de productos */}
      <Card className="overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-2 text-gray-600">Cargando productos...</span>
          </div>
        ) : productos.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No se encontraron productos
            </h3>
            <p className="text-gray-600">
              {searchTerm || estadoFilter || stockBajoFilter
                ? "Intenta ajustar los filtros de búsqueda"
                : "No hay productos registrados en el sistema"}
            </p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Producto
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Código
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stock Actual
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stock Mínimo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Precio
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {productos.map((producto) => (
                    <tr key={producto.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            {producto.imagen_url ? (
                              <img
                                className="h-10 w-10 rounded-full object-cover"
                                src={producto.imagen_url}
                                alt={producto.nombre}
                              />
                            ) : (
                              <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                                <Package className="w-5 h-5 text-gray-500" />
                              </div>
                            )}
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {producto.nombre}
                            </div>
                            <div className="text-sm text-gray-500">
                              {producto.categoria_nombre}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {producto.codigo}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span
                            className={`text-sm font-medium ${
                              producto.necesita_reposicion
                                ? "text-red-600"
                                : "text-gray-900"
                            }`}
                          >
                            {producto.stock} {producto.unidad_medida}
                          </span>
                          {producto.necesita_reposicion && (
                            <AlertTriangle className="w-4 h-4 text-red-500 ml-2" />
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {producto.stock_minimo} {producto.unidad_medida}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getEstadoBadge(producto.estado)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        Bs. {Number(producto.precio).toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => handleAjustar(producto)}
                        >
                          <Edit className="w-4 h-4 mr-1" />
                          Ajustar Stock
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Paginación */}
            <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Mostrando{" "}
                  <span className="font-medium">
                    {(pagination.page - 1) * pagination.pageSize + 1}
                  </span>{" "}
                  a{" "}
                  <span className="font-medium">
                    {Math.min(
                      pagination.page * pagination.pageSize,
                      pagination.total
                    )}
                  </span>{" "}
                  de <span className="font-medium">{pagination.total}</span>{" "}
                  resultados
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() =>
                      setPagination((prev) => ({
                        ...prev,
                        page: Math.max(1, prev.page - 1),
                      }))
                    }
                    disabled={pagination.page === 1}
                  >
                    Anterior
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() =>
                      setPagination((prev) => ({
                        ...prev,
                        page: Math.min(totalPages, prev.page + 1),
                      }))
                    }
                    disabled={pagination.page >= totalPages}
                  >
                    Siguiente
                  </Button>
                </div>
              </div>
            </div>
          </>
        )}
      </Card>

      {/* Modal de ajuste */}
      {selectedProducto && modalMode === "ajustar" && (
        <AjustarStockModal
          isOpen={true}
          onClose={() => {
            setModalMode(null);
            setSelectedProducto(null);
          }}
          producto={selectedProducto}
          onSuccess={handleAjusteSuccess}
        />
      )}
    </div>
  );
}

export default function InventarioPage() {
  return (
    <ProtectedRoute requiredPermissions={[PermissionCodes.CLIENT_VIEW]}>
      <DashboardLayout>
        <InventarioPageContent />
      </DashboardLayout>
    </ProtectedRoute>
  );
}
