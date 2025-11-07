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
import asistenciaService, {
  InscritoClase,
  InscritosClaseResponse,
} from "@/lib/services/asistencia.service";
import { getClases } from "@/lib/services/clase.service";

export default function AsistenciasPage() {
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
        <span className="px-3 py-1 text-xs font-medium rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
          Sin registrar
        </span>
      );
    }

    const badges: Record<string, { bg: string; text: string; icon: any }> = {
      presente: {
        bg: "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400",
        text: "Presente",
        icon: CheckCircle,
      },
      ausente: {
        bg: "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400",
        text: "Ausente",
        icon: XCircle,
      },
      tardanza: {
        bg: "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400",
        text: "Tardanza",
        icon: Clock,
      },
      justificado: {
        bg: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400",
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
      {/* Header con gradiente */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg">
            <Activity className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
              Control de Asistencias
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Registra la asistencia de clientes a las clases programadas
            </p>
          </div>
        </div>
      </div>

      {/* Selector de Clase - Card mejorado */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2 mb-4">
          <Calendar className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <label className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
            Seleccionar Clase
          </label>
        </div>
        <select
          value={claseSeleccionada || ""}
          onChange={(e) => handleSeleccionarClase(Number(e.target.value))}
          className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border-2 border-gray-200 dark:border-gray-600 rounded-xl text-gray-900 dark:text-gray-100 focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 dark:focus:border-blue-400 transition-all duration-200 cursor-pointer font-medium"
        >
          <option value="">-- Selecciona una clase --</option>
          {clases.map((clase) => (
            <option key={clase.id} value={clase.id}>
              {clase.disciplina_nombre} - {clase.fecha} {clase.hora_inicio} ({clase.salon_nombre})
            </option>
          ))}
        </select>
      </div>

      {/* Información de la Clase - Cards con iconos */}
      {claseInfo && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-2 border-blue-200 dark:border-blue-800 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500 rounded-lg">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs font-medium text-blue-700 dark:text-blue-300 uppercase">Disciplina</p>
                <p className="text-lg font-bold text-blue-900 dark:text-blue-100">{claseInfo.disciplina}</p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-2 border-purple-200 dark:border-purple-800 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-500 rounded-lg">
                <Calendar className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs font-medium text-purple-700 dark:text-purple-300 uppercase">Fecha</p>
                <p className="text-lg font-bold text-purple-900 dark:text-purple-100">{claseInfo.fecha}</p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-2 border-green-200 dark:border-green-800 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-500 rounded-lg">
                <Clock className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs font-medium text-green-700 dark:text-green-300 uppercase">Horario</p>
                <p className="text-lg font-bold text-green-900 dark:text-green-100">
                  {claseInfo.hora_inicio} - {claseInfo.hora_fin}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 border-2 border-orange-200 dark:border-orange-800 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-500 rounded-lg">
                <MapPin className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs font-medium text-orange-700 dark:text-orange-300 uppercase">Salón</p>
                <p className="text-lg font-bold text-orange-900 dark:text-orange-100">{claseInfo.salon}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Estadísticas */}
      {inscritos.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border-2 border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Inscritos</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-1">{totalInscritos}</p>
              </div>
              <div className="p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
                <Users className="w-6 h-6 text-gray-600 dark:text-gray-400" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border-2 border-blue-200 dark:border-blue-700 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Registrados</p>
                <p className="text-3xl font-bold text-blue-700 dark:text-blue-300 mt-1">{totalRegistrados}</p>
              </div>
              <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <UserCheck className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border-2 border-green-200 dark:border-green-700 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-600 dark:text-green-400">Presentes</p>
                <p className="text-3xl font-bold text-green-700 dark:text-green-300 mt-1">{totalPresentes}</p>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl p-5 border-2 border-indigo-400 shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-white/90">% Asistencia</p>
                <p className="text-3xl font-bold text-white mt-1">{porcentajeAsistencia}%</p>
              </div>
              <div className="p-3 bg-white/20 rounded-lg backdrop-blur-sm">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filtros y Búsqueda */}
      {inscritos.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-5 border border-gray-200 dark:border-gray-700">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Búsqueda */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por nombre o CI..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-gray-50 dark:bg-gray-700 border-2 border-gray-200 dark:border-gray-600 rounded-xl text-gray-900 dark:text-gray-100 focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 dark:focus:border-blue-400 transition-all"
              />
            </div>

            {/* Filtro por estado */}
            <div className="relative min-w-[200px]">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={filtroEstado}
                onChange={(e) => setFiltroEstado(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-gray-50 dark:bg-gray-700 border-2 border-gray-200 dark:border-gray-600 rounded-xl text-gray-900 dark:text-gray-100 focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 dark:focus:border-blue-400 transition-all cursor-pointer"
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
          <p className="text-gray-600 dark:text-gray-400 font-medium">Cargando inscritos...</p>
        </div>
      ) : inscritosFiltrados.length > 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden border border-gray-200 dark:border-gray-700">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 border-b-2 border-gray-200 dark:border-gray-600">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4" />
                      Cliente
                    </div>
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                    CI
                  </th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {inscritosFiltrados.map((inscrito, index) => (
                  <tr
                    key={inscrito.inscripcion_id}
                    className={`hover:bg-blue-50 dark:hover:bg-gray-700/50 transition-colors ${
                      index % 2 === 0 ? "bg-white dark:bg-gray-800" : "bg-gray-50/50 dark:bg-gray-800/50"
                    }`}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-bold shadow-md">
                          {inscrito.cliente_nombre.charAt(0)}
                        </div>
                        <span className="font-semibold text-gray-900 dark:text-gray-100">
                          {inscrito.cliente_nombre}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400 font-medium">
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
                          className="group p-2.5 bg-green-500 hover:bg-green-600 text-white rounded-lg disabled:opacity-50 transition-all duration-200 shadow-md hover:shadow-lg hover:scale-105 disabled:hover:scale-100"
                          title="Presente"
                        >
                          <CheckCircle className="w-4 h-4 group-hover:scale-110 transition-transform" />
                        </button>
                        <button
                          onClick={() => handleMarcarAsistencia(inscrito, "ausente")}
                          disabled={guardando}
                          className="group p-2.5 bg-red-500 hover:bg-red-600 text-white rounded-lg disabled:opacity-50 transition-all duration-200 shadow-md hover:shadow-lg hover:scale-105 disabled:hover:scale-100"
                          title="Ausente"
                        >
                          <XCircle className="w-4 h-4 group-hover:scale-110 transition-transform" />
                        </button>
                        <button
                          onClick={() => handleMarcarAsistencia(inscrito, "tardanza")}
                          disabled={guardando}
                          className="group p-2.5 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg disabled:opacity-50 transition-all duration-200 shadow-md hover:shadow-lg hover:scale-105 disabled:hover:scale-100"
                          title="Tardanza"
                        >
                          <Clock className="w-4 h-4 group-hover:scale-110 transition-transform" />
                        </button>
                        <button
                          onClick={() => handleMarcarAsistencia(inscrito, "justificado")}
                          disabled={guardando}
                          className="group p-2.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg disabled:opacity-50 transition-all duration-200 shadow-md hover:shadow-lg hover:scale-105 disabled:hover:scale-100"
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
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 px-6 py-4 border-t-2 border-gray-200 dark:border-gray-600">
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Mostrando <span className="font-bold text-blue-600 dark:text-blue-400">{inscritosFiltrados.length}</span> de{" "}
                <span className="font-bold">{inscritos.length}</span> inscritos
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Registrados: <span className="font-bold text-green-600 dark:text-green-400">{totalRegistrados}</span>
              </div>
            </div>
          </div>
        </div>
      ) : claseSeleccionada ? (
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-16 text-center border border-gray-200 dark:border-gray-700">
          <div className="max-w-md mx-auto">
            <div className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <Activity className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              No hay inscritos para esta clase
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              La clase seleccionada no tiene clientes inscritos en este momento
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 rounded-2xl shadow-lg p-16 text-center border-2 border-dashed border-blue-300 dark:border-gray-600">
          <div className="max-w-md mx-auto">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
              <Calendar className="w-10 h-10 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Selecciona una clase
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Elige una clase del menú desplegable para ver los inscritos y registrar su asistencia
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
