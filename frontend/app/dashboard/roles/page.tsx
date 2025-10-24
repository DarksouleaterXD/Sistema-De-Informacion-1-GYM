"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import {
  Shield,
  Plus,
  Eye,
  Edit,
  Trash2,
  X,
  Users,
  Check,
  XCircle,
} from "lucide-react";
import {
  roleService,
  Role,
  RoleCreate,
  RoleUpdate,
} from "@/lib/services/role.service";

export default function RolesPage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);

  const [formData, setFormData] = useState<RoleCreate>({
    nombre: "",
    descripcion: "",
  });

  const [updateData, setUpdateData] = useState<RoleUpdate>({
    nombre: "",
    descripcion: "",
  });

  useEffect(() => {
    loadRoles();
  }, []);

  const loadRoles = async () => {
    try {
      setLoading(true);
      const data = await roleService.getAll();
      setRoles(data);
    } catch (error) {
      console.error("Error al cargar roles:", error);
      alert("Error al cargar los roles");
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    if (!formData.nombre.trim()) {
      alert("El nombre del rol es requerido");
      return;
    }

    try {
      await roleService.create(formData);
      setShowCreateModal(false);
      setFormData({ nombre: "", descripcion: "" });
      await loadRoles(); // Esperar a que cargue antes de mostrar el alert
      alert("Rol creado exitosamente");
    } catch (error: any) {
      console.error("Error al crear rol:", error);
      const errorMsg =
        error.errors?.nombre?.[0] || error.message || "Error al crear el rol";
      alert(errorMsg);
    }
  };

  const handleUpdate = async () => {
    if (!selectedRole) return;
    try {
      await roleService.update(selectedRole.id, updateData);
      setShowEditModal(false);
      setSelectedRole(null);
      await loadRoles();
      alert("Rol actualizado exitosamente");
    } catch (error: any) {
      console.error("Error al actualizar rol:", error);
      const errorMsg =
        error.errors?.nombre?.[0] ||
        error.message ||
        "Error al actualizar el rol";
      alert(errorMsg);
    }
  };

  const handleDelete = async (id: number, nombre: string) => {
    if (!confirm(`¿Está seguro de eliminar el rol "${nombre}"?`)) return;
    try {
      await roleService.delete(id);
      await loadRoles();
      alert("Rol eliminado exitosamente");
    } catch (error) {
      console.error("Error al eliminar rol:", error);
      alert("Error al eliminar el rol. Puede tener usuarios asignados.");
    }
  };

  const openEditModal = (role: Role) => {
    setSelectedRole(role);
    setUpdateData({
      nombre: role.nombre,
      descripcion: role.descripcion || "",
    });
    setShowEditModal(true);
  };

  const openDetailModal = async (role: Role) => {
    try {
      const fullRole = await roleService.getById(role.id);
      setSelectedRole(fullRole);
      setShowDetailModal(true);
    } catch (error) {
      console.error("Error al cargar detalle:", error);
      alert("Error al cargar el detalle del rol");
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Roles y Permisos
            </h1>
            <p className="text-gray-600 mt-1">
              Gestiona los roles y permisos del sistema
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            Nuevo Rol
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Roles</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  {Array.isArray(roles) ? roles.length : 0}
                </p>
              </div>
              <Shield className="h-12 w-12 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Usuarios</p>
                <p className="text-3xl font-bold text-purple-600 mt-1">
                  {Array.isArray(roles)
                    ? roles.reduce((sum, r) => sum + r.usuarios_count, 0)
                    : 0}
                </p>
              </div>
              <Users className="h-12 w-12 text-purple-600" />
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <p className="text-gray-600">Cargando roles...</p>
            </div>
          ) : roles.length === 0 ? (
            <div className="p-8 text-center">
              <Shield className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No hay roles registrados</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Nombre
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Descripción
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Usuarios
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Permisos
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {Array.isArray(roles) &&
                    roles.map((role) => (
                      <tr key={role.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <Shield className="h-5 w-5 text-blue-600 mr-2" />
                            <span className="text-sm font-medium text-gray-900">
                              {role.nombre}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-sm text-gray-600">
                            {role.descripcion || "Sin descripción"}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center text-sm text-gray-900">
                            <Users className="h-4 w-4 mr-1 text-purple-600" />
                            {role.usuarios_count}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm text-gray-900">
                            {role.permisos.length} permisos
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => openDetailModal(role)}
                              className="text-blue-600 hover:text-blue-800"
                              title="Ver detalle"
                            >
                              <Eye className="h-5 w-5" />
                            </button>
                            <button
                              onClick={() => openEditModal(role)}
                              className="text-yellow-600 hover:text-yellow-800"
                              title="Editar"
                            >
                              <Edit className="h-5 w-5" />
                            </button>
                            <button
                              onClick={() => handleDelete(role.id, role.nombre)}
                              className="text-red-600 hover:text-red-800"
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
          )}
        </div>

        {/* Modal Crear */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">
                  Nuevo Rol
                </h2>
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setFormData({ nombre: "", descripcion: "" });
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              <form onSubmit={handleCreate} className="p-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nombre *
                    </label>
                    <input
                      type="text"
                      value={formData.nombre}
                      onChange={(e) =>
                        setFormData({ ...formData, nombre: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Descripción
                    </label>
                    <textarea
                      value={formData.descripcion}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          descripcion: e.target.value,
                        })
                      }
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                    />
                  </div>
                </div>

                <div className="flex gap-3 mt-6">
                  <button
                    type="submit"
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg"
                  >
                    Crear Rol
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false);
                      setFormData({
                        nombre: "",
                        descripcion: "",
                      });
                    }}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-2 px-4 rounded-lg"
                  >
                    Cancelar
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal Editar */}
        {showEditModal && selectedRole && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">
                  Editar Rol
                </h2>
                <button
                  onClick={() => {
                    setShowEditModal(false);
                    setSelectedRole(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              <div className="p-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nombre *
                    </label>
                    <input
                      type="text"
                      value={updateData.nombre}
                      onChange={(e) =>
                        setUpdateData({ ...updateData, nombre: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Descripción
                    </label>
                    <textarea
                      value={updateData.descripcion}
                      onChange={(e) =>
                        setUpdateData({
                          ...updateData,
                          descripcion: e.target.value,
                        })
                      }
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                    />
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
                      setSelectedRole(null);
                    }}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-2 px-4 rounded-lg"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Modal Detalle */}
        {showDetailModal && selectedRole && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">
                  Detalle del Rol
                </h2>
                <button
                  onClick={() => {
                    setShowDetailModal(false);
                    setSelectedRole(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              <div className="p-6 space-y-6">
                {/* Información Básica */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Información Básica
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Nombre</p>
                      <p className="text-base font-medium text-gray-900 mt-1">
                        {selectedRole.nombre}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Fecha de Creación</p>
                      <p className="text-base text-gray-900 mt-1">
                        {new Date(selectedRole.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="col-span-2">
                      <p className="text-sm text-gray-600">Descripción</p>
                      <p className="text-base text-gray-900 mt-1">
                        {selectedRole.descripcion || "Sin descripción"}
                      </p>
                    </div>
                    <div className="col-span-2">
                      <p className="text-sm text-gray-600">
                        Usuarios Asignados
                      </p>
                      <p className="text-base font-medium text-gray-900 mt-1 flex items-center">
                        <Users className="h-4 w-4 mr-1 text-purple-600" />
                        {selectedRole.usuarios_count}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Permisos */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Permisos Asignados ({selectedRole.permisos.length})
                  </h3>
                  {selectedRole.permisos.length === 0 ? (
                    <p className="text-gray-600">No tiene permisos asignados</p>
                  ) : (
                    <div className="grid grid-cols-1 gap-2">
                      {selectedRole.permisos.map((permiso) => (
                        <div
                          key={permiso.id}
                          className="flex items-start p-3 bg-blue-50 rounded-lg"
                        >
                          <Check className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {permiso.nombre}
                            </p>
                            {permiso.descripcion && (
                              <p className="text-xs text-gray-600 mt-0.5">
                                {permiso.descripcion}
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="sticky bottom-0 bg-gray-50 px-6 py-4">
                <button
                  onClick={() => {
                    setShowDetailModal(false);
                    setSelectedRole(null);
                  }}
                  className="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-2 px-4 rounded-lg"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
