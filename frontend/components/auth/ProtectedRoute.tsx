/**
 * Componente para proteger rutas y elementos según permisos
 */

"use client";

import { useAuth } from "@/lib/contexts/auth-context";
import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import type { PermissionCode } from "@/lib/utils/permissions";

interface ProtectedRouteProps {
  children: ReactNode;
  requiredPermission?: PermissionCode;
  requiredPermissions?: PermissionCode[];
  requireAll?: boolean; // Si es true, require ALL permissions, sino ANY
  fallback?: ReactNode;
  redirectTo?: string;
}

/**
 * Componente que protege una ruta completa.
 * Redirige al usuario si no tiene los permisos necesarios.
 */
export function ProtectedRoute({
  children,
  requiredPermission,
  requiredPermissions,
  requireAll = false,
  fallback,
  redirectTo = "/dashboard",
}: ProtectedRouteProps) {
  const { hasPermission, hasAnyPermission, hasAllPermissions, loading } =
    useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;

    let hasAccess = true;

    if (requiredPermission) {
      hasAccess = hasPermission(requiredPermission);
    } else if (requiredPermissions && requiredPermissions.length > 0) {
      hasAccess = requireAll
        ? hasAllPermissions(requiredPermissions)
        : hasAnyPermission(requiredPermissions);
    }

    if (!hasAccess) {
      router.push(redirectTo);
    }
  }, [
    loading,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    requiredPermission,
    requiredPermissions,
    requireAll,
    redirectTo,
    router,
  ]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  let hasAccess = true;

  if (requiredPermission) {
    hasAccess = hasPermission(requiredPermission);
  } else if (requiredPermissions && requiredPermissions.length > 0) {
    hasAccess = requireAll
      ? hasAllPermissions(requiredPermissions)
      : hasAnyPermission(requiredPermissions);
  }

  if (!hasAccess) {
    return fallback ? <>{fallback}</> : null;
  }

  return <>{children}</>;
}

interface CanProps {
  children: ReactNode;
  permission?: PermissionCode;
  permissions?: PermissionCode[];
  requireAll?: boolean;
  fallback?: ReactNode;
}

/**
 * Componente que muestra u oculta elementos según permisos.
 * No redirige, solo controla visibilidad.
 *
 * Uso:
 * <Can permission={PermissionCodes.CLIENT_CREATE}>
 *   <Button>Crear Cliente</Button>
 * </Can>
 */
export function Can({
  children,
  permission,
  permissions,
  requireAll = false,
  fallback,
}: CanProps) {
  const { hasPermission, hasAnyPermission, hasAllPermissions, loading } =
    useAuth();

  if (loading) {
    return null;
  }

  let hasAccess = true;

  if (permission) {
    hasAccess = hasPermission(permission);
  } else if (permissions && permissions.length > 0) {
    hasAccess = requireAll
      ? hasAllPermissions(permissions)
      : hasAnyPermission(permissions);
  }

  if (!hasAccess) {
    return fallback ? <>{fallback}</> : null;
  }

  return <>{children}</>;
}

/**
 * Componente inverso - muestra contenido cuando NO tiene permiso
 */
export function Cannot({
  children,
  permission,
  permissions,
  requireAll = false,
}: CanProps) {
  const { hasPermission, hasAnyPermission, hasAllPermissions, loading } =
    useAuth();

  if (loading) {
    return null;
  }

  let hasAccess = true;

  if (permission) {
    hasAccess = hasPermission(permission);
  } else if (permissions && permissions.length > 0) {
    hasAccess = requireAll
      ? hasAllPermissions(permissions)
      : hasAnyPermission(permissions);
  }

  // Mostrar si NO tiene acceso
  if (hasAccess) {
    return null;
  }

  return <>{children}</>;
}
