/**
 * Configuración de API con detección automática de entorno
 * Funciona tanto en desarrollo local como en producción/nube
 */

/**
 * Detecta si estamos en el navegador o en el servidor
 */
const isBrowser = typeof window !== "undefined";

/**
 * Detecta el entorno actual
 */
export const detectEnvironment = () => {
  if (!isBrowser) {
    // Servidor: usar variable de entorno
    return process.env.NEXT_PUBLIC_API_URL || "http://backend:8000";
  }

  // Navegador: detectar automáticamente
  const hostname = window.location.hostname;

  // Desarrollo local
  if (hostname === "localhost" || hostname === "127.0.0.1") {
    return "http://localhost:8000";
  }

  // Producción: usar mismo dominio o variable de entorno
  return (
    process.env.NEXT_PUBLIC_API_URL ||
    `${window.location.protocol}//${hostname}:8000`
  );
};

/**
 * URL base de la API
 */
export const API_BASE_URL = detectEnvironment();

/**
 * Endpoints de la API (solo rutas relativas)
 * La URL base se concatena en el HttpClient
 */
export const API_ENDPOINTS = {
  // Autenticación
  AUTH: {
    LOGIN: "/api/auth/login/",
    LOGOUT: "/api/auth/logout/",
    REFRESH: "/api/token/refresh/",
    ME: "/api/users/me/",
    PASSWORD_RESET: "/api/auth/password/reset/request/",
  },

  // Usuarios
  USERS: {
    BASE: "/api/users/",
    DETAIL: (id: string | number) => `/api/users/${id}/`,
  },

  // Clientes
  CLIENTS: {
    BASE: "/api/clients/",
    DETAIL: (id: string | number) => `/api/clients/${id}/`,
  },

  // Membresías
  MEMBRESIAS: {
    BASE: "/api/membresias/",
    DETAIL: (id: string | number) => `/api/membresias/${id}/`,
    INSCRIPCIONES: "/api/membresias/inscripciones/",
  },

  // Roles
  ROLES: {
    BASE: "/api/roles/",
    DETAIL: (id: string | number) => `/api/roles/${id}/`,
    PERMISOS: "/api/roles/permisos/",
  },

  // Promociones
  PROMOCIONES: {
    BASE: "/api/promociones/",
    DETAIL: (id: string | number) => `/api/promociones/${id}/`,
  },

  // Auditoría/Bitácora
  AUDIT: {
    BASE: "/api/audit/",
    DETAIL: (id: string | number) => `/api/audit/${id}/`,
  },
};

/**
 * Información del entorno (para debugging)
 */
export const getEnvironmentInfo = () => {
  if (!isBrowser) {
    return {
      type: "server",
      apiUrl: API_BASE_URL,
    };
  }

  return {
    type: "browser",
    hostname: window.location.hostname,
    protocol: window.location.protocol,
    apiUrl: API_BASE_URL,
  };
};

// Log del entorno en desarrollo
if (process.env.NODE_ENV === "development" && isBrowser) {
  console.log("🌍 Environment Info:", getEnvironmentInfo());
}
