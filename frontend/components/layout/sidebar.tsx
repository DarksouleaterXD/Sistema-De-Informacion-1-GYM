/**
 * Componente Sidebar - Navegación lateral responsiva
 */

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Users,
  CreditCard,
  Shield,
  Tag,
  FileText,
  Menu,
  X,
  UserCircle,
  Dumbbell,
  GraduationCap,
  Calendar,
  Activity,
  ScrollText,
  Building2,
  ClipboardList,
  Truck,
  Package,
  FolderTree,
  BarChart3,
  ShoppingCart,
  ShoppingBag,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/lib/contexts/auth-context";
import { PermissionCodes } from "@/lib/utils/permissions";
import { canAccessRoute } from "@/lib/utils/permissions";

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  requiredPermission?: string;
  group?: string;
}

interface NavGroup {
  name: string;
  items: NavItem[];
  defaultOpen?: boolean;
}

const navItems: NavItem[] = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: Home,
    requiredPermission: PermissionCodes.DASHBOARD_VIEW,
  },
  {
    name: "Clientes",
    href: "/dashboard/clients",
    icon: UserCircle,
    requiredPermission: PermissionCodes.CLIENT_VIEW,
    group: "Gestión de Clientes",
  },
  {
    name: "Membresías",
    href: "/dashboard/membresias",
    icon: CreditCard,
    requiredPermission: PermissionCodes.MEMBERSHIP_VIEW,
    group: "Gestión de Clientes",
  },
  {
    name: "Planes",
    href: "/dashboard/planes-membresia",
    icon: FileText,
    requiredPermission: PermissionCodes.PLAN_VIEW,
    group: "Gestión de Clientes",
  },
  {
    name: "Disciplinas",
    href: "/dashboard/disciplinas",
    icon: Dumbbell,
    requiredPermission: PermissionCodes.DISCIPLINE_VIEW,
    group: "Gestión de Clases",
  },
  {
    name: "Clases",
    href: "/dashboard/clases",
    icon: Calendar,
    requiredPermission: PermissionCodes.CLASE_VIEW,
    group: "Gestión de Clases",
  },
  {
    name: "Salones",
    href: "/dashboard/salones",
    icon: Building2,
    requiredPermission: PermissionCodes.SALON_VIEW,
    group: "Gestión de Clases",
  },
  {
    name: "Inscripciones",
    href: "/dashboard/inscripciones",
    icon: ClipboardList,
    requiredPermission: PermissionCodes.ENROLLMENT_VIEW,
    group: "Gestión de Clases",
  },
  {
    name: "Asistencias",
    href: "/dashboard/asistencias",
    icon: Activity,
    requiredPermission: PermissionCodes.ASISTENCIA_VIEW,
    group: "Gestión de Clases",
  },
  {
    name: "Instructores",
    href: "/dashboard/instructores",
    icon: GraduationCap,
    requiredPermission: PermissionCodes.INSTRUCTOR_VIEW,
    group: "Gestión de Clases",
  },
  {
    name: "Promociones",
    href: "/dashboard/promociones",
    icon: Tag,
    requiredPermission: PermissionCodes.PROMOTION_VIEW,
    group: "Marketing",
  },
  {
    name: "Proveedores",
    href: "/dashboard/proveedores",
    icon: Truck,
    requiredPermission: PermissionCodes.CLIENT_VIEW,
    group: "Gestión de Productos",
  },
  {
    name: "Categorías",
    href: "/dashboard/categorias-producto",
    icon: FolderTree,
    requiredPermission: PermissionCodes.CLIENT_VIEW,
    group: "Gestión de Productos",
  },
  {
    name: "Productos",
    href: "/dashboard/productos",
    icon: Package,
    requiredPermission: PermissionCodes.CLIENT_VIEW,
    group: "Gestión de Productos",
  },
  {
    name: "Inventario",
    href: "/dashboard/inventario",
    icon: BarChart3,
    requiredPermission: PermissionCodes.CLIENT_VIEW,
    group: "Gestión de Productos",
  },
  {
    name: "Ventas",
    href: "/dashboard/ventas",
    icon: ShoppingCart,
    requiredPermission: PermissionCodes.CLIENT_VIEW,
    group: "Gestión de Productos",
  },
  {
    name: "Compras",
    href: "/dashboard/compras",
    icon: ShoppingBag,
    requiredPermission: PermissionCodes.CLIENT_VIEW,
    group: "Gestión de Productos",
  },
  {
    name: "Usuarios",
    href: "/dashboard/users",
    icon: Users,
    requiredPermission: PermissionCodes.USER_VIEW,
    group: "Administración",
  },
  {
    name: "Roles",
    href: "/dashboard/roles",
    icon: Shield,
    requiredPermission: PermissionCodes.ROLE_VIEW,
    group: "Administración",
  },
  {
    name: "Bitácora",
    href: "/dashboard/audit",
    icon: ScrollText,
    requiredPermission: PermissionCodes.AUDIT_VIEW,
    group: "Administración",
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, permissions, isSuperuser, loading } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({
    "Gestión de Clientes": true,
    "Gestión de Clases": true,
    "Gestión de Productos": true,
    Marketing: true,
    Administración: true,
  });

  const toggleSidebar = () => setIsOpen(!isOpen);

  const toggleGroup = (groupName: string) => {
    setOpenGroups((prev) => ({
      ...prev,
      [groupName]: !prev[groupName],
    }));
  };

  // Agrupar items por módulo
  const groupItems = (
    items: NavItem[]
  ): { groups: NavGroup[]; ungrouped: NavItem[] } => {
    const groupsMap = new Map<string, NavItem[]>();
    const ungrouped: NavItem[] = [];

    items.forEach((item) => {
      if (item.group) {
        if (!groupsMap.has(item.group)) {
          groupsMap.set(item.group, []);
        }
        groupsMap.get(item.group)!.push(item);
      } else {
        ungrouped.push(item);
      }
    });

    const groups: NavGroup[] = Array.from(groupsMap.entries()).map(
      ([name, items]) => ({
        name,
        items,
        defaultOpen: true,
      })
    );

    return { groups, ungrouped };
  };

  // Filtrar items según permisos
  const filterItemsByPermissions = (items: NavItem[]): NavItem[] => {
    // Si no hay usuario, no mostrar nada
    if (!user) {
      return [];
    }

    // Obtener permisos a usar: del contexto o del localStorage como fallback
    let permissionsToUse = permissions || [];
    let isSuperuserToUse = isSuperuser || false;

    // Si aún está cargando o no hay permisos en el contexto, intentar cargar del localStorage
    if (
      (loading || permissionsToUse.length === 0) &&
      typeof window !== "undefined"
    ) {
      try {
        const storedPermissions = localStorage.getItem("permissions");
        const storedUser = localStorage.getItem("user");
        if (storedPermissions) {
          permissionsToUse = JSON.parse(storedPermissions);
        }
        if (storedUser) {
          const parsedUser = JSON.parse(storedUser);
          isSuperuserToUse = parsedUser.is_superuser || false;
        }
      } catch (error) {
        // Si hay error parseando, usar los permisos del contexto
        console.warn("Error cargando permisos del localStorage:", error);
      }
    }

    return items.filter((item) => {
      if (!item.requiredPermission) return true;
      // Usar permissions del contexto o del localStorage como fallback
      return canAccessRoute(item.href, permissionsToUse, isSuperuserToUse);
    });
  };

  return (
    <>
      {/* Botón móvil */}
      <button
        onClick={toggleSidebar}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-blue-600 text-white shadow-lg"
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Overlay móvil con animación de fade */}
      <div
        className={`
          lg:hidden fixed inset-0 bg-black/50 z-30
          transition-opacity duration-300 ease-in-out
          ${
            isOpen
              ? "opacity-100 pointer-events-auto"
              : "opacity-0 pointer-events-none"
          }
        `}
        onClick={toggleSidebar}
      />

      {/* Sidebar con animación suave */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-40
          w-64 bg-gradient-to-b from-gray-900 to-gray-800 text-white
          transform transition-all duration-300 ease-in-out
          lg:translate-x-0
          ${isOpen ? "translate-x-0 shadow-2xl" : "-translate-x-full"}
          flex flex-col h-screen
        `}
      >
        {/* Logo y Título */}
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Dumbbell className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Gym Spartan</h1>
              <p className="text-xs text-gray-400">Panel Admin</p>
            </div>
          </div>
        </div>

        {/* Usuario actual */}
        {user && (
          <div className="p-4 border-b border-gray-700">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
                <span className="text-sm font-semibold">
                  {user.nombre?.[0]}
                  {user.apellido?.[0]}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {user.nombre} {user.apellido}
                </p>
                <p className="text-xs text-gray-400 truncate">{user.email}</p>
              </div>
            </div>
          </div>
        )}

        {/* Navegación */}
        <nav className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-1 px-3">
            {(() => {
              const filteredItems = filterItemsByPermissions(navItems);
              const { groups, ungrouped } = groupItems(filteredItems);
              let itemIndex = 0;

              return (
                <>
                  {/* Items sin grupo (Dashboard) */}
                  {ungrouped.map((item) => {
                    const Icon = item.icon;
                    const isActive =
                      pathname === item.href ||
                      (item.href !== "/dashboard" &&
                        pathname.startsWith(item.href + "/"));
                    const currentIndex = itemIndex++;

                    return (
                      <li
                        key={item.href}
                        style={{
                          animation: isOpen
                            ? `slideInLeft 0.3s ease-out ${
                                currentIndex * 0.05
                              }s both`
                            : "none",
                        }}
                      >
                        <Link
                          href={item.href}
                          onClick={() => setIsOpen(false)}
                          className={`
                            flex items-center space-x-3 px-4 py-3 rounded-lg
                            transition-all duration-200
                            transform hover:scale-105
                            ${
                              isActive
                                ? "bg-blue-600 text-white shadow-lg"
                                : "text-gray-300 hover:bg-gray-700 hover:text-white"
                            }
                          `}
                        >
                          <Icon className="w-5 h-5 transition-transform duration-200 group-hover:rotate-12" />
                          <span className="font-medium">{item.name}</span>
                        </Link>
                      </li>
                    );
                  })}

                  {/* Grupos de items */}
                  {groups.map((group) => {
                    const filteredGroupItems = filterItemsByPermissions(
                      group.items
                    );
                    if (filteredGroupItems.length === 0) return null;

                    const isGroupOpen =
                      openGroups[group.name] ?? group.defaultOpen ?? true;
                    const hasActiveItem = filteredGroupItems.some(
                      (item) =>
                        pathname === item.href ||
                        (item.href !== "/dashboard" &&
                          pathname.startsWith(item.href + "/"))
                    );

                    return (
                      <li key={group.name} className="mt-2">
                        <button
                          onClick={() => toggleGroup(group.name)}
                          className={`
                            w-full flex items-center justify-between px-4 py-2 rounded-lg
                            transition-all duration-200
                            text-gray-400 hover:text-white hover:bg-gray-700
                            ${hasActiveItem ? "text-white bg-gray-800" : ""}
                          `}
                        >
                          <span className="text-xs font-semibold uppercase tracking-wider">
                            {group.name}
                          </span>
                          {isGroupOpen ? (
                            <ChevronDown className="w-4 h-4" />
                          ) : (
                            <ChevronRight className="w-4 h-4" />
                          )}
                        </button>
                        {isGroupOpen && (
                          <ul className="mt-1 space-y-1 ml-2 border-l-2 border-gray-700 pl-2">
                            {filteredGroupItems.map((item) => {
                              const Icon = item.icon;
                              const isActive =
                                pathname === item.href ||
                                (item.href !== "/dashboard" &&
                                  pathname.startsWith(item.href + "/"));
                              const currentIndex = itemIndex++;

                              return (
                                <li
                                  key={item.href}
                                  style={{
                                    animation: isOpen
                                      ? `slideInLeft 0.3s ease-out ${
                                          currentIndex * 0.05
                                        }s both`
                                      : "none",
                                  }}
                                >
                                  <Link
                                    href={item.href}
                                    onClick={() => setIsOpen(false)}
                                    className={`
                                      flex items-center space-x-3 px-3 py-2 rounded-lg
                                      transition-all duration-200
                                      transform hover:scale-105
                                      ${
                                        isActive
                                          ? "bg-blue-600 text-white shadow-lg"
                                          : "text-gray-300 hover:bg-gray-700 hover:text-white"
                                      }
                                    `}
                                  >
                                    <Icon className="w-4 h-4 transition-transform duration-200 group-hover:rotate-12" />
                                    <span className="text-sm font-medium">
                                      {item.name}
                                    </span>
                                  </Link>
                                </li>
                              );
                            })}
                          </ul>
                        )}
                      </li>
                    );
                  })}
                </>
              );
            })()}
          </ul>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-700">
          <p className="text-xs text-gray-400 text-center">
            © 2025 Gym Spartan
          </p>
        </div>
      </aside>
    </>
  );
}
