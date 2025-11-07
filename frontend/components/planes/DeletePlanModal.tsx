'use client';

import { useState } from 'react';
import { X, AlertTriangle } from 'lucide-react';
import planMembresiaService from '@/lib/services/plan-membresia.service';
import { PlanMembresia } from '@/lib/types';

interface DeletePlanModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  plan: PlanMembresia | null;
}

export default function DeletePlanModal({
  isOpen,
  onClose,
  onSuccess,
  plan,
}: DeletePlanModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDelete = async () => {
    if (!plan) return;

    setLoading(true);
    setError('');

    try {
      await planMembresiaService.delete(plan.id);
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error eliminando plan:', err);
      if (err.message) {
        setError(err.message);
      } else {
        setError('Error al eliminar el plan. Por favor intente nuevamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !plan) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Eliminar Plan</h2>
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
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <p className="text-gray-700 mb-4">
            ¿Estás seguro de que deseas eliminar este plan de membresía?
          </p>

          {/* Plan Details */}
          <div className="bg-gray-50 rounded-lg p-4 space-y-2">
            <div className="flex justify-between">
              <span className="text-sm font-medium text-gray-500">Nombre:</span>
              <span className="text-sm text-gray-900 font-semibold">{plan.nombre}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-medium text-gray-500">Duración:</span>
              <span className="text-sm text-gray-900">{plan.duracion} días</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-medium text-gray-500">Precio:</span>
              <span className="text-sm text-gray-900">Bs. {plan.precio_base}</span>
            </div>
          </div>

          <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <div className="flex gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-yellow-800">
                  Advertencia
                </p>
                <p className="text-sm text-yellow-700 mt-1">
                  Si hay membresías activas usando este plan, no podrás eliminarlo. Deberás esperar a que expiren o migrarlas a otro plan.
                </p>
              </div>
            </div>
          </div>

          <p className="text-sm text-gray-500 mt-4">
            Esta acción no se puede deshacer.
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3 justify-end p-6 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            onClick={handleDelete}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? 'Eliminando...' : 'Eliminar Plan'}
          </button>
        </div>
      </div>
    </div>
  );
}
