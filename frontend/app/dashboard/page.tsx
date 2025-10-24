"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import { Users, CreditCard, TrendingUp, Activity } from "lucide-react";

interface DashboardStats {
  totalClients: number;
  activeMembresias: number;
  monthlyRevenue: number;
  todayCheckIns: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    totalClients: 0,
    activeMembresias: 0,
    monthlyRevenue: 0,
    todayCheckIns: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulación de carga de datos
    // En producción, aquí harías llamadas a tu API
    setTimeout(() => {
      setStats({
        totalClients: 156,
        activeMembresias: 128,
        monthlyRevenue: 45600,
        todayCheckIns: 42,
      });
      setLoading(false);
    }, 1000);
  }, []);

  const statCards = [
    {
      title: "Total Clientes",
      value: stats.totalClients,
      icon: Users,
      color: "bg-blue-500",
      change: "+12%",
    },
    {
      title: "Membresías Activas",
      value: stats.activeMembresias,
      icon: CreditCard,
      color: "bg-green-500",
      change: "+8%",
    },
    {
      title: "Ingresos del Mes",
      value: `Bs. ${stats.monthlyRevenue.toLocaleString()}`,
      icon: TrendingUp,
      color: "bg-blue-500",
      change: "+15%",
    },
    {
      title: "Check-ins Hoy",
      value: stats.todayCheckIns,
      icon: Activity,
      color: "bg-purple-500",
      change: "+5",
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Bienvenido al panel de administración de Gym Spartan
          </p>
        </div>

        {/* Stats Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="bg-white p-6 rounded-lg shadow-sm animate-pulse"
              >
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {statCards.map((card, index) => {
              const Icon = card.icon;
              return (
                <div
                  key={index}
                  className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className={`${card.color} p-3 rounded-lg`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <span className="text-sm font-medium text-green-600">
                      {card.change}
                    </span>
                  </div>
                  <h3 className="text-gray-600 text-sm font-medium mb-1">
                    {card.title}
                  </h3>
                  <p className="text-2xl font-bold text-gray-900">
                    {card.value}
                  </p>
                </div>
              );
            })}
          </div>
        )}

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Últimas Inscripciones */}
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Últimas Inscripciones
            </h2>
            <div className="space-y-4">
              {loading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className="animate-pulse flex items-center space-x-3"
                    >
                      <div className="h-10 w-10 bg-gray-200 rounded-full"></div>
                      <div className="flex-1">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-3">
                  {[
                    {
                      name: "Juan Pérez",
                      plan: "Plan Mensual",
                      date: "Hoy, 10:30 AM",
                    },
                    {
                      name: "María López",
                      plan: "Plan Trimestral",
                      date: "Hoy, 09:15 AM",
                    },
                    {
                      name: "Carlos García",
                      plan: "Plan Anual",
                      date: "Ayer, 04:20 PM",
                    },
                  ].map((item, index) => (
                    <div
                      key={index}
                      className="flex items-center space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors"
                    >
                      <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 font-semibold">
                          {item.name.charAt(0)}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {item.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {item.plan} • {item.date}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Membresías por Vencer */}
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Membresías por Vencer
            </h2>
            <div className="space-y-4">
              {loading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className="animate-pulse flex items-center space-x-3"
                    >
                      <div className="h-10 w-10 bg-gray-200 rounded-full"></div>
                      <div className="flex-1">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-3">
                  {[
                    { name: "Ana Martínez", days: 3, plan: "Plan Mensual" },
                    { name: "Pedro Rojas", days: 5, plan: "Plan Trimestral" },
                    { name: "Luis Fernández", days: 7, plan: "Plan Mensual" },
                  ].map((item, index) => (
                    <div
                      key={index}
                      className="flex items-center space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors"
                    >
                      <div className="h-10 w-10 bg-red-100 rounded-full flex items-center justify-center">
                        <span className="text-red-600 font-semibold">
                          {item.name.charAt(0)}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {item.name}
                        </p>
                        <p className="text-xs text-gray-500">{item.plan}</p>
                      </div>
                      <span className="text-xs font-medium text-red-600 bg-red-50 px-2 py-1 rounded">
                        {item.days}d
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Acciones Rápidas
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-center">
              <Users className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">
                Nuevo Cliente
              </span>
            </button>
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-center">
              <CreditCard className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">
                Nueva Membresía
              </span>
            </button>
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-center">
              <TrendingUp className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">
                Ver Reportes
              </span>
            </button>
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-center">
              <Activity className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">
                Registrar Asistencia
              </span>
            </button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
