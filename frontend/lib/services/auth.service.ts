/**
 * Servicio de autenticación
 */

import { httpClient } from "../config/http-client";
import { API_ENDPOINTS } from "../config/api";
import type { LoginResponse, User } from "../types";

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface PasswordResetRequest {
  email: string;
}

export const authService = {
  /**
   * Iniciar sesión
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await httpClient.post<LoginResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      credentials
    );

    // Guardar tokens en localStorage
    if (typeof window !== "undefined") {
      localStorage.setItem("access_token", response.access);
      localStorage.setItem("refresh_token", response.refresh);
      localStorage.setItem("user", JSON.stringify(response.user));
    }

    return response;
  },

  /**
   * Cerrar sesión
   */
  async logout(): Promise<void> {
    try {
      await httpClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    } finally {
      // Limpiar localStorage incluso si falla la petición
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");
      }
    }
  },

  /**
   * Obtener información del usuario actual
   */
  async getCurrentUser(): Promise<User> {
    return httpClient.get<User>(API_ENDPOINTS.AUTH.ME);
  },

  /**
   * Renovar token de acceso
   */
  async refreshToken(): Promise<{ access: string }> {
    if (typeof window === "undefined") {
      throw new Error("Cannot refresh token on server side");
    }

    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      throw new Error("No refresh token available");
    }

    const response = await httpClient.post<{ access: string }>(
      API_ENDPOINTS.AUTH.REFRESH,
      { refresh: refreshToken }
    );

    localStorage.setItem("access_token", response.access);
    return response;
  },

  /**
   * Solicitar restablecimiento de contraseña
   */
  async requestPasswordReset(data: PasswordResetRequest): Promise<void> {
    await httpClient.post(API_ENDPOINTS.AUTH.PASSWORD_RESET, data);
  },

  /**
   * Verificar si el usuario está autenticado
   */
  isAuthenticated(): boolean {
    if (typeof window === "undefined") {
      return false;
    }

    const token = localStorage.getItem("access_token");
    return !!token;
  },

  /**
   * Obtener usuario guardado en localStorage
   */
  getStoredUser(): User | null {
    if (typeof window === "undefined") {
      return null;
    }

    const userStr = localStorage.getItem("user");
    if (!userStr) {
      return null;
    }

    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },
};
