'use client';

import { useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';
import { deleteClase, Clase } from '@/lib/services/clase.service';

interface DeleteClaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  clase: Clase | null;
}

export default function DeleteClaseModal({
  isOpen,
  onClose,
  onSuccess,
  clase,
}: DeleteClaseModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDelete = async () => {
    if (!clase) return;

    setLoading(true);
    setError('');

    try {
      await deleteClase(clase.id);
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error eliminando clase:', err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Error al eliminar la clase. Por favor intente nuevamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !clase) return null;

  const tieneInscripciones = clase.cupos_disponibles !== clase.cupo_maximo;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Eliminar Clase</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <p className="text-gray-700">
              ¿Está seguro que desea eliminar la siguiente clase?
            </p>

            <div className="bg-gray-50 p-4 rounded-lg space-y-2">
              <p className="text-sm text-gray-600">
                <span className="font-medium text-gray-900">Disciplina:</span>{' '}
                {clase.disciplina_nombre}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium text-gray-900">Fecha:</span>{' '}
                {new Date(clase.fecha).toLocaleDateString('es-ES')}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium text-gray-900">Horario:</span>{' '}
                {clase.hora_inicio} - {clase.hora_fin}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium text-gray-900">Salón:</span>{' '}
                {clase.salon_nombre}
              </p>
              {tieneInscripciones && (
                <p className="text-sm text-gray-600">
                  <span className="font-medium text-gray-900">Inscripciones:</span>{' '}
                  {clase.cupo_maximo - (clase.cupos_disponibles || 0)} de {clase.cupo_maximo}
                </p>
              )}
            </div>

            {tieneInscripciones && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <div className="flex gap-3">
                  <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-amber-900">
                      Esta clase tiene clientes inscritos
                    </p>
                    <p className="text-sm text-amber-700 mt-1">
                      Al eliminar esta clase, también se cancelarán todas las inscripciones
                      asociadas.
                    </p>
                  </div>
                </div>
              </div>
            )}

            <p className="text-sm text-gray-500">
              Esta acción no se puede deshacer.
            </p>
          </div>
        </div>

        {/* Buttons */}
        <div className="flex gap-3 justify-end p-6 border-t border-gray-200">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleDelete}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? 'Eliminando...' : 'Eliminar Clase'}
          </button>
        </div>
      </div>
    </div>
  );
}
