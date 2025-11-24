"use client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import {
  Search,
  Plus,
  Edit,
  Trash2,
  Building2,
  Phone,
  Mail,
  MapPin,
  User,
  FileText,
  Loader2,
  CheckCircle,
  XCircle,
  Ban,
  RefreshCw,
} from "lucide-react";
import { Proveedor, CreateProveedorDTO, proveedorService } from "@/lib/services/proveedor.service";
import { Card, Button, Input } from "@/components/ui";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PermissionCodes } from "@/lib/utils/permissions";

type ModalMode = "create" | "edit" | null;

function ProveedoresPageContent() {
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [estadoFilter, setEstadoFilter] = useState<string>("");
  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const [selectedProveedor, setSelectedProveedor] = useState<Proveedor | null>(null);
  const [formData, setFormData] = useState<CreateProveedorDTO>({
    razon_social: "",
    nit: "",
    telefono: "",
    email: "",
    direccion: "",
    contacto_nombre: "",
    notas: "",
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    total: 0,
  });

  // Cargar proveedores
  const loadProveedores = async () => {
    try {
      setLoading(true);
      const response = await proveedorService.getAll({
        search: searchTerm,
        estado: estadoFilter,
        page: pagination.page,
        page_size: pagination.pageSize,
      });
      setProveedores(response?.results || []);
      setPagination((prev) => ({ ...prev, total: response?.count || 0 }));
    } catch (error: any) {
      console.error("Error al cargar proveedores:", error);
      setProveedores([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProveedores();
  }, [searchTerm, estadoFilter, pagination.page]);

  const handleCreate = () => {
    setModalMode("create");
    setFormData({
      razon_social: "",
      nit: "",
      telefono: "",
      email: "",
      direccion: "",
      contacto_nombre: "",
      notas: "",
    });
    setFormErrors({});
    setSelectedProveedor(null);
  };

  const handleEdit = (proveedor: Proveedor) => {
    setModalMode("edit");
    setSelectedProveedor(proveedor);
    setFormData({
      razon_social: proveedor.razon_social,
      nit: proveedor.nit,
      telefono: proveedor.telefono || "",
      email: proveedor.email || "",
      direccion: proveedor.direccion || "",
      contacto_nombre: proveedor.contacto_nombre || "",
      notas: proveedor.notas || "",
    });
    setFormErrors({});
  };

  const handleDeactivate = async (id: number, razonSocial: string) => {
    if (!confirm(`¿Está seguro de desactivar el proveedor "${razonSocial}"?\n\nEsto cambiará su estado a Inactivo, pero podrá reactivarlo después.`)) return;

    try {
      await proveedorService.deactivate(id);
      alert("Proveedor desactivado exitosamente");
      loadProveedores();
    } catch (error: any) {
      console.error("Error al desactivar proveedor:", error);
      alert(error.response?.data?.detail || "Error al desactivar proveedor");
    }
  };

  const handleDeletePermanent = async (id: number, razonSocial: string) => {
    if (!confirm(`⚠️ ADVERTENCIA: ¿Está seguro de ELIMINAR PERMANENTEMENTE el proveedor "${razonSocial}"?\n\n❌ Esta acción NO SE PUEDE DESHACER.\n❌ El proveedor será eliminado completamente de la base de datos.\n\nEscriba "ELIMINAR" para confirmar:`)) return;

    const confirmation = prompt('Para confirmar, escriba "ELIMINAR" (en mayúsculas):');
    if (confirmation !== "ELIMINAR") {
      alert("Eliminación cancelada");
      return;
    }

    try {
      await proveedorService.deletePermanent(id);
      alert("Proveedor eliminado permanentemente");
      loadProveedores();
    } catch (error: any) {
      console.error("Error al eliminar proveedor:", error);
      alert(error.response?.data?.detail || "Error al eliminar proveedor");
    }
  };

  const handleActivate = async (id: number, razonSocial: string) => {
    if (!confirm(`¿Está seguro de activar el proveedor "${razonSocial}"?\n\nEsto cambiará su estado a Activo.`)) return;

    try {
      await proveedorService.activate(id);
      alert("Proveedor activado exitosamente");
      loadProveedores();
    } catch (error: any) {
      console.error("Error al activar proveedor:", error);
      alert(error.response?.data?.detail || "Error al activar proveedor");
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.razon_social?.trim()) {
      errors.razon_social = "La razón social es obligatoria";
    }

    if (!formData.nit?.trim()) {
      errors.nit = "El NIT es obligatorio";
    }

    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = "Email inválido";
    }

    if (formData.telefono && !/^\d{7,15}$/.test(formData.telefono.replace(/\D/g, ""))) {
      errors.telefono = "El teléfono debe tener entre 7 y 15 dígitos";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      setSubmitting(true);

      if (modalMode === "create") {
        await proveedorService.create(formData);
        alert("Proveedor creado exitosamente");
      } else if (modalMode === "edit" && selectedProveedor) {
        // Enviar todos los datos del formulario
        await proveedorService.update(selectedProveedor.id, formData);
        alert("Proveedor actualizado exitosamente");
      }

      setModalMode(null);
      loadProveedores();
    } catch (error: any) {
      console.error("Error al guardar proveedor:", error);
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === "object") {
          setFormErrors(detail);
        } else {
          alert(detail);
        }
      } else {
        alert("Error al guardar el proveedor");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <DashboardLayout title="Proveedores" description="Gestión de proveedores del gimnasio">
      <div className="space-y-6">
        {/* Barra de búsqueda y filtros */}
        <Card className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Buscar por razón social, NIT, email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={estadoFilter}
              onChange={(e) => setEstadoFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos los estados</option>
              <option value="A">Activos</option>
              <option value="I">Inactivos</option>
              <option value="S">Suspendidos</option>
            </select>
            <Button onClick={handleCreate} className="flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Nuevo Proveedor
            </Button>
          </div>
        </Card>

        {/* Lista de proveedores */}
        <Card className="overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
          ) : proveedores.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              No se encontraron proveedores
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Proveedor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contacto
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Dirección
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Notas
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fecha Registro
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {proveedores.map((proveedor) => (
                    <tr key={proveedor.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <Building2 className="w-5 h-5 text-gray-400 mr-3" />
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {proveedor.razon_social}
                            </div>
                            <div className="text-sm text-gray-500">
                              NIT: {proveedor.nit}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {proveedor.telefono && (
                            <div className="flex items-center gap-1 mb-1">
                              <Phone className="w-4 h-4 text-gray-400" />
                              {proveedor.telefono}
                            </div>
                          )}
                          {proveedor.email && (
                            <div className="flex items-center gap-1">
                              <Mail className="w-4 h-4 text-gray-400" />
                              {proveedor.email}
                            </div>
                          )}
                          {!proveedor.telefono && !proveedor.email && (
                            <span className="text-gray-400">Sin contacto</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 max-w-xs">
                          {proveedor.direccion ? (
                            <div className="flex items-start gap-1">
                              <MapPin className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                              <span className="truncate" title={proveedor.direccion}>
                                {proveedor.direccion}
                              </span>
                            </div>
                          ) : (
                            <span className="text-gray-400">Sin dirección</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 max-w-xs">
                          {proveedor.notas ? (
                            <div className="flex items-start gap-1">
                              <FileText className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                              <span className="truncate" title={proveedor.notas}>
                                {proveedor.notas}
                              </span>
                            </div>
                          ) : (
                            <span className="text-gray-400">Sin notas</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            proveedor.estado === "A"
                              ? "bg-green-100 text-green-800"
                              : proveedor.estado === "I"
                              ? "bg-gray-100 text-gray-800"
                              : "bg-yellow-100 text-yellow-800"
                          }`}
                        >
                          {proveedor.esta_activo ? (
                            <CheckCircle className="w-3 h-3 mr-1" />
                          ) : (
                            <XCircle className="w-3 h-3 mr-1" />
                          )}
                          {proveedor.estado_display}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {new Date(proveedor.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-right text-sm font-medium">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleEdit(proveedor)}
                            className="text-blue-600 hover:text-blue-900 p-1 rounded hover:bg-blue-50"
                            title="Editar"
                          >
                            <Edit className="w-5 h-5" />
                          </button>
                          {proveedor.estado === "A" ? (
                            <button
                              onClick={() => handleDeactivate(proveedor.id, proveedor.razon_social)}
                              className="text-orange-600 hover:text-orange-900 p-1 rounded hover:bg-orange-50"
                              title="Desactivar (cambiar estado a Inactivo)"
                            >
                              <Ban className="w-5 h-5" />
                            </button>
                          ) : (
                            <button
                              onClick={() => handleActivate(proveedor.id, proveedor.razon_social)}
                              className="text-green-600 hover:text-green-900 p-1 rounded hover:bg-green-50"
                              title="Activar (cambiar estado a Activo)"
                            >
                              <RefreshCw className="w-5 h-5" />
                            </button>
                          )}
                          <button
                            onClick={() => handleDeletePermanent(proveedor.id, proveedor.razon_social)}
                            className="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50"
                            title="Eliminar permanentemente"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        {/* Paginación */}
        {pagination.total > pagination.pageSize && (
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Mostrando {(pagination.page - 1) * pagination.pageSize + 1} a{" "}
              {Math.min(pagination.page * pagination.pageSize, pagination.total)} de{" "}
              {pagination.total} proveedores
            </div>
            <div className="flex gap-2">
              <Button
                onClick={() => setPagination((p) => ({ ...p, page: p.page - 1 }))}
                disabled={pagination.page === 1}
                variant="outline"
              >
                Anterior
              </Button>
              <Button
                onClick={() => setPagination((p) => ({ ...p, page: p.page + 1 }))}
                disabled={pagination.page * pagination.pageSize >= pagination.total}
                variant="outline"
              >
                Siguiente
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Modal de Crear/Editar */}
      {modalMode && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">
                  {modalMode === "create" ? "Nuevo Proveedor" : "Editar Proveedor"}
                </h2>
                <button
                  onClick={() => setModalMode(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <Trash2 className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Razón Social */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Razón Social <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <Input
                      type="text"
                      value={formData.razon_social}
                      onChange={(e) =>
                        setFormData({ ...formData, razon_social: e.target.value })
                      }
                      className={`pl-10 ${formErrors.razon_social ? "border-red-500" : ""}`}
                      placeholder="Ej: Distribuidora ABC S.A."
                    />
                  </div>
                  {formErrors.razon_social && (
                    <p className="text-red-500 text-sm mt-1">{formErrors.razon_social}</p>
                  )}
                </div>

                {/* NIT */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    NIT / ID Fiscal <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <FileText className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <Input
                      type="text"
                      value={formData.nit}
                      onChange={(e) => setFormData({ ...formData, nit: e.target.value })}
                      className={`pl-10 ${formErrors.nit ? "border-red-500" : ""}`}
                      placeholder="Ej: 1234567890"
                      disabled={modalMode === "edit"}
                    />
                  </div>
                  {formErrors.nit && (
                    <p className="text-red-500 text-sm mt-1">{formErrors.nit}</p>
                  )}
                  {modalMode === "edit" && (
                    <p className="text-gray-500 text-sm mt-1">El NIT no se puede modificar</p>
                  )}
                </div>

                {/* Teléfono */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Teléfono
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <Input
                      type="text"
                      value={formData.telefono}
                      onChange={(e) =>
                        setFormData({ ...formData, telefono: e.target.value })
                      }
                      className={`pl-10 ${formErrors.telefono ? "border-red-500" : ""}`}
                      placeholder="Ej: 71234567"
                    />
                  </div>
                  {formErrors.telefono && (
                    <p className="text-red-500 text-sm mt-1">{formErrors.telefono}</p>
                  )}
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <Input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className={`pl-10 ${formErrors.email ? "border-red-500" : ""}`}
                      placeholder="Ej: contacto@proveedor.com"
                    />
                  </div>
                  {formErrors.email && (
                    <p className="text-red-500 text-sm mt-1">{formErrors.email}</p>
                  )}
                </div>

                {/* Dirección */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Dirección
                  </label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-3 text-gray-400 w-5 h-5" />
                    <textarea
                      value={formData.direccion}
                      onChange={(e) =>
                        setFormData({ ...formData, direccion: e.target.value })
                      }
                      className="w-full pl-10 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                      placeholder="Ej: Av. Principal #123, La Paz"
                      rows={2}
                    />
                  </div>
                </div>

                {/* Contacto Nombre */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Persona de Contacto
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <Input
                      type="text"
                      value={formData.contacto_nombre}
                      onChange={(e) =>
                        setFormData({ ...formData, contacto_nombre: e.target.value })
                      }
                      className="pl-10"
                      placeholder="Ej: Juan Pérez"
                    />
                  </div>
                </div>

                {/* Notas */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Notas</label>
                  <textarea
                    value={formData.notas}
                    onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                    placeholder="Observaciones adicionales..."
                    rows={3}
                  />
                </div>

                {/* Botones */}
                <div className="flex justify-end gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setModalMode(null)}
                    disabled={submitting}
                  >
                    Cancelar
                  </Button>
                  <Button type="submit" disabled={submitting}>
                    {submitting ? (
                      <>
                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        Guardando...
                      </>
                    ) : (
                      <>
                        <Plus className="w-5 h-5 mr-2" />
                        {modalMode === "create" ? "Crear Proveedor" : "Guardar Cambios"}
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}

export default function ProveedoresPage() {
  return (
    <ProtectedRoute requiredPermission={PermissionCodes.CLIENT_VIEW}>
      <ProveedoresPageContent />
    </ProtectedRoute>
  );
}
