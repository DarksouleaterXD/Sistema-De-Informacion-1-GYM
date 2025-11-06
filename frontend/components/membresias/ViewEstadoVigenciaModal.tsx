"use client";

/**
 * CU17: Modal para Consultar Estado/Vigencia de Membresía
 */

import { useState, useEffect } from "react";
import { X, Calendar, Clock, TrendingUp, Tag, CheckCircle, XCircle, AlertCircle } from "lucide-react";
import membresiaService, { MembresiaEstadoVigencia } from "@/lib/services/membresia.service";

interface ViewEstadoVigenciaModalProps {
  isOpen: boolean;
  onClose: () => void;
  membresiaId?: number;
  clienteId?: number;
}

export default function ViewEstadoVigenciaModal({
  isOpen,
  onClose,
  membresiaId,
  clienteId,
}: ViewEstadoVigenciaModalProps) {
  const [data, setData] = useState<MembresiaEstadoVigencia | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen && (membresiaId || clienteId)) {
      fetchEstadoVigencia();
    }
  }, [isOpen, membresiaId, clienteId]);

  const fetchEstadoVigencia = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await membresiaService.consultarEstadoVigencia({
        membresiaId,
        clienteId,
      });
      setData(response);
    } catch (err: any) {
      setError(err.response?.data?.error || "Error al consultar el estado de la membresía");
      console.error("Error:", err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const getEstadoBadgeColor = (estado: string) => {
    switch (estado.toLowerCase()) {
      case "activo":
        return "bg-green-100 text-green-800 border-green-200";
      case "suspendido":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "cancelado":
        return "bg-red-100 text-red-800 border-red-200";
      case "vencido":
        return "bg-gray-100 text-gray-800 border-gray-200";
      default:
        return "bg-blue-100 text-blue-800 border-blue-200";
    }
  };

  const getEstadoIcon = (estado: string) => {
    switch (estado.toLowerCase()) {
      case "activo":
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case "suspendido":
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case "cancelado":
      case "vencido":
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Clock className="w-5 h-5 text-blue-600" />;
    }
  };

  const getProgressBarColor = (porcentaje: number) => {
    if (porcentaje >= 80) return "bg-red-500";
    if (porcentaje >= 50) return "bg-yellow-500";
    return "bg-green-500";
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4 flex items-center justify-between rounded-t-xl">
          <div className="flex items-center gap-3">
            <Calendar className="w-6 h-6" />
            <h2 className="text-xl font-bold">Estado y Vigencia de Membresía</h2>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 mt-4">Consultando estado...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              <p className="font-semibold">Error</p>
              <p className="text-sm">{error}</p>
            </div>
          )}

          {!loading && !error && data && (
            <div className="space-y-6">
              {/* Cliente Info */}
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                  Información del Cliente
                </h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-gray-500">Nombre:</span>
                    <p className="font-medium text-gray-900">{data.cliente.nombre_completo}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">CI:</span>
                    <p className="font-medium text-gray-900">{data.cliente.ci}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Teléfono:</span>
                    <p className="font-medium text-gray-900">{data.cliente.telefono}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">ID Membresía:</span>
                    <p className="font-medium text-gray-900">#{data.id}</p>
                  </div>
                </div>
              </div>

              {/* Estado Actual */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Estado */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    {getEstadoIcon(data.estado)}
                    <span className="text-sm text-gray-500">Estado Actual</span>
                  </div>
                  <div
                    className={`inline-flex items-center px-3 py-1 rounded-full border font-semibold ${getEstadoBadgeColor(
                      data.estado
                    )}`}
                  >
                    {data.estado_display}
                  </div>
                </div>

                {/* Vigencia */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    {data.vigente ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-600" />
                    )}
                    <span className="text-sm text-gray-500">Vigencia</span>
                  </div>
                  <div
                    className={`inline-flex items-center px-3 py-1 rounded-full border font-semibold ${
                      data.vigente
                        ? "bg-green-100 text-green-800 border-green-200"
                        : "bg-red-100 text-red-800 border-red-200"
                    }`}
                  >
                    {data.vigente ? "Vigente" : "No Vigente"}
                  </div>
                </div>
              </div>

              {/* Plan Info */}
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <h3 className="font-semibold text-blue-700 mb-3 flex items-center gap-2">
                  <Tag className="w-5 h-5" />
                  Plan de Membresía
                </h3>
                <div className="grid grid-cols-3 gap-3 text-sm">
                  <div>
                    <span className="text-blue-600">Nombre:</span>
                    <p className="font-medium text-gray-900">{data.plan.nombre}</p>
                  </div>
                  <div>
                    <span className="text-blue-600">Duración:</span>
                    <p className="font-medium text-gray-900">{data.plan.duracion} días</p>
                  </div>
                  <div>
                    <span className="text-blue-600">Precio Base:</span>
                    <p className="font-medium text-gray-900">Bs. {data.plan.precio_base}</p>
                  </div>
                </div>
              </div>

              {/* Fechas y Días */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Fechas */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-gray-600" />
                    Período
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Fecha Inicio:</span>
                      <span className="font-medium text-gray-900">
                        {new Date(data.fecha_inicio).toLocaleDateString("es-BO")}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Fecha Fin:</span>
                      <span className="font-medium text-gray-900">
                        {new Date(data.fecha_fin).toLocaleDateString("es-BO")}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Estadísticas de Uso */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-gray-600" />
                    Uso del Plan
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Días Transcurridos:</span>
                      <span className="font-medium text-gray-900">{data.dias_transcurridos}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Días Restantes:</span>
                      <span className={`font-medium ${data.dias_restantes <= 7 ? 'text-red-600' : 'text-green-600'}`}>
                        {data.dias_restantes}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Barra de Progreso */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700">Porcentaje de Uso</span>
                  <span className="text-sm font-bold text-gray-900">{data.porcentaje_uso}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all duration-300 ${getProgressBarColor(
                      data.porcentaje_uso
                    )}`}
                    style={{ width: `${Math.min(data.porcentaje_uso, 100)}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {data.porcentaje_uso >= 80
                    ? "La membresía está próxima a vencer"
                    : data.porcentaje_uso >= 50
                    ? "A mitad del período de membresía"
                    : "Membresía en período inicial"}
                </p>
              </div>

              {/* Promociones */}
              {data.promociones && data.promociones.length > 0 && (
                <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                  <h3 className="font-semibold text-purple-700 mb-3">Promociones Aplicadas</h3>
                  <div className="space-y-2">
                    {data.promociones.map((promo) => (
                      <div
                        key={promo.id}
                        className="flex justify-between items-center bg-white px-3 py-2 rounded border border-purple-100"
                      >
                        <span className="text-sm font-medium text-gray-900">{promo.nombre}</span>
                        <span className="text-sm font-semibold text-purple-600">
                          -{promo.descuento}% descuento
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end rounded-b-xl">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
