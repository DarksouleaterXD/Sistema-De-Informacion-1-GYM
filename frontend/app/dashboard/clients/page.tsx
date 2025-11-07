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
  Mail,
  Calendar,
  Loader2,
} from "lucide-react";
import { Client } from "@/lib/types";
import { clientService, CreateClientDTO } from "@/lib/services/client.service";
import { Card, Button, Input } from "@/components/ui";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PermissionCodes } from "@/lib/utils/permissions";

type ModalMode = "create" | "edit" | null;

function ClientsPageContent() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [formData, setFormData] = useState<CreateClientDTO>({
    nombre: "",
    apellido: "",
    ci: "",
    telefono: "",
    email: "",
    peso: "",
    altura: "",
    experiencia: "principiante",
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    total: 0,
  });

  // Cargar clientes
  const loadClients = async () => {
    try {
      setLoading(true);
      const response = await clientService.getAll({
        search: searchTerm,
        page: pagination.page,
        page_size: pagination.pageSize,
      });
      setClients(response.results);
      setPagination((prev) => ({ ...prev, total: response.count }));
    } catch (error: any) {
      console.error("Error al cargar clientes:", error);
      alert("Error al cargar los clientes");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadClients();
  }, [searchTerm, pagination.page]);

  const handleCreate = () => {
    setModalMode("create");
    setFormData({
      nombre: "",
      apellido: "",
      ci: "",
      telefono: "",
      email: "",
      peso: "",
      altura: "",
      experiencia: "principiante",
    });
    setFormErrors({});
    setSelectedClient(null);
  };

  const handleEdit = (client: Client) => {
    setModalMode("edit");
    setSelectedClient(client);
    setFormData({
      nombre: client.nombre,
      apellido: client.apellido,
      ci: client.ci,
      telefono: client.telefono || "",
      email: client.email || "",
      peso: client.peso || "",
      altura: client.altura || "",
      experiencia: client.experiencia || "principiante",
    });
    setFormErrors({});
  };

  const handleCloseModal = () => {
    setModalMode(null);
    setSelectedClient(null);
    setFormData({
      nombre: "",
      apellido: "",
      ci: "",
      telefono: "",
      email: "",
      peso: "",
      altura: "",
      experiencia: "principiante",
    });
    setFormErrors({});
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.nombre.trim()) errors.nombre = "El nombre es obligatorio";
    if (!formData.apellido.trim())
      errors.apellido = "El apellido es obligatorio";
    if (!formData.ci.trim()) {
      errors.ci = "La CI es obligatoria";
    } else if (!/^\d{6,10}$/.test(formData.ci)) {
      errors.ci = "La CI debe tener entre 6 y 10 dígitos";
    }
    if (formData.telefono && !/^\d{8}$/.test(formData.telefono)) {
      errors.telefono = "El teléfono debe tener 8 dígitos";
    }
    if (formData.email && !/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = "El email no es válido";
    }
    if (
      formData.peso &&
      (parseFloat(formData.peso.toString()) < 20 ||
        parseFloat(formData.peso.toString()) > 300)
    ) {
      errors.peso = "El peso debe estar entre 20 y 300 kg";
    }
    if (
      formData.altura &&
      (parseFloat(formData.altura.toString()) < 0.5 ||
        parseFloat(formData.altura.toString()) > 2.5)
    ) {
      errors.altura = "La altura debe estar entre 0.5 y 2.5 metros";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    try {
      setSubmitting(true);
      if (modalMode === "create") {
        await clientService.create(formData);
        alert("Cliente creado exitosamente");
      } else if (modalMode === "edit" && selectedClient) {
        await clientService.update(selectedClient.id, formData);
        alert("Cliente actualizado exitosamente");
      }
      handleCloseModal();
      loadClients();
    } catch (error: any) {
      console.error("Error al guardar:", error);
      if (error.errors) {
        setFormErrors(error.errors);
      } else {
        alert(error.message || "Error al guardar el cliente");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (client: Client) => {
    if (!confirm(`¿Estás seguro de eliminar a ${client.nombre_completo}?`))
      return;

    try {
      await clientService.delete(client.id);
      alert("Cliente eliminado exitosamente");
      loadClients();
    } catch (error: any) {
      console.error("Error al eliminar:", error);
      alert(error.message || "Error al eliminar el cliente");
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("es-BO", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Clientes</h1>
            <p className="text-gray-600 mt-1">
              Gestiona la información de los clientes del gimnasio
            </p>
          </div>
          <Button onClick={handleCreate}>
            <Plus className="h-5 w-5 mr-2" />
            Nuevo Cliente
          </Button>
        </div>

        <Card>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por nombre, CI o email..."
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
              <p className="mt-4 text-gray-600">Cargando clientes...</p>
            </div>
          ) : clients.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-gray-600">No se encontraron clientes</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Cliente
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      CI
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Contacto
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Fecha Registro
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {clients.map((client) => (
                    <tr key={client.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <span className="text-blue-600 font-medium">
                              {client.nombre[0]}
                              {client.apellido[0]}
                            </span>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {client.nombre_completo}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{client.ci}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 space-y-1">
                          {client.telefono && (
                            <div className="flex items-center">
                              <Phone className="h-4 w-4 mr-2 text-gray-400" />
                              {client.telefono}
                            </div>
                          )}
                          {client.email && (
                            <div className="flex items-center">
                              <Mail className="h-4 w-4 mr-2 text-gray-400" />
                              {client.email}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center text-sm text-gray-900">
                          <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                          {formatDate(client.fecha_registro)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end gap-2">
                          <Button
                            onClick={() => handleEdit(client)}
                            variant="secondary"
                            size="sm"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            onClick={() => handleDelete(client)}
                            variant="danger"
                            size="sm"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {!loading && clients.length > 0 && (
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-600">
              Mostrando {clients.length} de {pagination.total} clientes
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

      {modalMode && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  {modalMode === "create" ? "Nuevo Cliente" : "Editar Cliente"}
                </h2>
                <button
                  onClick={handleCloseModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Nombre *"
                    type="text"
                    value={formData.nombre}
                    onChange={(e) =>
                      setFormData({ ...formData, nombre: e.target.value })
                    }
                    error={formErrors.nombre}
                  />

                  <Input
                    label="Apellido *"
                    type="text"
                    value={formData.apellido}
                    onChange={(e) =>
                      setFormData({ ...formData, apellido: e.target.value })
                    }
                    error={formErrors.apellido}
                  />
                </div>

                <Input
                  label="Cédula de Identidad *"
                  type="text"
                  value={formData.ci}
                  onChange={(e) =>
                    setFormData({ ...formData, ci: e.target.value })
                  }
                  error={formErrors.ci}
                  maxLength={10}
                />

                <Input
                  label="Teléfono"
                  type="text"
                  value={formData.telefono}
                  onChange={(e) =>
                    setFormData({ ...formData, telefono: e.target.value })
                  }
                  error={formErrors.telefono}
                  maxLength={8}
                />

                <Input
                  label="Email"
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  error={formErrors.email}
                />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Peso (kg)"
                    type="number"
                    step="0.01"
                    min="20"
                    max="300"
                    value={formData.peso}
                    onChange={(e) =>
                      setFormData({ ...formData, peso: e.target.value })
                    }
                    error={formErrors.peso}
                    placeholder="ej: 75.5"
                  />

                  <Input
                    label="Altura (m)"
                    type="number"
                    step="0.01"
                    min="0.5"
                    max="2.5"
                    value={formData.altura}
                    onChange={(e) =>
                      setFormData({ ...formData, altura: e.target.value })
                    }
                    error={formErrors.altura}
                    placeholder="ej: 1.75"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nivel de Experiencia
                  </label>
                  <select
                    value={formData.experiencia}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        experiencia: e.target.value as any,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                  >
                    <option value="principiante">Principiante</option>
                    <option value="intermedio">Intermedio</option>
                    <option value="avanzado">Avanzado</option>
                  </select>
                </div>
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

export default function ClientsPage() {
  return (
    <ProtectedRoute requiredPermission={PermissionCodes.CLIENT_VIEW}>
      <ClientsPageContent />
    </ProtectedRoute>
  );
}
