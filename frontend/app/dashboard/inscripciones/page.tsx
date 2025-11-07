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
} from "@/lib/services/inscripcion-clase.service";
import claseService, { Clase } from "@/lib/services/clase.service";
import clientService, { Client } from "@/lib/services/client.service";
import { Button, Card, Badge } from "@/components/ui";

interface InscribirModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

function InscribirModal({ isOpen, onClose, onSuccess }: InscribirModalProps) {
  const [clases, setClases] = useState<Clase[]>([]);
  const [clientes, setClientes] = useState<Client[]>([]);
  const [selectedClase, setSelectedClase] = useState<number | "">("");
  const [selectedCliente, setSelectedCliente] = useState<number | "">("");
  const [observaciones, setObservaciones] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    setLoadingData(true);
    setError("");
    try {
      const [clasesData, clientesData] = await Promise.all([
        claseService.getClasesDisponibles({ estado: "programada" }),
        clientService.getClients(),
      ]);
      
      // Filtrar solo clases con cupos disponibles
      const clasesDisponibles = clasesData.filter(
        (clase) => clase.cupos_disponibles && clase.cupos_disponibles > 0
      );
      
      setClases(clasesDisponibles);
      setClientes(clientesData);
      
      if (clasesDisponibles.length === 0) {
        setError("No hay clases programadas con cupos disponibles");
      }
    } catch (err: any) {
      console.error("Error cargando datos:", err);
      setError(err?.message || "Error al cargar clases y clientes. Por favor, verifica que el backend esté funcionando.");
    } finally {
      setLoadingData(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedClase || !selectedCliente) {
      setError("Debe seleccionar una clase y un cliente");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await inscripcionClaseService.createInscripcionClase({
        clase: Number(selectedClase),
        cliente: Number(selectedCliente),
        observaciones: observaciones || undefined,
      });

      alert("Cliente inscrito exitosamente");
      onSuccess();
      handleClose();
    } catch (err: any) {
      console.error("Error al inscribir:", err);
      
      // Mostrar errores específicos de validación
      if (err.errors) {
        const errorMessages = Object.entries(err.errors)
          .map(([field, messages]) => `${field}: ${(messages as string[]).join(", ")}`)
          .join("\n");
        setError(errorMessages);
      } else {
        setError(err.message || "Error al inscribir cliente");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSelectedClase("");
    setSelectedCliente("");
    setObservaciones("");
    setError("");
    onClose();
  };

  if (!isOpen) return null;

  const claseSeleccionada = clases.find((c) => c.id === selectedClase);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header del Modal */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white">Inscribir Cliente a Clase</h2>
          <button
            onClick={handleClose}
            className="text-white hover:text-gray-200 text-3xl font-bold leading-none"
            type="button"
          >
            ×
          </button>
        </div>

        {/* Contenido del Modal */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          {loadingData ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Cargando clases y clientes...</p>
            </div>
          ) : error && !clases.length && !clientes.length ? (
            <div className="text-center py-12">
              <div className="mb-4 text-red-600">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-red-600 font-semibold mb-2">Error al cargar datos</p>
              <p className="text-gray-600 mb-4">{error}</p>
              <button
                onClick={loadData}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                type="button"
              >
                Reintentar
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Seleccionar Clase */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Clase <span className="text-red-500">*</span>
                </label>
                <select
                  value={selectedClase}
                  onChange={(e) => setSelectedClase(e.target.value ? Number(e.target.value) : "")}
                  required
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                >
                  <option value="">-- Seleccionar clase --</option>
                  {clases.length === 0 ? (
                    <option disabled>No hay clases disponibles</option>
                  ) : (
                    clases.map((clase) => (
                      <option key={clase.id} value={clase.id}>
                        {clase.disciplina_nombre} - {clase.fecha} {clase.hora_inicio} 
                        ({clase.instructor_nombre}) - {clase.cupos_disponibles} cupos disponibles
                      </option>
                    ))
                  )}
                </select>
                {claseSeleccionada && (
                  <div className="mt-3 p-4 bg-gradient-to-r from-blue-50 to-blue-100 border-l-4 border-blue-500 rounded-r-lg">
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <p className="text-gray-600">Salón</p>
                        <p className="font-semibold text-gray-900">{claseSeleccionada.salon_nombre}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Horario</p>
                        <p className="font-semibold text-gray-900">
                          {claseSeleccionada.hora_inicio} - {claseSeleccionada.hora_fin}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Cupos disponibles</p>
                        <p className="font-semibold text-green-600">
                          {claseSeleccionada.cupos_disponibles} de {claseSeleccionada.cupo_maximo}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Estado</p>
                        <p className="font-semibold text-gray-900">{claseSeleccionada.estado_display}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Seleccionar Cliente */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Cliente <span className="text-red-500">*</span>
                </label>
                <select
                  value={selectedCliente}
                  onChange={(e) => setSelectedCliente(e.target.value ? Number(e.target.value) : "")}
                  required
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                >
                  <option value="">-- Seleccionar cliente --</option>
                  {clientes.length === 0 ? (
                    <option disabled>No hay clientes registrados</option>
                  ) : (
                    clientes.map((cliente) => (
                      <option key={cliente.id} value={cliente.id}>
                        {cliente.nombre_completo} - CI: {cliente.ci}
                      </option>
                    ))
                  )}
                </select>
                <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start">
                  <svg className="w-5 h-5 text-yellow-600 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <p className="text-xs text-yellow-800">
                    El sistema verificará automáticamente que el cliente tenga una membresía activa antes de inscribirlo.
                  </p>
                </div>
              </div>

              {/* Observaciones */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Observaciones (Opcional)
                </label>
                <textarea
                  value={observaciones}
                  onChange={(e) => setObservaciones(e.target.value)}
                  rows={3}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-none"
                  placeholder="Información adicional sobre la inscripción..."
                />
              </div>

              {/* Error */}
              {error && (
                <div className="p-4 bg-red-50 border-l-4 border-red-500 rounded-r-lg">
                  <div className="flex items-start">
                    <svg className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-sm text-red-700 whitespace-pre-line">{error}</p>
                  </div>
                </div>
              )}

              {/* Botones */}
              <div className="flex justify-end space-x-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={handleClose}
                  disabled={loading}
                  className="px-6 py-2.5 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading || !selectedClase || !selectedCliente}
                  className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Inscribiendo...
                    </>
                  ) : (
                    "Inscribir Cliente"
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

function InscripcionesClasePageContent() {
  const [inscripciones, setInscripciones] = useState<InscripcionClase[]>([]);
  const [loading, setLoading] = useState(true);
  const [showInscribirModal, setShowInscribirModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterEstado, setFilterEstado] = useState<string>("");

  useEffect(() => {
    loadInscripciones();
  }, []);

  const loadInscripciones = async () => {
    setLoading(true);
    try {
      const data = await inscripcionClaseService.getInscripcionesClase();
      setInscripciones(data);
    } catch (error) {
      console.error("Error al cargar inscripciones:", error);
      alert("Error al cargar las inscripciones");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number, clienteNombre: string) => {
    if (!confirm(`¿Está seguro de cancelar la inscripción de ${clienteNombre}?`)) {
      return;
    }

    try {
      await inscripcionClaseService.deleteInscripcionClase(id);
      alert("Inscripción cancelada exitosamente");
      loadInscripciones();
    } catch (error) {
      console.error("Error al cancelar inscripción:", error);
      alert("Error al cancelar la inscripción");
    }
  };

  // Filtrar inscripciones
  const inscripcionesFiltradas = Array.isArray(inscripciones) 
    ? inscripciones.filter((inscripcion) => {
        const matchSearch =
          inscripcion.cliente_nombre?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          inscripcion.disciplina_nombre?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          inscripcion.cliente_ci?.includes(searchTerm);

        const matchEstado = !filterEstado || inscripcion.estado === filterEstado;

        return matchSearch && matchEstado;
      })
    : [];

  const getEstadoBadgeColor = (estado: string) => {
    switch (estado) {
      case "confirmada":
        return "bg-green-100 text-green-800";
      case "cancelada":
        return "bg-red-100 text-red-800";
      case "pendiente":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Inscripciones a Clases
          </h1>
          <p className="text-gray-600 mt-1">
            Gestión de inscripciones de clientes a clases programadas
          </p>
        </div>

        {/* Filtros y Acciones */}
        <Card className="mb-6">
          <div className="flex flex-col md:flex-row gap-4 md:items-center md:justify-between">
            {/* Búsqueda */}
            <div className="flex-1 max-w-md">
              <input
                type="text"
                placeholder="Buscar por cliente, disciplina o CI..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Filtro Estado */}
            <select
              value={filterEstado}
              onChange={(e) => setFilterEstado(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos los estados</option>
              <option value="confirmada">Confirmada</option>
              <option value="cancelada">Cancelada</option>
              <option value="pendiente">Pendiente</option>
            </select>

            {/* Botón Inscribir */}
            <Button onClick={() => setShowInscribirModal(true)}>
              + Inscribir Cliente
            </Button>
          </div>
        </Card>

        {/* Tabla de Inscripciones */}
        {loading ? (
          <Card>
            <div className="text-center py-12">
              <p className="text-gray-600">Cargando inscripciones...</p>
            </div>
          </Card>
        ) : inscripcionesFiltradas.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <p className="text-gray-600">
                {searchTerm || filterEstado
                  ? "No se encontraron inscripciones con los filtros aplicados"
                  : "No hay inscripciones registradas"}
              </p>
            </div>
          </Card>
        ) : (
          <Card>
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
                      Fecha/Hora
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Instructor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fecha Inscripción
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {inscripcionesFiltradas.map((inscripcion) => (
                    <tr key={inscripcion.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <div className="font-medium text-gray-900">
                            {inscripcion.cliente_nombre}
                          </div>
                          <div className="text-sm text-gray-500">
                            CI: {inscripcion.cliente_ci}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-medium text-gray-900">
                          {inscripcion.disciplina_nombre}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {inscripcion.fecha_clase}
                        </div>
                        <div className="text-sm text-gray-500">
                          {inscripcion.hora_clase}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {inscripcion.instructor_nombre}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <Badge className={getEstadoBadgeColor(inscripcion.estado)}>
                          {inscripcion.estado_display}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(inscripcion.fecha_inscripcion).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {inscripcion.estado !== "cancelada" && (
                          <button
                            onClick={() => handleDelete(inscripcion.id, inscripcion.cliente_nombre)}
                            className="text-red-600 hover:text-red-900 font-medium"
                          >
                            Cancelar
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Totales */}
            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
              <p className="text-sm text-gray-600">
                Total de inscripciones: <strong>{inscripcionesFiltradas.length}</strong>
              </p>
            </div>
          </Card>
        )}

        {/* Modal Inscribir */}
        <InscribirModal
          isOpen={showInscribirModal}
          onClose={() => setShowInscribirModal(false)}
          onSuccess={loadInscripciones}
        />
      </div>
    </DashboardLayout>
  );
}

export default function InscripcionesClasePage() {
  return (
    <ProtectedRoute requiredPermission={PermissionCodes.INSCRIPCION_CLASE_VIEW}>
      <InscripcionesClasePageContent />
    </ProtectedRoute>
  );
}
