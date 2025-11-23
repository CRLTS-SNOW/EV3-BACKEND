// frontend/src/components/supplier-orders/SupplierOrderForm.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Swal from 'sweetalert2';
import {
  validateRequired,
  validateMaxLength
} from '../../utils/validators';

const SupplierOrderForm = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [suppliers, setSuppliers] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [zones, setZones] = useState([]);
  const [formData, setFormData] = useState({
    supplier: '',
    warehouse: '',
    zone: '',
    expected_delivery_date: '',
    observaciones: '',
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    loadSuppliers();
    loadWarehouses();
  }, []);

  useEffect(() => {
    if (formData.warehouse) {
      loadZones(formData.warehouse);
    }
  }, [formData.warehouse]);

  const loadSuppliers = async () => {
    try {
      const response = await api.getSuppliers();
      setSuppliers(response.data.results || response.data);
    } catch (error) {
      console.error('Error al cargar proveedores:', error);
    }
  };

  const loadWarehouses = async () => {
    try {
      const response = await api.getWarehouses();
      setWarehouses(response.data.results || response.data);
    } catch (error) {
      console.error('Error al cargar bodegas:', error);
    }
  };

  const loadZones = async (warehouseId) => {
    try {
      const response = await api.getZonesByWarehouse(warehouseId);
      setZones(response.data.zones || []);
    } catch (error) {
      console.error('Error al cargar zonas:', error);
    }
  };

  const validateField = (name, value) => {
    let error = '';
    
    switch (name) {
      case 'supplier':
        error = validateRequired(value, 'El proveedor');
        break;
      case 'warehouse':
        error = validateRequired(value, 'La bodega');
        break;
      case 'zone':
        error = validateRequired(value, 'La zona');
        break;
      case 'observaciones':
        if (value) error = validateMaxLength(value, 1000, 'Las observaciones');
        break;
      default:
        break;
    }
    
    return error;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    // Validar campo en tiempo real
    const error = validateField(name, value);
    setErrors({
      ...errors,
      [name]: error,
    });
    
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const validateForm = () => {
    const newErrors = {};
    
    newErrors.supplier = validateField('supplier', formData.supplier);
    newErrors.warehouse = validateField('warehouse', formData.warehouse);
    newErrors.zone = validateField('zone', formData.zone);
    newErrors.observaciones = validateField('observaciones', formData.observaciones);
    
    setErrors(newErrors);
    
    return Object.values(newErrors).every(error => error === '');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      Swal.fire({
        icon: 'error',
        title: 'Error de validación',
        text: 'Por favor, corrige los errores en el formulario antes de guardar',
      });
      return;
    }
    
    setLoading(true);

    try {
      const response = await api.createSupplierOrder(formData);
      Swal.fire({
        icon: 'success',
        title: '¡Éxito!',
        text: 'Orden creada exitosamente',
      });
      navigate(`/supplier-orders/${response.data.id}`);
    } catch (error) {
      const errorMessage = error.response?.data?.error || Object.values(error.response?.data || {}).flat().join(', ') || 'Error al crear orden';
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: errorMessage,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Nueva Orden a Proveedor</h1>
      <div className="card">
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Proveedor *</label>
                <select
                  className={`form-select ${errors.supplier ? 'is-invalid' : ''}`}
                  name="supplier"
                  value={formData.supplier}
                  onChange={handleChange}
                  required
                >
                  <option value="">Seleccionar...</option>
                  {suppliers.map((supplier) => (
                    <option key={supplier.id} value={supplier.id}>
                      {supplier.nombre_display || supplier.razon_social}
                    </option>
                  ))}
                </select>
                {errors.supplier && (
                  <div className="invalid-feedback">{errors.supplier}</div>
                )}
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Bodega *</label>
                <select
                  className={`form-select ${errors.warehouse ? 'is-invalid' : ''}`}
                  name="warehouse"
                  value={formData.warehouse}
                  onChange={handleChange}
                  required
                >
                  <option value="">Seleccionar...</option>
                  {warehouses.map((warehouse) => (
                    <option key={warehouse.id} value={warehouse.id}>
                      {warehouse.name}
                    </option>
                  ))}
                </select>
                {errors.warehouse && (
                  <div className="invalid-feedback">{errors.warehouse}</div>
                )}
              </div>
            </div>

            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Zona *</label>
                <select
                  className={`form-select ${errors.zone ? 'is-invalid' : ''}`}
                  name="zone"
                  value={formData.zone}
                  onChange={handleChange}
                  required
                  disabled={!formData.warehouse}
                >
                  <option value="">Seleccionar bodega primero...</option>
                  {zones.map((zone) => (
                    <option key={zone.id} value={zone.id}>
                      {zone.name}
                    </option>
                  ))}
                </select>
                {errors.zone && (
                  <div className="invalid-feedback">{errors.zone}</div>
                )}
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Fecha Esperada de Entrega</label>
                <input
                  type="date"
                  className="form-control"
                  name="expected_delivery_date"
                  value={formData.expected_delivery_date}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="mb-3">
              <label className="form-label">Observaciones</label>
              <textarea
                className={`form-control ${errors.observaciones ? 'is-invalid' : ''}`}
                name="observaciones"
                rows="3"
                value={formData.observaciones}
                onChange={handleChange}
                maxLength={1000}
              />
              {errors.observaciones && (
                <div className="invalid-feedback">{errors.observaciones}</div>
              )}
            </div>

            <div className="d-flex justify-content-end gap-2">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate('/supplier-orders')}
              >
                Cancelar
              </button>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Guardando...' : 'Crear Orden'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SupplierOrderForm;

