"use client";

import React, { useState, useEffect } from "react";
import { X, Plus, Trash2, Search } from "lucide-react";
import {
  Venta,
  ventaService,
  CreateVentaDTO,
  DetalleVentaCreate,
} from "@/lib/services/venta.service";
import { clientService } from "@/lib/services/client.service";
import { productoService, Producto } from "@/lib/services/producto.service";

interface CreateEditVentaModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  venta?: Venta | null;
}

const METODOS_PAGO = [
  { value: "efectivo", label: "Efectivo" },
  { value: "tarjeta", label: "Tarjeta" },
  { value: "transferencia", label: "Transferencia" },
  { value: "qr", label: "QR" },
];

export default function CreateEditVentaModal({
  isOpen,
  onClose,
  onSuccess,
  venta,
}: CreateEditVentaModalProps) {
  const [formData, setFormData] = useState<CreateVentaDTO>({
    cliente: 0,
    metodo_pago: "efectivo",
    descuento: 0,
    observaciones: "",
    detalles: [],
  });
  const [clientes, setClientes] = useState<any[]>([]);
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
      loadClientes();
      loadProductos();
      if (venta) {
        // Cargar datos de la venta para editar
        setFormData({
          cliente: venta.cliente,
          metodo_pago: venta.metodo_pago,
          descuento: parseFloat(venta.descuento),
          observaciones: venta.observaciones || "",
          detalles: venta.detalles?.map((d) => ({
            producto: d.producto,
            cantidad: d.cantidad,
            precio_unitario: parseFloat(d.precio_unitario),
            descuento: parseFloat(d.descuento),
          })) || [],
        });
      } else {
        setFormData({
          cliente: 0,
          metodo_pago: "efectivo",
          descuento: 0,
          observaciones: "",
          detalles: [],
        });
      }
      setError("");
    }
  }, [isOpen, venta]);

  const loadClientes = async () => {
    try {
      const response = await clientService.getAll({ page_size: 100 });
      setClientes(response.results || []);
    } catch (error) {
      console.error("Error al cargar clientes:", error);
    }
  };

  const loadProductos = async () => {
    try {
      setLoadingData(true);
      const response = await productoService.getAll({
        page_size: 100,
        estado: "ACTIVO",
      });
      const productosActivos = (response?.results || []).filter(
        (p) => p.stock > 0
      );
      setProductos(productosActivos);
      setProductosDisponibles(productosActivos);
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

    if (cantidadProducto > selectedProducto.stock) {
      alert(`Stock insuficiente. Disponible: ${selectedProducto.stock}`);
      return;
    }

    const precio = precioProducto || parseFloat(selectedProducto.precio);
    const descuento = descuentoProducto || 0;

    const nuevoDetalle: DetalleVentaCreate = {
      producto: selectedProducto.id,
      cantidad: cantidadProducto,
      precio_unitario: precio,
      descuento: descuento,
    };

    setFormData({
      ...formData,
      detalles: [...formData.detalles, nuevoDetalle],
    });

    // Reset
    setSelectedProducto(null);
    setCantidadProducto(1);
    setPrecioProducto(0);
    setDescuentoProducto(0);
    setSearchProducto("");
  };

  const handleRemoveProducto = (index: number) => {
    const nuevosDetalles = formData.detalles.filter((_, i) => i !== index);
    setFormData({ ...formData, detalles: nuevosDetalles });
  };

  const calcularTotal = () => {
    const subtotal = formData.detalles.reduce(
      (sum, detalle) =>
        sum + detalle.cantidad * detalle.precio_unitario - (detalle.descuento || 0),
      0
    );
    return subtotal - (formData.descuento || 0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    if (formData.cliente === 0) {
      setError("Debe seleccionar un cliente");
      setLoading(false);
      return;
    }

    if (formData.detalles.length === 0) {
      setError("Debe agregar al menos un producto");
      setLoading(false);
      return;
    }

    try {
      if (venta) {
        await ventaService.update(venta.id, {
          metodo_pago: formData.metodo_pago,
          descuento: formData.descuento,
          observaciones: formData.observaciones,
        });
      } else {
        await ventaService.create(formData);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error("Error al guardar venta:", err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else if (err.response?.data) {
        const errors = Object.values(err.response.data).flat();
        setError(errors.join(", "));
      } else {
        setError("Error al guardar la venta");
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const subtotal = formData.detalles.reduce(
    (sum, detalle) =>
      sum + detalle.cantidad * detalle.precio_unitario - (detalle.descuento || 0),
    0
  );
  const total = subtotal - (formData.descuento || 0);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            {venta ? "Editar Venta" : "Nueva Venta"}
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

          {/* Cliente */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cliente <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.cliente}
              onChange={(e) =>
                setFormData({ ...formData, cliente: parseInt(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              required
              disabled={!!venta}
            >
              <option value={0}>Seleccione un cliente</option>
              {clientes.map((cliente) => (
                <option key={cliente.id} value={cliente.id}>
                  {cliente.nombre} {cliente.apellido} - CI: {cliente.ci}
                </option>
              ))}
            </select>
          </div>

          {/* Agregar Producto */}
          {!venta && (
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
                      setPrecioProducto(parseFloat(producto.precio));
                    }
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                >
                  <option value="">Seleccione un producto</option>
                  {productosDisponibles.map((producto) => (
                    <option key={producto.id} value={producto.id}>
                      {producto.nombre} - Stock: {producto.stock} - Precio: $
                      {parseFloat(producto.precio).toFixed(2)}
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
                      max={selectedProducto.stock}
                      value={cantidadProducto}
                      onChange={(e) =>
                        setCantidadProducto(parseInt(e.target.value) || 1)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Stock disponible: {selectedProducto.stock}
                    </p>
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
          {formData.detalles.length > 0 && (
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <table className="w-full">
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
                    {!venta && (
                      <th className="px-4 py-2 text-center text-sm font-semibold text-gray-700">
                        Acción
                      </th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {formData.detalles.map((detalle, index) => {
                    const producto = productos.find(
                      (p) => p.id === detalle.producto
                    );
                    const subtotalDetalle =
                      detalle.cantidad * detalle.precio_unitario -
                      (detalle.descuento || 0);
                    return (
                      <tr key={index} className="border-t border-gray-200">
                        <td className="px-4 py-2">
                          {producto?.nombre || `Producto #${detalle.producto}`}
                        </td>
                        <td className="px-4 py-2 text-center">
                          {detalle.cantidad}
                        </td>
                        <td className="px-4 py-2 text-right">
                          ${detalle.precio_unitario.toFixed(2)}
                        </td>
                        <td className="px-4 py-2 text-right">
                          ${(detalle.descuento || 0).toFixed(2)}
                        </td>
                        <td className="px-4 py-2 text-right font-medium">
                          ${subtotalDetalle.toFixed(2)}
                        </td>
                        {!venta && (
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

          {/* Método de Pago */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Método de Pago
            </label>
            <select
              value={formData.metodo_pago}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  metodo_pago: e.target.value as any,
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
            >
              {METODOS_PAGO.map((metodo) => (
                <option key={metodo.value} value={metodo.value}>
                  {metodo.label}
                </option>
              ))}
            </select>
          </div>

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
                : venta
                ? "Guardar Cambios"
                : "Crear Venta"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

