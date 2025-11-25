'use client';

import { useState, useEffect, useCallback } from 'react';
import { Plus, Search, Edit2, Trash2, Calendar, DollarSign } from 'lucide-react';
import DashboardLayout from '@/components/layout/dashboard-layout';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import CreateEditPlanModal from '@/components/planes/CreateEditPlanModal';
import DeletePlanModal from '@/components/planes/DeletePlanModal';
import planMembresiaService, { PaginatedPlanMembresiaResponse } from '@/lib/services/plan-membresia.service';
import { PlanMembresia } from '@/lib/types';

export default function PlanesMembresiaPage() {
  return (
    <ProtectedRoute requiredPermissions={['plan.view']}>
      <DashboardLayout>
        <PlanesMembresiaContent />
      </DashboardLayout>
    </ProtectedRoute>
  );
}

function PlanesMembresiaContent() {
  const [planes, setPlanes] = useState<PlanMembresia[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Filtros y paginación
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Modales
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<PlanMembresia | null>(null);

  const fetchPlanes = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const response = await planMembresiaService.getAll({
        page: currentPage,
        search: searchTerm,
      });

      setPlanes(response.results);
      setTotalPages(Math.ceil(response.count / 10));
    } catch (err) {
      console.error('Error cargando planes:', err);
      setError('Error al cargar los planes de membresía');
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchTerm]);

  useEffect(() => {
    fetchPlanes();
  }, [fetchPlanes]);

  const handleSearch = (value: string) => {
    setSearchTerm(value);
    setCurrentPage(1);
  };

  const handleEdit = (plan: PlanMembresia) => {
    setSelectedPlan(plan);
    setShowEditModal(true);
  };

  const handleDelete = (plan: PlanMembresia) => {
    setSelectedPlan(plan);
    setShowDeleteModal(true);
  };

  const handleSuccess = () => {
    fetchPlanes();
  };

  const formatDuracion = (dias: number) => {
    if (dias === 30) return '1 Mes';
    if (dias === 90) return '3 Meses';
    if (dias === 180) return '6 Meses';
    if (dias === 365) return '1 Año';
    return `${dias} días`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Planes de Membresía</h1>
          <p className="text-gray-600 mt-1">Gestiona los planes disponibles para clientes</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Nuevo Plan
        </button>
      </div>

      {/* Search */}
      <div className="bg-white p-4 rounded-lg shadow-sm">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Buscar planes..."
            value={searchTerm}
            onChange={(e) => handleSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
          />
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Plans Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div>
          <p className="text-gray-600 mt-4">Cargando planes...</p>
        </div>
      ) : planes.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
          <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No hay planes de membresía
          </h3>
          <p className="text-gray-600 mb-6">
            Crea tu primer plan de membresía para empezar
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Nuevo Plan
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {planes.map((plan) => (
            <div
              key={plan.id}
              className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow border-2 border-gray-100"
            >
              {/* Header */}
              <div className="mb-4">
                <h3 className="text-xl font-bold text-gray-900">{plan.nombre}</h3>
                <div className="flex items-center gap-2 mt-2 text-blue-600">
                  <DollarSign className="w-5 h-5" />
                  <span className="text-2xl font-bold">Bs. {plan.precio_base}</span>
                </div>
              </div>

              {/* Details */}
              <div className="space-y-3 mb-4">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Calendar className="w-4 h-4" />
                  <span>{formatDuracion(plan.duracion)}</span>
                </div>

                {plan.descripcion && (
                  <p className="text-sm text-gray-600 line-clamp-3">
                    {plan.descripcion}
                  </p>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleEdit(plan)}
                  className="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
                >
                  <Edit2 className="w-4 h-4" />
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(plan)}
                  className="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center gap-2">
          <button
            onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Anterior
          </button>
          <span className="px-4 py-2 text-sm text-gray-700">
            Página {currentPage} de {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Siguiente
          </button>
        </div>
      )}

      {/* Modals */}
      <CreateEditPlanModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={handleSuccess}
      />

      <CreateEditPlanModal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setSelectedPlan(null);
        }}
        onSuccess={handleSuccess}
        plan={selectedPlan}
      />

      <DeletePlanModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setSelectedPlan(null);
        }}
        onSuccess={handleSuccess}
        plan={selectedPlan}
      />
    </div>
  );
}
