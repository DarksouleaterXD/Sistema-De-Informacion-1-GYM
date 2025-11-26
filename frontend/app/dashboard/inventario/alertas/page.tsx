"use client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import {
  AlertTriangle,
  XCircle,
  Clock,
  Package,
  Loader2,
  RefreshCw,
  Filter,
  Download,
} from "lucide-react";
import { Card, Button } from "@/components/ui";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PermissionCodes } from "@/lib/utils/permissions";
import inventarioService from "@/lib/services/inventario.service";
import { AlertaInventario, AlertasResponse } from "@/lib/types";

type TipoAlerta = "stock_bajo" | "stock_critico" | "proximo_vencer" | "vencido" | "todas";

function AlertasPageContent() {
  const [alertas, setAlertas] = useState<AlertasResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [filtroTipo, setFiltroTipo] = useState<TipoAlerta>("todas");

  useEffect(() => {
    loadAlertas();
  }, []);

  const loadAlertas = async () => {
    try {
      setLoading(true);
      const response = await inventarioService.getAlertas();
      console.log("✅ Alertas cargadas:", response);
      setAlertas(response);
    } catch (error: any) {
      console.error("❌ Error al cargar alertas:", error);
    } finally {
      setLoading(false);
    }
  };

  const getAlertasByTipo = (): AlertaInventario[] => {
    if (!alertas) return [];

    switch (filtroTipo) {
      case "stock_bajo":
        return alertas.stock_bajo;
      case "stock_critico":
        return alertas.stock_critico;
      case "proximo_vencer":
        return alertas.proximo_vencer;
      case "vencido":
        return alertas.vencido;
      case "todas":
      default:
        return [
          ...alertas.stock_critico,
          ...alertas.vencido,
          ...alertas.stock_bajo,
          ...alertas.proximo_vencer,
        ];
    }
  };

  const getSeveridadColor = (severidad: string) => {
    return severidad === "critica"
      ? "bg-red-100 text-red-800 border-red-300"
      : "bg-yellow-100 text-yellow-800 border-yellow-300";
  };

  const getTipoIcon = (tipo: string) => {
    switch (tipo) {
      case "stock_critico":
        return <XCircle className="w-5 h-5 text-red-600" />;
      case "stock_bajo":
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case "vencido":
        return <XCircle className="w-5 h-5 text-red-600" />;
      case "proximo_vencer":
        return <Clock className="w-5 h-5 text-yellow-600" />;
      default:
        return <Package className="w-5 h-5" />;
    }
  };

  const getTipoLabel = (tipo: string) => {
    const labels: Record<string, string> = {
      stock_critico: "Stock Crítico",
      stock_bajo: "Stock Bajo",
      vencido: "Vencido",
      proximo_vencer: "Próximo a Vencer",
    };
    return labels[tipo] || tipo;
  };

  const alertasFiltradas = getAlertasByTipo();

  return (
    <div className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Alertas de Inventario
        </h1>
        <p className="text-gray-600">
          Consulta alertas de stock bajo, stock crítico, productos próximos a
          vencer y vencidos
        </p>
      </div>

      {/* Estadísticas de Alertas */}
      {alertas && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Stock Crítico
                </p>
                <p className="text-3xl font-bold text-red-600 mt-1">
                  {alertas.stock_critico.length}
                </p>
              </div>
              <div className="bg-red-100 p-3 rounded-lg">
                <XCircle className="w-8 h-8 text-red-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6 border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Stock Bajo</p>
                <p className="text-3xl font-bold text-yellow-600 mt-1">
                  {alertas.stock_bajo.length}
                </p>
              </div>
              <div className="bg-yellow-100 p-3 rounded-lg">
                <AlertTriangle className="w-8 h-8 text-yellow-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Vencidos</p>
                <p className="text-3xl font-bold text-red-600 mt-1">
                  {alertas.vencido.length}
                </p>
              </div>
              <div className="bg-red-100 p-3 rounded-lg">
                <XCircle className="w-8 h-8 text-red-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6 border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Próximos a Vencer
                </p>
                <p className="text-3xl font-bold text-yellow-600 mt-1">
                  {alertas.proximo_vencer.length}
                </p>
              </div>
              <div className="bg-yellow-100 p-3 rounded-lg">
                <Clock className="w-8 h-8 text-yellow-600" />
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Filtros y acciones */}
      <Card className="p-6 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-600" />
            <label className="text-sm font-medium text-gray-700">
              Filtrar por:
            </label>
            <select
              value={filtroTipo}
              onChange={(e) => setFiltroTipo(e.target.value as TipoAlerta)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 bg-white"
            >
              <option value="todas">Todas las Alertas</option>
              <option value="stock_critico">Stock Crítico</option>
              <option value="stock_bajo">Stock Bajo</option>
              <option value="vencido">Vencidos</option>
              <option value="proximo_vencer">Próximos a Vencer</option>
            </select>
          </div>

          <div className="ml-auto flex gap-2">
            <Button variant="secondary" onClick={loadAlertas}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Actualizar
            </Button>
          </div>
        </div>
      </Card>

      {/* Lista de Alertas */}
      <Card className="overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-2 text-gray-600">Cargando alertas...</span>
          </div>
        ) : alertasFiltradas.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No hay alertas
            </h3>
            <p className="text-gray-600">
              {filtroTipo === "todas"
                ? "¡Excelente! No hay alertas de inventario en este momento"
                : `No hay alertas de tipo "${getTipoLabel(filtroTipo)}"`}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {alertasFiltradas.map((alerta, index) => (
              <div
                key={`${alerta.tipo}-${alerta.id}-${index}`}
                className={`p-6 hover:bg-gray-50 transition-colors border-l-4 ${
                  alerta.severidad === "critica"
                    ? "border-red-500"
                    : "border-yellow-500"
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 mt-1">
                    {getTipoIcon(alerta.tipo)}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <div>
                        <h4 className="text-lg font-semibold text-gray-900">
                          {alerta.nombre}
                        </h4>
                        <p className="text-sm text-gray-600">
                          Código: {alerta.codigo}
                        </p>
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium border ${getSeveridadColor(
                          alerta.severidad
                        )}`}
                      >
                        {getTipoLabel(alerta.tipo)}
                      </span>
                    </div>

                    <p
                      className={`text-sm font-medium mb-3 ${
                        alerta.severidad === "critica"
                          ? "text-red-700"
                          : "text-yellow-700"
                      }`}
                    >
                      {alerta.mensaje}
                    </p>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      {alerta.stock_actual !== undefined && (
                        <div>
                          <span className="text-gray-600">Stock Actual:</span>
                          <span className="ml-2 font-medium text-gray-900">
                            {alerta.stock_actual} {alerta.unidad_medida}
                          </span>
                        </div>
                      )}
                      {alerta.stock_minimo !== undefined && (
                        <div>
                          <span className="text-gray-600">Stock Mínimo:</span>
                          <span className="ml-2 font-medium text-gray-900">
                            {alerta.stock_minimo} {alerta.unidad_medida}
                          </span>
                        </div>
                      )}
                      {alerta.fecha_vencimiento && (
                        <div>
                          <span className="text-gray-600">Vencimiento:</span>
                          <span className="ml-2 font-medium text-gray-900">
                            {new Date(
                              alerta.fecha_vencimiento
                            ).toLocaleDateString("es-ES")}
                          </span>
                        </div>
                      )}
                      {alerta.categoria && (
                        <div>
                          <span className="text-gray-600">Categoría:</span>
                          <span className="ml-2 font-medium text-gray-900">
                            {alerta.categoria}
                          </span>
                        </div>
                      )}
                    </div>

                    {alerta.proveedor && (
                      <div className="mt-2 text-sm">
                        <span className="text-gray-600">Proveedor:</span>
                        <span className="ml-2 font-medium text-gray-900">
                          {alerta.proveedor}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Resumen */}
      {alertas && alertas.total_alertas > 0 && (
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center gap-2 text-blue-800">
            <Package className="w-5 h-5" />
            <span className="font-medium">
              Total de alertas: {alertas.total_alertas} productos requieren
              atención
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default function AlertasPage() {
  return (
    <ProtectedRoute requiredPermissions={[PermissionCodes.PRODUCTOS_VIEW]}>
      <DashboardLayout>
        <AlertasPageContent />
      </DashboardLayout>
    </ProtectedRoute>
  );
}
