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
    try {
      const [clasesData, clientesData] = await Promise.all([
        claseService.getClases({ estado: "programada" }),
        clientService.getClients(),
      ]);
      
      // Filtrar solo clases futuras o de hoy con cupos disponibles
      const clasesDisponibles = clasesData.filter(
        (clase) => clase.cupos_disponibles > 0
      );
      
      setClases(clasesDisponibles);
      setClientes(clientesData);
    } catch (err) {
      console.error("Error cargando datos:", err);
      setError("Error al cargar clases y clientes");
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
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Inscribir Cliente a Clase</h2>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {loadingData ? (
          <div className="text-center py-8">
            <p className="text-gray-600">Cargando datos...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Seleccionar Clase */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Clase <span className="text-red-500">*</span>
              </label>
              <select
                value={selectedClase}
                onChange={(e) => setSelectedClase(e.target.value ? Number(e.target.value) : "")}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Seleccionar clase...</option>
                {clases.map((clase) => (
                  <option key={clase.id} value={clase.id}>
                    {clase.disciplina_nombre} - {clase.fecha} {clase.hora_inicio} 
                    ({clase.instructor_nombre}) - {clase.cupos_disponibles} cupos
                  </option>
                ))}
              </select>
              {claseSeleccionada && (
                <div className="mt-2 p-3 bg-blue-50 rounded-lg text-sm">
                  <p><strong>Salón:</strong> {claseSeleccionada.salon_nombre}</p>
                  <p><strong>Horario:</strong> {claseSeleccionada.hora_inicio} - {claseSeleccionada.hora_fin}</p>
                  <p><strong>Cupos disponibles:</strong> {claseSeleccionada.cupos_disponibles} de {claseSeleccionada.cupo_maximo}</p>
                </div>
              )}
            </div>

            {/* Seleccionar Cliente */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cliente <span className="text-red-500">*</span>
              </label>
              <select
                value={selectedCliente}
                onChange={(e) => setSelectedCliente(e.target.value ? Number(e.target.value) : "")}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Seleccionar cliente...</option>
                {clientes.map((cliente) => (
                  <option key={cliente.id} value={cliente.id}>
                    {cliente.nombre_completo} - CI: {cliente.ci}
                  </option>
                ))}
              </select>
              <p className="mt-1 text-xs text-gray-500">
                ⚠️ El sistema verificará que el cliente tenga membresía activa
              </p>
            </div>

            {/* Observaciones */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Observaciones
              </label>
              <textarea
                value={observaciones}
                onChange={(e) => setObservaciones(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Información adicional (opcional)"
              />
            </div>

            {/* Error */}
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600 whitespace-pre-line">{error}</p>
              </div>
            )}

            {/* Botones */}
            <div className="flex justify-end space-x-3">
              <Button
                type="button"
                onClick={handleClose}
                variant="outline"
                disabled={loading}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? "Inscribiendo..." : "Inscribir Cliente"}
              </Button>
            </div>
          </form>
        )}
      </Card>
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
