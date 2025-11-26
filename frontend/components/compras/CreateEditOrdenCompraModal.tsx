"use client";

import React, { useState, useEffect } from "react";
import { X, Plus, Trash2, Search } from "lucide-react";
import {
  OrdenCompra,
  compraService,
  CreateOrdenCompraDTO,
  ItemOrdenCompraCreate,
} from "@/lib/services/compra.service";
import { proveedorService } from "@/lib/services/proveedor.service";
import { productoService, Producto } from "@/lib/services/producto.service";

interface CreateEditOrdenCompraModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  orden?: OrdenCompra | null;
}

export default function CreateEditOrdenCompraModal({
  isOpen,
  onClose,
  onSuccess,
  orden,
}: CreateEditOrdenCompraModalProps) {
  const [formData, setFormData] = useState<CreateOrdenCompraDTO>({
    proveedor: 0,
    fecha_esperada: "",
    descuento: 0,
    observaciones: "",
    items: [],
  });
  const [proveedores, setProveedores] = useState<any[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [productosDisponibles, setProductosDisponibles] = useState<Producto[]>(
    []
  );
  const [searchProducto, setSearchProducto] = useState("");
  const [selectedProducto, setSelectedProducto] = useState<Producto | null>(
    null
  );
  const [cantidadProducto, setCantidadProducto] = useState(1);
  const [precioProducto, setPrecioProducto] = useState(0);
  const [descuentoProducto, setDescuentoProducto] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    if (isOpen) {
      loadProveedores();
      loadProductos();
      if (orden) {
        // Cargar datos de la orden para editar
        setFormData({
          proveedor: orden.proveedor,
          fecha_esperada: orden.fecha_esperada || "",
          descuento: parseFloat(orden.descuento),
          observaciones: orden.observaciones || "",
          items: orden.items?.map((item) => ({
            producto: item.producto,
            cantidad: item.cantidad,
            precio_unitario: parseFloat(item.precio_unitario),
            descuento: parseFloat(item.descuento),
          })) || [],
        });
      } else {
        setFormData({
          proveedor: 0,
          fecha_esperada: "",
          descuento: 0,
          observaciones: "",
          items: [],
        });
      }
      setError("");
    }
  }, [isOpen, orden]);

  const loadProveedores = async () => {
    try {
      const response = await proveedorService.getAll({ page_size: 100 });
      setProveedores(response?.results || []);
    } catch (error) {
      console.error("Error al cargar proveedores:", error);
    }
  };

  const loadProductos = async () => {
    try {
      setLoadingData(true);
      const response = await productoService.getAll({
        page_size: 100,
      });
      setProductos(response?.results || []);
      setProductosDisponibles(response?.results || []);
    } catch (error) {
      console.error("Error al cargar productos:", error);
    } finally {
      setLoadingData(false);
    }
  };

  useEffect(() => {
    if (searchProducto) {
      const filtered = productos.filter(
        (p) =>
          p.nombre.toLowerCase().includes(searchProducto.toLowerCase()) ||
          p.codigo.toLowerCase().includes(searchProducto.toLowerCase())
      );
      setProductosDisponibles(filtered);
    } else {
      setProductosDisponibles(productos);
    }
  }, [searchProducto, productos]);

  const handleAddProducto = () => {
    if (!selectedProducto) {
      alert("Seleccione un producto");
      return;
    }

    if (cantidadProducto <= 0) {
      alert("La cantidad debe ser mayor a 0");
      return;
    }

    const precio = precioProducto || parseFloat(selectedProducto.costo || "0");
    const descuento = descuentoProducto || 0;

    const nuevoItem: ItemOrdenCompraCreate = {
      producto: selectedProducto.id,
      cantidad: cantidadProducto,
      precio_unitario: precio,
      descuento: descuento,
    };

    setFormData({
      ...formData,
      items: [...formData.items, nuevoItem],
    });

    // Reset
    setSelectedProducto(null);
    setCantidadProducto(1);
    setPrecioProducto(0);
    setDescuentoProducto(0);
    setSearchProducto("");
  };

  const handleRemoveProducto = (index: number) => {
    const nuevosItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: nuevosItems });
  };

  const calcularTotal = () => {
    const subtotal = formData.items.reduce(
      (sum, item) =>
        sum + item.cantidad * item.precio_unitario - (item.descuento || 0),
      0
    );
    return subtotal - (formData.descuento || 0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    if (formData.proveedor === 0) {
      setError("Debe seleccionar un proveedor");
      setLoading(false);
      return;
    }

    if (formData.items.length === 0) {
      setError("Debe agregar al menos un producto");
      setLoading(false);
      return;
    }

    try {
      if (orden) {
        await compraService.update(orden.id, {
          fecha_esperada: formData.fecha_esperada || undefined,
          descuento: formData.descuento,
          observaciones: formData.observaciones,
        });
      } else {
        await compraService.create(formData);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error("Error al guardar orden:", err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else if (err.response?.data) {
        const errors = Object.values(err.response.data).flat();
        setError(errors.join(", "));
      } else {
        setError("Error al guardar la orden");
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const subtotal = formData.items.reduce(
    (sum, item) =>
      sum + item.cantidad * item.precio_unitario - (item.descuento || 0),
    0
  );
  const total = subtotal - (formData.descuento || 0);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            {orden ? "Editar Orden de Compra" : "Nueva Orden de Compra"}
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

          {/* Proveedor */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Proveedor <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.proveedor}
              onChange={(e) =>
                setFormData({ ...formData, proveedor: parseInt(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              required
              disabled={!!orden}
            >
              <option value={0}>Seleccione un proveedor</option>
              {proveedores.map((proveedor) => (
                <option key={proveedor.id} value={proveedor.id}>
                  {proveedor.razon_social} - NIT: {proveedor.nit}
                </option>
              ))}
            </select>
          </div>

          {/* Fecha Esperada */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Fecha Esperada de Entrega
            </label>
            <input
              type="date"
              value={formData.fecha_esperada}
              onChange={(e) =>
                setFormData({ ...formData, fecha_esperada: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
            />
          </div>

          {/* Agregar Producto */}
          {!orden && (
            <div className="border border-gray-200 rounded-lg p-4 space-y-4">
              <h3 className="font-semibold text-gray-900">Agregar Producto</h3>
              
              {/* Búsqueda de producto */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Buscar producto..."
                  value={searchProducto}
                  onChange={(e) => setSearchProducto(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                />
              </div>

              {productosDisponibles.length > 0 && (
                <select
                  value={selectedProducto?.id || ""}
                  onChange={(e) => {
                    const producto = productosDisponibles.find(
                      (p) => p.id === parseInt(e.target.value)
                    );
                    if (producto) {
                      setSelectedProducto(producto);
                      setPrecioProducto(parseFloat(producto.costo || "0"));
                    }
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                >
                  <option value="">Seleccione un producto</option>
                  {productosDisponibles.map((producto) => (
                    <option key={producto.id} value={producto.id}>
                      {producto.nombre} - Costo: $
                      {parseFloat(producto.costo || "0").toFixed(2)}
                    </option>
                  ))}
                </select>
              )}

              {selectedProducto && (
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Cantidad
                    </label>
                    <input
                      type="number"
                      min="1"
                      value={cantidadProducto}
                      onChange={(e) =>
                        setCantidadProducto(parseInt(e.target.value) || 1)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Precio Unit.
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={precioProducto}
                      onChange={(e) =>
                        setPrecioProducto(parseFloat(e.target.value) || 0)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Descuento
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={descuentoProducto}
                      onChange={(e) =>
                        setDescuentoProducto(parseFloat(e.target.value) || 0)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                    />
                  </div>
                </div>
              )}

              <button
                type="button"
                onClick={handleAddProducto}
                disabled={!selectedProducto}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors flex items-center justify-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Agregar Producto
              </button>
            </div>
          )}

          {/* Lista de Productos */}
          {formData.items.length > 0 && (
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <table className="w-full bg-white">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">
                      Producto
                    </th>
                    <th className="px-4 py-2 text-center text-sm font-semibold text-gray-700">
                      Cantidad
                    </th>
                    <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">
                      Precio Unit.
                    </th>
                    <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">
                      Descuento
                    </th>
                    <th className="px-4 py-2 text-right text-sm font-semibold text-gray-700">
                      Subtotal
                    </th>
                    {!orden && (
                      <th className="px-4 py-2 text-center text-sm font-semibold text-gray-700">
                        Acción
                      </th>
                    )}
                  </tr>
                </thead>
                <tbody className="bg-white">
                  {formData.items.map((item, index) => {
                    const producto = productos.find(
                      (p) => p.id === item.producto
                    );
                    const subtotalItem =
                      item.cantidad * item.precio_unitario -
                      (item.descuento || 0);
                    return (
                      <tr key={index} className="border-t border-gray-200 bg-white">
                        <td className="px-4 py-2 text-gray-900">
                          {producto?.nombre || `Producto #${item.producto}`}
                        </td>
                        <td className="px-4 py-2 text-center text-gray-900">
                          {item.cantidad}
                        </td>
                        <td className="px-4 py-2 text-right text-gray-900">
                          ${item.precio_unitario.toFixed(2)}
                        </td>
                        <td className="px-4 py-2 text-right text-gray-900">
                          ${(item.descuento || 0).toFixed(2)}
                        </td>
                        <td className="px-4 py-2 text-right font-medium text-gray-900">
                          ${subtotalItem.toFixed(2)}
                        </td>
                        {!orden && (
                          <td className="px-4 py-2 text-center">
                            <button
                              type="button"
                              onClick={() => handleRemoveProducto(index)}
                              className="text-red-600 hover:text-red-800"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </td>
                        )}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {/* Descuento General */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Descuento General
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={formData.descuento || 0}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  descuento: parseFloat(e.target.value) || 0,
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
            />
          </div>

          {/* Observaciones */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Observaciones
            </label>
            <textarea
              value={formData.observaciones}
              onChange={(e) =>
                setFormData({ ...formData, observaciones: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              rows={3}
            />
          </div>

          {/* Totales */}
          <div className="border-t border-gray-200 pt-4 space-y-2">
            <div className="flex justify-between">
              <span className="font-medium text-gray-700">Subtotal:</span>
              <span className="font-medium text-gray-900">
                ${subtotal.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium text-gray-700">Descuento:</span>
              <span className="font-medium text-gray-900">
                ${(formData.descuento || 0).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between text-lg font-bold border-t border-gray-200 pt-2">
              <span className="text-gray-900">Total:</span>
              <span className="text-blue-600">${total.toFixed(2)}</span>
            </div>
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
                : orden
                ? "Guardar Cambios"
                : "Crear Orden"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

