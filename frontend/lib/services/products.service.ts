import api from "@/lib/services/api";
import { Category, CategoryFormData } from "@/lib/types/products";

export const categoryService = {
  getAll: async (params?: {
    search?: string;
    activo?: boolean;
    page?: number;
  }) => {
    const response = await api.get<{ count: number; results: Category[] }>(
      "/products/categories/",
      { params }
    );
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get<Category>(`/products/categories/${id}/`);
    return response.data;
  },

  create: async (data: CategoryFormData) => {
    const response = await api.post<Category>("/products/categories/", data);
    return response.data;
  },

  update: async (id: number, data: Partial<CategoryFormData>) => {
    const response = await api.put<Category>(
      `/products/categories/${id}/`,
      data
    );
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/products/categories/${id}/`);
  },
};
