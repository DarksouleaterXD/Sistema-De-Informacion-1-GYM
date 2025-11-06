"use client";

import React, { useState, useEffect } from "react";
import { X } from "lucide-react";
import disciplinaService, {
  Disciplina,
  DisciplinaCreate,
} from "@/lib/services/disciplina.service";

interface CreateEditDisciplinaModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  disciplina?: Disciplina | null;
}

export default function CreateEditDisciplinaModal({
  isOpen,
  onClose,
  onSuccess,
  disciplina,
}: CreateEditDisciplinaModalProps) {
  const [formData, setFormData] = useState<DisciplinaCreate>({
    nombre: "",
    descripcion: "",
    activa: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    if (disciplina) {
      setFormData({
        nombre: disciplina.nombre,
        descripcion: disciplina.descripcion,
        activa: disciplina.activa,
      });
    } else {
      setFormData({
        nombre: "",
        descripcion: "",
        activa: true,
      });
    }
    setError("");
  }, [disciplina, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (disciplina) {
        // Editar
        await disciplinaService.updateDisciplina(disciplina.id, formData);
      } else {
        // Crear
        await disciplinaService.createDisciplina(formData);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error("Error al guardar disciplina:", err);
      if (err.response?.data?.nombre) {
        setError(err.response.data.nombre[0]);
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Error al guardar la disciplina");
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            {disciplina ? "Editar Disciplina" : "Registrar Nueva Disciplina"}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Nombre */}
          <div>
            <label
              htmlFor="nombre"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Nombre de la Disciplina <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="nombre"
              value={formData.nombre}
              onChange={(e) =>
                setFormData({ ...formData, nombre: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
              placeholder="Ej: Yoga, Spinning, Crossfit..."
              required
              maxLength={100}
            />
            <p className="text-xs text-gray-500 mt-1">
              Máximo 100 caracteres. Debe ser único.
            </p>
          </div>

          {/* Descripción */}
          <div>
            <label
              htmlFor="descripcion"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Descripción <span className="text-red-500">*</span>
            </label>
            <textarea
              id="descripcion"
              value={formData.descripcion}
              onChange={(e) =>
                setFormData({ ...formData, descripcion: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
              placeholder="Descripción detallada de la disciplina..."
              rows={4}
              required
            />
          </div>

          {/* Estado Activa */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="activa"
              checked={formData.activa}
              onChange={(e) =>
                setFormData({ ...formData, activa: e.target.checked })
              }
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="activa" className="ml-2 text-sm text-gray-700">
              Disciplina activa (disponible para programar clases)
            </label>
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
              disabled={loading}
            >
              {loading
                ? "Guardando..."
                : disciplina
                  ? "Guardar Cambios"
                  : "Registrar Disciplina"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
