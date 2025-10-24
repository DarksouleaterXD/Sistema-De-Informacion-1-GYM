import { httpClient } from "../config/http-client";
import { clientService } from "./client.service";
import { membresiaService, MembresiaStats } from "./membresia.service";

/**
 * Estadísticas del dashboard
 */
export interface DashboardStats {
  totalClients: number;
  activeMembresias: number;
  monthlyRevenue: number;
  todayCheckIns: number;
}

/**
 * Últimas inscripciones
 */
export interface RecentInscription {
  id: number;
  name: string;
  plan: string;
  date: string;
  amount: number;
}

/**
 * Membresías próximas a vencer
 */
export interface ExpiringMembresia {
  id: number;
  name: string;
  plan: string;
  daysRemaining: number;
  fechaFin: string;
}

/**
 * Respuesta completa del dashboard
 */
export interface DashboardData {
  stats: DashboardStats;
  recentInscriptions: RecentInscription[];
  expiringMembresias: ExpiringMembresia[];
}

class DashboardService {
  /**
   * Obtener todas las estadísticas del dashboard
   */
  async getDashboardStats(): Promise<DashboardStats> {
    try {
      // Obtener estadísticas de membresías (incluye ingresos)
      const membresiaStats = await membresiaService.getStats();

      // Obtener total de clientes
      const clientsResponse = await clientService.getAll({ page_size: 1 });

      // TODO: Implementar endpoint de check-ins en el backend
      // Por ahora retornamos 0
      const todayCheckIns = 0;

      return {
        totalClients: clientsResponse.count,
        activeMembresias: membresiaStats.activas,
        monthlyRevenue: membresiaStats.ingresos_mes_actual,
        todayCheckIns,
      };
    } catch (error) {
      console.error("Error al obtener estadísticas del dashboard:", error);
      throw error;
    }
  }

  /**
   * Obtener últimas inscripciones
   */
  async getRecentInscriptions(limit: number = 5): Promise<RecentInscription[]> {
    try {
      const response = await membresiaService.getAll({
        page: 1,
        estado: "activo",
      });

      // Ordenar por fecha de creación y tomar las más recientes
      const sorted = response.results
        .sort((a, b) => {
          const dateA = new Date(a.fecha_inicio).getTime();
          const dateB = new Date(b.fecha_inicio).getTime();
          return dateB - dateA;
        })
        .slice(0, limit);

      return sorted.map((membresia) => ({
        id: membresia.id,
        name: membresia.cliente_nombre,
        plan: this.getPlanName(membresia.monto),
        date: this.formatDate(membresia.fecha_inicio),
        amount: membresia.monto,
      }));
    } catch (error) {
      console.error("Error al obtener inscripciones recientes:", error);
      return [];
    }
  }

  /**
   * Obtener membresías próximas a vencer
   */
  async getExpiringMembresias(
    daysThreshold: number = 7
  ): Promise<ExpiringMembresia[]> {
    try {
      const response = await membresiaService.getAll({
        page: 1,
        estado: "activo",
      });

      // Filtrar membresías que vencen en los próximos N días
      const expiring = response.results
        .filter(
          (m) =>
            m.dias_restantes !== undefined &&
            m.dias_restantes <= daysThreshold &&
            m.dias_restantes > 0
        )
        .sort((a, b) => {
          const daysA = a.dias_restantes || 999;
          const daysB = b.dias_restantes || 999;
          return daysA - daysB;
        })
        .slice(0, 5);

      return expiring.map((membresia) => ({
        id: membresia.id,
        name: membresia.cliente_nombre,
        plan: this.getPlanName(membresia.monto),
        daysRemaining: membresia.dias_restantes || 0,
        fechaFin: membresia.fecha_fin,
      }));
    } catch (error) {
      console.error("Error al obtener membresías por vencer:", error);
      return [];
    }
  }

  /**
   * Obtener todos los datos del dashboard en una sola llamada
   */
  async getDashboardData(): Promise<DashboardData> {
    try {
      const [stats, recentInscriptions, expiringMembresias] = await Promise.all(
        [
          this.getDashboardStats(),
          this.getRecentInscriptions(5),
          this.getExpiringMembresias(7),
        ]
      );

      return {
        stats,
        recentInscriptions,
        expiringMembresias,
      };
    } catch (error) {
      console.error("Error al obtener datos del dashboard:", error);
      throw error;
    }
  }

  /**
   * Determinar nombre del plan basado en el monto
   * TODO: Esto debería venir del backend cuando se implementen los planes
   */
  private getPlanName(monto: number): string {
    if (monto >= 500) return "Plan Anual";
    if (monto >= 150) return "Plan Trimestral";
    return "Plan Mensual";
  }

  /**
   * Formatear fecha para mostrar
   */
  private formatDate(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const diffDays = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      const hours = date.getHours().toString().padStart(2, "0");
      const minutes = date.getMinutes().toString().padStart(2, "0");
      return `Hoy, ${hours}:${minutes}`;
    } else if (diffDays === 1) {
      const hours = date.getHours().toString().padStart(2, "0");
      const minutes = date.getMinutes().toString().padStart(2, "0");
      return `Ayer, ${hours}:${minutes}`;
    } else {
      return date.toLocaleDateString("es-ES", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      });
    }
  }
}

export const dashboardService = new DashboardService();
export default dashboardService;
