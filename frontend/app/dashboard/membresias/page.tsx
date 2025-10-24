"use client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import {
  Search,
  Plus,
  Edit,
  Trash2,
  Eye,
  Calendar,
  DollarSign,
  Users,
  TrendingUp,
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react";
import membresiaService, {
  MembresiaList,
  MembresiaStats,
  Membresia,
  MembresiaCreate,
} from "@/lib/services/membresia.service";
import { clientService } from "@/lib/services/client.service";
import { Client } from "@/lib/types";

export default function MembresiasPage() {
  const [membresias, setMembresias] = useState<MembresiaList[]>([]);
  const [stats, setStats] = useState<MembresiaStats | null>(null);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [estadoFilter, setEstadoFilter] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  // Modales
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedMembresia, setSelectedMembresia] = useState<Membresia | null>(
    null
  );

  // Formulario
  const [formData, setFormData] = useState<MembresiaCreate>({
    cliente: 0,
    monto: 0,
    metodo_de_pago: "efectivo",
    estado: "activo",
    fecha_inicio: new Date().toISOString().split("T")[0],
    fecha_fin: "",
  });

  useEffect(() => {
    fetchMembresias();
    fetchStats();
    fetchClients();
  }, [currentPage, estadoFilter]);

  const fetchMembresias = async () => {
    try {
      setLoading(true);
      const response = await membresiaService.getAll({
        page: currentPage,
        search: searchTerm,
        estado: estadoFilter,
      });
      setMembresias(response.results);
      setTotalCount(response.count);
      setTotalPages(Math.ceil(response.count / 10)); // 10 items por página
    } catch (error) {
      console.error("Error al cargar membresías:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await membresiaService.getStats();
      setStats(data);
    } catch (error) {
      console.error("Error al cargar estadísticas:", error);
    }
  };

  const fetchClients = async () => {
    try {
      const response = await clientService.getAll({ page_size: 100 });
      setClients(response.results);
    } catch (error) {
      console.error("Error al cargar clientes:", error);
    }
  };

  const handleSearch = () => {
    setCurrentPage(1);
    fetchMembresias();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("es-BO", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const getEstadoBadge = (estado: string, estaActiva: boolean) => {
    if (estaActiva && estado === "activo") {
      return "bg-green-100 text-green-800";
    }
    return "bg-red-100 text-red-800";
  };

  // CRUD Functions
  const handleCreate = async () => {
    try {
      if (!formData.cliente || !formData.monto || !formData.fecha_fin) {
        alert("Por favor complete todos los campos obligatorios");
        return;
      }

      await membresiaService.create(formData);
      setShowCreateModal(false);
      resetForm();
      fetchMembresias();
      fetchStats();
      alert("Membresía creada exitosamente");
    } catch (error) {
      console.error("Error al crear membresía:", error);
      alert("Error al crear membresía");
    }
  };

  const handleViewDetail = async (id: number) => {
    try {
      const data = await membresiaService.getById(id);
      setSelectedMembresia(data);
      setShowDetailModal(true);
    } catch (error) {
      console.error("Error al cargar detalle:", error);
      alert("Error al cargar detalle");
    }
  };

  const handleEdit = async (id: number) => {
    try {
      const data = await membresiaService.getById(id);
      setSelectedMembresia(data);
      setFormData({
        cliente: data.inscripcion_info?.cliente || 0,
        monto: data.inscripcion_info?.monto || 0,
        metodo_de_pago: data.inscripcion_info?.metodo_de_pago || "efectivo",
        estado: data.estado,
        fecha_inicio: data.fecha_inicio,
        fecha_fin: data.fecha_fin,
      });
      setShowEditModal(true);
    } catch (error) {
      console.error("Error al cargar membresía:", error);
      alert("Error al cargar membresía");
    }
  };

  const handleUpdate = async () => {
    if (!selectedMembresia) return;

    try {
      await membresiaService.patch(selectedMembresia.id, {
        estado: formData.estado,
        fecha_inicio: formData.fecha_inicio,
        fecha_fin: formData.fecha_fin,
      });
      setShowEditModal(false);
      setSelectedMembresia(null);
      resetForm();
      fetchMembresias();
      fetchStats();
      alert("Membresía actualizada exitosamente");
    } catch (error) {
      console.error("Error al actualizar membresía:", error);
      alert("Error al actualizar membresía");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("¿Está seguro de eliminar esta membresía?")) return;

    try {
      await membresiaService.delete(id);
      fetchMembresias();
      fetchStats();
      alert("Membresía eliminada exitosamente");
    } catch (error) {
      console.error("Error al eliminar membresía:", error);
      alert("Error al eliminar membresía");
    }
  };

  const resetForm = () => {
    setFormData({
      cliente: 0,
      monto: 0,
      metodo_de_pago: "efectivo",
      estado: "activo",
      fecha_inicio: new Date().toISOString().split("T")[0],
      fecha_fin: "",
    });
  };

  const calculateFechaFin = (fechaInicio: string, dias: number) => {
    const fecha = new Date(fechaInicio);
    fecha.setDate(fecha.getDate() + dias);
    return fecha.toISOString().split("T")[0];
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Membresías</h1>
            <p className="text-gray-600 mt-1">
              Gestiona los planes de membresía del gimnasio
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            Nueva Membresía
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Membresías</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  {stats?.total_membresias || 0}
                </p>
              </div>
              <div className="bg-blue-100 p-3 rounded-lg">
                <TrendingUp className="h-8 w-8 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Activas</p>
                <p className="text-3xl font-bold text-green-600 mt-1">
                  {stats?.activas || 0}
                </p>
              </div>
              <div className="bg-green-100 p-3 rounded-lg">
                <Users className="h-8 w-8 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Ingresos Totales</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  Bs. {stats?.ingresos_totales.toLocaleString() || 0}
                </p>
              </div>
              <div className="bg-purple-100 p-3 rounded-lg">
                <DollarSign className="h-8 w-8 text-purple-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="bg-white p-4 rounded-lg shadow-sm">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por nombre o CI del cliente..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              />
            </div>
            <select
              value={estadoFilter}
              onChange={(e) => {
                setEstadoFilter(e.target.value);
                setCurrentPage(1);
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
            >
              <option value="">Todos los estados</option>
              <option value="activo">Activas</option>
              <option value="vencido">Vencidas</option>
            </select>
            <button
              onClick={handleSearch}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              Buscar
            </button>
          </div>
        </div>

        {/* Tabla de Membresías */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Cargando membresías...</p>
            </div>
          ) : membresias.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-gray-600">No se encontraron membresías</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Cliente
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        CI
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Fecha Inicio
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Fecha Fin
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Días Rest.
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Monto
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Estado
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {membresias.map((membresia) => (
                      <tr key={membresia.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {membresia.cliente_nombre}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {membresia.cliente_ci}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {formatDate(membresia.fecha_inicio)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {formatDate(membresia.fecha_fin)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div
                            className={`text-sm font-medium ${
                              membresia.dias_restantes > 7
                                ? "text-green-600"
                                : membresia.dias_restantes > 0
                                ? "text-yellow-600"
                                : "text-red-600"
                            }`}
                          >
                            {membresia.dias_restantes > 0
                              ? `${membresia.dias_restantes} días`
                              : "Vencida"}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            Bs. {membresia.monto}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getEstadoBadge(
                              membresia.estado,
                              membresia.esta_activa
                            )}`}
                          >
                            {membresia.estado_display}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleViewDetail(membresia.id)}
                              className="text-blue-600 hover:text-blue-900"
                              title="Ver detalle"
                            >
                              <Eye className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleEdit(membresia.id)}
                              className="text-indigo-600 hover:text-indigo-900"
                              title="Editar"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(membresia.id)}
                              className="text-red-600 hover:text-red-900"
                              title="Eliminar"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Paginación */}
              {totalPages > 1 && (
                <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
                  <div className="flex-1 flex justify-between sm:hidden">
                    <button
                      onClick={() =>
                        setCurrentPage((prev) => Math.max(prev - 1, 1))
                      }
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Anterior
                    </button>
                    <button
                      onClick={() =>
                        setCurrentPage((prev) => Math.min(prev + 1, totalPages))
                      }
                      disabled={currentPage === totalPages}
                      className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Siguiente
                    </button>
                  </div>
                  <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm text-gray-700">
                        Mostrando{" "}
                        <span className="font-medium">
                          {(currentPage - 1) * 10 + 1}
                        </span>{" "}
                        a{" "}
                        <span className="font-medium">
                          {Math.min(currentPage * 10, totalCount)}
                        </span>{" "}
                        de <span className="font-medium">{totalCount}</span>{" "}
                        resultados
                      </p>
                    </div>
                    <div>
                      <nav
                        className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px"
                        aria-label="Pagination"
                      >
                        <button
                          onClick={() =>
                            setCurrentPage((prev) => Math.max(prev - 1, 1))
                          }
                          disabled={currentPage === 1}
                          className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <ChevronLeft className="h-5 w-5" />
                        </button>
                        <span className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                          Página {currentPage} de {totalPages}
                        </span>
                        <button
                          onClick={() =>
                            setCurrentPage((prev) =>
                              Math.min(prev + 1, totalPages)
                            )
                          }
                          disabled={currentPage === totalPages}
                          className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <ChevronRight className="h-5 w-5" />
                        </button>
                      </nav>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Modal Crear Membresía */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    Nueva Membresía
                  </h2>
                  <button
                    onClick={() => {
                      setShowCreateModal(false);
                      resetForm();
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="h-6 w-6" />
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Cliente *
                    </label>
                    <select
                      value={formData.cliente}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          cliente: Number(e.target.value),
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                      required
                    >
                      <option value={0}>Seleccione un cliente</option>
                      {clients.map((client) => (
                        <option key={client.id} value={client.id}>
                          {client.nombre} {client.apellido} - CI: {client.ci}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Monto (Bs.) *
                      </label>
                      <input
                        type="number"
                        value={formData.monto}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            monto: Number(e.target.value),
                          })
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                        required
                        min="0"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Método de Pago *
                      </label>
                      <select
                        value={formData.metodo_de_pago}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            metodo_de_pago: e.target.value,
                          })
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                      >
                        <option value="efectivo">Efectivo</option>
                        <option value="tarjeta">Tarjeta</option>
                        <option value="transferencia">Transferencia</option>
                        <option value="qr">QR</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Fecha Inicio *
                      </label>
                      <input
                        type="date"
                        value={formData.fecha_inicio}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            fecha_inicio: e.target.value,
                          })
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Fecha Fin *
                      </label>
                      <input
                        type="date"
                        value={formData.fecha_fin}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            fecha_fin: e.target.value,
                          })
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                        required
                      />
                    </div>
                  </div>

                  {/* Atajos de duración */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Atajos de duración:
                    </label>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() =>
                          setFormData({
                            ...formData,
                            fecha_fin: calculateFechaFin(
                              formData.fecha_inicio,
                              30
                            ),
                          })
                        }
                        className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm"
                      >
                        1 Mes
                      </button>
                      <button
                        type="button"
                        onClick={() =>
                          setFormData({
                            ...formData,
                            fecha_fin: calculateFechaFin(
                              formData.fecha_inicio,
                              90
                            ),
                          })
                        }
                        className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm"
                      >
                        3 Meses
                      </button>
                      <button
                        type="button"
                        onClick={() =>
                          setFormData({
                            ...formData,
                            fecha_fin: calculateFechaFin(
                              formData.fecha_inicio,
                              180
                            ),
                          })
                        }
                        className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm"
                      >
                        6 Meses
                      </button>
                      <button
                        type="button"
                        onClick={() =>
                          setFormData({
                            ...formData,
                            fecha_fin: calculateFechaFin(
                              formData.fecha_inicio,
                              365
                            ),
                          })
                        }
                        className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm"
                      >
                        1 Año
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Estado *
                    </label>
                    <select
                      value={formData.estado}
                      onChange={(e) =>
                        setFormData({ ...formData, estado: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="activo">Activo</option>
                      <option value="suspendido">Suspendido</option>
                      <option value="vencido">Vencido</option>
                    </select>
                  </div>
                </div>

                <div className="flex gap-3 mt-6">
                  <button
                    onClick={handleCreate}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg"
                  >
                    Crear Membresía
                  </button>
                  <button
                    onClick={() => {
                      setShowCreateModal(false);
                      resetForm();
                    }}
                    className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-lg"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Modal Editar Membresía */}
        {showEditModal && selectedMembresia && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    Editar Membresía
                  </h2>
                  <button
                    onClick={() => {
                      setShowEditModal(false);
                      setSelectedMembresia(null);
                      resetForm();
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="h-6 w-6" />
                  </button>
                </div>

                <div className="space-y-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Cliente:</p>
                    <p className="font-medium">
                      {selectedMembresia.inscripcion_info?.cliente_info?.nombre}{" "}
                      {
                        selectedMembresia.inscripcion_info?.cliente_info
                          ?.apellido
                      }
                    </p>
                    <p className="text-sm text-gray-600 mt-2">Monto:</p>
                    <p className="font-medium">
                      Bs. {selectedMembresia.inscripcion_info?.monto}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Fecha Inicio *
                      </label>
                      <input
                        type="date"
                        value={formData.fecha_inicio}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            fecha_inicio: e.target.value,
                          })
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Fecha Fin *
                      </label>
                      <input
                        type="date"
                        value={formData.fecha_fin}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            fecha_fin: e.target.value,
                          })
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Estado *
                    </label>
                    <select
                      value={formData.estado}
                      onChange={(e) =>
                        setFormData({ ...formData, estado: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                    >
                      <option value="activo">Activo</option>
                      <option value="suspendido">Suspendido</option>
                      <option value="vencido">Vencido</option>
                    </select>
                  </div>
                </div>

                <div className="flex gap-3 mt-6">
                  <button
                    onClick={handleUpdate}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg"
                  >
                    Guardar Cambios
                  </button>
                  <button
                    onClick={() => {
                      setShowEditModal(false);
                      setSelectedMembresia(null);
                      resetForm();
                    }}
                    className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-lg"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Modal Ver Detalle */}
        {showDetailModal && selectedMembresia && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    Detalle de Membresía
                  </h2>
                  <button
                    onClick={() => {
                      setShowDetailModal(false);
                      setSelectedMembresia(null);
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="h-6 w-6" />
                  </button>
                </div>

                <div className="space-y-6">
                  {/* Información del Cliente */}
                  <div>
                    <h3 className="text-lg font-semibold mb-3">
                      Información del Cliente
                    </h3>
                    <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Nombre:</span>
                        <span className="font-medium">
                          {
                            selectedMembresia.inscripcion_info?.cliente_info
                              ?.nombre
                          }{" "}
                          {
                            selectedMembresia.inscripcion_info?.cliente_info
                              ?.apellido
                          }
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">CI:</span>
                        <span className="font-medium">
                          {selectedMembresia.inscripcion_info?.cliente_info?.ci}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Email:</span>
                        <span className="font-medium">
                          {selectedMembresia.inscripcion_info?.cliente_info
                            ?.email || "N/A"}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Celular:</span>
                        <span className="font-medium">
                          {selectedMembresia.inscripcion_info?.cliente_info
                            ?.celular || "N/A"}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Información de la Inscripción */}
                  <div>
                    <h3 className="text-lg font-semibold mb-3">
                      Información de Inscripción
                    </h3>
                    <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Monto:</span>
                        <span className="font-medium text-green-600">
                          Bs. {selectedMembresia.inscripcion_info?.monto}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Método de Pago:</span>
                        <span className="font-medium">
                          {
                            selectedMembresia.inscripcion_info
                              ?.metodo_de_pago_display
                          }
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">
                          Fecha de Inscripción:
                        </span>
                        <span className="font-medium">
                          {selectedMembresia.inscripcion_info?.created_at &&
                            formatDate(
                              selectedMembresia.inscripcion_info.created_at
                            )}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Información de la Membresía */}
                  <div>
                    <h3 className="text-lg font-semibold mb-3">
                      Información de Membresía
                    </h3>
                    <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Estado:</span>
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${getEstadoBadge(
                            selectedMembresia.estado,
                            selectedMembresia.esta_activa || false
                          )}`}
                        >
                          {selectedMembresia.estado_display}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Fecha Inicio:</span>
                        <span className="font-medium">
                          {formatDate(selectedMembresia.fecha_inicio)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Fecha Fin:</span>
                        <span className="font-medium">
                          {formatDate(selectedMembresia.fecha_fin)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Duración:</span>
                        <span className="font-medium">
                          {selectedMembresia.duracion_dias} días
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Días Restantes:</span>
                        <span
                          className={`font-medium ${
                            (selectedMembresia.dias_restantes || 0) > 7
                              ? "text-green-600"
                              : (selectedMembresia.dias_restantes || 0) > 0
                              ? "text-yellow-600"
                              : "text-red-600"
                          }`}
                        >
                          {(selectedMembresia.dias_restantes || 0) > 0
                            ? `${selectedMembresia.dias_restantes} días`
                            : "Vencida"}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Registrado por:</span>
                        <span className="font-medium">
                          {selectedMembresia.usuario_registro_nombre}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-6">
                  <button
                    onClick={() => {
                      setShowDetailModal(false);
                      setSelectedMembresia(null);
                    }}
                    className="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-2 px-4 rounded-lg"
                  >
                    Cerrar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
