"use client";

import React, { useState, useEffect } from "react";
import { X } from "lucide-react";
import categoriaService, {
  CategoriaProducto,
  CategoriaProductoCreate,
} from "@/lib/services/categoria.service";

interface CreateEditCategoriaModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  categoria?: CategoriaProducto | null;
}

export default function CreateEditCategoriaModal({
  isOpen,
  onClose,
  onSuccess,
  categoria,
}: CreateEditCategoriaModalProps) {
  const [formData, setFormData] = useState<CategoriaProductoCreate>({
    nombre: "",
    codigo: "",
    descripcion: "",
    activo: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    if (categoria) {
      setFormData({
        nombre: categoria.nombre,
        codigo: categoria.codigo,
        descripcion: categoria.descripcion,
        activo: categoria.activo,
      });
    } else {
      setFormData({
        nombre: "",
        codigo: "",
        descripcion: "",
        activo: true,
      });
    }
    setError("");
  }, [categoria, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (categoria) {
        // Editar
        await categoriaService.updateCategoria(categoria.id, formData);
      } else {
        // Crear
        await categoriaService.createCategoria(formData);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error("Error al guardar categoría:", err);
      if (err.response?.data?.nombre) {
        setError(err.response.data.nombre[0]);
      } else if (err.response?.data?.codigo) {
        setError(err.response.data.codigo[0]);
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Error al guardar la categoría");
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
            {categoria ? "Editar Categoría" : "Registrar Nueva Categoría"}
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
              Nombre de la Categoría <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="nombre"
              value={formData.nombre}
              onChange={(e) =>
                setFormData({ ...formData, nombre: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
              placeholder="Ej: Suplementos Proteicos, Equipamiento..."
              required
              maxLength={100}
            />
            <p className="text-xs text-gray-500 mt-1">
              Máximo 100 caracteres. Debe ser único.
            </p>
          </div>

          {/* Código */}
          <div>
            <label
              htmlFor="codigo"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Código <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="codigo"
              value={formData.codigo}
              onChange={(e) =>
                setFormData({ ...formData, codigo: e.target.value.toUpperCase() })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
              placeholder="Ej: SUP-PROT, EQUIP..."
              required
              maxLength={20}
            />
            <p className="text-xs text-gray-500 mt-1">
              Máximo 20 caracteres. Debe ser único. Se convertirá a mayúsculas.
            </p>
          </div>

          {/* Descripción */}
          <div>
            <label
              htmlFor="descripcion"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Descripción
            </label>
            <textarea
              id="descripcion"
              value={formData.descripcion}
              onChange={(e) =>
                setFormData({ ...formData, descripcion: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
              placeholder="Descripción detallada de la categoría..."
              rows={4}
            />
          </div>

          {/* Estado Activo */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="activo"
              checked={formData.activo}
              onChange={(e) =>
                setFormData({ ...formData, activo: e.target.checked })
              }
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="activo" className="ml-2 text-sm text-gray-700">
              Categoría activa (disponible para productos)
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
                : categoria
                  ? "Guardar Cambios"
                  : "Registrar Categoría"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

