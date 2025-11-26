"use client";

import { useState } from "react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import {
  FileText,
  Download,
  Calendar,
  TrendingUp,
  Package,
  ShoppingCart,
  ShoppingBag,
  Users,
  DollarSign,
  BarChart3,
  Loader2,
} from "lucide-react";
import { Card, Button } from "@/components/ui";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import reporteService, {
  TipoReporte,
  TipoPeriodo,
  FormatoReporte,
  ReporteVentas,
  ReporteCompras,
  ReporteInventario,
  ReporteMembresias,
  ReporteFinanciero,
} from "@/lib/services/reporte.service";

const TIPOS_REPORTE: Array<{ value: TipoReporte; label: string; icon: any }> = [
  { value: "ventas", label: "Ventas", icon: ShoppingCart },
  { value: "compras", label: "Compras", icon: ShoppingBag },
  { value: "inventario", label: "Inventario", icon: Package },
  { value: "membresias", label: "Membresías", icon: Users },
  { value: "financiero", label: "Financiero", icon: DollarSign },
];

const TIPOS_PERIODO: Array<{ value: TipoPeriodo; label: string }> = [
  { value: "dia", label: "Hoy" },
  { value: "semana", label: "Esta Semana" },
  { value: "mes", label: "Este Mes" },
  { value: "anio", label: "Este Año" },
  { value: "personalizado", label: "Rango Personalizado" },
];

function ReportesPageContent() {
  const [tipoReporte, setTipoReporte] = useState<TipoReporte>("ventas");
  const [tipoPeriodo, setTipoPeriodo] = useState<TipoPeriodo>("mes");
  const [fechaInicio, setFechaInicio] = useState("");
  const [fechaFin, setFechaFin] = useState("");
  const [formato, setFormato] = useState<FormatoReporte>("json");
  const [loading, setLoading] = useState(false);
  const [reporteData, setReporteData] = useState<
    | ReporteVentas
    | ReporteCompras
    | ReporteInventario
    | ReporteMembresias
    | ReporteFinanciero
    | null
  >(null);

  const handleGenerarReporte = async () => {
    try {
      setLoading(true);
      setReporteData(null);

      const filtros = {
        tipo_periodo: tipoPeriodo,
        fecha_inicio: tipoPeriodo === "personalizado" ? fechaInicio : undefined,
        fecha_fin: tipoPeriodo === "personalizado" ? fechaFin : undefined,
        formato: formato as FormatoReporte,
      };

      let resultado;

      switch (tipoReporte) {
        case "ventas":
          resultado = await reporteService.generarReporteVentas(filtros);
          break;
        case "compras":
          resultado = await reporteService.generarReporteCompras(filtros);
          break;
        case "inventario":
          resultado = await reporteService.generarReporteInventario(formato);
          break;
        case "membresias":
          resultado = await reporteService.generarReporteMembresias(filtros);
          break;
        case "financiero":
          resultado = await reporteService.generarReporteFinanciero(filtros);
          break;
      }

      // Si es PDF, descargar directamente
      if (resultado instanceof Blob) {
        const nombreArchivo = `reporte_${tipoReporte}_${
          new Date().toISOString().split("T")[0]
        }.pdf`;
        reporteService.descargarPDF(resultado, nombreArchivo);
      } else {
        setReporteData(resultado as any);
      }
    } catch (error: any) {
      console.error("Error al generar reporte:", error);
      alert(
        "Error al generar el reporte: " + (error.message || "Error desconocido")
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDescargarPDF = async () => {
    try {
      setLoading(true);
      const filtros = {
        tipo_periodo: tipoPeriodo,
        fecha_inicio: tipoPeriodo === "personalizado" ? fechaInicio : undefined,
        fecha_fin: tipoPeriodo === "personalizado" ? fechaFin : undefined,
        formato: "pdf" as FormatoReporte,
      };

      let resultado: Blob;

      switch (tipoReporte) {
        case "ventas":
          resultado = (await reporteService.generarReporteVentas(
            filtros
          )) as Blob;
          break;
        case "compras":
          resultado = (await reporteService.generarReporteCompras(
            filtros
          )) as Blob;
          break;
        case "inventario":
          resultado = (await reporteService.generarReporteInventario(
            "pdf"
          )) as Blob;
          break;
        case "membresias":
          resultado = (await reporteService.generarReporteMembresias(
            filtros
          )) as Blob;
          break;
        case "financiero":
          resultado = (await reporteService.generarReporteFinanciero(
            filtros
          )) as Blob;
          break;
        default:
          throw new Error("Tipo de reporte no válido");
      }

      const nombreArchivo = `reporte_${tipoReporte}_${
        new Date().toISOString().split("T")[0]
      }.pdf`;
      reporteService.descargarPDF(resultado, nombreArchivo);
    } catch (error: any) {
      console.error("Error al descargar PDF:", error);
      alert(
        "Error al descargar el PDF: " + (error.message || "Error desconocido")
      );
    } finally {
      setLoading(false);
    }
  };

  const renderReporteContent = () => {
    if (!reporteData) return null;

    switch (tipoReporte) {
      case "ventas":
        return <RenderReporteVentas data={reporteData as ReporteVentas} />;
      case "compras":
        return <RenderReporteCompras data={reporteData as ReporteCompras} />;
      case "inventario":
        return (
          <RenderReporteInventario data={reporteData as ReporteInventario} />
        );
      case "membresias":
        return (
          <RenderReporteMembresias data={reporteData as ReporteMembresias} />
        );
      case "financiero":
        return (
          <RenderReporteFinanciero data={reporteData as ReporteFinanciero} />
        );
      default:
        return null;
    }
  };

  return (
    <DashboardLayout
      title="Reportes"
      description="Genera reportes dinámicos de ventas, compras, inventario y más"
    >
      <div className="space-y-6">
        {/* Filtros */}
        <Card className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Filtros del Reporte
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Tipo de Reporte */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Reporte
              </label>
              <select
                value={tipoReporte}
                onChange={(e) => {
                  setTipoReporte(e.target.value as TipoReporte);
                  setReporteData(null);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              >
                {TIPOS_REPORTE.map((tipo) => (
                  <option key={tipo.value} value={tipo.value}>
                    {tipo.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Tipo de Período */}
            {tipoReporte !== "inventario" && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Período
                </label>
                <select
                  value={tipoPeriodo}
                  onChange={(e) => {
                    setTipoPeriodo(e.target.value as TipoPeriodo);
                    setReporteData(null);
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                >
                  {TIPOS_PERIODO.map((periodo) => (
                    <option key={periodo.value} value={periodo.value}>
                      {periodo.label}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Fechas personalizadas */}
            {tipoPeriodo === "personalizado" &&
              tipoReporte !== "inventario" && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Fecha Inicio
                    </label>
                    <input
                      type="date"
                      value={fechaInicio}
                      onChange={(e) => {
                        setFechaInicio(e.target.value);
                        setReporteData(null);
                      }}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Fecha Fin
                    </label>
                    <input
                      type="date"
                      value={fechaFin}
                      onChange={(e) => {
                        setFechaFin(e.target.value);
                        setReporteData(null);
                      }}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                    />
                  </div>
                </>
              )}

            {/* Formato */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Formato
              </label>
              <select
                value={formato}
                onChange={(e) => setFormato(e.target.value as FormatoReporte)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              >
                <option value="json">JSON (Visualizar)</option>
                <option value="pdf">PDF (Descargar)</option>
              </select>
            </div>
          </div>

          {/* Botones */}
          <div className="flex gap-3 mt-6">
            <Button
              onClick={handleGenerarReporte}
              disabled={loading}
              className="flex items-center gap-2"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <FileText className="w-4 h-4" />
              )}
              {formato === "pdf" ? "Descargar PDF" : "Generar Reporte"}
            </Button>
            {reporteData && formato === "json" && (
              <Button
                onClick={handleDescargarPDF}
                disabled={loading}
                variant="outline"
                className="flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Descargar PDF
              </Button>
            )}
          </div>
        </Card>

        {/* Contenido del Reporte */}
        {reporteData && formato === "json" && (
          <div className="space-y-6">{renderReporteContent()}</div>
        )}
      </div>
    </DashboardLayout>
  );
}

// Componentes para renderizar cada tipo de reporte
function RenderReporteVentas({ data }: { data: ReporteVentas }) {
  return (
    <>
      <Card className="p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          Resumen de Ventas
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Total de Ventas</p>
            <p className="text-2xl font-bold text-blue-600">
              $
              {data.total_ventas.toLocaleString("es-BO", {
                minimumFractionDigits: 2,
              })}
            </p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Cantidad de Ventas</p>
            <p className="text-2xl font-bold text-green-600">
              {data.cantidad_ventas}
            </p>
          </div>
        </div>
      </Card>

      {Object.keys(data.ventas_por_metodo_pago).length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">
            Ventas por Método de Pago
          </h3>
          <div className="space-y-2">
            {Object.entries(data.ventas_por_metodo_pago).map(
              ([metodo, info]) => (
                <div
                  key={metodo}
                  className="flex justify-between items-center p-3 bg-gray-50 rounded"
                >
                  <span className="font-medium text-gray-900 capitalize">
                    {metodo}
                  </span>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">
                      $
                      {info.total.toLocaleString("es-BO", {
                        minimumFractionDigits: 2,
                      })}
                    </p>
                    <p className="text-sm text-gray-600">
                      {info.cantidad} ventas
                    </p>
                  </div>
                </div>
              )
            )}
          </div>
        </Card>
      )}

      {data.productos_mas_vendidos.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">
            Productos Más Vendidos
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">
                    Producto
                  </th>
                  <th className="px-4 py-2 text-center text-sm font-semibold text-gray-700">
                    Cantidad
                  </th>
                  <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">
                    Total
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white">
                {data.productos_mas_vendidos.map((producto, idx) => (
                  <tr key={idx} className="border-t border-gray-200">
                    <td className="px-4 py-2 text-gray-900">
                      {producto.producto}
                    </td>
                    <td className="px-4 py-2 text-center text-gray-900">
                      {producto.cantidad}
                    </td>
                    <td className="px-4 py-2 text-right text-gray-900">
                      $
                      {producto.total.toLocaleString("es-BO", {
                        minimumFractionDigits: 2,
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </>
  );
}

function RenderReporteCompras({ data }: { data: ReporteCompras }) {
  return (
    <>
      <Card className="p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          Resumen de Compras
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Total de Compras</p>
            <p className="text-2xl font-bold text-blue-600">
              $
              {data.total_compras.toLocaleString("es-BO", {
                minimumFractionDigits: 2,
              })}
            </p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Cantidad de Órdenes</p>
            <p className="text-2xl font-bold text-green-600">
              {data.cantidad_ordenes}
            </p>
          </div>
        </div>
      </Card>

      {data.compras_por_proveedor.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">
            Compras por Proveedor
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">
                    Proveedor
                  </th>
                  <th className="px-4 py-2 text-center text-sm font-semibold text-gray-700">
                    Órdenes
                  </th>
                  <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">
                    Total
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white">
                {data.compras_por_proveedor.map((proveedor, idx) => (
                  <tr key={idx} className="border-t border-gray-200">
                    <td className="px-4 py-2 text-gray-900">
                      {proveedor.proveedor}
                    </td>
                    <td className="px-4 py-2 text-center text-gray-900">
                      {proveedor.cantidad_ordenes}
                    </td>
                    <td className="px-4 py-2 text-right text-gray-900">
                      $
                      {proveedor.total_comprado.toLocaleString("es-BO", {
                        minimumFractionDigits: 2,
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </>
  );
}

function RenderReporteInventario({ data }: { data: ReporteInventario }) {
  return (
    <Card className="p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">
        Resumen de Inventario
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Total Productos</p>
          <p className="text-2xl font-bold text-blue-600">
            {data.total_productos}
          </p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Activos</p>
          <p className="text-2xl font-bold text-green-600">
            {data.productos_activos}
          </p>
        </div>
        <div className="bg-red-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Agotados</p>
          <p className="text-2xl font-bold text-red-600">
            {data.productos_agotados}
          </p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Bajo Stock</p>
          <p className="text-2xl font-bold text-yellow-600">
            {data.productos_bajo_stock}
          </p>
        </div>
      </div>
      <div className="bg-gray-50 p-4 rounded-lg">
        <p className="text-sm text-gray-600">Valor Total del Inventario</p>
        <p className="text-2xl font-bold text-gray-900">
          $
          {data.valor_total_inventario.toLocaleString("es-BO", {
            minimumFractionDigits: 2,
          })}
        </p>
      </div>
    </Card>
  );
}

function RenderReporteMembresias({ data }: { data: ReporteMembresias }) {
  return (
    <>
      <Card className="p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          Resumen de Membresías
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Total</p>
            <p className="text-2xl font-bold text-blue-600">
              {data.total_membresias}
            </p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Activas</p>
            <p className="text-2xl font-bold text-green-600">
              {data.membresias_activas}
            </p>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Vencidas</p>
            <p className="text-2xl font-bold text-red-600">
              {data.membresias_vencidas}
            </p>
          </div>
        </div>
        <div className="mt-4 bg-gray-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Ingresos por Membresías</p>
          <p className="text-2xl font-bold text-gray-900">
            $
            {data.ingresos_membresias.toLocaleString("es-BO", {
              minimumFractionDigits: 2,
            })}
          </p>
        </div>
      </Card>
    </>
  );
}

function RenderReporteFinanciero({ data }: { data: ReporteFinanciero }) {
  return (
    <Card className="p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">
        Resumen Financiero
      </h3>
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-green-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Ingresos Totales</p>
          <p className="text-2xl font-bold text-green-600">
            $
            {data.ingresos_totales.toLocaleString("es-BO", {
              minimumFractionDigits: 2,
            })}
          </p>
        </div>
        <div className="bg-red-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Egresos Totales</p>
          <p className="text-2xl font-bold text-red-600">
            $
            {data.egresos_totales.toLocaleString("es-BO", {
              minimumFractionDigits: 2,
            })}
          </p>
        </div>
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Ganancia Neta</p>
          <p className="text-2xl font-bold text-blue-600">
            $
            {data.ganancia_neta.toLocaleString("es-BO", {
              minimumFractionDigits: 2,
            })}
          </p>
        </div>
      </div>
    </Card>
  );
}

export default function ReportesPage() {
  return (
    <ProtectedRoute requiredPermission="report.view">
      <ReportesPageContent />
    </ProtectedRoute>
  );
}
