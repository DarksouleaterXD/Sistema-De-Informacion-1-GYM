'use client';

import { useState, useEffect, useCallback } from 'react';
import { Plus, Search, Filter, Calendar, Clock, Users, Edit2, Trash2 } from 'lucide-react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import CreateEditClaseModal from '@/components/clases/CreateEditClaseModal';
import DeleteClaseModal from '@/components/clases/DeleteClaseModal';
import { getClases, Clase } from '@/lib/services/clase.service';
import { getDisciplinas, Disciplina } from '@/lib/services/disciplina.service';

export default function ClasesPage() {
  return (
    <ProtectedRoute requiredPermissions={['clase.view']}>
      <DashboardLayout>
        <ClasesContent />
      </DashboardLayout>
    </ProtectedRoute>
  );
}

function ClasesContent() {
  const [clases, setClases] = useState<Clase[]>([]);
  const [disciplinas, setDisciplinas] = useState<Disciplina[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Filtros y paginación
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEstado, setSelectedEstado] = useState<string>('');
  const [selectedDisciplina, setSelectedDisciplina] = useState<number | undefined>(undefined);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Modales
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedClase, setSelectedClase] = useState<Clase | null>(null);

  const fetchClases = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const response = await getClases(
        currentPage,
        searchTerm,
        selectedEstado || undefined,
        undefined, // fecha
        selectedDisciplina
      );

      setClases(response.results);
      setTotalPages(Math.ceil(response.count / 10));
    } catch (err) {
      console.error('Error cargando clases:', err);
      setError('Error al cargar las clases');
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchTerm, selectedEstado, selectedDisciplina]);

  const fetchDisciplinas = async () => {
    try {
      const response = await getDisciplinas(1, '', true);
      setDisciplinas(response.results);
    } catch (err) {
      console.error('Error cargando disciplinas:', err);
    }
  };

  useEffect(() => {
    fetchClases();
  }, [fetchClases]);

  useEffect(() => {
    fetchDisciplinas();
  }, []);

  const handleSearch = (value: string) => {
    setSearchTerm(value);
    setCurrentPage(1);
  };

  const handleEstadoChange = (estado: string) => {
    setSelectedEstado(estado);
    setCurrentPage(1);
  };

  const handleDisciplinaChange = (disciplinaId: string) => {
    setSelectedDisciplina(disciplinaId ? Number(disciplinaId) : undefined);
    setCurrentPage(1);
  };

  const handleEdit = (clase: Clase) => {
    setSelectedClase(clase);
    setShowEditModal(true);
  };

  const handleDelete = (clase: Clase) => {
    setSelectedClase(clase);
    setShowDeleteModal(true);
  };

  const handleSuccess = () => {
    fetchClases();
  };

  const getEstadoBadge = (estado: string) => {
    const badges = {
      programada: 'bg-blue-100 text-blue-800',
      en_progreso: 'bg-green-100 text-green-800',
      completada: 'bg-gray-100 text-gray-800',
      cancelada: 'bg-red-100 text-red-800',
    };
    const labels = {
      programada: 'Programada',
      en_progreso: 'En Progreso',
      completada: 'Completada',
      cancelada: 'Cancelada',
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${badges[estado as keyof typeof badges]}`}>
        {labels[estado as keyof typeof labels]}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Programación de Clases</h1>
          <p className="text-gray-600 mt-1">Gestiona el horario de clases del gimnasio</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Programar Clase
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Buscar clases..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
            />
          </div>

          {/* Estado Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <select
              value={selectedEstado}
              onChange={(e) => handleEstadoChange(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white text-gray-900"
            >
              <option value="">Todos los estados</option>
              <option value="programada">Programada</option>
              <option value="en_progreso">En Progreso</option>
              <option value="completada">Completada</option>
              <option value="cancelada">Cancelada</option>
            </select>
          </div>

          {/* Disciplina Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <select
              value={selectedDisciplina || ''}
              onChange={(e) => handleDisciplinaChange(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white text-gray-900"
            >
              <option value="">Todas las disciplinas</option>
              {disciplinas.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.nombre}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Classes Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div>
          <p className="text-gray-600 mt-4">Cargando clases...</p>
        </div>
      ) : clases.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
          <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No hay clases programadas
          </h3>
          <p className="text-gray-600 mb-6">
            Comienza programando tu primera clase
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Programar Clase
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {clases.map((clase) => (
            <div
              key={clase.id}
              className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {clase.disciplina_nombre}
                  </h3>
                  <p className="text-sm text-gray-600">{clase.instructor_nombre}</p>
                </div>
                {getEstadoBadge(clase.estado)}
              </div>

              {/* Details */}
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Calendar className="w-4 h-4" />
                  <span>
                    {new Date(clase.fecha).toLocaleDateString('es-ES', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </span>
                </div>

                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Clock className="w-4 h-4" />
                  <span>
                    {clase.hora_inicio} - {clase.hora_fin}
                  </span>
                </div>

                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Users className="w-4 h-4" />
                  <span>
                    {clase.cupo_maximo - (clase.cupos_disponibles || 0)} / {clase.cupo_maximo} inscritos
                  </span>
                </div>

                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <div className="w-4 h-4 flex items-center justify-center">📍</div>
                  <span>{clase.salon_nombre}</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 mt-4 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleEdit(clase)}
                  className="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
                >
                  <Edit2 className="w-4 h-4" />
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(clase)}
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
      <CreateEditClaseModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={handleSuccess}
      />

      <CreateEditClaseModal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setSelectedClase(null);
        }}
        onSuccess={handleSuccess}
        clase={selectedClase}
      />

      <DeleteClaseModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setSelectedClase(null);
        }}
        onSuccess={handleSuccess}
        clase={selectedClase}
      />
    </div>
  );
}
