// Ejemplo: Cómo usar los componentes UI en promociones/page.tsx

"use client";
import { Card, CardHeader, CardBody, Button, Badge } from "@/components/ui";
import { Plus, Tag } from "lucide-react";

export default function PromocionesPage() {
  return (
    <div className="space-y-6">
      {/* Header con componentes reutilizables */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Promociones</h1>
              <p className="text-gray-600 mt-1">
                Gestiona las promociones y descuentos
              </p>
            </div>
            <Button variant="primary" size="md">
              <Plus className="h-5 w-5 mr-2" />
              Nueva Promoción
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Stats Cards usando componentes */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardBody>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Promociones</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">15</p>
              </div>
              <Tag className="h-12 w-12 text-blue-600" />
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Tabla con componentes */}
      <Card>
        <CardBody>
          <table className="w-full">
            <tbody>
              <tr>
                <td>Promoción Verano</td>
                <td>
                  <Badge variant="success">Activa</Badge>
                </td>
                <td>
                  <div className="flex gap-2">
                    <Button variant="secondary" size="sm">
                      Editar
                    </Button>
                    <Button variant="danger" size="sm">
                      Eliminar
                    </Button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}

// ✅ Ventajas de este enfoque:
// - Código más limpio y legible
// - Reutilización de componentes
// - Consistencia visual automática
// - Fácil de mantener
// - NO necesitas archivos CSS separados
