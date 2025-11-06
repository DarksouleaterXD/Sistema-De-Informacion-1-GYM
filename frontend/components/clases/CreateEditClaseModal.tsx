'use client';

import { useState, useEffect } from 'react';
import { X, Calendar, Clock, Users, MapPin } from 'lucide-react';
import { createClase, updateClase, Clase, ClaseFormData } from '@/lib/services/clase.service';
import { getDisciplinas, Disciplina } from '@/lib/services/disciplina.service';
import { getSalones, Salon } from '@/lib/services/clase.service';

interface CreateEditClaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  clase?: Clase | null;
}

export default function CreateEditClaseModal({
  isOpen,
  onClose,
  onSuccess,
  clase,
}: CreateEditClaseModalProps) {
  const [formData, setFormData] = useState<ClaseFormData>({
    disciplina: 0,
    instructor: 1, // Por ahora, ID del instructor por defecto
    salon: 0,
    fecha: '',
    hora_inicio: '',
    hora_fin: '',
    cupo_maximo: 0,
    estado: 'programada',
    observaciones: '',
  });

  const [disciplinas, setDisciplinas] = useState<Disciplina[]>([]);
  const [salones, setSalones] = useState<Salon[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadOptions();
      if (clase) {
        setFormData({
          disciplina: clase.disciplina,
          instructor: clase.instructor,
          salon: clase.salon,
          fecha: clase.fecha,
          hora_inicio: clase.hora_inicio,
          hora_fin: clase.hora_fin,
          cupo_maximo: clase.cupo_maximo,
          estado: clase.estado,
          observaciones: clase.observaciones || '',
        });
      } else {
        resetForm();
      }
    }
  }, [isOpen, clase]);

  const loadOptions = async () => {
    try {
      // Cargar disciplinas activas
      const disciplinasRes = await getDisciplinas(1, '', true);
      setDisciplinas(disciplinasRes.results);

      // Cargar salones activos
      const salonesRes = await getSalones(1, '', true);
      setSalones(salonesRes.results);
    } catch (err) {
      console.error('Error cargando opciones:', err);
    }
  };

  const resetForm = () => {
    setFormData({
      disciplina: 0,
      instructor: 1,
      salon: 0,
      fecha: '',
      hora_inicio: '',
      hora_fin: '',
      cupo_maximo: 0,
      estado: 'programada',
      observaciones: '',
    });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (clase) {
        await updateClase(clase.id, formData);
      } else {
        await createClase(formData);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error guardando clase:', err);
      
      if (err.response?.data) {
        const errors = err.response.data;
        if (typeof errors === 'object') {
          // Mostrar todos los errores de validación
          const errorMessages = Object.entries(errors)
            .map(([field, messages]) => {
              if (Array.isArray(messages)) {
                return messages.join(', ');
              }
              return String(messages);
            })
            .join('. ');
          setError(errorMessages);
        } else {
          setError(String(errors));
        }
      } else {
        setError('Error al guardar la clase. Por favor intente nuevamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSalonChange = (salonId: number) => {
    const salonSeleccionado = salones.find(s => s.id === salonId);
    setFormData({
      ...formData,
      salon: salonId,
      cupo_maximo: salonSeleccionado?.capacidad || 0,
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {clase ? 'Editar Clase' : 'Programar Nueva Clase'}
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

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Disciplina */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Disciplina <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.disciplina}
                onChange={(e) => setFormData({ ...formData, disciplina: Number(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                required
              >
                <option value={0}>Seleccionar disciplina</option>
                {disciplinas.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.nombre}
                  </option>
                ))}
              </select>
            </div>

            {/* Salón */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Salón <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.salon}
                onChange={(e) => handleSalonChange(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                required
              >
                <option value={0}>Seleccionar salón</option>
                {salones.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.nombre} (Cap: {s.capacidad})
                  </option>
                ))}
              </select>
            </div>

            {/* Fecha */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Calendar className="w-4 h-4 inline mr-1" />
                Fecha <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.fecha}
                onChange={(e) => setFormData({ ...formData, fecha: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                required
              />
            </div>

            {/* Hora Inicio */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Clock className="w-4 h-4 inline mr-1" />
                Hora Inicio <span className="text-red-500">*</span>
              </label>
              <input
                type="time"
                value={formData.hora_inicio}
                onChange={(e) => setFormData({ ...formData, hora_inicio: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                required
              />
            </div>

            {/* Hora Fin */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Clock className="w-4 h-4 inline mr-1" />
                Hora Fin <span className="text-red-500">*</span>
              </label>
              <input
                type="time"
                value={formData.hora_fin}
                onChange={(e) => setFormData({ ...formData, hora_fin: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                required
              />
            </div>

            {/* Cupo Máximo */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Users className="w-4 h-4 inline mr-1" />
                Cupo Máximo <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                min="1"
                value={formData.cupo_maximo}
                onChange={(e) => setFormData({ ...formData, cupo_maximo: Number(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                required
              />
            </div>

            {/* Estado */}
            {clase && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Estado
                </label>
                <select
                  value={formData.estado}
                  onChange={(e) => setFormData({ ...formData, estado: e.target.value as any })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                >
                  <option value="programada">Programada</option>
                  <option value="en_progreso">En Progreso</option>
                  <option value="completada">Completada</option>
                  <option value="cancelada">Cancelada</option>
                </select>
              </div>
            )}
          </div>

          {/* Observaciones */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Observaciones
            </label>
            <textarea
              value={formData.observaciones}
              onChange={(e) => setFormData({ ...formData, observaciones: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              placeholder="Notas adicionales sobre la clase..."
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
              {loading ? 'Guardando...' : clase ? 'Actualizar' : 'Programar Clase'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
