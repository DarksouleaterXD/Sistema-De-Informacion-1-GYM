"use client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import {
  Search,
  Plus,
  Edit,
  Trash2,
  X,
  Save,
  Phone,
  Calendar,
  Loader2,
  Award,
  User,
} from "lucide-react";
import { Instructor,
  instructorService,
  CreateInstructorDTO,
  UpdateInstructorDTO,
} from "@/lib/services/instructor.service";
import { Card, Button, Input } from "@/components/ui";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PermissionCodes } from "@/lib/utils/permissions";
import { userService } from "@/lib/services/user.service";

type ModalMode = "create" | "edit" | null;

function InstructorsPageContent() {
  const [instructors, setInstructors] = useState<Instructor[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const [selectedInstructor, setSelectedInstructor] = useState<Instructor | null>(null);
  const [formData, setFormData] = useState<CreateInstructorDTO | UpdateInstructorDTO>({
    usuario_id: 0,
    especialidades: "",
    experiencia_anos: 0,
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    total: 0,
  });

  const loadInstructors = async () => {
    try {
      setLoading(true);
      const response = await instructorService.getAll({
        search: searchTerm,
        page: pagination.page,
        page_size: pagination.pageSize,
      });
      setInstructors(response.results);
      setPagination((prev) => ({ ...prev, total: response.count }));
    } catch (error: any) {
      console.error("Error al cargar instructores:", error);
      alert("Error al cargar los instructores");
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await userService.getAll({});
      setUsers(response.results);
    } catch (error) {
      console.error("Error al cargar usuarios:", error);
    }
  };

  useEffect(() => {
    loadInstructors();
  }, [searchTerm, pagination.page]);

  useEffect(() => {
    if (modalMode === "create") {
      loadUsers();
    }
  }, [modalMode]);

  const handleCreate = () => {
    setModalMode("create");
    setFormData({
      usuario_id: 0,
      especialidades: "",
      experiencia_anos: 0,
      activo: true,
    });
    setFormErrors({});
    setSelectedInstructor(null);
  };

  const handleEdit = (instructor: Instructor) => {
    setModalMode("edit");
    setSelectedInstructor(instructor);
    setFormData({
      especialidades: instructor.especialidades,
      certificaciones: instructor.certificaciones || "",
      experiencia_anos: instructor.experiencia_anos,
      telefono: instructor.telefono || "",
      telefono_emergencia: instructor.telefono_emergencia || "",
      biografia: instructor.biografia || "",
      foto_url: instructor.foto_url || "",
      activo: instructor.activo,
      fecha_ingreso: instructor.fecha_ingreso || "",
    });
    setFormErrors({});
  };

  const handleCloseModal = () => {
    setModalMode(null);
    setSelectedInstructor(null);
    setFormData({
      usuario_id: 0,
      especialidades: "",
      experiencia_anos: 0,
    });
    setFormErrors({});
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (modalMode === "create") {
      const createData = formData as CreateInstructorDTO;
      if (!createData.usuario_id) {
        errors.usuario_id = "Debes seleccionar un usuario";
      }
    }

    if (!formData.especialidades?.trim()) {
      errors.especialidades = "Las especialidades son obligatorias";
    }

    if (!formData.experiencia_anos || formData.experiencia_anos < 0) {
      errors.experiencia_anos = "Los años de experiencia deben ser un número positivo";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    try {
      setSubmitting(true);
      if (modalMode === "create") {
        await instructorService.create(formData as CreateInstructorDTO);
        alert("Instructor creado exitosamente");
      } else if (modalMode === "edit" && selectedInstructor) {
        await instructorService.update(
          selectedInstructor.id,
          formData as UpdateInstructorDTO
        );
        alert("Instructor actualizado exitosamente");
      }
      handleCloseModal();
      loadInstructors();
    } catch (error: any) {
      console.error("Error al guardar:", error);
      if (error.errors) {
        setFormErrors(error.errors);
      } else {
        alert(error.message || "Error al guardar el instructor");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (instructor: Instructor) => {
    if (!confirm(`¿Estás seguro de desactivar a ${instructor.nombre_completo}?`))
      return;

    try {
      await instructorService.delete(instructor.id);
      alert("Instructor desactivado exitosamente");
      loadInstructors();
    } catch (error: any) {
      console.error("Error al desactivar:", error);
      alert(error.message || "Error al desactivar el instructor");
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Instructores</h1>
            <p className="text-gray-600 mt-1">
              Gestiona los perfiles de los instructores del gimnasio
            </p>
          </div>
          <Button onClick={handleCreate}>
            <Plus className="h-5 w-5 mr-2" />
            Nuevo Instructor
          </Button>
        </div>

        <Card>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por nombre, email o especialidades..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setPagination((prev) => ({ ...prev, page: 1 }));
              }}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
            />
          </div>
        </Card>

        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <Loader2 className="animate-spin h-12 w-12 text-blue-600 mx-auto" />
              <p className="mt-4 text-gray-600">Cargando instructores...</p>
            </div>
          ) : instructors.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-gray-600">No se encontraron instructores</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Instructor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Especialidades
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Experiencia
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {instructors.map((instructor) => (
                    <tr key={instructor.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            {instructor.foto_url ? (
                              <img
                                className="h-10 w-10 rounded-full"
                                src={instructor.foto_url}
                                alt=""
                              />
                            ) : (
                              <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                                <User className="h-6 w-6 text-blue-600" />
                              </div>
                            )}
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {instructor.nombre_completo}
                            </div>
                            <div className="text-sm text-gray-500">
                              {instructor.email}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {instructor.especialidades}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center text-sm text-gray-900">
                          <Award className="h-4 w-4 mr-2 text-yellow-500" />
                          {instructor.experiencia_anos} años
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            instructor.activo
                              ? "bg-green-100 text-green-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {instructor.activo ? "Activo" : "Inactivo"}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleEdit(instructor)}
                          className="text-blue-600 hover:text-blue-900 mr-4"
                        >
                          <Edit className="h-5 w-5" />
                        </button>
                        <button
                          onClick={() => handleDelete(instructor)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="h-5 w-5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {!loading && instructors.length > 0 && (
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-600">
              Mostrando {instructors.length} de {pagination.total} instructores
            </p>
            <div className="flex gap-2">
              <Button
                onClick={() =>
                  setPagination((prev) => ({ ...prev, page: prev.page - 1 }))
                }
                disabled={pagination.page === 1}
                variant="secondary"
              >
                Anterior
              </Button>
              <Button
                onClick={() =>
                  setPagination((prev) => ({ ...prev, page: prev.page + 1 }))
                }
                disabled={
                  pagination.page * pagination.pageSize >= pagination.total
                }
                variant="secondary"
              >
                Siguiente
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Modal Create/Edit */}
      {modalMode && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  {modalMode === "create"
                    ? "Nuevo Instructor"
                    : "Editar Instructor"}
                </h2>
                <button
                  onClick={handleCloseModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-4">
                {modalMode === "create" && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Usuario *
                    </label>
                    <select
                      value={(formData as CreateInstructorDTO).usuario_id || 0}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          usuario_id: parseInt(e.target.value),
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                    >
                      <option value="0">Seleccione un usuario</option>
                      {users.map((user) => (
                        <option key={user.id} value={user.id}>
                          {user.first_name} {user.last_name} ({user.email})
                        </option>
                      ))}
                    </select>
                    {formErrors.usuario_id && (
                      <p className="mt-1 text-sm text-red-600">
                        {formErrors.usuario_id}
                      </p>
                    )}
                  </div>
                )}

                <Input
                  label="Especialidades *"
                  type="text"
                  value={formData.especialidades}
                  onChange={(e) =>
                    setFormData({ ...formData, especialidades: e.target.value })
                  }
                  error={formErrors.especialidades}
                  placeholder="ej: Yoga, Spinning, CrossFit"
                />

                <Input
                  label="Años de Experiencia *"
                  type="number"
                  min="0"
                  value={formData.experiencia_anos?.toString() || "0"}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      experiencia_anos: parseInt(e.target.value) || 0,
                    })
                  }
                  error={formErrors.experiencia_anos}
                />

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Certificaciones
                  </label>
                  <textarea
                    value={formData.certificaciones || ""}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        certificaciones: e.target.value,
                      })
                    }
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                    placeholder="Certificaciones y títulos profesionales"
                  />
                </div>

                <Input
                  label="Teléfono"
                  type="text"
                  value={formData.telefono || ""}
                  onChange={(e) =>
                    setFormData({ ...formData, telefono: e.target.value })
                  }
                  maxLength={20}
                />

                <Input
                  label="Fecha de Ingreso"
                  type="date"
                  value={formData.fecha_ingreso || ""}
                  onChange={(e) =>
                    setFormData({ ...formData, fecha_ingreso: e.target.value })
                  }
                />
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <Button
                  onClick={handleCloseModal}
                  disabled={submitting}
                  variant="secondary"
                >
                  Cancelar
                </Button>
                <Button onClick={handleSave} disabled={submitting}>
                  {submitting ? (
                    <>
                      <Loader2 className="animate-spin h-5 w-5 mr-2" />
                      Guardando...
                    </>
                  ) : (
                    <>
                      <Save className="h-5 w-5 mr-2" />
                      Guardar
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}

export default function InstructorsPage() {
  return (
    <ProtectedRoute requiredPermission={PermissionCodes.INSTRUCTOR_VIEW}>
      <InstructorsPageContent />
    </ProtectedRoute>
  );
}
