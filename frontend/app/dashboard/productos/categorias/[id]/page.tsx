"use client";

import { useEffect, useState } from "react";
import CategoryForm from "@/components/products/CategoryForm";
import { categoryService } from "@/lib/services/products.service";
import { Category } from "@/lib/types/products";

export default function EditCategoryPage({
  params,
}: {
  params: { id: string };
}) {
  const [category, setCategory] = useState<Category | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadCategory = async () => {
      try {
        const data = await categoryService.getById(parseInt(params.id));
        setCategory(data);
      } catch (error) {
        console.error("Error loading category:", error);
      } finally {
        setLoading(false);
      }
    };

    loadCategory();
  }, [params.id]);

  if (loading) {
    return <div className="p-8 text-center text-gray-500">Cargando...</div>;
  }

  if (!category) {
    return (
      <div className="p-8 text-center text-red-500">
        Categoría no encontrada
      </div>
    );
  }

  return <CategoryForm initialData={category} isEditing />;
}
