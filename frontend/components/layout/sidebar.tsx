/**
 * Componente Sidebar - Navegación lateral responsiva con RBAC
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
  ClipboardList,
} from "lucide-react";
import { useState, useMemo } from "react";
import { useAuth } from "@/lib/contexts/auth-context";
import { PermissionCodes, PermissionCode } from "@/lib/utils/permissions";

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  requiredPermission?: PermissionCode; // Permiso requerido para mostrar el item
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
  },
  {
    name: "Membresías",
    href: "/dashboard/membresias",
    icon: CreditCard,
    requiredPermission: PermissionCodes.MEMBERSHIP_VIEW,
  },
  {
    name: "Disciplinas",
    href: "/dashboard/disciplinas",
    icon: Dumbbell,
    requiredPermission: PermissionCodes.DISCIPLINE_VIEW,
  },
  {
    name: "Inscripciones",
    href: "/dashboard/inscripciones",
    icon: ClipboardList,
    requiredPermission: PermissionCodes.ENROLLMENT_VIEW,
  },
  {
    name: "Promociones",
    href: "/dashboard/promociones",
    icon: Tag,
    requiredPermission: PermissionCodes.PROMOTION_VIEW,
  },
  {
    name: "Usuarios",
    href: "/dashboard/users",
    icon: Users,
    requiredPermission: PermissionCodes.USER_VIEW,
  },
  {
    name: "Roles",
    href: "/dashboard/roles",
    icon: Shield,
    requiredPermission: PermissionCodes.ROLE_VIEW,
  },
  {
    name: "Bitácora",
    href: "/dashboard/audit",
    icon: FileText,
    requiredPermission: PermissionCodes.AUDIT_VIEW,
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, hasPermission, isSuperuser } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  // Filtrar items del menú por permisos
  const visibleNavItems = useMemo(() => {
    // Superusers ven todo
    if (isSuperuser) return navItems;

    // Filtrar por permisos
    return navItems.filter((item) => {
      // Si no requiere permiso, mostrar siempre
      if (!item.requiredPermission) return true;

      // Verificar si el usuario tiene el permiso
      return hasPermission(item.requiredPermission);
    });
  }, [hasPermission, isSuperuser]);

  const toggleSidebar = () => setIsOpen(!isOpen);

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
            {visibleNavItems.map((item, index) => {
              const Icon = item.icon;
              // Validación exacta: solo activo si la ruta coincide exactamente
              // o si es una subruta directa (pero no para /dashboard en /dashboard/clients)
              const isActive =
                pathname === item.href ||
                (item.href !== "/dashboard" &&
                  pathname.startsWith(item.href + "/"));

              return (
                <li
                  key={item.href}
                  style={{
                    animation: isOpen
                      ? `slideInLeft 0.3s ease-out ${index * 0.05}s both`
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
