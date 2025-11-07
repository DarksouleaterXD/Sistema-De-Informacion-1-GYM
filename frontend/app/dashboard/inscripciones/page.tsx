"use client";

/**
 * CU21: Inscribir Cliente a Clase
 * Página para gestionar inscripciones de clientes a clases programadas
 * 
 * Actores: Superusuario, Administrador, Instructor
 * Validaciones:
 * - Cliente con membresía activa
 * - Clase con cupo disponible
 * - Cliente no puede inscribirse dos veces en la misma clase
 */

import { useState, useEffect } from "react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PermissionCodes } from "@/lib/utils/permissions";
import inscripcionClaseService, {
  InscripcionClase,
  CreateInscripcionDTO,
} from "@/lib/services/inscripcion-clase.service";
import claseService, { Clase } from "@/lib/services/clase.service";
import { clientService } from "@/lib/services/client.service";
import { Client } from "@/lib/types";
import { Button, Card, Badge } from "@/components/ui";

// ==================== MODAL INSCRIBIR ====================

interface InscribirModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

function InscribirModal({ isOpen, onClose, onSuccess }: InscribirModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [clases, setClases] = useState<Clase[]>([]);
  const [clientes, setClientes] = useState<Client[]>([]);
  const [formData, setFormData] = useState<CreateInscripcionDTO>({
    clase: 0,
    cliente: 0,
    observaciones: "",
  });

  // Cargar clases disponibles y clientes al abrir modal
  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [clasesData, clientesData] = await Promise.all([
        claseService.getClasesDisponibles({ estado: "programada" }),
        clientService.getClients(),
      ]);

      setClases(clasesData);
      setClientes(clientesData);

      if (clasesData.length === 0) {
        setError("No hay clases disponibles con cupos libres");
      }
    } catch (err: any) {
      console.error("Error cargando datos:", err);
      setError(err.message || "Error al cargar clases y clientes");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.clase || !formData.cliente) {
      setError("Debe seleccionar una clase y un cliente");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      await inscripcionClaseService.create({
        clase: formData.clase,
        cliente: formData.cliente,
        observaciones: formData.observaciones || undefined,
      });

      onSuccess();
      onClose();
      resetForm();
    } catch (err: any) {
      console.error("Error al inscribir:", err);
      
      // Extraer mensaje de error del backend
      if (err.response?.data) {
        const errorData = err.response.data;
        if (errorData.clase) {
          setError(errorData.clase[0]);
        } else if (errorData.cliente) {
          setError(errorData.cliente[0]);
        } else if (errorData.non_field_errors) {
          setError(errorData.non_field_errors[0]);
        } else if (typeof errorData === 'string') {
          setError(errorData);
        } else {
          setError("Error al inscribir cliente");
        }
      } else {
        setError(err.message || "Error al inscribir cliente");
      }
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      clase: 0,
      cliente: 0,
      observaciones: "",
    });
    setError(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header con degradado */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white px-6 py-4 rounded-t-lg">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
              Inscribir Cliente a Clase
            </h2>
            <button
              onClick={handleClose}
              className="text-white hover:text-gray-200 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6">
          {loading && !clases.length && !clientes.length ? (
            <div className="flex flex-col items-center justify-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
              <p className="text-gray-600">Cargando datos...</p>
            </div>
          ) : (
            <>
              {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                  <svg className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h4 className="text-red-800 font-semibold mb-1">Error al cargar datos</h4>
                    <p className="text-red-700 text-sm">{error}</p>
                  </div>
                </div>
              )}

              <div className="space-y-4">
                {/* Select Clase */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Clase *
                  </label>
                  <select
                    value={formData.clase}
                    onChange={(e) => setFormData({ ...formData, clase: Number(e.target.value) })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                    disabled={loading || clases.length === 0}
                  >
                    <option value={0}>Seleccione una clase</option>
                    {clases.map((clase) => (
                      <option key={clase.id} value={clase.id}>
                        {clase.disciplina_nombre} - {clase.fecha} {clase.hora_inicio} 
                        {clase.cupos_disponibles !== undefined && ` (${clase.cupos_disponibles} cupos)`}
                      </option>
                    ))}
                  </select>
                  {formData.clase > 0 && (
                    <p className="mt-1 text-xs text-green-600">
                      ✓ Clase con cupos disponibles
                    </p>
                  )}
                </div>

                {/* Select Cliente */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Cliente *
                  </label>
                  <select
                    value={formData.cliente}
                    onChange={(e) => setFormData({ ...formData, cliente: Number(e.target.value) })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                    disabled={loading}
                  >
                    <option value={0}>Seleccione un cliente</option>
                    {clientes.map((cliente) => (
                      <option key={cliente.id} value={cliente.id}>
                        {cliente.nombre} {cliente.apellido} - CI: {cliente.ci}
                      </option>
                    ))}
                  </select>
                  <p className="mt-1 text-xs text-gray-500">
                    ⚠️ El cliente debe tener membresía activa
                  </p>
                </div>

                {/* Observaciones */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Observaciones (opcional)
                  </label>
                  <textarea
                    value={formData.observaciones}
                    onChange={(e) => setFormData({ ...formData, observaciones: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Notas adicionales..."
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Footer con botones */}
              <div className="flex justify-end gap-3 mt-6 pt-4 border-t">
                <Button
                  type="button"
                  onClick={handleClose}
                  variant="outline"
                  disabled={loading}
                >
                  Cancelar
                </Button>
                <Button
                  type="submit"
                  disabled={loading || clases.length === 0}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {loading ? (
                    <>
                      <span className="animate-spin mr-2">⏳</span>
                      Inscribiendo...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Inscribir
                    </>
                  )}
                </Button>
              </div>
            </>
          )}
        </form>
      </div>
    </div>
  );
}

// ==================== MODAL ELIMINAR ====================

interface DeleteModalProps {
  isOpen: boolean;
  inscripcion: InscripcionClase | null;
  onClose: () => void;
  onConfirm: () => void;
  loading: boolean;
}

function DeleteModal({ isOpen, inscripcion, onClose, onConfirm, loading }: DeleteModalProps) {
  if (!isOpen || !inscripcion) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="p-6">
          <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full mb-4">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          
          <h3 className="text-lg font-semibold text-gray-900 text-center mb-2">
            Eliminar Inscripción
          </h3>
          
          <p className="text-gray-600 text-center mb-6">
            ¿Está seguro que desea eliminar la inscripción de{" "}
            <span className="font-semibold">{inscripcion.cliente_nombre}</span> a la clase{" "}
            <span className="font-semibold">{inscripcion.clase_info}</span>?
          </p>

          <div className="flex gap-3">
            <Button
              onClick={onClose}
              variant="outline"
              disabled={loading}
              className="flex-1"
            >
              Cancelar
            </Button>
            <Button
              onClick={onConfirm}
              disabled={loading}
              className="flex-1 bg-red-600 hover:bg-red-700 text-white"
            >
              {loading ? "Eliminando..." : "Eliminar"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ==================== PÁGINA PRINCIPAL ====================

function InscripcionesPageContent() {
  const [inscripciones, setInscripciones] = useState<InscripcionClase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Paginación
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 10;

  // Filtros
  const [searchTerm, setSearchTerm] = useState("");
  const [estadoFilter, setEstadoFilter] = useState("");

  // Modales
  const [showInscribirModal, setShowInscribirModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedInscripcion, setSelectedInscripcion] = useState<InscripcionClase | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  useEffect(() => {
    loadInscripciones();
  }, [currentPage, estadoFilter]);

  const loadInscripciones = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await inscripcionClaseService.getAll({
        page: currentPage,
        page_size: pageSize,
        estado: estadoFilter || undefined,
        search: searchTerm || undefined,
      });

      setInscripciones(Array.isArray(response.results) ? response.results : []);
      setTotalCount(response.count);
      setTotalPages(Math.ceil(response.count / pageSize));
    } catch (err: any) {
      console.error("Error cargando inscripciones:", err);
      setError("Error al cargar inscripciones");
      setInscripciones([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    loadInscripciones();
  };

  const handleDelete = async () => {
    if (!selectedInscripcion) return;

    try {
      setDeleteLoading(true);
      await inscripcionClaseService.delete(selectedInscripcion.id);
      
      setShowDeleteModal(false);
      setSelectedInscripcion(null);
      loadInscripciones();
    } catch (err: any) {
      console.error("Error eliminando inscripción:", err);
      alert("Error al eliminar inscripción");
    } finally {
      setDeleteLoading(false);
    }
  };

  const getEstadoBadgeColor = (estado: string) => {
    const colors: Record<string, string> = {
      confirmada: "bg-blue-100 text-blue-800",
      cancelada: "bg-red-100 text-red-800",
      asistio: "bg-green-100 text-green-800",
      no_asistio: "bg-yellow-100 text-yellow-800",
    };
    return colors[estado] || "bg-gray-100 text-gray-800";
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Inscripciones a Clases
          </h1>
          <p className="text-gray-600">
            CU21: Gestión de inscripciones de clientes a clases programadas
          </p>
        </div>

        {/* Filtros y Acciones */}
        <Card className="mb-6">
          <div className="flex flex-col md:flex-row gap-4 items-end">
            {/* Búsqueda */}
            <form onSubmit={handleSearch} className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Buscar
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Buscar por cliente o clase..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <Button type="submit" variant="outline">
                  Buscar
                </Button>
              </div>
            </form>

            {/* Filtro Estado */}
            <div className="w-full md:w-48">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Estado
              </label>
              <select
                value={estadoFilter}
                onChange={(e) => {
                  setEstadoFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos</option>
                <option value="confirmada">Confirmada</option>
                <option value="cancelada">Cancelada</option>
                <option value="asistio">Asistió</option>
                <option value="no_asistio">No Asistió</option>
              </select>
            </div>

            {/* Botón Inscribir */}
            <Button
              onClick={() => setShowInscribirModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white whitespace-nowrap"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Inscribir Cliente
            </Button>
          </div>
        </Card>

        {/* Tabla */}
        <Card>
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
              <p className="text-gray-600">Cargando inscripciones...</p>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <svg className="w-12 h-12 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-gray-600 mb-4">{error}</p>
              <Button onClick={loadInscripciones} variant="outline">
                Reintentar
              </Button>
            </div>
          ) : inscripciones.length === 0 ? (
            <div className="text-center py-12">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-gray-600 mb-4">
                No hay inscripciones registradas
              </p>
              <Button onClick={() => setShowInscribirModal(true)}>
                Crear primera inscripción
              </Button>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Cliente
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Clase
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Fecha Clase
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Horario
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Estado
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Fecha Inscripción
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {inscripciones.map((inscripcion) => (
                      <tr key={inscripcion.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {inscripcion.cliente_nombre}
                          </div>
                          <div className="text-sm text-gray-500">
                            CI: {inscripcion.cliente_ci}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">
                            {inscripcion.disciplina_nombre}
                          </div>
                          <div className="text-sm text-gray-500">
                            {inscripcion.cupos_disponibles !== undefined &&
                              `${inscripcion.cupos_disponibles} cupos disponibles`}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {inscripcion.fecha_clase}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {inscripcion.hora_inicio} - {inscripcion.hora_fin}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge className={getEstadoBadgeColor(inscripcion.estado)}>
                            {inscripcion.estado_display}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(inscripcion.fecha_inscripcion).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => {
                              setSelectedInscripcion(inscripcion);
                              setShowDeleteModal(true);
                            }}
                            className="text-red-600 hover:text-red-900 transition-colors"
                            title="Eliminar"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Paginación */}
              {totalPages > 1 && (
                <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                  <div className="text-sm text-gray-700">
                    Mostrando <span className="font-medium">{(currentPage - 1) * pageSize + 1}</span> a{" "}
                    <span className="font-medium">
                      {Math.min(currentPage * pageSize, totalCount)}
                    </span>{" "}
                    de <span className="font-medium">{totalCount}</span> resultados
                  </div>
                  
                  <div className="flex gap-2">
                    <Button
                      onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      variant="outline"
                      size="sm"
                    >
                      Anterior
                    </Button>
                    
                    <div className="flex items-center gap-1">
                      {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                        let pageNum;
                        if (totalPages <= 5) {
                          pageNum = i + 1;
                        } else if (currentPage <= 3) {
                          pageNum = i + 1;
                        } else if (currentPage >= totalPages - 2) {
                          pageNum = totalPages - 4 + i;
                        } else {
                          pageNum = currentPage - 2 + i;
                        }

                        return (
                          <button
                            key={i}
                            onClick={() => setCurrentPage(pageNum)}
                            className={`px-3 py-1 rounded ${
                              currentPage === pageNum
                                ? "bg-blue-600 text-white"
                                : "bg-white text-gray-700 hover:bg-gray-100 border"
                            }`}
                          >
                            {pageNum}
                          </button>
                        );
                      })}
                    </div>

                    <Button
                      onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      variant="outline"
                      size="sm"
                    >
                      Siguiente
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </Card>

        {/* Modales */}
        <InscribirModal
          isOpen={showInscribirModal}
          onClose={() => setShowInscribirModal(false)}
          onSuccess={loadInscripciones}
        />

        <DeleteModal
          isOpen={showDeleteModal}
          inscripcion={selectedInscripcion}
          onClose={() => {
            setShowDeleteModal(false);
            setSelectedInscripcion(null);
          }}
          onConfirm={handleDelete}
          loading={deleteLoading}
        />
      </div>
    </DashboardLayout>
  );
}

export default function InscripcionesPage() {
  return (
    <ProtectedRoute requiredPermission={PermissionCodes.ENROLLMENT_VIEW}>
      <InscripcionesPageContent />
    </ProtectedRoute>
  );
}
