/**
 * Hook para gestionar notificaciones de alertas de inventario
 */
"use client";

import { useState, useEffect } from "react";
import inventarioService from "@/lib/services/inventario.service";
import { AlertasResponse } from "@/lib/types";

const STORAGE_KEY = "alertas_leidas";

export function useAlertasNotifications() {
  const [totalAlertas, setTotalAlertas] = useState<number>(0);
  const [alertasNoLeidas, setAlertasNoLeidas] = useState<number>(0);
  const [alertas, setAlertas] = useState<AlertasResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // Obtener alertas leídas del localStorage
  const getAlertasLeidas = (): Set<string> => {
    if (typeof window === "undefined") return new Set();
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? new Set(JSON.parse(stored)) : new Set();
    } catch {
      return new Set();
    }
  };

  // Guardar alertas leídas en localStorage
  const saveAlertasLeidas = (alertasLeidas: Set<string>) => {
    if (typeof window === "undefined") return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(alertasLeidas)));
    } catch (error) {
      console.error("Error al guardar alertas leídas:", error);
    }
  };

  // Generar ID único para cada alerta
  const getAlertaId = (tipo: string, productoId: number): string => {
    return `${tipo}-${productoId}`;
  };

  const loadAlertas = async () => {
    try {
      setLoading(true);
      const response = await inventarioService.getAlertas();
      setAlertas(response);
      setTotalAlertas(response.total_alertas);

      // Calcular alertas no leídas
      const leidas = getAlertasLeidas();
      const todasAlertas = [
        ...response.stock_critico,
        ...response.vencido,
        ...response.stock_bajo,
        ...response.proximo_vencer,
      ];

      const noLeidas = todasAlertas.filter(
        (alerta) => !leidas.has(getAlertaId(alerta.tipo, alerta.id))
      ).length;

      setAlertasNoLeidas(noLeidas);
    } catch (error) {
      console.error("Error al cargar alertas:", error);
      setTotalAlertas(0);
      setAlertasNoLeidas(0);
    } finally {
      setLoading(false);
    }
  };

  const marcarComoLeida = (tipo: string, productoId: number) => {
    const alertaId = getAlertaId(tipo, productoId);
    const leidas = getAlertasLeidas();
    leidas.add(alertaId);
    saveAlertasLeidas(leidas);
    
    // Recalcular no leídas
    if (alertas) {
      const todasAlertas = [
        ...alertas.stock_critico,
        ...alertas.vencido,
        ...alertas.stock_bajo,
        ...alertas.proximo_vencer,
      ];
      const noLeidas = todasAlertas.filter(
        (alerta) => !leidas.has(getAlertaId(alerta.tipo, alerta.id))
      ).length;
      setAlertasNoLeidas(noLeidas);
    }
  };

  const marcarTodasComoLeidas = () => {
    if (!alertas) return;
    
    const leidas = getAlertasLeidas();
    const todasAlertas = [
      ...alertas.stock_critico,
      ...alertas.vencido,
      ...alertas.stock_bajo,
      ...alertas.proximo_vencer,
    ];

    todasAlertas.forEach((alerta) => {
      leidas.add(getAlertaId(alerta.tipo, alerta.id));
    });

    saveAlertasLeidas(leidas);
    setAlertasNoLeidas(0);
  };

  const isAlertaLeida = (tipo: string, productoId: number): boolean => {
    const leidas = getAlertasLeidas();
    return leidas.has(getAlertaId(tipo, productoId));
  };

  useEffect(() => {
    // Cargar alertas al montar
    loadAlertas();

    // Actualizar cada 5 minutos
    const interval = setInterval(() => {
      loadAlertas();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  return {
    totalAlertas,
    alertasNoLeidas,
    alertas,
    loading,
    refresh: loadAlertas,
    marcarComoLeida,
    marcarTodasComoLeidas,
    isAlertaLeida,
  };
}
