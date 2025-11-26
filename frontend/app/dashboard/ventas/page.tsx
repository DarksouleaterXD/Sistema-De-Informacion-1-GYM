"use client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import {
  Search,
  Plus,
  FileText,
  X,
  ShoppingCart,
  DollarSign,
  Calendar,
  User,
  Download,
  Trash2,
  AlertCircle,
} from "lucide-react";
import {
  Venta,
  ventaService,
  CreateVentaDTO,
  DetalleVentaCreate,
} from "@/lib/services/venta.service";
import { clientService } from "@/lib/services/client.service";
import { productoService, Producto } from "@/lib/services/producto.service";
import { Card, Button, Input } from "@/components/ui";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import CreateEditVentaModal from "@/components/ventas/CreateEditVentaModal";

const METODOS_PAGO = [
  { value: "efectivo", label: "Efectivo" },
  { value: "tarjeta", label: "Tarjeta" },
  { value: "transferencia", label: "Transferencia" },
  { value: "qr", label: "QR" },
];

const ESTADOS_VENTA = [
  { value: "", label: "Todos" },
  { value: "pendiente", label: "Pendiente" },
  { value: "completada", label: "Completada" },
  { value: "cancelada", label: "Cancelada" },
];

function VentasPageContent() {
  const [ventas, setVentas] = useState<Venta[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [estadoFilter, setEstadoFilter] = useState("");
  const [metodoPagoFilter, setMetodoPagoFilter] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedVenta, setSelectedVenta] = useState<Venta | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    total: 0,
  });

  useEffect(() => {
    loadVentas();
  }, [searchTerm, estadoFilter, metodoPagoFilter, pagination.page]);

  const loadVentas = async () => {
    try {
      setLoading(true);
      const response = await ventaService.getAll({
        page: pagination.page,
        search: searchTerm || undefined,
        estado: estadoFilter || undefined,
        metodo_pago: metodoPagoFilter || undefined,
      });
      setVentas(response?.results || []);
      setPagination((prev) => ({
        ...prev,
        total: response?.count || 0,
      }));
    } catch (error) {
      console.error("Error al cargar ventas:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setSelectedVenta(null);
    setModalOpen(true);
  };

  const handleEdit = (venta: Venta) => {
    setSelectedVenta(venta);
    setModalOpen(true);
  };

  const handleDelete = async (venta: Venta) => {
    if (!confirm(`¿Está seguro de cancelar la venta ${venta.numero_venta}?`)) {
      return;
    }

    try {
      await ventaService.cancelar(venta.id);
      alert("Venta cancelada exitosamente");
      loadVentas();
    } catch (error: any) {
      console.error("Error al cancelar venta:", error);
      alert(error.response?.data?.detail || "Error al cancelar la venta");
    }
  };

  const handleGenerarPDF = async (venta: Venta) => {
    try {
      await ventaService.generarPDF(venta.id);
    } catch (error: any) {
      console.error("Error al generar PDF:", error);
      alert("Error al generar el PDF");
    }
  };

  const getEstadoBadge = (estado: string) => {
    const styles = {
      completada: "bg-green-100 text-green-800",
      pendiente: "bg-yellow-100 text-yellow-800",
      cancelada: "bg-red-100 text-red-800",
    };
    return (
      <span
        className={`px-2 py-1 rounded-full text-xs font-medium ${
          styles[estado as keyof typeof styles] || "bg-gray-100 text-gray-800"
        }`}
      >
        {estado === "completada"
          ? "Completada"
          : estado === "pendiente"
          ? "Pendiente"
          : "Cancelada"}
      </span>
    );
  };

  const getMetodoPagoLabel = (metodo: string) => {
    return METODOS_PAGO.find((m) => m.value === metodo)?.label || metodo;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("es-ES", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <DashboardLayout
      title="Ventas"
      description="Gestión de ventas de productos"
    >
      <div className="space-y-6">
        {/* Barra de búsqueda y filtros */}
        <Card className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Buscar por número de venta, cliente..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={estadoFilter}
              onChange={(e) => setEstadoFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
            >
              {ESTADOS_VENTA.map((estado) => (
                <option key={estado.value} value={estado.value}>
                  {estado.label}
                </option>
              ))}
            </select>
            <select
              value={metodoPagoFilter}
              onChange={(e) => setMetodoPagoFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
            >
              <option value="">Todos los métodos</option>
              {METODOS_PAGO.map((metodo) => (
                <option key={metodo.value} value={metodo.value}>
                  {metodo.label}
                </option>
              ))}
            </select>
            <Button onClick={handleCreate} className="whitespace-nowrap">
              <Plus className="w-4 h-4 mr-2" />
              Nueva Venta
            </Button>
          </div>
        </Card>

        {/* Tabla de ventas */}
        <Card className="p-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Cargando ventas...</p>
            </div>
          ) : ventas.length === 0 ? (
            <div className="text-center py-12">
              <ShoppingCart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No hay ventas registradas</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto -mx-4 sm:mx-0">
                <div className="inline-block min-w-full align-middle px-4 sm:px-0">
                  <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">
                        Número
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">
                        Cliente
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">
                        Fecha
                      </th>
                      <th className="text-center py-3 px-4 font-semibold text-gray-700">
                        Cantidad
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">
                        Estado
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">
                        Método Pago
                      </th>
                      <th className="text-right py-3 px-4 font-semibold text-gray-700">
                        Total
                      </th>
                      <th className="text-center py-3 px-4 font-semibold text-gray-700">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {ventas.map((venta) => (
                      <tr
                        key={venta.id}
                        className="border-b border-gray-100 hover:bg-gray-50"
                      >
                        <td className="py-3 px-4">
                          <span className="font-medium text-gray-900">
                            {venta.numero_venta}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div>
                            <div className="font-medium text-gray-900">
                              {venta.cliente_nombre}
                            </div>
                            <div className="text-sm text-gray-500">
                              CI: {venta.cliente_ci}
                            </div>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {formatDate(venta.fecha_venta)}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className="text-sm font-medium text-gray-900">
                            {venta.cantidad_items || 0} {venta.cantidad_items === 1 ? "item" : "items"}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          {getEstadoBadge(venta.estado)}
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {getMetodoPagoLabel(venta.metodo_pago)}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <span className="font-semibold text-gray-900">
                            ${parseFloat(venta.total).toLocaleString("es-ES", {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => handleGenerarPDF(venta)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                              title="Generar PDF"
                            >
                              <Download className="w-4 h-4" />
                            </button>
                            {venta.estado !== "cancelada" && (
                              <button
                                onClick={() => handleDelete(venta)}
                                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                title="Cancelar venta"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                </div>
              </div>

              {/* Paginación */}
              {pagination.total > pagination.pageSize && (
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
                  <div className="text-sm text-gray-600">
                    Mostrando {(pagination.page - 1) * pagination.pageSize + 1}{" "}
                    a{" "}
                    {Math.min(
                      pagination.page * pagination.pageSize,
                      pagination.total
                    )}{" "}
                    de {pagination.total} ventas
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={() =>
                        setPagination((prev) => ({
                          ...prev,
                          page: Math.max(1, prev.page - 1),
                        }))
                      }
                      disabled={pagination.page === 1}
                      variant="outline"
                    >
                      Anterior
                    </Button>
                    <Button
                      onClick={() =>
                        setPagination((prev) => ({
                          ...prev,
                          page: prev.page + 1,
                        }))
                      }
                      disabled={
                        pagination.page * pagination.pageSize >= pagination.total
                      }
                      variant="outline"
                    >
                      Siguiente
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </Card>

        {/* Modal */}
        <CreateEditVentaModal
          isOpen={modalOpen}
          onClose={() => {
            setModalOpen(false);
            setSelectedVenta(null);
          }}
          onSuccess={loadVentas}
          venta={selectedVenta}
        />
      </div>
    </DashboardLayout>
  );
}

export default function VentasPage() {
  return (
    <ProtectedRoute requiredPermission="ventas.view">
      <VentasPageContent />
    </ProtectedRoute>
  );
}

