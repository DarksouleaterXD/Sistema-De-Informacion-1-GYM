/**
 * Componente NotificationsDropdown - Muestra alertas de inventario
 */
"use client";

import { Bell, AlertTriangle, XCircle, Clock, Package } from "lucide-react";
import { useState } from "react";
import Link from "next/link";
import { useAlertasNotifications } from "@/lib/hooks/useAlertasNotifications";
import { AlertaInventario } from "@/lib/types";

export default function NotificationsDropdown() {
  const { 
    totalAlertas, 
    alertasNoLeidas, 
    alertas, 
    loading, 
    refresh,
    marcarComoLeida,
    marcarTodasComoLeidas,
    isAlertaLeida,
  } = useAlertasNotifications();
  const [showDropdown, setShowDropdown] = useState(false);

  const getTipoIcon = (tipo: string) => {
    switch (tipo) {
      case "stock_critico":
        return <XCircle className="w-4 h-4 text-red-600" />;
      case "stock_bajo":
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case "vencido":
        return <XCircle className="w-4 h-4 text-red-600" />;
      case "proximo_vencer":
        return <Clock className="w-4 h-4 text-yellow-600" />;
      default:
        return <Package className="w-4 h-4" />;
    }
  };

  const getSeveridadColor = (severidad: string) => {
    return severidad === "critica"
      ? "border-l-4 border-red-500 bg-red-50"
      : "border-l-4 border-yellow-500 bg-yellow-50";
  };

  // Obtener las alertas más críticas (máximo 5)
  const getTopAlertas = (): AlertaInventario[] => {
    if (!alertas) return [];
    
    const todasAlertas = [
      ...alertas.stock_critico,
      ...alertas.vencido,
      ...alertas.stock_bajo,
      ...alertas.proximo_vencer,
    ];
    
    return todasAlertas.slice(0, 5);
  };

  const topAlertas = getTopAlertas();

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors relative"
        title="Notificaciones de Inventario"
      >
        <Bell className="w-5 h-5" />
        {alertasNoLeidas > 0 && (
          <>
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-600 rounded-full animate-pulse"></span>
            <span className="absolute -top-1 -right-1 bg-red-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
              {alertasNoLeidas > 9 ? "9+" : alertasNoLeidas}
            </span>
          </>
        )}
      </button>

      {/* Dropdown */}
      {showDropdown && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setShowDropdown(false)}
          />
          <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-20 max-h-[600px] overflow-hidden flex flex-col">
            {/* Header */}
            <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-gray-900">
                  Alertas de Inventario
                </h3>
                {totalAlertas > 0 && (
                  <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
                    {alertasNoLeidas} nuevas
                  </span>
                )}
              </div>
              {alertasNoLeidas > 0 && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    marcarTodasComoLeidas();
                  }}
                  className="w-full text-xs text-blue-600 hover:text-blue-700 font-medium text-left"
                >
                  Marcar todas como leídas
                </button>
              )}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto">
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : totalAlertas === 0 ? (
                <div className="text-center py-8 px-4">
                  <Package className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-sm font-medium text-gray-900 mb-1">
                    No hay alertas
                  </p>
                  <p className="text-xs text-gray-600">
                    ¡Todo está en orden!
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-gray-100">
                  {topAlertas.map((alerta, index) => {
                    const leida = isAlertaLeida(alerta.tipo, alerta.id);
                    return (
                      <div
                        key={`${alerta.tipo}-${alerta.id}-${index}`}
                        className={`relative ${getSeveridadColor(alerta.severidad)} ${
                          leida ? 'opacity-60' : ''
                        }`}
                      >
                        <Link
                          href="/dashboard/inventario/alertas"
                          onClick={() => setShowDropdown(false)}
                          className="block px-4 py-3 hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex items-start gap-3">
                            {!leida && (
                              <div className="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-1.5"></div>
                            )}
                            <div className="flex-shrink-0 mt-0.5">
                              {getTipoIcon(alerta.tipo)}
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 truncate">
                                {alerta.nombre}
                              </p>
                              <p className="text-xs text-gray-600 mt-0.5">
                                {alerta.mensaje}
                              </p>
                              <p className="text-xs text-gray-500 mt-1">
                                Código: {alerta.codigo}
                              </p>
                            </div>
                          </div>
                        </Link>
                        {!leida && (
                          <button
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              marcarComoLeida(alerta.tipo, alerta.id);
                            }}
                            className="absolute top-2 right-2 px-2 py-1 text-xs text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded transition-colors"
                            title="Marcar como leída"
                          >
                            Marcar como leída
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Footer */}
            {totalAlertas > 0 && (
              <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
                <Link
                  href="/dashboard/inventario/alertas"
                  onClick={() => setShowDropdown(false)}
                  className="block text-center text-sm font-medium text-blue-600 hover:text-blue-700"
                >
                  Ver todas las alertas ({totalAlertas})
                </Link>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
