"use client";

import React, { useState } from "react";
import { AlertTriangle, X } from "lucide-react";
import categoriaService, { CategoriaProducto } from "@/lib/services/categoria.service";

interface DeleteCategoriaModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  categoria: CategoriaProducto | null;
}

export default function DeleteCategoriaModal({
  isOpen,
  onClose,
  onSuccess,
  categoria,
}: DeleteCategoriaModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const handleDelete = async () => {
    if (!categoria) return;

    setLoading(true);
    setError("");

    try {
      await categoriaService.deleteCategoria(categoria.id);
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error("Error al eliminar categoría:", err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Error al eliminar la categoría");
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !categoria) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">
              Eliminar Categoría
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <p className="text-gray-700">
            ¿Estás seguro de que deseas eliminar la categoría{" "}
            <span className="font-semibold">{categoria.nombre}</span>?
          </p>

          {categoria.total_productos && categoria.total_productos > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-yellow-800">
                <strong>Advertencia:</strong> Esta categoría tiene{" "}
                {categoria.total_productos} producto(s) asociado(s). 
                La eliminación podría afectar estos productos.
              </p>
            </div>
          )}

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm text-yellow-800">
              <strong>Advertencia:</strong> Esta acción no se puede deshacer.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t border-gray-200">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleDelete}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:bg-gray-400"
            disabled={loading}
          >
            {loading ? "Eliminando..." : "Eliminar Categoría"}
          </button>
        </div>
      </div>
    </div>
  );
}

