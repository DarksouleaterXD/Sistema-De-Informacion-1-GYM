'use client';

import { useState, useEffect } from 'react';
import { X, Calendar, DollarSign } from 'lucide-react';
import planMembresiaService, { PlanMembresiaCreate } from '@/lib/services/plan-membresia.service';
import { PlanMembresia } from '@/lib/types';

interface CreateEditPlanModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  plan?: PlanMembresia | null;
}

export default function CreateEditPlanModal({
  isOpen,
  onClose,
  onSuccess,
  plan,
}: CreateEditPlanModalProps) {
  const [formData, setFormData] = useState<PlanMembresiaCreate>({
    nombre: '',
    duracion: 30,
    precio_base: '',
    descripcion: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      if (plan) {
        setFormData({
          nombre: plan.nombre,
          duracion: plan.duracion,
          precio_base: plan.precio_base.toString(),
          descripcion: plan.descripcion || '',
        });
      } else {
        resetForm();
      }
    }
  }, [isOpen, plan]);

  const resetForm = () => {
    setFormData({
      nombre: '',
      duracion: 30,
      precio_base: '',
      descripcion: '',
    });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (plan) {
        await planMembresiaService.update(plan.id, formData);
      } else {
        await planMembresiaService.create(formData);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error guardando plan:', err);
      
      if (err.message) {
        setError(err.message);
      } else {
        setError('Error al guardar el plan. Por favor intente nuevamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {plan ? 'Editar Plan' : 'Nuevo Plan de Membresía'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Nombre */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre del Plan <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              placeholder="Ej: Mensual Básico"
              required
            />
          </div>

          {/* Duración */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Calendar className="w-4 h-4 inline mr-1" />
              Duración (días) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="1"
              value={formData.duracion}
              onChange={(e) => setFormData({ ...formData, duracion: Number(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              placeholder="Ej: 30, 90, 180, 365"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Sugerencias: 30 días (1 mes), 90 días (3 meses), 180 días (6 meses), 365 días (1 año)
            </p>
          </div>

          {/* Precio Base */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <DollarSign className="w-4 h-4 inline mr-1" />
              Precio Base (Bs.) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={formData.precio_base}
              onChange={(e) => setFormData({ ...formData, precio_base: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              placeholder="150.00"
              required
            />
          </div>

          {/* Descripción */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descripción
            </label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              placeholder="Descripción del plan y beneficios incluidos..."
            />
          </div>

          {/* Buttons */}
          <div className="flex gap-3 justify-end pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Guardando...' : plan ? 'Actualizar' : 'Crear Plan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
