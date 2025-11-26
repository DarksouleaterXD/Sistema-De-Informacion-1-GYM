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
  Truck,
  Download,
  CheckCircle,
  Package,
} from "lucide-react";
import {
  OrdenCompra,
  compraService,
} from "@/lib/services/compra.service";
import { Card, Button, Input } from "@/components/ui";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import CreateEditOrdenCompraModal from "@/components/compras/CreateEditOrdenCompraModal";

const ESTADOS_ORDEN = [
  { value: "", label: "Todas" },
  { value: "pendiente", label: "Pendiente" },
  { value: "confirmada", label: "Confirmada" },
  { value: "recibida", label: "Recibida" },
  { value: "cancelada", label: "Cancelada" },
];

function ComprasPageContent() {
  const [ordenes, setOrdenes] = useState<OrdenCompra[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [estadoFilter, setEstadoFilter] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedOrden, setSelectedOrden] = useState<OrdenCompra | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    total: 0,
  });

  useEffect(() => {
    loadOrdenes();
  }, [searchTerm, estadoFilter, pagination.page]);

  const loadOrdenes = async () => {
    try {
      setLoading(true);
      const response = await compraService.getAll({
        page: pagination.page,
        search: searchTerm || undefined,
        estado: estadoFilter || undefined,
      });
      setOrdenes(response?.results || []);
      setPagination((prev) => ({
        ...prev,
        total: response?.count || 0,
      }));
    } catch (error) {
      console.error("Error al cargar órdenes:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setSelectedOrden(null);
    setModalOpen(true);
  };

  const handleConfirmar = async (orden: OrdenCompra) => {
    if (!confirm(`¿Confirmar la orden ${orden.numero_orden}?`)) {
      return;
    }

    try {
      await compraService.confirmar(orden.id);
      alert("Orden confirmada exitosamente");
      loadOrdenes();
    } catch (error: any) {
      console.error("Error al confirmar orden:", error);
      alert(error.response?.data?.detail || "Error al confirmar la orden");
    }
  };

  const handleRecibir = async (orden: OrdenCompra) => {
    if (!confirm(`¿Recibir la orden ${orden.numero_orden}? Esto actualizará el stock.`)) {
      return;
    }

    try {
      await compraService.recibir(orden.id);
      alert("Orden recibida exitosamente. Stock actualizado.");
      loadOrdenes();
    } catch (error: any) {
      console.error("Error al recibir orden:", error);
      alert(error.response?.data?.detail || "Error al recibir la orden");
    }
  };

  const handleCancelar = async (orden: OrdenCompra) => {
    if (!confirm(`¿Cancelar la orden ${orden.numero_orden}?`)) {
      return;
    }

    try {
      await compraService.cancelar(orden.id);
      alert("Orden cancelada exitosamente");
      loadOrdenes();
    } catch (error: any) {
      console.error("Error al cancelar orden:", error);
      alert(error.response?.data?.detail || "Error al cancelar la orden");
    }
  };

  const handleGenerarPDF = async (orden: OrdenCompra) => {
    try {
      await compraService.generarPDF(orden.id);
    } catch (error: any) {
      console.error("Error al generar PDF:", error);
      alert("Error al generar el PDF");
    }
  };

  const getEstadoBadge = (estado: string) => {
    const styles = {
      recibida: "bg-green-100 text-green-800",
      confirmada: "bg-blue-100 text-blue-800",
      pendiente: "bg-yellow-100 text-yellow-800",
      cancelada: "bg-red-100 text-red-800",
    };
    return (
      <span
        className={`px-2 py-1 rounded-full text-xs font-medium ${
          styles[estado as keyof typeof styles] || "bg-gray-100 text-gray-800"
        }`}
      >
        {estado === "recibida"
          ? "Recibida"
          : estado === "confirmada"
          ? "Confirmada"
          : estado === "pendiente"
          ? "Pendiente"
          : "Cancelada"}
      </span>
    );
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
      title="Compras"
      description="Gestión de órdenes de compra"
    >
      <div className="space-y-6">
        {/* Barra de búsqueda y filtros */}
        <Card className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Buscar por número de orden, proveedor..."
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
              {ESTADOS_ORDEN.map((estado) => (
                <option key={estado.value} value={estado.value}>
                  {estado.label}
                </option>
              ))}
            </select>
            <Button onClick={handleCreate} className="whitespace-nowrap">
              <Plus className="w-4 h-4 mr-2" />
              Nueva Orden
            </Button>
          </div>
        </Card>

        {/* Tabla de órdenes */}
        <Card className="p-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Cargando órdenes...</p>
            </div>
          ) : ordenes.length === 0 ? (
            <div className="text-center py-12">
              <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No hay órdenes de compra registradas</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">
                        Número
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">
                        Proveedor
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">
                        Fecha
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">
                        Estado
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
                    {ordenes.map((orden) => (
                      <tr
                        key={orden.id}
                        className="border-b border-gray-100 hover:bg-gray-50"
                      >
                        <td className="py-3 px-4">
                          <span className="font-medium text-gray-900">
                            {orden.numero_orden}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div>
                            <div className="font-medium text-gray-900">
                              {orden.proveedor_nombre}
                            </div>
                            <div className="text-sm text-gray-500">
                              NIT: {orden.proveedor_nit}
                            </div>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {formatDate(orden.fecha_orden)}
                        </td>
                        <td className="py-3 px-4">
                          {getEstadoBadge(orden.estado)}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <span className="font-semibold text-gray-900">
                            ${parseFloat(orden.total).toLocaleString("es-ES", {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => handleGenerarPDF(orden)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                              title="Generar PDF"
                            >
                              <Download className="w-4 h-4" />
                            </button>
                            {orden.estado === "pendiente" && (
                              <button
                                onClick={() => handleConfirmar(orden)}
                                className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                title="Confirmar orden"
                              >
                                <CheckCircle className="w-4 h-4" />
                              </button>
                            )}
                            {(orden.estado === "pendiente" ||
                              orden.estado === "confirmada") && (
                              <button
                                onClick={() => handleRecibir(orden)}
                                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                title="Recibir orden (actualiza stock)"
                              >
                                <Package className="w-4 h-4" />
                              </button>
                            )}
                            {orden.estado !== "cancelada" &&
                              orden.estado !== "recibida" && (
                                <button
                                  onClick={() => handleCancelar(orden)}
                                  className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                  title="Cancelar orden"
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
                    de {pagination.total} órdenes
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
        <CreateEditOrdenCompraModal
          isOpen={modalOpen}
          onClose={() => {
            setModalOpen(false);
            setSelectedOrden(null);
          }}
          onSuccess={loadOrdenes}
          orden={selectedOrden}
        />
      </div>
    </DashboardLayout>
  );
}

export default function ComprasPage() {
  return (
    <ProtectedRoute requiredPermission="compras.view">
      <ComprasPageContent />
    </ProtectedRoute>
  );
}

