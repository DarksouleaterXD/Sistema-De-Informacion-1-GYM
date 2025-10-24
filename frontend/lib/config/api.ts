/**
 * Configuración de API con detección automática de entorno
 * Funciona tanto en desarrollo local como en producción/nube
 */

/**
 * Detecta si estamos en el navegador o en el servidor
 */
const isBrowser = typeof window !== "undefined";

/**
 * Detecta el entorno actual y retorna la URL base de la API
 *
 * LÓGICA:
 * 1. En Azure con Nginx: usa /api (ruta relativa, Nginx hace proxy)
 * 2. En local sin Nginx: usa http://localhost:8000 (directo al backend)
 * 3. Server-side: usa http://backend:8000 (nombre del contenedor)
 */
export const detectEnvironment = () => {
  // SERVER SIDE (durante SSR/SSG)
  if (!isBrowser) {
    // Primero verificar variable de entorno
    const envApiUrl = process.env.NEXT_PUBLIC_API_URL;

    // Si es ruta relativa, en SSR necesitamos la URL completa del contenedor
    if (envApiUrl === "/api") {
      return "http://backend:8000"; // Nombre del contenedor Docker
    }

    return envApiUrl || "http://backend:8000";
  }

  // CLIENT SIDE (navegador)
  // Siempre usar la variable de entorno del cliente
  const envApiUrl = process.env.NEXT_PUBLIC_API_URL;

  if (envApiUrl) {
    // Si es ruta relativa (/api), usar directamente
    if (envApiUrl.startsWith("/")) {
      return envApiUrl;
    }
    // Si es URL completa, usarla
    return envApiUrl;
  }

  // FALLBACK: detectar por hostname (solo si no hay variable de entorno)
  const hostname = window.location.hostname;

  // Desarrollo local
  if (hostname === "localhost" || hostname === "127.0.0.1") {
    return "http://localhost:8000";
  }

  // Producción: intentar con /api primero (asume Nginx)
  return "/api";
};

/**
 * URL base de la API
 */
export const API_BASE_URL = detectEnvironment();

/**
 * Endpoints de la API (solo rutas relativas)
 * La URL base se concatena en el HttpClient
 * NOTA: No incluir /api aquí, ya está en API_BASE_URL cuando es necesario
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
