/**
 * Definición de permisos del sistema
 * Deben coincidir con los códigos del backend
 */

export const PermissionCodes = {
  // Dashboard
  DASHBOARD_VIEW: "dashboard.view",

  // Usuarios
  USER_VIEW: "user.view",
  USER_CREATE: "user.create",
  USER_EDIT: "user.edit",
  USER_DELETE: "user.delete",
  USER_VIEW_DETAILS: "user.view_details",

  // Roles
  ROLE_VIEW: "role.view",
  ROLE_CREATE: "role.create",
  ROLE_EDIT: "role.edit",
  ROLE_DELETE: "role.delete",
  ROLE_ASSIGN_PERMISSIONS: "role.assign_permissions",
  ROLE_ASSIGN_TO_USER: "role.assign_to_user",

  // Permisos
  PERMISSION_VIEW: "permission.view",
  PERMISSION_CREATE: "permission.create",
  PERMISSION_EDIT: "permission.edit",
  PERMISSION_DELETE: "permission.delete",

  // Clientes
  CLIENT_VIEW: "client.view",
  CLIENT_CREATE: "client.create",
  CLIENT_EDIT: "client.edit",
  CLIENT_DELETE: "client.delete",
  CLIENT_VIEW_DETAILS: "client.view_details",

  // Membresías
  MEMBERSHIP_VIEW: "membership.view",
  MEMBERSHIP_CREATE: "membership.create",
  MEMBERSHIP_EDIT: "membership.edit",
  MEMBERSHIP_DELETE: "membership.delete",
  MEMBERSHIP_VIEW_STATS: "membership.view_stats",
  MEMBERSHIP_VIEW_DETAILS: "membership.view_details",

  // Planes
  PLAN_VIEW: "plan.view",
  PLAN_CREATE: "plan.create",
  PLAN_EDIT: "plan.edit",
  PLAN_DELETE: "plan.delete",

  // Promociones
  PROMOTION_VIEW: "promotion.view",
  PROMOTION_CREATE: "promotion.create",
  PROMOTION_EDIT: "promotion.edit",
  PROMOTION_DELETE: "promotion.delete",
  PROMOTION_VIEW_DETAILS: "promotion.view_details",

  // Inscripciones
  ENROLLMENT_VIEW: "enrollment.view",
  ENROLLMENT_CREATE: "enrollment.create",
  ENROLLMENT_EDIT: "enrollment.edit",
  ENROLLMENT_DELETE: "enrollment.delete",

  // Disciplinas
  DISCIPLINE_VIEW: "discipline.view",
  DISCIPLINE_CREATE: "discipline.create",
  DISCIPLINE_EDIT: "discipline.edit",
  DISCIPLINE_DELETE: "discipline.delete",

  // Instructores
  INSTRUCTOR_VIEW: "instructor.view",
  INSTRUCTOR_CREATE: "instructor.create",
  INSTRUCTOR_EDIT: "instructor.edit",
  INSTRUCTOR_DELETE: "instructor.delete",
  INSTRUCTOR_VIEW_DETAILS: "instructor.view_details",

  // Salones
  SALON_VIEW: "salon.view",
  SALON_CREATE: "salon.create",
  SALON_EDIT: "salon.edit",
  SALON_DELETE: "salon.delete",

  // Clases
  CLASE_VIEW: "clase.view",
  CLASE_CREATE: "clase.create",
  CLASE_EDIT: "clase.edit",
  CLASE_DELETE: "clase.delete",

  // Inscripciones a Clases
  INSCRIPCION_CLASE_VIEW: "inscripcion_clase.view",
  INSCRIPCION_CLASE_CREATE: "inscripcion_clase.create",
  INSCRIPCION_CLASE_EDIT: "inscripcion_clase.edit",
  INSCRIPCION_CLASE_DELETE: "inscripcion_clase.delete",

  // Asistencias a Clases
  ASISTENCIA_VIEW: "asistencia.view",
  ASISTENCIA_CREATE: "asistencia.create",
  ASISTENCIA_EDIT: "asistencia.edit",
  ASISTENCIA_DELETE: "asistencia.delete",
  ASISTENCIA_VIEW_DETAILS: "asistencia.view_details",

  // Auditoría
  AUDIT_VIEW: "audit.view",
  AUDIT_VIEW_DETAILS: "audit.view_details",
  AUDIT_EXPORT: "audit.export",

  // Reportes
  REPORT_VIEW: "report.view",
  REPORT_GENERATE: "report.generate",
  REPORT_EXPORT: "report.export",
} as const;

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
export const hasPermission = (
  userPermissions: string[],
  permission: PermissionCode,
  isSuperuser: boolean = false
): boolean => {
  if (isSuperuser) return true;
  return userPermissions.includes(permission);
};

/**
 * Verifica si el usuario tiene al menos uno de los permisos especificados
 */
export const hasAnyPermission = (
  userPermissions: string[],
  permissions: PermissionCode[],
  isSuperuser: boolean = false
): boolean => {
  if (isSuperuser) return true;
  return permissions.some((permission) => userPermissions.includes(permission));
};

/**
 * Verifica si el usuario tiene todos los permisos especificados
 */
export const hasAllPermissions = (
  userPermissions: string[],
  permissions: PermissionCode[],
  isSuperuser: boolean = false
): boolean => {
  if (isSuperuser) return true;
  return permissions.every((permission) =>
    userPermissions.includes(permission)
  );
};

/**
 * Mapeo de rutas a permisos requeridos
 */
const routePermissions: Record<string, PermissionCode[]> = {
  "/dashboard": [PermissionCodes.DASHBOARD_VIEW],
  "/dashboard/users": [PermissionCodes.USER_VIEW],
  "/dashboard/roles": [PermissionCodes.ROLE_VIEW],
  "/dashboard/clients": [PermissionCodes.CLIENT_VIEW],
  "/dashboard/membresias": [PermissionCodes.MEMBERSHIP_VIEW],
  "/dashboard/promociones": [PermissionCodes.PROMOTION_VIEW],
  "/dashboard/disciplinas": [PermissionCodes.DISCIPLINE_VIEW],
  "/dashboard/instructores": [PermissionCodes.INSTRUCTOR_VIEW],
  "/dashboard/clases": [PermissionCodes.CLASE_VIEW],
  "/dashboard/inscripciones": [PermissionCodes.INSCRIPCION_CLASE_VIEW],
  "/dashboard/audit": [PermissionCodes.AUDIT_VIEW],
};

/**
 * Verifica si el usuario puede acceder a una ruta específica
 */
export const canAccessRoute = (
  route: string,
  userPermissions: string[],
  isSuperuser: boolean = false
): boolean => {
  if (isSuperuser) return true;

  const requiredPermissions = routePermissions[route];
  if (!requiredPermissions) return true; // Si no hay permisos definidos, permite acceso

  return hasAnyPermission(userPermissions, requiredPermissions, isSuperuser);
};
