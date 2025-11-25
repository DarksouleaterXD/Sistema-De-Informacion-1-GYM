export interface Category {
  id: number;
  nombre: string;
  descripcion: string;
  activo: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CategoryFormData {
  nombre: string;
  descripcion: string;
  activo: boolean;
}
