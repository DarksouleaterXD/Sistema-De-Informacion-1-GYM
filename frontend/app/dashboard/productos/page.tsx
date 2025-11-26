"use client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import {
  Search,
  Plus,
  Edit,
  Trash2,
  Package,
  DollarSign,
  TrendingDown,
  TrendingUp,
  Loader2,
  CheckCircle,
  AlertTriangle,
  Tag,
  Layers,
  ShoppingCart,
  BarChart3,
} from "lucide-react";
import {
  Producto,
  CategoriaProducto,
  CreateProductoDTO,
  productoService,
} from "@/lib/services/producto.service";
import { proveedorService } from "@/lib/services/proveedor.service";
import { Card, Button, Input } from "@/components/ui";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PermissionCodes } from "@/lib/utils/permissions";

type ModalMode = "create" | "edit" | "stock" | null;

const UNIDADES_MEDIDA = [
  { value: "UNIDAD", label: "Unidad" },
  { value: "KG", label: "Kilogramo" },
  { value: "GR", label: "Gramo" },
  { value: "LT", label: "Litro" },
  { value: "ML", label: "Mililitro" },
  { value: "CAJA", label: "Caja" },
  { value: "PACK", label: "Pack" },
];

function ProductosPageContent() {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [categorias, setCategorias] = useState<CategoriaProducto[]>([]);
  const [proveedores, setProveedores] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [categoriaFilter, setCategoriaFilter] = useState<string>("");
  const [estadoFilter, setEstadoFilter] = useState<string>("");
  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const [selectedProducto, setSelectedProducto] = useState<Producto | null>(
    null
  );
  const [formData, setFormData] = useState<CreateProductoDTO>({
    nombre: "",
    codigo: "",
    descripcion: "",
    imagen: null,
    categoria: 0,
    proveedor: null,
    precio: 0,
    costo: null,
    stock: 0,
    stock_minimo: 0,
    unidad_medida: "UNIDAD",
    promocion: null,
  });
  const [imagenPreview, setImagenPreview] = useState<string | null>(null);
  const [stockData, setStockData] = useState({
    cantidad: 0,
    tipo_movimiento: "entrada" as "entrada" | "salida",
    motivo: "",
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    total: 0,
  });

  // Cargar datos iniciales
  useEffect(() => {
    loadProductos();
    loadCategorias();
    loadProveedores();
  }, [searchTerm, categoriaFilter, estadoFilter, pagination.page]);

  const loadProductos = async () => {
    try {
      setLoading(true);
      const response = await productoService.getAll({
        search: searchTerm,
        categoria: categoriaFilter ? parseInt(categoriaFilter) : undefined,
        estado: estadoFilter,
        page: pagination.page,
        page_size: pagination.pageSize,
      });
      setProductos(response?.results || []);
      setPagination((prev) => ({ ...prev, total: response?.count || 0 }));
    } catch (error: any) {
      console.error("Error al cargar productos:", error);
      setProductos([]);
    } finally {
      setLoading(false);
    }
  };

  const loadCategorias = async () => {
    try {
      const data = await productoService.getCategoriasActivas();
      setCategorias(data);
    } catch (error) {
      console.error("Error al cargar categorías:", error);
    }
  };

  const loadProveedores = async () => {
    try {
      const response = await proveedorService.getAll({ estado: "A" });
      setProveedores(response?.results || []);
    } catch (error) {
      console.error("Error al cargar proveedores:", error);
    }
  };

  const handleCreate = () => {
    setModalMode("create");
    setFormData({
      nombre: "",
      codigo: "",
      descripcion: "",
      imagen: null,
      categoria: categorias[0]?.id || 0,
      proveedor: null,
      precio: 0,
      costo: null,
      stock: 0,
      stock_minimo: 5,
      unidad_medida: "UNIDAD",
      promocion: null,
    });
    setImagenPreview(null);
    setFormErrors({});
    setSelectedProducto(null);
  };

  const handleEdit = (producto: Producto) => {
    setModalMode("edit");
    setSelectedProducto(producto);
    setFormData({
      nombre: producto.nombre,
      codigo: producto.codigo,
      descripcion: producto.descripcion || "",
      imagen: null,
      categoria: producto.categoria,
      proveedor: producto.proveedor,
      precio: parseFloat(producto.precio),
      costo: producto.costo ? parseFloat(producto.costo) : null,
      stock: producto.stock,
      stock_minimo: producto.stock_minimo,
      unidad_medida: producto.unidad_medida,
      promocion: producto.promocion,
    });
    setImagenPreview(producto.imagen_url || null);
    setFormErrors({});
  };

  const handleStock = (producto: Producto) => {
    setModalMode("stock");
    setSelectedProducto(producto);
    setStockData({
      cantidad: 0,
      tipo_movimiento: "entrada",
      motivo: "",
    });
  };

  const handleDelete = async (id: number, nombre: string) => {
    if (
      !confirm(
        `¿Está seguro de eliminar el producto "${nombre}"?\n\nEsta acción no se puede deshacer.`
      )
    )
      return;

    try {
      await productoService.delete(id);
      alert("Producto eliminado exitosamente");
      loadProductos();
    } catch (error: any) {
      console.error("Error al eliminar producto:", error);
      // Extraer mensaje de error del backend
      let errorMessage = "Error al eliminar producto";
      if (error.response?.data) {
        if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (typeof error.response.data === "string") {
          errorMessage = error.response.data;
        } else if (error.response.data.non_field_errors) {
          errorMessage = error.response.data.non_field_errors[0];
        }
      }
      alert(errorMessage);
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.nombre?.trim()) {
      errors.nombre = "El nombre es obligatorio";
    }

    if (!formData.codigo?.trim()) {
      errors.codigo = "El código es obligatorio";
    }

    if (!formData.categoria || formData.categoria === 0) {
      errors.categoria = "La categoría es obligatoria";
    }

    if (formData.precio <= 0) {
      errors.precio = "El precio debe ser mayor a 0";
    }

    if (
      formData.costo !== null &&
      formData.costo !== undefined &&
      formData.costo < 0
    ) {
      errors.costo = "El costo no puede ser negativo";
    }

    // Validar que precio sea mayor que costo (solo si costo está presente)
    if (
      formData.costo &&
      formData.costo > 0 &&
      formData.precio < formData.costo
    ) {
      errors.precio = "El precio de venta no puede ser menor que el costo";
    }

    if (formData.stock < 0) {
      errors.stock = "El stock no puede ser negativo";
    }

    if (formData.stock_minimo < 0) {
      errors.stock_minimo = "El stock mínimo no puede ser negativo";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      setSubmitting(true);

      if (modalMode === "create") {
        await productoService.create(formData);
        alert("Producto creado exitosamente");
      } else if (modalMode === "edit" && selectedProducto) {
        await productoService.update(selectedProducto.id, formData);
        alert("Producto actualizado exitosamente");
      }

      setModalMode(null);
      loadProductos();
    } catch (error: any) {
      console.error("Error al guardar producto:", error);

      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === "object") {
          setFormErrors(detail);
        } else {
          alert(detail);
        }
      } else {
        alert("Error al guardar el producto");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleStockSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedProducto) return;

    if (stockData.cantidad <= 0) {
      alert("La cantidad debe ser mayor a 0");
      return;
    }

    try {
      setSubmitting(true);
      await productoService.actualizarStock(selectedProducto.id, stockData);
      alert("Stock actualizado exitosamente");
      setModalMode(null);
      loadProductos();
    } catch (error: any) {
      console.error("Error al actualizar stock:", error);
      alert(error.response?.data?.detail || "Error al actualizar stock");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <DashboardLayout
      title="Productos"
      description="Gestión de productos del gimnasio"
    >
      <div className="space-y-6">
        {/* Barra de búsqueda y filtros */}
        <Card className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Buscar por nombre, código..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={categoriaFilter}
              onChange={(e) => setCategoriaFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
            >
              <option value="">Todas las categorías</option>
              {categorias.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.nombre}
                </option>
              ))}
            </select>
            <select
              value={estadoFilter}
              onChange={(e) => setEstadoFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
            >
              <option value="">Todos los estados</option>
              <option value="ACTIVO">Activos</option>
              <option value="AGOTADO">Agotados</option>
            </select>
            <Button onClick={handleCreate} className="flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Nuevo Producto
            </Button>
          </div>
        </Card>

        {/* Lista de productos */}
        <Card className="overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
          ) : productos.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              No se encontraron productos
            </div>
          ) : (
            <div className="overflow-x-auto -mx-4 sm:mx-0">
              <div className="inline-block min-w-full align-middle px-4 sm:px-0">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Producto
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Categoría
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Proveedor
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Precio
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Stock
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Estado
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {productos.map((producto) => (
                      <tr key={producto.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="flex items-center">
                            {producto.imagen_url ? (
                              <img
                                src={producto.imagen_url}
                                alt={producto.nombre}
                                className="w-12 h-12 object-cover rounded-lg mr-3"
                                onError={(e) => {
                                  (e.target as HTMLImageElement).style.display =
                                    "none";
                                }}
                              />
                            ) : (
                              <Package className="w-5 h-5 text-gray-400 mr-3" />
                            )}
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {producto.nombre}
                              </div>
                              <div className="text-sm text-gray-500">
                                Código: {producto.codigo}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-1">
                            <Layers className="w-4 h-4 text-gray-400" />
                            <span className="text-sm text-gray-900">
                              {producto.categoria_nombre}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">
                            {producto.proveedor_nombre || (
                              <span className="text-gray-400">
                                Sin proveedor
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm">
                            <div className="font-medium text-gray-900">
                              Bs. {parseFloat(producto.precio).toFixed(2)}
                            </div>
                            {producto.costo && (
                              <div className="text-gray-500">
                                Costo: Bs.{" "}
                                {parseFloat(producto.costo).toFixed(2)}
                              </div>
                            )}
                            {producto.promocion_nombre && (
                              <div className="text-green-600 text-xs">
                                {producto.promocion_nombre}
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm">
                            <div
                              className={`font-medium ${
                                producto.necesita_reposicion
                                  ? "text-red-600"
                                  : "text-gray-900"
                              }`}
                            >
                              {producto.stock} {producto.unidad_medida_display}
                            </div>
                            <div className="text-gray-500 text-xs">
                              Mín: {producto.stock_minimo}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              producto.estado === "ACTIVO"
                                ? "bg-green-100 text-green-800"
                                : "bg-red-100 text-red-800"
                            }`}
                          >
                            {producto.estado === "ACTIVO" ? (
                              <CheckCircle className="w-3 h-3 mr-1" />
                            ) : (
                              <AlertTriangle className="w-3 h-3 mr-1" />
                            )}
                            {producto.estado_display}
                          </span>
                          {producto.necesita_reposicion && (
                            <div className="mt-1">
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                                <TrendingDown className="w-3 h-3 mr-1" />
                                Bajo stock
                              </span>
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 text-right text-sm font-medium">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleStock(producto)}
                              className="text-purple-600 hover:text-purple-900 p-1 rounded hover:bg-purple-50"
                              title="Actualizar stock"
                            >
                              <ShoppingCart className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => handleEdit(producto)}
                              className="text-blue-600 hover:text-blue-900 p-1 rounded hover:bg-blue-50"
                              title="Editar"
                            >
                              <Edit className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() =>
                                handleDelete(producto.id, producto.nombre)
                              }
                              className="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50"
                              title="Eliminar"
                            >
                              <Trash2 className="w-5 h-5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </Card>

        {/* Paginación */}
        {pagination.total > pagination.pageSize && (
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Mostrando {(pagination.page - 1) * pagination.pageSize + 1} a{" "}
              {Math.min(
                pagination.page * pagination.pageSize,
                pagination.total
              )}{" "}
              de {pagination.total} productos
            </div>
            <div className="flex gap-2">
              <Button
                onClick={() =>
                  setPagination((p) => ({ ...p, page: p.page - 1 }))
                }
                disabled={pagination.page === 1}
                variant="outline"
              >
                Anterior
              </Button>
              <Button
                onClick={() =>
                  setPagination((p) => ({ ...p, page: p.page + 1 }))
                }
                disabled={
                  pagination.page * pagination.pageSize >= pagination.total
                }
                variant="outline"
              >
                Siguiente
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Modal de Crear/Editar */}
      {(modalMode === "create" || modalMode === "edit") && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto mx-4 sm:mx-0">
            <div className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  {modalMode === "create"
                    ? "Nuevo Producto"
                    : "Editar Producto"}
                </h2>
                <button
                  onClick={() => setModalMode(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Nombre */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Nombre del Producto{" "}
                      <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <Package className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <Input
                        type="text"
                        value={formData.nombre}
                        onChange={(e) =>
                          setFormData({ ...formData, nombre: e.target.value })
                        }
                        className={`pl-10 ${
                          formErrors.nombre ? "border-red-500" : ""
                        }`}
                        placeholder="Ej: Proteína Whey Gold"
                      />
                    </div>
                    {formErrors.nombre && (
                      <p className="text-red-500 text-sm mt-1">
                        {formErrors.nombre}
                      </p>
                    )}
                  </div>

                  {/* Código */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Código <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <Tag className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <Input
                        type="text"
                        value={formData.codigo}
                        onChange={(e) =>
                          setFormData({ ...formData, codigo: e.target.value })
                        }
                        className={`pl-10 ${
                          formErrors.codigo ? "border-red-500" : ""
                        }`}
                        placeholder="Ej: PROT-001"
                        disabled={modalMode === "edit"}
                      />
                    </div>
                    {formErrors.codigo && (
                      <p className="text-red-500 text-sm mt-1">
                        {formErrors.codigo}
                      </p>
                    )}
                    {modalMode === "edit" && (
                      <p className="text-gray-500 text-sm mt-1">
                        El código no se puede modificar
                      </p>
                    )}
                  </div>
                </div>

                {/* Descripción */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Descripción
                  </label>
                  <textarea
                    value={formData.descripcion}
                    onChange={(e) =>
                      setFormData({ ...formData, descripcion: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                    placeholder="Descripción del producto..."
                    rows={3}
                  />
                </div>

                {/* Imagen */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Imagen del Producto
                  </label>
                  <div className="space-y-2">
                    {imagenPreview && (
                      <div className="relative w-32 h-32 border border-gray-300 rounded-lg overflow-hidden">
                        <img
                          src={imagenPreview}
                          alt="Vista previa"
                          className="w-full h-full object-cover"
                        />
                        <button
                          type="button"
                          onClick={() => {
                            setImagenPreview(null);
                            setFormData({ ...formData, imagen: null });
                          }}
                          className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
                        >
                          ✕
                        </button>
                      </div>
                    )}
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          setFormData({ ...formData, imagen: file });
                          const reader = new FileReader();
                          reader.onloadend = () => {
                            setImagenPreview(reader.result as string);
                          };
                          reader.readAsDataURL(file);
                        }
                      }}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white"
                    />
                    <p className="text-xs text-gray-500">
                      Formatos soportados: JPG, PNG, GIF. Tamaño máximo
                      recomendado: 2MB
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Categoría */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Categoría <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.categoria}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          categoria: parseInt(e.target.value),
                        })
                      }
                      className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900 ${
                        formErrors.categoria
                          ? "border-red-500"
                          : "border-gray-300"
                      }`}
                    >
                      <option value={0}>Seleccione una categoría</option>
                      {categorias.map((cat) => (
                        <option key={cat.id} value={cat.id}>
                          {cat.nombre}
                        </option>
                      ))}
                    </select>
                    {formErrors.categoria && (
                      <p className="text-red-500 text-sm mt-1">
                        {formErrors.categoria}
                      </p>
                    )}
                  </div>

                  {/* Proveedor */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Proveedor
                    </label>
                    <select
                      value={formData.proveedor || ""}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          proveedor: e.target.value
                            ? parseInt(e.target.value)
                            : null,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
                    >
                      <option value="">Sin proveedor</option>
                      {proveedores.map((prov) => (
                        <option key={prov.id} value={prov.id}>
                          {prov.razon_social}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Precio */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Precio (Bs.) <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <Input
                        type="number"
                        step="0.01"
                        min="0"
                        value={formData.precio || ""}
                        onChange={(e) => {
                          const value =
                            e.target.value === ""
                              ? 0
                              : parseFloat(e.target.value) || 0;
                          setFormData({ ...formData, precio: value });
                        }}
                        className={`pl-10 ${
                          formErrors.precio ? "border-red-500" : ""
                        }`}
                        placeholder="0.00"
                      />
                    </div>
                    {formErrors.precio && (
                      <p className="text-red-500 text-sm mt-1">
                        {formErrors.precio}
                      </p>
                    )}
                  </div>

                  {/* Costo */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Costo (Bs.){" "}
                      <span className="text-gray-400 text-xs">(Opcional)</span>
                    </label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      value={
                        formData.costo && formData.costo > 0
                          ? formData.costo
                          : ""
                      }
                      onChange={(e) => {
                        const value =
                          e.target.value === ""
                            ? null
                            : parseFloat(e.target.value) || null;
                        setFormData({ ...formData, costo: value });
                      }}
                      className={formErrors.costo ? "border-red-500" : ""}
                      placeholder="0.00 (opcional)"
                    />
                    {formErrors.costo && (
                      <p className="text-red-500 text-sm mt-1">
                        {formErrors.costo}
                      </p>
                    )}
                  </div>

                  {/* Unidad de Medida */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Unidad
                    </label>
                    <select
                      value={formData.unidad_medida}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          unidad_medida: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
                    >
                      {UNIDADES_MEDIDA.map((unidad) => (
                        <option key={unidad.value} value={unidad.value}>
                          {unidad.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Stock */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Stock Actual <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="number"
                      min="0"
                      value={formData.stock || ""}
                      onChange={(e) => {
                        const value =
                          e.target.value === ""
                            ? 0
                            : parseInt(e.target.value) || 0;
                        setFormData({ ...formData, stock: value });
                      }}
                      className={formErrors.stock ? "border-red-500" : ""}
                      placeholder="0"
                    />
                    {formErrors.stock && (
                      <p className="text-red-500 text-sm mt-1">
                        {formErrors.stock}
                      </p>
                    )}
                  </div>

                  {/* Stock Mínimo */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Stock Mínimo <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="number"
                      min="0"
                      value={formData.stock_minimo || ""}
                      onChange={(e) => {
                        const value =
                          e.target.value === ""
                            ? 0
                            : parseInt(e.target.value) || 0;
                        setFormData({ ...formData, stock_minimo: value });
                      }}
                      className={
                        formErrors.stock_minimo ? "border-red-500" : ""
                      }
                      placeholder="5"
                    />
                    {formErrors.stock_minimo && (
                      <p className="text-red-500 text-sm mt-1">
                        {formErrors.stock_minimo}
                      </p>
                    )}
                  </div>
                </div>

                {/* Botones */}
                <div className="flex justify-end gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setModalMode(null)}
                    disabled={submitting}
                  >
                    Cancelar
                  </Button>
                  <Button type="submit" disabled={submitting}>
                    {submitting ? (
                      <>
                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        Guardando...
                      </>
                    ) : (
                      <>
                        <Plus className="w-5 h-5 mr-2" />
                        {modalMode === "create"
                          ? "Crear Producto"
                          : "Guardar Cambios"}
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Actualizar Stock */}
      {modalMode === "stock" && selectedProducto && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  Actualizar Stock
                </h2>
                <button
                  onClick={() => setModalMode(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Producto</p>
                <p className="font-medium text-gray-900">
                  {selectedProducto.nombre}
                </p>
                <p className="text-sm text-gray-600 mt-2">Stock actual</p>
                <p className="text-2xl font-bold text-blue-600">
                  {selectedProducto.stock}{" "}
                  {selectedProducto.unidad_medida_display}
                </p>
              </div>

              <form onSubmit={handleStockSubmit} className="space-y-4">
                {/* Tipo de Movimiento */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tipo de Movimiento
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() =>
                        setStockData({
                          ...stockData,
                          tipo_movimiento: "entrada",
                        })
                      }
                      className={`px-4 py-2 rounded-lg border-2 font-medium ${
                        stockData.tipo_movimiento === "entrada"
                          ? "border-green-500 bg-green-50 text-green-700"
                          : "border-gray-300 text-gray-700"
                      }`}
                    >
                      <TrendingUp className="w-5 h-5 mx-auto mb-1" />
                      Entrada
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        setStockData({
                          ...stockData,
                          tipo_movimiento: "salida",
                        })
                      }
                      className={`px-4 py-2 rounded-lg border-2 font-medium ${
                        stockData.tipo_movimiento === "salida"
                          ? "border-red-500 bg-red-50 text-red-700"
                          : "border-gray-300 text-gray-700"
                      }`}
                    >
                      <TrendingDown className="w-5 h-5 mx-auto mb-1" />
                      Salida
                    </button>
                  </div>
                </div>

                {/* Cantidad */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Cantidad
                  </label>
                  <Input
                    type="number"
                    min="1"
                    value={stockData.cantidad || ""}
                    onChange={(e) => {
                      const value =
                        e.target.value === ""
                          ? 0
                          : parseInt(e.target.value) || 0;
                      setStockData({ ...stockData, cantidad: value });
                    }}
                    placeholder="0"
                  />
                </div>

                {/* Motivo */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Motivo (opcional)
                  </label>
                  <textarea
                    value={stockData.motivo}
                    onChange={(e) =>
                      setStockData({ ...stockData, motivo: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                    placeholder="Razón del movimiento..."
                    rows={3}
                  />
                </div>

                {/* Nuevo Stock */}
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Nuevo stock</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {stockData.tipo_movimiento === "entrada"
                      ? selectedProducto.stock + (stockData.cantidad || 0)
                      : Math.max(
                          0,
                          selectedProducto.stock - (stockData.cantidad || 0)
                        )}{" "}
                    {selectedProducto.unidad_medida_display}
                  </p>
                </div>

                {/* Botones */}
                <div className="flex justify-end gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setModalMode(null)}
                    disabled={submitting}
                  >
                    Cancelar
                  </Button>
                  <Button type="submit" disabled={submitting}>
                    {submitting ? (
                      <>
                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        Actualizando...
                      </>
                    ) : (
                      <>
                        <ShoppingCart className="w-5 h-5 mr-2" />
                        Actualizar Stock
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}

export default function ProductosPage() {
  return (
    <ProtectedRoute requiredPermission={PermissionCodes.CLIENT_VIEW}>
      <ProductosPageContent />
    </ProtectedRoute>
  );
}
