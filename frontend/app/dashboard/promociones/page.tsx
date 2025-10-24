"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import {
  Tag,
  Plus,
  Eye,
  Edit,
  Trash2,
  X,
  Calendar,
  Percent,
  DollarSign,
  CheckCircle,
  XCircle,
} from "lucide-react";
import {
  promocionService,
  Promocion,
  PromocionCreate,
  PromocionUpdate,
} from "@/lib/services/promocion.service";

export default function PromocionesPage() {
  const [promociones, setPromociones] = useState<Promocion[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedPromocion, setSelectedPromocion] = useState<Promocion | null>(
    null
  );

  const [formData, setFormData] = useState<PromocionCreate>({
    nombre: "",
    meses: 1,
    descuento: 0,
    fecha_inicio: "",
    fecha_fin: "",
    estado: "ACTIVA",
  });

  const [updateData, setUpdateData] = useState<PromocionUpdate>({
    nombre: "",
    meses: 1,
    descuento: 0,
    fecha_inicio: "",
    fecha_fin: "",
    estado: "ACTIVA",
  });

  useEffect(() => {
    loadPromociones();
  }, []);

  const loadPromociones = async () => {
    try {
      setLoading(true);
      const data = await promocionService.getAll();
      setPromociones(data);
    } catch (error) {
      console.error("Error al cargar promociones:", error);
      alert("Error al cargar las promociones");
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await promocionService.create(formData);
      alert("Promoción creada exitosamente");
      setShowCreateModal(false);
      setFormData({
        nombre: "",
        meses: 1,
        descuento: 0,
        fecha_inicio: "",
        fecha_fin: "",
        estado: "ACTIVA",
      });
      loadPromociones();
    } catch (error: any) {
      console.error("Error al crear promoción:", error);
      alert(error.response?.data?.message || "Error al crear la promoción");
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPromocion) return;

    try {
      await promocionService.update(selectedPromocion.id, updateData);
      alert("Promoción actualizada exitosamente");
      setShowEditModal(false);
      setSelectedPromocion(null);
      loadPromociones();
    } catch (error: any) {
      console.error("Error al actualizar promoción:", error);
      alert(
        error.response?.data?.message || "Error al actualizar la promoción"
      );
    }
  };

  const handleDelete = async (id: number, nombre: string) => {
    if (!confirm(`¿Estás seguro de eliminar la promoción "${nombre}"?`)) {
      return;
    }

    try {
      await promocionService.delete(id);
      alert("Promoción eliminada exitosamente");
      loadPromociones();
    } catch (error) {
      console.error("Error al eliminar promoción:", error);
      alert("Error al eliminar la promoción");
    }
  };

  const handleViewDetail = async (id: number) => {
    try {
      const data = await promocionService.getById(id);
      setSelectedPromocion(data);
      setShowDetailModal(true);
    } catch (error) {
      console.error("Error al cargar detalle:", error);
      alert("Error al cargar el detalle de la promoción");
    }
  };

  const handleEdit = (promocion: Promocion) => {
    setSelectedPromocion(promocion);
    setUpdateData({
      nombre: promocion.nombre,
      meses: promocion.meses,
      descuento: parseFloat(promocion.descuento),
      fecha_inicio: promocion.fecha_inicio,
      fecha_fin: promocion.fecha_fin,
      estado: promocion.estado,
    });
    setShowEditModal(true);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("es-BO", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Promociones</h1>
            <p className="text-gray-600 mt-1">
              Gestiona las promociones y descuentos
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            Nueva Promoción
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Promociones</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  {Array.isArray(promociones) ? promociones.length : 0}
                </p>
              </div>
              <Tag className="h-12 w-12 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Activas</p>
                <p className="text-3xl font-bold text-green-600 mt-1">
                  {Array.isArray(promociones)
                    ? promociones.filter((p) => p.estado === 'ACTIVA').length
                    : 0}
                </p>
              </div>
              <CheckCircle className="h-12 w-12 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Vigentes Ahora</p>
                <p className="text-3xl font-bold text-purple-600 mt-1">
                  {Array.isArray(promociones)
                    ? promociones.filter((p) => p.esta_vigente).length
                    : 0}
                </p>
              </div>
              <Calendar className="h-12 w-12 text-purple-600" />
            </div>
          </div>
        </div>

        {/* Tabla */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Promoción
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Descuento
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duración
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vigencia
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
                {Array.isArray(promociones) &&
                  promociones.map((promocion) => (
                    <tr key={promocion.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <Tag className="h-5 w-5 text-blue-600 mr-2" />
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {promocion.nombre}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Percent className="h-4 w-4 text-green-600 mr-1" />
                          <span className="text-sm font-semibold text-green-600">
                            {promocion.descuento}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">
                          {promocion.meses} {promocion.meses === 1 ? 'mes' : 'meses'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-xs text-gray-600">
                          <div>{formatDate(promocion.fecha_inicio)}</div>
                          <div className="text-gray-400">hasta</div>
                          <div>{formatDate(promocion.fecha_fin)}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-col gap-1">
                          {promocion.estado === 'ACTIVA' ? (
                            <span className="inline-flex items-center px-2 py-1 text-xs font-medium text-green-800 bg-green-100 rounded-full">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Activa
                            </span>
                          ) : promocion.estado === 'VENCIDA' ? (
                            <span className="inline-flex items-center px-2 py-1 text-xs font-medium text-red-800 bg-red-100 rounded-full">
                              <XCircle className="h-3 w-3 mr-1" />
                              Vencida
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2 py-1 text-xs font-medium text-gray-800 bg-gray-100 rounded-full">
                              <XCircle className="h-3 w-3 mr-1" />
                              Inactiva
                            </span>
                          )}
                          {promocion.esta_vigente && (
                            <span className="inline-flex items-center px-2 py-1 text-xs font-medium text-purple-800 bg-purple-100 rounded-full">
                              <Calendar className="h-3 w-3 mr-1" />
                              Vigente
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleViewDetail(promocion.id)}
                            className="text-blue-600 hover:text-blue-900"
                            title="Ver detalle"
                          >
                            <Eye className="h-5 w-5" />
                          </button>
                          <button
                            onClick={() => handleEdit(promocion)}
                            className="text-yellow-600 hover:text-yellow-900"
                            title="Editar"
                          >
                            <Edit className="h-5 w-5" />
                          </button>
                          <button
                            onClick={() =>
                              handleDelete(promocion.id, promocion.nombre)
                            }
                            className="text-red-600 hover:text-red-900"
                            title="Eliminar"
                          >
                            <Trash2 className="h-5 w-5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>

          {loading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-sm text-gray-600">
                Cargando promociones...
              </p>
            </div>
          )}

          {!loading &&
            Array.isArray(promociones) &&
            promociones.length === 0 && (
              <div className="text-center py-12">
                <Tag className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No hay promociones registradas</p>
              </div>
            )}
        </div>

        {/* Modal Crear */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b">
                <h2 className="text-xl font-bold text-gray-900">
                  Nueva Promoción
                </h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              <form onSubmit={handleCreate} className="p-6 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Nombre <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.nombre}
                      onChange={(e) =>
                        setFormData({ ...formData, nombre: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Ej: Promoción Verano 2025"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Meses de Duración <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      required
                      min="1"
                      step="1"
                      value={formData.meses}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          meses: parseInt(e.target.value) || 1,
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="6"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Descuento (%) <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      required
                      min="0"
                      max="100"
                      step="0.01"
                      value={formData.descuento}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          descuento: parseFloat(e.target.value) || 0,
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="15.00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Fecha de Inicio <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      required
                      value={formData.fecha_inicio}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          fecha_inicio: e.target.value,
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Fecha de Fin <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      required
                      value={formData.fecha_fin}
                      onChange={(e) =>
                        setFormData({ ...formData, fecha_fin: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Estado <span className="text-red-500">*</span>
                    </label>
                    <select
                      required
                      value={formData.estado}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          estado: e.target.value as 'ACTIVA' | 'INACTIVA' | 'VENCIDA',
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="ACTIVA">Activa</option>
                      <option value="INACTIVA">Inactiva</option>
                      <option value="VENCIDA">Vencida</option>
                    </select>
                  </div>
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                  >
                    Crear Promoción
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal Editar */}
        {showEditModal && selectedPromocion && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b">
                <h2 className="text-xl font-bold text-gray-900">
                  Editar Promoción
                </h2>
                <button
                  onClick={() => {
                    setShowEditModal(false);
                    setSelectedPromocion(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              <form onSubmit={handleUpdate} className="p-6 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Nombre <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={updateData.nombre}
                      onChange={(e) =>
                        setUpdateData({ ...updateData, nombre: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Meses de Duración <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      required
                      min="1"
                      step="1"
                      value={updateData.meses}
                      onChange={(e) =>
                        setUpdateData({
                          ...updateData,
                          meses: parseInt(e.target.value) || 1,
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Descuento (%) <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      required
                      min="0"
                      max="100"
                      step="0.01"
                      value={updateData.descuento}
                      onChange={(e) =>
                        setUpdateData({
                          ...updateData,
                          descuento: parseFloat(e.target.value) || 0,
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Fecha de Inicio <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      required
                      value={updateData.fecha_inicio}
                      onChange={(e) =>
                        setUpdateData({
                          ...updateData,
                          fecha_inicio: e.target.value,
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Fecha de Fin <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      required
                      value={updateData.fecha_fin}
                      onChange={(e) =>
                        setUpdateData({
                          ...updateData,
                          fecha_fin: e.target.value,
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Estado <span className="text-red-500">*</span>
                    </label>
                    <select
                      required
                      value={updateData.estado}
                      onChange={(e) =>
                        setUpdateData({
                          ...updateData,
                          estado: e.target.value as 'ACTIVA' | 'INACTIVA' | 'VENCIDA',
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="ACTIVA">Activa</option>
                      <option value="INACTIVA">Inactiva</option>
                      <option value="VENCIDA">Vencida</option>
                    </select>
                  </div>
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t">
                  <button
                    type="button"
                    onClick={() => {
                      setShowEditModal(false);
                      setSelectedPromocion(null);
                    }}
                    className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                  >
                    Actualizar
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal Detalle */}
        {showDetailModal && selectedPromocion && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b">
                <h2 className="text-xl font-bold text-gray-900">
                  Detalle de Promoción
                </h2>
                <button
                  onClick={() => {
                    setShowDetailModal(false);
                    setSelectedPromocion(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              <div className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="text-sm font-medium text-gray-500">
                      Nombre
                    </label>
                    <p className="text-lg font-semibold text-gray-900">
                      {selectedPromocion.nombre}
                    </p>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-500">
                      Descuento
                    </label>
                    <p className="text-lg font-bold text-green-600">
                      {selectedPromocion.descuento}%
                    </p>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-500">
                      Duración
                    </label>
                    <p className="text-gray-900">
                      {selectedPromocion.meses} {selectedPromocion.meses === 1 ? 'mes' : 'meses'}
                    </p>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-500">
                      Fecha de Inicio
                    </label>
                    <p className="text-gray-900">
                      {formatDate(selectedPromocion.fecha_inicio)}
                    </p>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-500">
                      Fecha de Fin
                    </label>
                    <p className="text-gray-900">
                      {formatDate(selectedPromocion.fecha_fin)}
                    </p>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-500">
                      Estado
                    </label>
                    <div className="flex gap-2 mt-1">
                      {selectedPromocion.estado === 'ACTIVA' ? (
                        <span className="inline-flex items-center px-3 py-1 text-sm font-medium text-green-800 bg-green-100 rounded-full">
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Activa
                        </span>
                      ) : selectedPromocion.estado === 'VENCIDA' ? (
                        <span className="inline-flex items-center px-3 py-1 text-sm font-medium text-red-800 bg-red-100 rounded-full">
                          <XCircle className="h-4 w-4 mr-1" />
                          Vencida
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-3 py-1 text-sm font-medium text-gray-800 bg-gray-100 rounded-full">
                          <XCircle className="h-4 w-4 mr-1" />
                          Inactiva
                        </span>
                      )}
                    </div>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-500">
                      Vigencia
                    </label>
                    <div className="mt-1">
                      {selectedPromocion.esta_vigente ? (
                        <span className="inline-flex items-center px-3 py-1 text-sm font-medium text-purple-800 bg-purple-100 rounded-full">
                          <Calendar className="h-4 w-4 mr-1" />
                          Vigente
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-3 py-1 text-sm font-medium text-gray-800 bg-gray-100 rounded-full">
                          No vigente
                        </span>
                      )}
                    </div>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-500">
                      Fecha de Creación
                    </label>
                    <p className="text-gray-700 text-sm">
                      {formatDate(selectedPromocion.created_at)}
                    </p>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-500">
                      Última Actualización
                    </label>
                    <p className="text-gray-700 text-sm">
                      {formatDate(selectedPromocion.updated_at)}
                    </p>
                  </div>
                </div>

                <div className="flex justify-end pt-4 border-t">
                  <button
                    onClick={() => {
                      setShowDetailModal(false);
                      setSelectedPromocion(null);
                    }}
                    className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
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
