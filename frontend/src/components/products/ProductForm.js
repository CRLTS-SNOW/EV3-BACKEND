// frontend/src/components/products/ProductForm.js
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Swal from 'sweetalert2';
import {
  validateRequired,
  validateMaxLength,
  validatePositiveNumber,
  validatePositiveNumberGreaterThanZero,
  validatePercentage,
  validateUrl,
  validateSkuEan
} from '../../utils/validators';

const ProductForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = !!id;
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [productData, setProductData] = useState(null);
  const [formData, setFormData] = useState({
    sku: '',
    ean_upc: '',
    name: '',
    descripcion: '',
    categoria: 'General',
    marca: '',
    modelo: '',
    uom_compra: 'UN',
    uom_venta: 'UN',
    factor_conversion: '1.0',
    costo_estandar: '',
    precio_venta: '',
    impuesto_iva: '19.0',
    stock_minimo: '0',
    stock_maximo: '',
    punto_reorden: '',
    perishable: false,
    control_por_lote: false,
    control_por_serie: false,
    imagen_url: '',
    ficha_tecnica_url: '',
  });

  useEffect(() => {
    if (isEdit) {
      loadProduct();
    }
  }, [id]);

  const loadProduct = async () => {
    try {
      const response = await api.getProduct(id);
      const data = response.data;
      setProductData(response.data);
      setFormData({
        sku: data.sku || '',
        ean_upc: data.ean_upc || '',
        name: data.name || '',
        descripcion: data.descripcion || '',
        categoria: data.categoria || 'General',
        marca: data.marca || '',
        modelo: data.modelo || '',
        uom_compra: data.uom_compra || 'UN',
        uom_venta: data.uom_venta || 'UN',
        factor_conversion: data.factor_conversion || '1.0',
        costo_estandar: data.costo_estandar || '',
        precio_venta: data.precio_venta || '',
        impuesto_iva: data.impuesto_iva || '19.0',
        stock_minimo: data.stock_minimo || '0',
        stock_maximo: data.stock_maximo || '',
        punto_reorden: data.punto_reorden || '',
        perishable: data.perishable || false,
        control_por_lote: data.control_por_lote || false,
        control_por_serie: data.control_por_serie || false,
        imagen_url: data.imagen_url || '',
        ficha_tecnica_url: data.ficha_tecnica_url || '',
      });
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al cargar el producto',
      });
      navigate('/products');
    }
  };

  // Validaciones
  const validateField = (name, value) => {
    let error = '';
    
    switch (name) {
      case 'name':
        error = validateRequired(value, 'El nombre');
        if (!error) error = validateMaxLength(value, 200, 'El nombre');
        break;
      case 'ean_upc':
        if (value) {
          error = validateSkuEan(value);
          if (!error) error = validateMaxLength(value, 50, 'El código EAN/UPC');
        }
        break;
      case 'descripcion':
        if (value) error = validateMaxLength(value, 2000, 'La descripción');
        break;
      case 'categoria':
        error = validateRequired(value, 'La categoría');
        if (!error) error = validateMaxLength(value, 100, 'La categoría');
        break;
      case 'marca':
        if (value) error = validateMaxLength(value, 100, 'La marca');
        break;
      case 'modelo':
        if (value) error = validateMaxLength(value, 100, 'El modelo');
        break;
      case 'factor_conversion':
        error = validateRequired(value, 'El factor de conversión');
        if (!error) {
          const num = parseFloat(value);
          if (isNaN(num)) error = 'El factor de conversión debe ser un número válido';
          else if (num < 0.0001) error = 'El factor de conversión debe ser al menos 0.0001';
          else if (num > 9999.9999) error = 'El factor de conversión es demasiado alto';
        }
        break;
      case 'costo_estandar':
        if (value) {
          error = validatePositiveNumber(value, 'El costo estándar');
          if (!error) {
            const num = parseFloat(value);
            if (num > 999999999999.999999) error = 'El costo estándar es demasiado alto';
          }
        }
        break;
      case 'precio_venta':
        if (value) {
          error = validatePositiveNumber(value, 'El precio de venta');
          if (!error) {
            const num = parseFloat(value);
            if (num > 999999999999999.99) error = 'El precio de venta es demasiado alto';
          }
        }
        break;
      case 'impuesto_iva':
        error = validateRequired(value, 'El impuesto IVA');
        if (!error) {
          const num = parseFloat(value);
          if (isNaN(num)) error = 'El impuesto IVA debe ser un número válido';
          else if (num < 0) error = 'El impuesto IVA no puede ser negativo';
          else if (num > 100) error = 'El impuesto IVA no puede ser mayor a 100%';
        }
        break;
      case 'stock_minimo':
        error = validateRequired(value, 'El stock mínimo');
        if (!error) error = validatePositiveNumber(value, 'El stock mínimo');
        break;
      case 'stock_maximo':
        if (value) {
          error = validatePositiveNumber(value, 'El stock máximo');
          if (!error && formData.stock_minimo) {
            const max = parseFloat(value);
            const min = parseFloat(formData.stock_minimo);
            if (max < min) error = 'El stock máximo debe ser mayor o igual al stock mínimo';
          }
        }
        break;
      case 'punto_reorden':
        if (value) {
          error = validatePositiveNumber(value, 'El punto de reorden');
          if (!error && formData.stock_minimo) {
            const punto = parseFloat(value);
            const min = parseFloat(formData.stock_minimo);
            if (punto < min) error = 'El punto de reorden debe ser mayor o igual al stock mínimo';
          }
        }
        break;
      case 'imagen_url':
        if (value) {
          error = validateUrl(value);
          if (!error) error = validateMaxLength(value, 500, 'La URL de la imagen');
        }
        break;
      case 'ficha_tecnica_url':
        if (value) {
          error = validateUrl(value);
          if (!error) error = validateMaxLength(value, 500, 'La URL de la ficha técnica');
        }
        break;
      default:
        break;
    }
    
    return error;
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    // Validar campo en tiempo real
    const error = validateField(name, value);
    setErrors({
      ...errors,
      [name]: error,
    });
    
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Validar todos los campos requeridos y opcionales
    newErrors.name = validateField('name', formData.name);
    newErrors.ean_upc = validateField('ean_upc', formData.ean_upc);
    newErrors.descripcion = validateField('descripcion', formData.descripcion);
    newErrors.categoria = validateField('categoria', formData.categoria);
    newErrors.marca = validateField('marca', formData.marca);
    newErrors.modelo = validateField('modelo', formData.modelo);
    newErrors.factor_conversion = validateField('factor_conversion', formData.factor_conversion);
    newErrors.costo_estandar = validateField('costo_estandar', formData.costo_estandar);
    newErrors.precio_venta = validateField('precio_venta', formData.precio_venta);
    newErrors.impuesto_iva = validateField('impuesto_iva', formData.impuesto_iva);
    newErrors.stock_minimo = validateField('stock_minimo', formData.stock_minimo);
    newErrors.stock_maximo = validateField('stock_maximo', formData.stock_maximo);
    newErrors.punto_reorden = validateField('punto_reorden', formData.punto_reorden);
    newErrors.imagen_url = validateField('imagen_url', formData.imagen_url);
    newErrors.ficha_tecnica_url = validateField('ficha_tecnica_url', formData.ficha_tecnica_url);
    
    setErrors(newErrors);
    
    // Verificar si hay errores
    return Object.values(newErrors).every(error => error === '');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validar formulario antes de enviar
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
      if (isEdit) {
        const response = await api.updateProduct(id, formData);
        setProductData(response.data); // Actualizar datos del producto para mostrar campos derivados
        Swal.fire({
          icon: 'success',
          title: '¡Éxito!',
          text: 'Producto actualizado exitosamente',
        });
      } else {
        await api.createProduct(formData);
        Swal.fire({
          icon: 'success',
          title: '¡Éxito!',
          text: 'Producto creado exitosamente',
        });
        navigate('/products');
      }
    } catch (error) {
      console.error('Error al guardar producto:', error);
      let errorMessage = 'Error al guardar producto';
      
      if (error.response?.data) {
        if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (typeof error.response.data === 'object') {
          // Formatear errores del formulario y actualizar errores de campos
          const formErrors = {};
          const errorList = [];
          
          for (const [key, value] of Object.entries(error.response.data)) {
            const errorText = Array.isArray(value) ? value.join(', ') : (typeof value === 'string' ? value : JSON.stringify(value));
            errorList.push(`${key}: ${errorText}`);
            formErrors[key] = errorText;
          }
          
          // Actualizar errores de campos
          setErrors(formErrors);
          
          errorMessage = errorList.length > 0 ? errorList.join('\n') : 'Error al guardar producto';
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      Swal.fire({
        icon: 'error',
        title: 'Error de validación',
        html: `<div style="text-align: left;">${errorMessage.split('\n').map(e => `<div>${e}</div>`).join('')}</div>`,
        width: '600px',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>{isEdit ? 'Editar Producto' : 'Nuevo Producto'}</h1>
      <div className="card">
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            <h5 className="mb-3">1. Identificación</h5>
            {isEdit && (
              <div className="row">
                <div className="col-md-6 mb-3">
                  <label className="form-label">SKU</label>
                  <input
                    type="text"
                    className="form-control"
                    value={formData.sku || ''}
                    disabled
                    readOnly
                  />
                  <small className="form-text text-muted">El SKU se genera automáticamente</small>
                </div>
              </div>
            )}
            
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Nombre *</label>
                <input
                  type="text"
                  className={`form-control ${errors.name ? 'is-invalid' : ''}`}
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  maxLength={200}
                />
                {errors.name && (
                  <div className="invalid-feedback">{errors.name}</div>
                )}
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Categoría *</label>
                <input
                  type="text"
                  className={`form-control ${errors.categoria ? 'is-invalid' : ''}`}
                  name="categoria"
                  value={formData.categoria}
                  onChange={handleChange}
                  required
                  maxLength={100}
                />
                {errors.categoria && (
                  <div className="invalid-feedback">{errors.categoria}</div>
                )}
              </div>
            </div>

            <div className="row">
              <div className="col-md-4 mb-3">
                <label className="form-label">EAN/UPC</label>
                <input
                  type="text"
                  className={`form-control ${errors.ean_upc ? 'is-invalid' : ''}`}
                  name="ean_upc"
                  value={formData.ean_upc}
                  onChange={handleChange}
                  maxLength={50}
                  placeholder="Código EAN/UPC (opcional)"
                />
                {errors.ean_upc && (
                  <div className="invalid-feedback">{errors.ean_upc}</div>
                )}
              </div>
              <div className="col-md-4 mb-3">
                <label className="form-label">Marca</label>
                <input
                  type="text"
                  className={`form-control ${errors.marca ? 'is-invalid' : ''}`}
                  name="marca"
                  value={formData.marca}
                  onChange={handleChange}
                  maxLength={100}
                />
                {errors.marca && (
                  <div className="invalid-feedback">{errors.marca}</div>
                )}
              </div>
              <div className="col-md-4 mb-3">
                <label className="form-label">Modelo</label>
                <input
                  type="text"
                  className={`form-control ${errors.modelo ? 'is-invalid' : ''}`}
                  name="modelo"
                  value={formData.modelo}
                  onChange={handleChange}
                  maxLength={100}
                />
                {errors.modelo && (
                  <div className="invalid-feedback">{errors.modelo}</div>
                )}
              </div>
            </div>

            <div className="mb-3">
              <label className="form-label">Descripción</label>
              <textarea
                className={`form-control ${errors.descripcion ? 'is-invalid' : ''}`}
                name="descripcion"
                rows="3"
                value={formData.descripcion}
                onChange={handleChange}
                placeholder="Descripción detallada del producto"
                maxLength={2000}
              />
              {errors.descripcion && (
                <div className="invalid-feedback">{errors.descripcion}</div>
              )}
            </div>

            <h5 className="mt-4 mb-3">2. Unidades y Precios</h5>
            <div className="row">
              <div className="col-md-3 mb-3">
                <label className="form-label">UOM Compra *</label>
                <select
                  className="form-select"
                  name="uom_compra"
                  value={formData.uom_compra}
                  onChange={handleChange}
                  required
                >
                  <option value="UN">Unidad (UN)</option>
                  <option value="CAJA">Caja (CAJA)</option>
                  <option value="KG">Kilogramo (KG)</option>
                  <option value="LT">Litro (LT)</option>
                  <option value="M">Metro (M)</option>
                </select>
              </div>
              <div className="col-md-3 mb-3">
                <label className="form-label">UOM Venta *</label>
                <select
                  className="form-select"
                  name="uom_venta"
                  value={formData.uom_venta}
                  onChange={handleChange}
                  required
                >
                  <option value="UN">Unidad (UN)</option>
                  <option value="CAJA">Caja (CAJA)</option>
                  <option value="KG">Kilogramo (KG)</option>
                  <option value="LT">Litro (LT)</option>
                  <option value="M">Metro (M)</option>
                </select>
              </div>
              <div className="col-md-3 mb-3">
                <label className="form-label">Factor Conversión *</label>
                <input
                  type="number"
                  step="0.0001"
                  min="0.0001"
                  className={`form-control ${errors.factor_conversion ? 'is-invalid' : ''}`}
                  name="factor_conversion"
                  value={formData.factor_conversion}
                  onChange={handleChange}
                  required
                />
                {errors.factor_conversion && (
                  <div className="invalid-feedback">{errors.factor_conversion}</div>
                )}
                <small className="form-text text-muted">Default: 1</small>
              </div>
              <div className="col-md-3 mb-3">
                <label className="form-label">Impuesto IVA (%) *</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  className={`form-control ${errors.impuesto_iva ? 'is-invalid' : ''}`}
                  name="impuesto_iva"
                  value={formData.impuesto_iva}
                  onChange={handleChange}
                  required
                />
                {errors.impuesto_iva && (
                  <div className="invalid-feedback">{errors.impuesto_iva}</div>
                )}
                <small className="form-text text-muted">Ej: 19%</small>
              </div>
            </div>

            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Costo Estándar</label>
                <input
                  type="number"
                  step="0.000001"
                  min="0"
                  className={`form-control ${errors.costo_estandar ? 'is-invalid' : ''}`}
                  name="costo_estandar"
                  value={formData.costo_estandar}
                  onChange={handleChange}
                />
                {errors.costo_estandar && (
                  <div className="invalid-feedback">{errors.costo_estandar}</div>
                )}
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Precio Venta</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  className={`form-control ${errors.precio_venta ? 'is-invalid' : ''}`}
                  name="precio_venta"
                  value={formData.precio_venta}
                  onChange={handleChange}
                />
                {errors.precio_venta && (
                  <div className="invalid-feedback">{errors.precio_venta}</div>
                )}
              </div>
            </div>

            {isEdit && (
              <div className="row mb-3">
                <div className="col-md-6">
                  <label className="form-label">Costo Promedio</label>
                  <input
                    type="number"
                    className="form-control"
                    value={productData?.costo_promedio || '0.00'}
                    disabled
                    readOnly
                  />
                  <small className="form-text text-muted">Solo lectura (calculado)</small>
                </div>
              </div>
            )}

            <h5 className="mt-4 mb-3">3. Stock y Control</h5>
            <div className="row">
              <div className="col-md-4 mb-3">
                <label className="form-label">Stock Mínimo *</label>
                <input
                  type="number"
                  step="0.0001"
                  min="0"
                  className={`form-control ${errors.stock_minimo ? 'is-invalid' : ''}`}
                  name="stock_minimo"
                  value={formData.stock_minimo}
                  onChange={handleChange}
                  required
                />
                {errors.stock_minimo && (
                  <div className="invalid-feedback">{errors.stock_minimo}</div>
                )}
                <small className="form-text text-muted">Default: 0</small>
              </div>
              <div className="col-md-4 mb-3">
                <label className="form-label">Stock Máximo</label>
                <input
                  type="number"
                  step="0.0001"
                  min="0"
                  className={`form-control ${errors.stock_maximo ? 'is-invalid' : ''}`}
                  name="stock_maximo"
                  value={formData.stock_maximo}
                  onChange={handleChange}
                />
                {errors.stock_maximo && (
                  <div className="invalid-feedback">{errors.stock_maximo}</div>
                )}
              </div>
              <div className="col-md-4 mb-3">
                <label className="form-label">Punto de Reorden</label>
                <input
                  type="number"
                  step="0.0001"
                  min="0"
                  className={`form-control ${errors.punto_reorden ? 'is-invalid' : ''}`}
                  name="punto_reorden"
                  value={formData.punto_reorden}
                  onChange={handleChange}
                />
                {errors.punto_reorden && (
                  <div className="invalid-feedback">{errors.punto_reorden}</div>
                )}
                <small className="form-text text-muted">Si no se especifica, usar stock mínimo</small>
              </div>
            </div>

            <div className="row">
              <div className="col-md-4 mb-3">
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="perishable"
                    checked={formData.perishable}
                    onChange={handleChange}
                  />
                  <label className="form-check-label">Perecedero</label>
                  <small className="form-text text-muted d-block">Producto con fecha de vencimiento</small>
                </div>
              </div>
              <div className="col-md-4 mb-3">
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="control_por_lote"
                    checked={formData.control_por_lote}
                    onChange={handleChange}
                  />
                  <label className="form-check-label">Control por Lote</label>
                </div>
              </div>
              <div className="col-md-4 mb-3">
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="control_por_serie"
                    checked={formData.control_por_serie}
                    onChange={handleChange}
                  />
                  <label className="form-check-label">Control por Serie</label>
                </div>
              </div>
            </div>

            {isEdit && (
              <>
                <h5 className="mt-4 mb-3">4. Derivados (Solo Lectura)</h5>
                <div className="row mb-3">
                  <div className="col-md-4">
                    <label className="form-label">Stock Actual</label>
                    <input
                      type="number"
                      className="form-control"
                      value={productData?.total_stock || 0}
                      disabled
                      readOnly
                    />
                    <small className="form-text text-muted">Calculado</small>
                  </div>
                  <div className="col-md-4">
                    <label className="form-label">Alerta Bajo Stock</label>
                    <input
                      type="text"
                      className={`form-control ${productData?.alerta_bajo_stock ? 'bg-warning' : ''}`}
                      value={productData?.alerta_bajo_stock ? 'Sí' : 'No'}
                      disabled
                      readOnly
                    />
                    <small className="form-text text-muted">Calculado</small>
                  </div>
                  <div className="col-md-4">
                    <label className="form-label">Alerta por Vencer</label>
                    <input
                      type="text"
                      className={`form-control ${productData?.alerta_por_vencer ? 'bg-danger text-white' : ''}`}
                      value={productData?.alerta_por_vencer ? 'Sí' : 'No'}
                      disabled
                      readOnly
                    />
                    <small className="form-text text-muted">Solo si es perecedero</small>
                  </div>
                </div>
              </>
            )}

            <h5 className="mt-4 mb-3">5. Relaciones y Soporte</h5>
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">URL Imagen</label>
                <input
                  type="url"
                  className={`form-control ${errors.imagen_url ? 'is-invalid' : ''}`}
                  name="imagen_url"
                  value={formData.imagen_url}
                  onChange={handleChange}
                  placeholder="https://ejemplo.com/imagen.jpg"
                  maxLength={500}
                />
                {errors.imagen_url && (
                  <div className="invalid-feedback">{errors.imagen_url}</div>
                )}
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">URL Ficha Técnica</label>
                <input
                  type="url"
                  className={`form-control ${errors.ficha_tecnica_url ? 'is-invalid' : ''}`}
                  name="ficha_tecnica_url"
                  value={formData.ficha_tecnica_url}
                  onChange={handleChange}
                  placeholder="https://ejemplo.com/ficha.pdf"
                  maxLength={500}
                />
                {errors.ficha_tecnica_url && (
                  <div className="invalid-feedback">{errors.ficha_tecnica_url}</div>
                )}
              </div>
            </div>

            <div className="d-flex justify-content-end gap-2">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate('/products')}
              >
                Cancelar
              </button>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Guardando...' : 'Guardar'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProductForm;

