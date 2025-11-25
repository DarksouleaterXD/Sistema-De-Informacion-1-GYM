"use client";

import { useState, useEffect } from "react";
import {
  Activity,
  Users,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  Calendar,
  MapPin,
  User,
  Search,
  Filter,
  TrendingUp,
  UserCheck
} from "lucide-react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import asistenciaService, {
  InscritoClase,
  InscritosClaseResponse,
} from "@/lib/services/asistencia.service";
import { getClases } from "@/lib/services/clase.service";

export default function AsistenciasPage() {
  return (
    <ProtectedRoute requiredPermissions={['asistencia.view']}>
      <DashboardLayout>
        <AsistenciasContent />
      </DashboardLayout>
    </ProtectedRoute>
  );
}

function AsistenciasContent() {
  const [clases, setClases] = useState<any[]>([]);
  const [claseSeleccionada, setClaseSeleccionada] = useState<number | null>(null);
  const [inscritos, setInscritos] = useState<InscritoClase[]>([]);
  const [claseInfo, setClaseInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [filtroEstado, setFiltroEstado] = useState<string>("todos");
  const [busqueda, setBusqueda] = useState("");

  // Cargar clases disponibles
  useEffect(() => {
    loadClases();
  }, []);

  const loadClases = async () => {
    try {
      const response = await getClases(1, "");
      setClases(response.results);
    } catch (error) {
      console.error("Error cargando clases:", error);
    }
  };

  // Cargar inscritos cuando se selecciona una clase
  const handleSeleccionarClase = async (claseId: number) => {
    setClaseSeleccionada(claseId);
    setLoading(true);

    try {
      const response: InscritosClaseResponse =
        await asistenciaService.getInscritosClase(claseId);

      setInscritos(response.inscritos);
      setClaseInfo(response.clase_info);
    } catch (error) {
      console.error("Error cargando inscritos:", error);
    } finally {
      setLoading(false);
    }
  };

  // Marcar asistencia individual
  const handleMarcarAsistencia = async (
    inscrito: InscritoClase,
    estado: string
  ) => {
    setGuardando(true);

    try {
      if (inscrito.tiene_asistencia && inscrito.asistencia_id) {
        // Actualizar asistencia existente
        await asistenciaService.update(inscrito.asistencia_id, { estado } as any);
      } else {
        // Registrar nueva asistencia
        await asistenciaService.registrarAsistencia({
          inscripcion_id: inscrito.inscripcion_id,
          estado: estado as any,
        });
      }

      // Recargar lista
      if (claseSeleccionada) {
        await handleSeleccionarClase(claseSeleccionada);
      }
    } catch (error: any) {
      console.error("Error guardando asistencia:", error);

      // Mostrar mensaje de error específico
      let mensaje = "Error al registrar asistencia";

      if (error.response?.data) {
        const errorData = error.response.data;

        // Si hay un error de validación de fecha
        if (errorData.clase) {
          mensaje = Array.isArray(errorData.clase)
            ? errorData.clase[0]
            : errorData.clase;
        } else if (errorData.detail) {
          mensaje = errorData.detail;
        } else if (errorData.non_field_errors) {
          mensaje = Array.isArray(errorData.non_field_errors)
            ? errorData.non_field_errors[0]
            : errorData.non_field_errors;
        } else if (typeof errorData === "string") {
          mensaje = errorData;
        } else {
          // Intentar extraer el primer mensaje de error
          const primerError = Object.values(errorData)[0];
          if (Array.isArray(primerError)) {
            mensaje = primerError[0];
          } else {
            mensaje = String(primerError);
          }
        }
      }

      alert(mensaje);
    } finally {
      setGuardando(false);
    }
  };

  // Obtener badge de estado
  const getBadgeEstado = (inscrito: InscritoClase) => {
    if (!inscrito.tiene_asistencia) {
      return (
        <span className="px-3 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-600">
          Sin registrar
        </span>
      );
    }

    const badges: Record<string, { bg: string; text: string; icon: any }> = {
      presente: {
        bg: "bg-green-100 text-green-700",
        text: "Presente",
        icon: CheckCircle,
      },
      ausente: {
        bg: "bg-red-100 text-red-700",
        text: "Ausente",
        icon: XCircle,
      },
      tardanza: {
        bg: "bg-yellow-100 text-yellow-700",
        text: "Tardanza",
        icon: Clock,
      },
      justificado: {
        bg: "bg-blue-100 text-blue-700",
        text: "Justificado",
        icon: AlertCircle,
      },
    };

    const badge = badges[inscrito.estado || ""];
    if (!badge) return null;

    const Icon = badge.icon;

    return (
      <span className={`px-3 py-1 text-xs font-medium rounded-full flex items-center gap-1 ${badge.bg}`}>
        <Icon className="w-3 h-3" />
        {badge.text}
      </span>
    );
  };

  // Filtrar inscritos
  const inscritosFiltrados = inscritos.filter((inscrito) => {
    // Filtro por búsqueda
    const coincideBusqueda =
      busqueda === "" ||
      inscrito.cliente_nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
      inscrito.cliente_ci.includes(busqueda);

    // Filtro por estado
    if (filtroEstado === "todos") return coincideBusqueda;
    if (filtroEstado === "sin_registrar") return coincideBusqueda && !inscrito.tiene_asistencia;
    return coincideBusqueda && inscrito.estado === filtroEstado;
  });

  // Estadísticas
  const totalInscritos = inscritos.length;
  const totalRegistrados = inscritos.filter((i) => i.tiene_asistencia).length;
  const totalPresentes = inscritos.filter((i) => i.estado === "presente").length;
  const porcentajeAsistencia = totalInscritos > 0 ? Math.round((totalPresentes / totalInscritos) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Control de Asistencias</h1>
          <p className="text-gray-600 mt-1">Registra la asistencia de clientes a las clases programadas</p>
        </div>
      </div>

      {/* Selector de Clase */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-300">
        <div className="flex items-center gap-2 mb-4">
          <Calendar className="w-5 h-5 text-blue-600" />
          <label className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
            Seleccionar Clase
          </label>
        </div>
        <select
          value={claseSeleccionada || ""}
          onChange={(e) => handleSeleccionarClase(Number(e.target.value))}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
        >
          <option value="">-- Selecciona una clase --</option>
          {clases.map((clase) => (
            <option key={clase.id} value={clase.id}>
              {clase.disciplina_nombre} - {clase.fecha} {clase.hora_inicio} ({clase.salon_nombre})
            </option>
          ))}
        </select>
      </div>

      {/* Información de la Clase */}
      {claseInfo && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white border border-gray-300 rounded-lg p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Activity className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-xs font-medium text-gray-600 uppercase">Disciplina</p>
                <p className="text-lg font-bold text-gray-900">{claseInfo.disciplina}</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-300 rounded-lg p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Calendar className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-xs font-medium text-gray-600 uppercase">Fecha</p>
                <p className="text-lg font-bold text-gray-900">{claseInfo.fecha}</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-300 rounded-lg p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Clock className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-xs font-medium text-gray-600 uppercase">Horario</p>
                <p className="text-lg font-bold text-gray-900">
                  {claseInfo.hora_inicio} - {claseInfo.hora_fin}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-300 rounded-lg p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <MapPin className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <p className="text-xs font-medium text-gray-600 uppercase">Salón</p>
                <p className="text-lg font-bold text-gray-900">{claseInfo.salon}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Estadísticas */}
      {inscritos.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-5 border border-gray-300 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Inscritos</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{totalInscritos}</p>
              </div>
              <div className="p-3 bg-gray-100 rounded-lg">
                <Users className="w-6 h-6 text-gray-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-5 border border-gray-300 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-600">Registrados</p>
                <p className="text-3xl font-bold text-blue-700 mt-1">{totalRegistrados}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <UserCheck className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-5 border border-gray-300 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-600">Presentes</p>
                <p className="text-3xl font-bold text-green-700 mt-1">{totalPresentes}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-5 border border-gray-300 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-indigo-600">% Asistencia</p>
                <p className="text-3xl font-bold text-indigo-700 mt-1">{porcentajeAsistencia}%</p>
              </div>
              <div className="p-3 bg-indigo-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-indigo-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filtros y Búsqueda */}
      {inscritos.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-300">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Búsqueda */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por nombre o CI..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
              />
            </div>

            {/* Filtro por estado */}
            <div className="relative min-w-[200px]">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={filtroEstado}
                onChange={(e) => setFiltroEstado(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white appearance-none"
              >
                <option value="todos">Todos los estados</option>
                <option value="sin_registrar">Sin registrar</option>
                <option value="presente">Presentes</option>
                <option value="ausente">Ausentes</option>
                <option value="tardanza">Tardanzas</option>
                <option value="justificado">Justificados</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Tabla de Asistencia */}
      {loading ? (
        <div className="text-center py-20">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mb-4"></div>
          <p className="text-gray-600 font-medium">Cargando inscritos...</p>
        </div>
      ) : inscritosFiltrados.length > 0 ? (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden border border-gray-300">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-300">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4" />
                      Cliente
                    </div>
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    CI
                  </th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {inscritosFiltrados.map((inscrito, index) => (
                  <tr
                    key={inscrito.inscripcion_id}
                    className={`hover:bg-gray-50 transition-colors ${
                      index % 2 === 0 ? "bg-white" : "bg-gray-50"
                    }`}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold">
                          {inscrito.cliente_nombre.charAt(0)}
                        </div>
                        <span className="font-semibold text-gray-900">
                          {inscrito.cliente_nombre}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-600 font-medium">
                      {inscrito.cliente_ci}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex justify-center">
                        {getBadgeEstado(inscrito)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex justify-center gap-2">
                        <button
                          onClick={() => handleMarcarAsistencia(inscrito, "presente")}
                          disabled={guardando}
                          className="group p-2.5 bg-green-500 hover:bg-green-600 text-white rounded-lg disabled:opacity-50 transition-all duration-200 shadow-sm hover:shadow-md hover:scale-105 disabled:hover:scale-100"
                          title="Presente"
                        >
                          <CheckCircle className="w-4 h-4 group-hover:scale-110 transition-transform" />
                        </button>
                        <button
                          onClick={() => handleMarcarAsistencia(inscrito, "ausente")}
                          disabled={guardando}
                          className="group p-2.5 bg-red-500 hover:bg-red-600 text-white rounded-lg disabled:opacity-50 transition-all duration-200 shadow-sm hover:shadow-md hover:scale-105 disabled:hover:scale-100"
                          title="Ausente"
                        >
                          <XCircle className="w-4 h-4 group-hover:scale-110 transition-transform" />
                        </button>
                        <button
                          onClick={() => handleMarcarAsistencia(inscrito, "tardanza")}
                          disabled={guardando}
                          className="group p-2.5 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg disabled:opacity-50 transition-all duration-200 shadow-sm hover:shadow-md hover:scale-105 disabled:hover:scale-100"
                          title="Tardanza"
                        >
                          <Clock className="w-4 h-4 group-hover:scale-110 transition-transform" />
                        </button>
                        <button
                          onClick={() => handleMarcarAsistencia(inscrito, "justificado")}
                          disabled={guardando}
                          className="group p-2.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg disabled:opacity-50 transition-all duration-200 shadow-sm hover:shadow-md hover:scale-105 disabled:hover:scale-100"
                          title="Justificado"
                        >
                          <AlertCircle className="w-4 h-4 group-hover:scale-110 transition-transform" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Footer con resumen */}
          <div className="bg-gray-50 px-6 py-4 border-t border-gray-300">
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-gray-700">
                Mostrando <span className="font-bold text-blue-600">{inscritosFiltrados.length}</span> de{" "}
                <span className="font-bold">{inscritos.length}</span> inscritos
              </div>
              <div className="text-sm text-gray-600">
                Registrados: <span className="font-bold text-green-600">{totalRegistrados}</span>
              </div>
            </div>
          </div>
        </div>
      ) : claseSeleccionada ? (
        <div className="bg-white rounded-lg shadow-sm p-16 text-center border border-gray-300">
          <div className="max-w-md mx-auto">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Activity className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              No hay inscritos para esta clase
            </h3>
            <p className="text-gray-600">
              La clase seleccionada no tiene clientes inscritos en este momento
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm p-16 text-center border border-gray-300">
          <div className="max-w-md mx-auto">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Calendar className="w-10 h-10 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Selecciona una clase
            </h3>
            <p className="text-gray-600">
              Elige una clase del menú desplegable para ver los inscritos y registrar su asistencia
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
