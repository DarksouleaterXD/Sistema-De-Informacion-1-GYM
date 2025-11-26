/**
 * Modal para Ajustar Stock de Inventario
 * Permite corregir diferencias entre inventario físico y registrado
 */
'use client';

import { useState } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import inventarioService from '@/lib/services/inventario.service';
import { Producto, AjustarStockResponse } from '@/lib/types';

interface AjustarStockModalProps {
  isOpen: boolean;
  onClose: () => void;
  producto: Producto;
  onSuccess?: (response: AjustarStockResponse) => void;
}

export default function AjustarStockModal({
  isOpen,
  onClose,
  producto,
  onSuccess,
}: AjustarStockModalProps) {
  const [cantidadReal, setCantidadReal] = useState<string>(producto.stock.toString());
  const [motivo, setMotivo] = useState('');
  const [referencia, setReferencia] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const diferencia = parseInt(cantidadReal || '0') - producto.stock;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validaciones
    if (!cantidadReal || parseInt(cantidadReal) < 0) {
      setError('La cantidad real debe ser un número mayor o igual a 0');
      return;
    }

    if (!motivo.trim()) {
      setError('El motivo del ajuste es obligatorio');
      return;
    }

    if (diferencia === 0) {
      setError('El stock registrado ya coincide con la cantidad ingresada');
      return;
    }

    setLoading(true);

    try {
      const response = await inventarioService.ajustarStock({
        producto_id: producto.id,
        cantidad_real: parseInt(cantidadReal),
        motivo: motivo.trim(),
        referencia: referencia.trim() || undefined,
      });

      if (onSuccess) {
        onSuccess(response);
      }

      // Resetear formulario
      setCantidadReal(producto.stock.toString());
      setMotivo('');
      setReferencia('');
      onClose();
    } catch (err: any) {
      console.error('Error en ajuste de stock:', err);
      const errorMessage = err.message || err.error || 'Error al ajustar el stock';
      setError(errorMessage);
      // No cerrar el modal para que el usuario vea el error
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setCantidadReal(producto.stock.toString());
      setMotivo('');
      setReferencia('');
      setError(null);
      onClose();
    }
  };

  if (!isOpen) return null;

  const tipoAjuste = diferencia > 0 ? 'Positivo (Exceso)' : diferencia < 0 ? 'Negativo (Faltante)' : 'Sin cambios';
  const colorDiferencia = diferencia > 0 ? 'text-green-600' : diferencia < 0 ? 'text-red-600' : 'text-gray-600';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center sticky top-0 bg-white">
          <h2 className="text-xl font-semibold text-gray-800">Ajustar Stock de Inventario</h2>
          <button
            onClick={handleClose}
            disabled={loading}
            className="text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Información del Producto */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">Producto Seleccionado</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-blue-700 font-medium">Código:</span>
                <span className="ml-2 text-blue-900">{producto.codigo}</span>
              </div>
              <div>
                <span className="text-blue-700 font-medium">Nombre:</span>
                <span className="ml-2 text-blue-900">{producto.nombre}</span>
              </div>
              <div>
                <span className="text-blue-700 font-medium">Stock Actual:</span>
                <span className="ml-2 text-blue-900 font-bold">{producto.stock} {producto.unidad_medida}</span>
              </div>
              <div>
                <span className="text-blue-700 font-medium">Stock Mínimo:</span>
                <span className="ml-2 text-blue-900">{producto.stock_minimo} {producto.unidad_medida}</span>
              </div>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
              <div className="flex items-center">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="font-medium">{error}</span>
              </div>
            </div>
          )}

          {/* Cantidad Real */}
          <div>
            <label htmlFor="cantidadReal" className="block text-sm font-medium text-gray-700 mb-1">
              Cantidad Física Real <span className="text-red-500">*</span>
            </label>
            <Input
              id="cantidadReal"
              type="number"
              value={cantidadReal}
              onChange={(e) => setCantidadReal(e.target.value)}
              min="0"
              required
              disabled={loading}
              placeholder="Ingrese la cantidad verificada físicamente"
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              Cantidad actual verificada en el inventario físico
            </p>
          </div>

          {/* Diferencia Calculada */}
          {diferencia !== 0 && (
            <div className={`border rounded-lg p-4 ${diferencia > 0 ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
              <h4 className="font-semibold text-gray-800 mb-2">Resumen del Ajuste</h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-700">Stock Registrado:</span>
                  <span className="font-medium">{producto.stock} {producto.unidad_medida}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-700">Cantidad Real:</span>
                  <span className="font-medium">{cantidadReal || 0} {producto.unidad_medida}</span>
                </div>
                <div className="border-t pt-2 mt-2">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-gray-800">Diferencia:</span>
                    <span className={`font-bold text-lg ${colorDiferencia}`}>
                      {diferencia > 0 ? '+' : ''}{diferencia} {producto.unidad_medida}
                    </span>
                  </div>
                  <div className="flex justify-between items-center mt-1">
                    <span className="text-gray-700">Tipo de Ajuste:</span>
                    <span className={`font-medium ${colorDiferencia}`}>{tipoAjuste}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Motivo */}
          <div>
            <label htmlFor="motivo" className="block text-sm font-medium text-gray-700 mb-1">
              Motivo del Ajuste <span className="text-red-500">*</span>
            </label>
            <textarea
              id="motivo"
              value={motivo}
              onChange={(e) => setMotivo(e.target.value)}
              required
              disabled={loading}
              rows={3}
              placeholder="Ej: Ajuste por inventario físico - Faltante detectado en revisión mensual"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed text-gray-900 bg-white"
            />
            <p className="text-xs text-gray-500 mt-1">
              Describa detalladamente el motivo del ajuste (por exceso, faltante o corrección administrativa)
            </p>
          </div>

          {/* Referencia */}
          <div>
            <label htmlFor="referencia" className="block text-sm font-medium text-gray-700 mb-1">
              Referencia / Nro. Documento (Opcional)
            </label>
            <Input
              id="referencia"
              type="text"
              value={referencia}
              onChange={(e) => setReferencia(e.target.value)}
              disabled={loading}
              placeholder="Ej: INV-2024-001"
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              Número de acta, documento o referencia del ajuste
            </p>
          </div>

          {/* Información Importante */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex">
              <svg className="w-5 h-5 text-yellow-600 mr-2 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div className="text-sm">
                <p className="font-medium text-yellow-800 mb-1">Información Importante:</p>
                <ul className="list-disc list-inside text-yellow-700 space-y-1">
                  <li>Este ajuste actualizará el stock del producto en el sistema</li>
                  <li>Se generará un movimiento de inventario tipo &quot;AJUSTE&quot;</li>
                  <li>La acción quedará registrada en la bitácora de auditoría</li>
                  <li>Esta operación no puede deshacerse</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button
              type="button"
              variant="secondary"
              onClick={handleClose}
              disabled={loading}
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={loading || diferencia === 0}
            >
              {loading ? 'Ajustando...' : 'Confirmar Ajuste'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
