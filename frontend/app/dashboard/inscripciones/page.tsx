"use client";

import DashboardLayout from "@/components/layout/dashboard-layout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PermissionCodes } from "@/lib/utils/permissions";

function InscripcionesPageContent() {
  return (
    <DashboardLayout>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Inscripciones</h1>
        <p className="text-gray-600">
          Página de inscripciones en construcción...
        </p>
      </div>
    </DashboardLayout>
  );
}

export default function InscripcionesPage() {
  return (
    <ProtectedRoute requiredPermission={PermissionCodes.ENROLLMENT_VIEW}>
      <InscripcionesPageContent />
    </ProtectedRoute>
  );
}
