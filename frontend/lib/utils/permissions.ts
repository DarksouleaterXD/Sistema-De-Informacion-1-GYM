/**
 * Sistema de permisos y RBAC para el frontend.
 * Define todos los códigos de permisos que existen en el sistema.
 */

// ==========================================
// CÓDIGOS DE PERMISOS (sincronizados con backend)
// ==========================================

export const PermissionCodes = {
  // DASHBOARD
  DASHBOARD_VIEW: "dashboard.view",

  // USUARIOS
  USER_VIEW: "user.view",
  USER_CREATE: "user.create",
  USER_EDIT: "user.edit",
  USER_DELETE: "user.delete",
  USER_VIEW_DETAILS: "user.view_details",

  // ROLES Y PERMISOS
  ROLE_VIEW: "role.view",
  ROLE_CREATE: "role.create",
  ROLE_EDIT: "role.edit",
  ROLE_DELETE: "role.delete",
  ROLE_ASSIGN_PERMISSIONS: "role.assign_permissions",
  ROLE_ASSIGN_TO_USER: "role.assign_to_user",

  PERMISSION_VIEW: "permission.view",
  PERMISSION_CREATE: "permission.create",
  PERMISSION_EDIT: "permission.edit",
  PERMISSION_DELETE: "permission.delete",

  // CLIENTES
  CLIENT_VIEW: "client.view",
  CLIENT_CREATE: "client.create",
  CLIENT_EDIT: "client.edit",
  CLIENT_DELETE: "client.delete",
  CLIENT_VIEW_DETAILS: "client.view_details",

  // MEMBRESÍAS
  MEMBERSHIP_VIEW: "membership.view",
  MEMBERSHIP_CREATE: "membership.create",
  MEMBERSHIP_EDIT: "membership.edit",
  MEMBERSHIP_DELETE: "membership.delete",
  MEMBERSHIP_VIEW_STATS: "membership.view_stats",
  MEMBERSHIP_VIEW_DETAILS: "membership.view_details",

  // PLANES DE MEMBRESÍA
  PLAN_VIEW: "plan.view",
  PLAN_CREATE: "plan.create",
  PLAN_EDIT: "plan.edit",
  PLAN_DELETE: "plan.delete",

  // PROMOCIONES
  PROMOTION_VIEW: "promotion.view",
  PROMOTION_CREATE: "promotion.create",
  PROMOTION_EDIT: "promotion.edit",
  PROMOTION_DELETE: "promotion.delete",
  PROMOTION_VIEW_DETAILS: "promotion.view_details",

  // INSCRIPCIONES
  ENROLLMENT_VIEW: "enrollment.view",
  ENROLLMENT_CREATE: "enrollment.create",
  ENROLLMENT_EDIT: "enrollment.edit",
  ENROLLMENT_DELETE: "enrollment.delete",

  // DISCIPLINAS
  DISCIPLINE_VIEW: "discipline.view",
  DISCIPLINE_CREATE: "discipline.create",
  DISCIPLINE_EDIT: "discipline.edit",
  DISCIPLINE_DELETE: "discipline.delete",

  // SALONES
  SALON_VIEW: "salon.view",
  SALON_CREATE: "salon.create",
  SALON_EDIT: "salon.edit",
  SALON_DELETE: "salon.delete",

  // CLASES
  CLASE_VIEW: "clase.view",
  CLASE_CREATE: "clase.create",
  CLASE_EDIT: "clase.edit",
  CLASE_DELETE: "clase.delete",

  // INSCRIPCIONES A CLASES
  INSCRIPCION_CLASE_VIEW: "inscripcion_clase.view",
  INSCRIPCION_CLASE_CREATE: "inscripcion_clase.create",
  INSCRIPCION_CLASE_EDIT: "inscripcion_clase.edit",
  INSCRIPCION_CLASE_DELETE: "inscripcion_clase.delete",

  // AUDITORÍA
  AUDIT_VIEW: "audit.view",
  AUDIT_VIEW_DETAILS: "audit.view_details",
  AUDIT_EXPORT: "audit.export",

  // REPORTES
  REPORT_VIEW: "report.view",
  REPORT_GENERATE: "report.generate",
  REPORT_EXPORT: "report.export",
} as const;

// Tipo para autocompletado de permisos
export type PermissionCode =
  (typeof PermissionCodes)[keyof typeof PermissionCodes];

// ==========================================
// MAPEO DE RUTAS A PERMISOS
// ==========================================

export const RoutePermissions: Record<string, PermissionCode[]> = {
  // Dashboard principal
  "/dashboard": [PermissionCodes.DASHBOARD_VIEW],

  // Usuarios
  "/dashboard/users": [PermissionCodes.USER_VIEW],
  "/dashboard/users/create": [PermissionCodes.USER_CREATE],
  "/dashboard/users/[id]": [PermissionCodes.USER_VIEW_DETAILS],
  "/dashboard/users/[id]/edit": [PermissionCodes.USER_EDIT],

  // Roles
  "/dashboard/roles": [PermissionCodes.ROLE_VIEW],
  "/dashboard/roles/create": [PermissionCodes.ROLE_CREATE],
  "/dashboard/roles/[id]": [PermissionCodes.ROLE_VIEW],
  "/dashboard/roles/[id]/edit": [PermissionCodes.ROLE_EDIT],

  // Clientes
  "/dashboard/clients": [PermissionCodes.CLIENT_VIEW],
  "/dashboard/clients/create": [PermissionCodes.CLIENT_CREATE],
  "/dashboard/clients/[id]": [PermissionCodes.CLIENT_VIEW_DETAILS],
  "/dashboard/clients/[id]/edit": [PermissionCodes.CLIENT_EDIT],

  // Membresías
  "/dashboard/memberships": [PermissionCodes.MEMBERSHIP_VIEW],
  "/dashboard/memberships/create": [PermissionCodes.MEMBERSHIP_CREATE],
  "/dashboard/memberships/[id]": [PermissionCodes.MEMBERSHIP_VIEW_DETAILS],
  "/dashboard/memberships/[id]/edit": [PermissionCodes.MEMBERSHIP_EDIT],

  // Planes de Membresía
  "/dashboard/planes-membresia": [PermissionCodes.PLAN_VIEW],

  // Promociones
  "/dashboard/promotions": [PermissionCodes.PROMOTION_VIEW],
  "/dashboard/promotions/create": [PermissionCodes.PROMOTION_CREATE],
  "/dashboard/promotions/[id]": [PermissionCodes.PROMOTION_VIEW_DETAILS],
  "/dashboard/promotions/[id]/edit": [PermissionCodes.PROMOTION_EDIT],

  // Disciplinas
  "/dashboard/disciplinas": [PermissionCodes.DISCIPLINE_VIEW],

  // Clases
  "/dashboard/clases": [PermissionCodes.CLASE_VIEW],

  // Auditoría
  "/dashboard/audit": [PermissionCodes.AUDIT_VIEW],
  "/dashboard/audit/[id]": [PermissionCodes.AUDIT_VIEW_DETAILS],
};

// ==========================================
// HELPER FUNCTIONS
// ==========================================

/**
 * Verifica si el usuario tiene un permiso específico
 */
export function hasPermission(
  userPermissions: string[],
  requiredPermission: PermissionCode,
  isSuperuser: boolean = false
): boolean {
  // El superusuario siempre tiene todos los permisos
  if (isSuperuser) return true;

  // Verificar si el usuario tiene el permiso
  return userPermissions.includes(requiredPermission);
}

/**
 * Verifica si el usuario tiene AL MENOS UNO de los permisos especificados
 */
export function hasAnyPermission(
  userPermissions: string[],
  requiredPermissions: PermissionCode[],
  isSuperuser: boolean = false
): boolean {
  if (isSuperuser) return true;
  return requiredPermissions.some((perm) => userPermissions.includes(perm));
}

/**
 * Verifica si el usuario tiene TODOS los permisos especificados
 */
export function hasAllPermissions(
  userPermissions: string[],
  requiredPermissions: PermissionCode[],
  isSuperuser: boolean = false
): boolean {
  if (isSuperuser) return true;
  return requiredPermissions.every((perm) => userPermissions.includes(perm));
}

/**
 * Verifica si el usuario puede acceder a una ruta específica
 */
export function canAccessRoute(
  route: string,
  userPermissions: string[],
  isSuperuser: boolean = false
): boolean {
  if (isSuperuser) return true;

  const requiredPermissions = RoutePermissions[route];
  if (!requiredPermissions) {
    // Si no hay permisos definidos para la ruta, permitir acceso
    return true;
  }

  // El usuario debe tener al menos uno de los permisos requeridos
  return hasAnyPermission(userPermissions, requiredPermissions, isSuperuser);
}

/**
 * Filtra las rutas del menú según los permisos del usuario
 */
export function filterMenuByPermissions(
  menuItems: Array<{ href: string; [key: string]: any }>,
  userPermissions: string[],
  isSuperuser: boolean = false
): Array<{ href: string; [key: string]: any }> {
  if (isSuperuser) return menuItems;

  return menuItems.filter((item) =>
    canAccessRoute(item.href, userPermissions, isSuperuser)
  );
}
