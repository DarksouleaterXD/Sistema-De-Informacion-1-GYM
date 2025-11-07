"use client";

/**
 * Contexto de autenticación con sistema de permisos RBAC
 */

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { authService } from "../services/auth.service";
import type { User } from "../types";
import {
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  canAccessRoute,
  type PermissionCode,
} from "../utils/permissions";

// Helper para acceso seguro a localStorage (fix SSR)
const safeLocalStorage = {
  getItem: (key: string): string | null => {
    if (typeof window === 'undefined') return null;
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  setItem: (key: string, value: string): void => {
    if (typeof window === 'undefined') return;
    try {
      localStorage.setItem(key, value);
    } catch (error) {
      console.warn('Error saving to localStorage:', error);
    }
  },
  removeItem: (key: string): void => {
    if (typeof window === 'undefined') return;
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.warn('Error removing from localStorage:', error);
    }
  }
};

interface Role {
  id: number;
  nombre: string;
  descripcion: string;
}

interface AuthContextType {
  user: User | null;
  permissions: string[];
  roles: Role[];
  isSuperuser: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  hasPermission: (permission: PermissionCode) => boolean;
  hasAnyPermission: (permissions: PermissionCode[]) => boolean;
  hasAllPermissions: (permissions: PermissionCode[]) => boolean;
  canAccessRoute: (route: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [permissions, setPermissions] = useState<string[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [isSuperuser, setIsSuperuser] = useState(false);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Cargar usuario y permisos al iniciar
  useEffect(() => {
    const loadUser = async () => {
      try {
        if (authService.isAuthenticated()) {
          const storedUser = authService.getStoredUser();
          if (storedUser) {
            setUser(storedUser);
            // Cargar permisos desde el servidor
            try {
              const currentUser = await authService.getCurrentUser();
              setUser(currentUser);
              setPermissions(currentUser.permissions || []);
              setRoles(currentUser.roles || []);
              setIsSuperuser(currentUser.is_superuser || false);
              safeLocalStorage.setItem("user", JSON.stringify(currentUser));
              safeLocalStorage.setItem(
                "permissions",
                JSON.stringify(currentUser.permissions || [])
              );
              safeLocalStorage.setItem(
                "roles",
                JSON.stringify(currentUser.roles || [])
              );
            } catch (error) {
              // Si falla, cargar permisos del localStorage
              console.error("Error verificando usuario:", error);
              const storedPermissions = safeLocalStorage.getItem("permissions");
              const storedRoles = safeLocalStorage.getItem("roles");
              if (storedPermissions)
                setPermissions(JSON.parse(storedPermissions));
              if (storedRoles) setRoles(JSON.parse(storedRoles));
            }
          }
        }
      } catch (error) {
        console.error("Error cargando usuario:", error);
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await authService.login({ email, password });
      setUser(response.user);

      // Cargar permisos del usuario recién logueado
      const currentUser = await authService.getCurrentUser();
      setPermissions(currentUser.permissions || []);
      setRoles(currentUser.roles || []);
      setIsSuperuser(currentUser.is_superuser || false);

      safeLocalStorage.setItem(
        "permissions",
        JSON.stringify(currentUser.permissions || [])
      );
      safeLocalStorage.setItem("roles", JSON.stringify(currentUser.roles || []));

      router.push("/dashboard");
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } finally {
      setUser(null);
      setPermissions([]);
      setRoles([]);
      setIsSuperuser(false);
      safeLocalStorage.removeItem("permissions");
      safeLocalStorage.removeItem("roles");
      router.push("/login");
    }
  };

  const value = {
    user,
    permissions,
    roles,
    isSuperuser,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
    hasPermission: (permission: PermissionCode) =>
      hasPermission(permissions, permission, isSuperuser),
    hasAnyPermission: (perms: PermissionCode[]) =>
      hasAnyPermission(permissions, perms, isSuperuser),
    hasAllPermissions: (perms: PermissionCode[]) =>
      hasAllPermissions(permissions, perms, isSuperuser),
    canAccessRoute: (route: string) =>
      canAccessRoute(route, permissions, isSuperuser),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
