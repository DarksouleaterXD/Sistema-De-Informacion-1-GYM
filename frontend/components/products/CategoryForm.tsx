"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Save } from "lucide-react";
import Link from "next/link";
import { categoryService } from "@/lib/services/products.service";
import { Category, CategoryFormData } from "@/lib/types/products";

interface CategoryFormProps {
  initialData?: Category;
  isEditing?: boolean;
}

export default function CategoryForm({
  initialData,
  isEditing = false,
}: CategoryFormProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState<CategoryFormData>({
    nombre: "",
    descripcion: "",
    activo: true,
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        nombre: initialData.nombre,
        descripcion: initialData.descripcion,
        activo: initialData.activo,
      });
    }
  }, [initialData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (isEditing && initialData) {
        await categoryService.update(initialData.id, formData);
      } else {
        await categoryService.create(formData);
      }
      router.push("/dashboard/productos/categorias");
      router.refresh();
    } catch (err: any) {
      console.error("Error saving category:", err);
      setError(
        err.response?.data?.nombre?.[0] ||
          "Error al guardar la categoría. Verifique los datos."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <Link
          href="/dashboard/productos/categorias"
          className="text-gray-500 hover:text-gray-700 flex items-center gap-2 mb-4 transition-colors"
        >
          <ArrowLeft size={20} />
          Volver a categorías
        </Link>
        <h1 className="text-2xl font-bold text-gray-800">
          {isEditing ? "Editar Categoría" : "Nueva Categoría"}
        </h1>
      </div>

      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-6"
      >
        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg text-sm">
            {error}
          </div>
        )}

        <div className="space-y-2">
          <label
            htmlFor="nombre"
            className="block text-sm font-medium text-gray-700"
          >
            Nombre <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="nombre"
            required
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            value={formData.nombre}
            onChange={(e) =>
              setFormData({ ...formData, nombre: e.target.value })
            }
            placeholder="Ej. Suplementos"
          />
        </div>

        <div className="space-y-2">
          <label
            htmlFor="descripcion"
            className="block text-sm font-medium text-gray-700"
          >
            Descripción
          </label>
          <textarea
            id="descripcion"
            rows={4}
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all resize-none"
            value={formData.descripcion}
            onChange={(e) =>
              setFormData({ ...formData, descripcion: e.target.value })
            }
            placeholder="Descripción breve de la categoría..."
          />
        </div>

        <div className="flex items-center gap-3 pt-2">
          <input
            type="checkbox"
            id="activo"
            className="w-5 h-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
            checked={formData.activo}
            onChange={(e) =>
              setFormData({ ...formData, activo: e.target.checked })
            }
          />
          <label
            htmlFor="activo"
            className="text-sm font-medium text-gray-700 cursor-pointer select-none"
          >
            Categoría activa
          </label>
        </div>

        <div className="pt-4 border-t border-gray-100 flex justify-end gap-3">
          <Link
            href="/dashboard/productos/categorias"
            className="px-4 py-2 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
          >
            Cancelar
          </Link>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save size={18} />
            {loading ? "Guardando..." : "Guardar Categoría"}
          </button>
        </div>
      </form>
    </div>
  );
}
