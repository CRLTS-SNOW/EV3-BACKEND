// frontend/src/components/suppliers/SupplierForm.js
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Swal from 'sweetalert2';
import {
  validateRequired,
  validateMaxLength,
  validateEmail,
  validatePhone,
  validateUrl,
  validateRutNif,
  validatePositiveNumber,
  validatePositiveNumberGreaterThanZero,
  validatePercentage
} from '../../utils/validators';

const SupplierForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = !!id;
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [supplierProducts, setSupplierProducts] = useState([]);
  const [availableProducts, setAvailableProducts] = useState([]);
  const [showProductForm, setShowProductForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [productFormData, setProductFormData] = useState({
    product: '',
    costo: '',
    lead_time_dias: 7,
    min_lote: 1,
    descuento_pct: 0,
    preferente: false,
  });
  const [formData, setFormData] = useState({
    rut_nif: '',
    razon_social: '',
    nombre_fantasia: '',
    email: '',
    telefono: '',
    sitio_web: '',
    direccion: '',
    ciudad: '',
    pais: 'Chile',
    condiciones_pago: '30 días',
    moneda: 'CLP',
    contacto_principal_nombre: '',
    contacto_principal_email: '',
    contacto_principal_telefono: '',
    estado: 'ACTIVO',
    observaciones: '',
  });

  useEffect(() => {
    if (isEdit) {
      loadSupplier();
      loadSupplierProducts();
    }
    loadProducts();
  }, [id]);
  
  const loadProducts = async () => {
    try {
      const response = await api.getProducts({});
      const products = Array.isArray(response.data) 
        ? response.data 
        : (response.data.results || []);
      setAvailableProducts(products);
    } catch (error) {
      console.error('Error al cargar productos:', error);
    }
  };
  
  const loadSupplierProducts = async () => {
    if (!isEdit) return;
    try {
      const response = await api.getSupplierProducts(id);
      setSupplierProducts(response.data || []);
    } catch (error) {
      console.error('Error al cargar productos del proveedor:', error);
    }
  };

  const loadSupplier = async () => {
    try {
      const response = await api.getSupplier(id);
      const data = response.data;
      setFormData({
        rut_nif: data.rut_nif || '',
        razon_social: data.razon_social || '',
        nombre_fantasia: data.nombre_fantasia || '',
        email: data.email || '',
        telefono: data.telefono || '',
        sitio_web: data.sitio_web || '',
        direccion: data.direccion || '',
        ciudad: data.ciudad || '',
        pais: data.pais || 'Chile',
        condiciones_pago: data.condiciones_pago || '30 días',
        moneda: data.moneda || 'CLP',
        contacto_principal_nombre: data.contacto_principal_nombre || '',
        contacto_principal_email: data.contacto_principal_email || '',
        contacto_principal_telefono: data.contacto_principal_telefono || '',
        estado: data.estado || 'ACTIVO',
        observaciones: data.observaciones || '',
      });
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al cargar el proveedor',
      });
      navigate('/suppliers');
    }
  };

  // Validaciones
  const validateField = (name, value) => {
    let error = '';
    
    switch (name) {
      case 'rut_nif':
        error = validateRutNif(value);
        break;
      case 'razon_social':
        error = validateRequired(value, 'La razón social');
        if (!error) error = validateMaxLength(value, 255, 'La razón social');
        break;
      case 'nombre_fantasia':
        if (value) error = validateMaxLength(value, 255, 'El nombre fantasía');
        break;
      case 'email':
        error = validateEmail(value);
        break;
      case 'telefono':
        error = validatePhone(value);
        break;
      case 'sitio_web':
        error = validateUrl(value);
        break;
      case 'condiciones_pago':
        error = validateRequired(value, 'Las condiciones de pago');
        if (!error) error = validateMaxLength(value, 100, 'Las condiciones de pago');
        break;
      case 'direccion':
        if (value) error = validateMaxLength(value, 255, 'La dirección');
        break;
      case 'ciudad':
        if (value) error = validateMaxLength(value, 128, 'La ciudad');
        break;
      case 'pais':
        error = validateRequired(value, 'El país');
        if (!error) error = validateMaxLength(value, 64, 'El país');
        break;
      case 'contacto_principal_nombre':
        if (value) error = validateMaxLength(value, 120, 'El nombre del contacto');
        break;
      case 'contacto_principal_email':
        if (value) {
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(value)) {
            error = 'El email del contacto no es válido';
          } else {
            error = validateMaxLength(value, 254, 'El email del contacto');
          }
        }
        break;
      case 'contacto_principal_telefono':
        if (value) {
          error = validatePhone(value);
        }
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
    
    // Validar todos los campos con límites de caracteres
    newErrors.rut_nif = validateField('rut_nif', formData.rut_nif, { maxLength: 20, required: true });
    newErrors.razon_social = validateField('razon_social', formData.razon_social, { maxLength: 255, required: true });
    newErrors.nombre_fantasia = validateField('nombre_fantasia', formData.nombre_fantasia, { maxLength: 255 });
    newErrors.email = validateField('email', formData.email, { maxLength: 254, required: true });
    newErrors.telefono = validateField('telefono', formData.telefono, { maxLength: 30 });
    newErrors.sitio_web = validateField('sitio_web', formData.sitio_web, { maxLength: 255 });
    newErrors.direccion = validateField('direccion', formData.direccion, { maxLength: 255 });
    newErrors.ciudad = validateField('ciudad', formData.ciudad, { maxLength: 128 });
    newErrors.pais = validateField('pais', formData.pais, { maxLength: 64, required: true });
    newErrors.condiciones_pago = validateField('condiciones_pago', formData.condiciones_pago, { maxLength: 100, required: true });
    newErrors.contacto_principal_nombre = validateField('contacto_principal_nombre', formData.contacto_principal_nombre, { maxLength: 120 });
    newErrors.contacto_principal_email = validateField('contacto_principal_email', formData.contacto_principal_email, { maxLength: 254 });
    newErrors.contacto_principal_telefono = validateField('contacto_principal_telefono', formData.contacto_principal_telefono, { maxLength: 30 });
    newErrors.observaciones = validateField('observaciones', formData.observaciones, { maxLength: 1000 });
    
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
        await api.updateSupplier(id, formData);
        Swal.fire({
          icon: 'success',
          title: '¡Éxito!',
          text: 'Proveedor actualizado exitosamente',
        });
      } else {
        await api.createSupplier(formData);
        Swal.fire({
          icon: 'success',
          title: '¡Éxito!',
          text: 'Proveedor creado exitosamente',
        });
      }
      navigate('/suppliers');
    } catch (error) {
      console.error('Error al guardar proveedor:', error);
      let errorMessage = 'Error al guardar proveedor';
      
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
          
          errorMessage = errorList.length > 0 ? errorList.join('\n') : 'Error al guardar proveedor';
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
      <h1>{isEdit ? 'Editar Proveedor' : 'Nuevo Proveedor'}</h1>
      <div className="card">
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">RUT/NIF *</label>
                <input
                  type="text"
                  className={`form-control ${errors.rut_nif ? 'is-invalid' : ''}`}
                  name="rut_nif"
                  value={formData.rut_nif}
                  onChange={handleChange}
                  required
                  maxLength={20}
                  placeholder="76.123.456-7"
                />
                {errors.rut_nif && (
                  <div className="invalid-feedback">{errors.rut_nif}</div>
                )}
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Razón Social *</label>
                <input
                  type="text"
                  className={`form-control ${errors.razon_social ? 'is-invalid' : ''}`}
                  name="razon_social"
                  value={formData.razon_social}
                  onChange={handleChange}
                  required
                  maxLength={255}
                />
                {errors.razon_social && (
                  <div className="invalid-feedback">{errors.razon_social}</div>
                )}
                <small className="form-text text-muted">
                  {formData.razon_social.length}/255 caracteres
                </small>
              </div>
            </div>

            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Nombre Fantasía</label>
                <input
                  type="text"
                  className={`form-control ${errors.nombre_fantasia ? 'is-invalid' : ''}`}
                  name="nombre_fantasia"
                  value={formData.nombre_fantasia}
                  onChange={handleChange}
                  maxLength={255}
                />
                {errors.nombre_fantasia && (
                  <div className="invalid-feedback">{errors.nombre_fantasia}</div>
                )}
                <small className="form-text text-muted">
                  {formData.nombre_fantasia.length}/255 caracteres
                </small>
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Email *</label>
                <input
                  type="email"
                  className={`form-control ${errors.email ? 'is-invalid' : ''}`}
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  maxLength={254}
                />
                {errors.email && (
                  <div className="invalid-feedback">{errors.email}</div>
                )}
                <small className="form-text text-muted">
                  {formData.email.length}/254 caracteres
                </small>
              </div>
            </div>

            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Teléfono</label>
                <input
                  type="tel"
                  className={`form-control ${errors.telefono ? 'is-invalid' : ''}`}
                  name="telefono"
                  value={formData.telefono}
                  onChange={handleChange}
                  placeholder="+56912345678"
                  maxLength={30}
                />
                {errors.telefono && (
                  <div className="invalid-feedback">{errors.telefono}</div>
                )}
                <small className={`form-text ${errors.telefono ? 'text-danger' : 'text-muted'}`}>
                  {formData.telefono.length}/30 caracteres - Formato chileno (ej: +56912345678 o 912345678)
                </small>
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Sitio Web</label>
                <input
                  type="url"
                  className={`form-control ${errors.sitio_web ? 'is-invalid' : ''}`}
                  name="sitio_web"
                  value={formData.sitio_web}
                  onChange={handleChange}
                  placeholder="https://www.proveedor.cl"
                  maxLength={255}
                />
                {errors.sitio_web && (
                  <div className="invalid-feedback">{errors.sitio_web}</div>
                )}
                <small className={`form-text ${errors.sitio_web ? 'text-danger' : 'text-muted'}`}>
                  {formData.sitio_web.length}/255 caracteres - URL del sitio web (opcional)
                </small>
              </div>
            </div>

            <div className="row">
              <div className="col-md-12 mb-3">
                <label className="form-label">Dirección</label>
                <input
                  type="text"
                  className={`form-control ${errors.direccion ? 'is-invalid' : ''}`}
                  name="direccion"
                  value={formData.direccion}
                  onChange={handleChange}
                  maxLength={255}
                  placeholder="Dirección completa"
                />
                {errors.direccion && (
                  <div className="invalid-feedback">{errors.direccion}</div>
                )}
                <small className="form-text text-muted">
                  {formData.direccion.length}/255 caracteres
                </small>
              </div>
            </div>

            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Ciudad</label>
                <input
                  type="text"
                  className={`form-control ${errors.ciudad ? 'is-invalid' : ''}`}
                  name="ciudad"
                  value={formData.ciudad}
                  onChange={handleChange}
                  maxLength={128}
                  placeholder="Ciudad"
                />
                {errors.ciudad && (
                  <div className="invalid-feedback">{errors.ciudad}</div>
                )}
                <small className="form-text text-muted">
                  {formData.ciudad.length}/128 caracteres
                </small>
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">País *</label>
                <input
                  type="text"
                  className={`form-control ${errors.pais ? 'is-invalid' : ''}`}
                  name="pais"
                  value={formData.pais}
                  onChange={handleChange}
                  required
                  maxLength={64}
                  placeholder="País"
                />
                {errors.pais && (
                  <div className="invalid-feedback">{errors.pais}</div>
                )}
                <small className="form-text text-muted">
                  {formData.pais.length}/64 caracteres
                </small>
              </div>
            </div>

            <h5 className="mt-4 mb-3">Información Comercial</h5>
            <div className="row">
              <div className="col-md-4 mb-3">
                <label className="form-label">Condiciones de Pago *</label>
                <input
                  type="text"
                  className={`form-control ${errors.condiciones_pago ? 'is-invalid' : ''}`}
                  name="condiciones_pago"
                  value={formData.condiciones_pago}
                  onChange={handleChange}
                  required
                  maxLength={100}
                  placeholder="Ej: 30 días, contado"
                />
                {errors.condiciones_pago && (
                  <div className="invalid-feedback">{errors.condiciones_pago}</div>
                )}
                <small className="form-text text-muted">
                  {formData.condiciones_pago.length}/100 caracteres
                </small>
              </div>
              <div className="col-md-4 mb-3">
                <label className="form-label">Moneda *</label>
                <select
                  className="form-select"
                  name="moneda"
                  value={formData.moneda}
                  onChange={handleChange}
                  required
                >
                  <option value="CLP">CLP</option>
                  <option value="USD">USD</option>
                </select>
              </div>
              <div className="col-md-4 mb-3">
                <label className="form-label">Estado *</label>
                <select
                  className="form-select"
                  name="estado"
                  value={formData.estado}
                  onChange={handleChange}
                  required
                >
                  <option value="ACTIVO">Activo</option>
                  <option value="BLOQUEADO">Bloqueado</option>
                </select>
              </div>
            </div>

            <h5 className="mt-4 mb-3">Contacto Principal</h5>
            <div className="row">
              <div className="col-md-4 mb-3">
                <label className="form-label">Nombre del Contacto</label>
                <input
                  type="text"
                  className={`form-control ${errors.contacto_principal_nombre ? 'is-invalid' : ''}`}
                  name="contacto_principal_nombre"
                  value={formData.contacto_principal_nombre}
                  onChange={handleChange}
                  maxLength={120}
                  placeholder="Nombre del contacto principal"
                />
                {errors.contacto_principal_nombre && (
                  <div className="invalid-feedback">{errors.contacto_principal_nombre}</div>
                )}
                <small className="form-text text-muted">
                  {formData.contacto_principal_nombre.length}/120 caracteres
                </small>
              </div>
              <div className="col-md-4 mb-3">
                <label className="form-label">Email del Contacto</label>
                <input
                  type="email"
                  className={`form-control ${errors.contacto_principal_email ? 'is-invalid' : ''}`}
                  name="contacto_principal_email"
                  value={formData.contacto_principal_email}
                  onChange={handleChange}
                  maxLength={254}
                  placeholder="email@contacto.cl"
                />
                {errors.contacto_principal_email && (
                  <div className="invalid-feedback">{errors.contacto_principal_email}</div>
                )}
                <small className="form-text text-muted">
                  {formData.contacto_principal_email.length}/254 caracteres
                </small>
              </div>
              <div className="col-md-4 mb-3">
                <label className="form-label">Teléfono del Contacto</label>
                <input
                  type="tel"
                  className={`form-control ${errors.contacto_principal_telefono ? 'is-invalid' : ''}`}
                  name="contacto_principal_telefono"
                  value={formData.contacto_principal_telefono}
                  onChange={handleChange}
                  placeholder="+56912345678"
                  maxLength={30}
                />
                {errors.contacto_principal_telefono && (
                  <div className="invalid-feedback">{errors.contacto_principal_telefono}</div>
                )}
                <small className={`form-text ${errors.contacto_principal_telefono ? 'text-danger' : 'text-muted'}`}>
                  {formData.contacto_principal_telefono.length}/30 caracteres - Formato chileno (ej: +56912345678 o 912345678)
                </small>
              </div>
            </div>

            <div className="row">
              <div className="col-12 mb-3">
                <label className="form-label">Observaciones</label>
                <textarea
                  className={`form-control ${errors.observaciones ? 'is-invalid' : ''}`}
                  name="observaciones"
                  value={formData.observaciones}
                  onChange={handleChange}
                  rows={3}
                  maxLength={1000}
                  placeholder="Observaciones adicionales"
                />
                {errors.observaciones && (
                  <div className="invalid-feedback">{errors.observaciones}</div>
                )}
                <small className="form-text text-muted">
                  {formData.observaciones.length}/1000 caracteres
                </small>
              </div>
            </div>

            {isEdit && (
              <>
                <h5 className="mt-4 mb-3">Productos Asociados</h5>
                <div className="mb-3">
                  <button
                    type="button"
                    className="btn btn-sm btn-primary"
                    onClick={() => {
                      setEditingProduct(null);
                      setProductFormData({
                        product: '',
                        costo: '',
                        lead_time_dias: 7,
                        min_lote: 1,
                        descuento_pct: 0,
                        preferente: false,
                      });
                      setShowProductForm(true);
                    }}
                  >
                    <i className="bi bi-plus-circle"></i> Agregar Producto
                  </button>
                </div>

                {showProductForm && (
                  <div className="card mb-3">
                    <div className="card-body">
                      <h6>{editingProduct ? 'Editar Producto' : 'Nuevo Producto'}</h6>
                      <div className="row">
                        <div className="col-md-4 mb-2">
                          <label className="form-label">Producto *</label>
                          <select
                            className="form-select"
                            value={productFormData.product}
                            onChange={(e) => setProductFormData({...productFormData, product: e.target.value})}
                            disabled={!!editingProduct}
                          >
                            <option value="">Seleccionar producto</option>
                            {availableProducts
                              .filter(p => !supplierProducts.some(sp => sp.product === p.id && sp.id !== editingProduct?.id))
                              .map(p => (
                                <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>
                              ))}
                          </select>
                        </div>
                        <div className="col-md-2 mb-2">
                          <label className="form-label">Costo *</label>
                          <input
                            type="number"
                            className="form-control"
                            value={productFormData.costo}
                            onChange={(e) => setProductFormData({...productFormData, costo: e.target.value})}
                            step="0.000001"
                            min="0"
                            required
                          />
                        </div>
                        <div className="col-md-2 mb-2">
                          <label className="form-label">Lead Time (días) *</label>
                          <input
                            type="number"
                            className="form-control"
                            value={productFormData.lead_time_dias}
                            onChange={(e) => setProductFormData({...productFormData, lead_time_dias: parseInt(e.target.value) || 7})}
                            min="0"
                            required
                          />
                        </div>
                        <div className="col-md-2 mb-2">
                          <label className="form-label">Mín. Lote</label>
                          <input
                            type="number"
                            className="form-control"
                            value={productFormData.min_lote}
                            onChange={(e) => setProductFormData({...productFormData, min_lote: e.target.value})}
                            step="0.000001"
                            min="0"
                          />
                        </div>
                        <div className="col-md-2 mb-2">
                          <label className="form-label">Descuento %</label>
                          <input
                            type="number"
                            className="form-control"
                            value={productFormData.descuento_pct}
                            onChange={(e) => setProductFormData({...productFormData, descuento_pct: e.target.value})}
                            step="0.01"
                            min="0"
                            max="100"
                          />
                        </div>
                      </div>
                      <div className="row">
                        <div className="col-md-12 mb-2">
                          <div className="form-check">
                            <input
                              className="form-check-input"
                              type="checkbox"
                              checked={productFormData.preferente}
                              onChange={(e) => setProductFormData({...productFormData, preferente: e.target.checked})}
                            />
                            <label className="form-check-label">Proveedor Preferente</label>
                          </div>
                        </div>
                      </div>
                      <div className="d-flex gap-2">
                        <button
                          type="button"
                          className="btn btn-sm btn-primary"
                          onClick={async () => {
                            if (!productFormData.product || !productFormData.costo) {
                              Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: 'Producto y costo son requeridos',
                              });
                              return;
                            }
                            
                            // Validar preferente: si se marca como preferente, verificar que no haya otro
                            if (productFormData.preferente) {
                              const existingPreferente = supplierProducts.find(
                                sp => sp.product === parseInt(productFormData.product) && 
                                      sp.preferente && 
                                      (!editingProduct || sp.id !== editingProduct.id)
                              );
                              
                              if (existingPreferente) {
                                const result = await Swal.fire({
                                  icon: 'warning',
                                  title: 'Proveedor Preferente Existente',
                                  text: `Ya existe un proveedor preferente para este producto. ¿Deseas reemplazarlo?`,
                                  showCancelButton: true,
                                  confirmButtonText: 'Sí, reemplazar',
                                  cancelButtonText: 'Cancelar',
                                });
                                
                                if (!result.isConfirmed) {
                                  return;
                                }
                              }
                            }
                            
                            try {
                              // Preparar datos para enviar
                              const dataToSend = {
                                product: editingProduct ? editingProduct.product : parseInt(productFormData.product),
                                costo: parseFloat(productFormData.costo),
                                lead_time_dias: parseInt(productFormData.lead_time_dias) || 7,
                                min_lote: productFormData.min_lote ? parseFloat(productFormData.min_lote) : null,
                                descuento_pct: productFormData.descuento_pct ? parseFloat(productFormData.descuento_pct) : 0,
                                preferente: productFormData.preferente || false,
                              };
                              
                              if (editingProduct) {
                                await api.updateSupplierProduct(id, dataToSend);
                                Swal.fire({
                                  icon: 'success',
                                  title: '¡Éxito!',
                                  text: 'Producto actualizado exitosamente',
                                  timer: 2000,
                                  showConfirmButton: false,
                                });
                              } else {
                                await api.addSupplierProduct(id, dataToSend);
                                Swal.fire({
                                  icon: 'success',
                                  title: '¡Éxito!',
                                  text: 'Producto agregado exitosamente',
                                  timer: 2000,
                                  showConfirmButton: false,
                                });
                              }
                              setShowProductForm(false);
                              setEditingProduct(null);
                              loadSupplierProducts();
                            } catch (error) {
                              let errorMessage = 'Error al guardar producto';
                              if (error.response?.data) {
                                if (typeof error.response.data === 'string') {
                                  errorMessage = error.response.data;
                                } else if (error.response.data.error) {
                                  errorMessage = error.response.data.error;
                                } else if (error.response.data.preferente) {
                                  errorMessage = Array.isArray(error.response.data.preferente) 
                                    ? error.response.data.preferente.join(', ')
                                    : error.response.data.preferente;
                                } else if (typeof error.response.data === 'object') {
                                  const errors = Object.values(error.response.data).flat();
                                  errorMessage = errors.join(', ');
                                }
                              }
                              Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: errorMessage,
                              });
                            }
                          }}
                        >
                          {editingProduct ? 'Actualizar' : 'Agregar'}
                        </button>
                        <button
                          type="button"
                          className="btn btn-sm btn-secondary"
                          onClick={() => {
                            setShowProductForm(false);
                            setEditingProduct(null);
                          }}
                        >
                          Cancelar
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th>Producto</th>
                        <th>SKU</th>
                        <th>Costo</th>
                        <th>Lead Time (días)</th>
                        <th>Mín. Lote</th>
                        <th>Descuento %</th>
                        <th>Preferente</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {supplierProducts.length === 0 ? (
                        <tr>
                          <td colSpan="8" className="text-center">No hay productos asociados</td>
                        </tr>
                      ) : (
                        supplierProducts.map((sp) => (
                          <tr key={sp.id}>
                            <td>{sp.product_name}</td>
                            <td>{sp.product_sku}</td>
                            <td>${parseFloat(sp.costo).toLocaleString('es-CL', {minimumFractionDigits: 2})}</td>
                            <td>{sp.lead_time_dias}</td>
                            <td>{sp.min_lote ? parseFloat(sp.min_lote).toLocaleString('es-CL') : '-'}</td>
                            <td>{sp.descuento_pct ? `${parseFloat(sp.descuento_pct).toFixed(2)}%` : '-'}</td>
                            <td>
                              {sp.preferente ? (
                                <span className="badge bg-success">Sí</span>
                              ) : (
                                <span className="badge bg-secondary">No</span>
                              )}
                            </td>
                            <td>
                              <button
                                type="button"
                                className="btn btn-sm btn-outline-primary me-1"
                                onClick={() => {
                                  setEditingProduct(sp);
                                  setProductFormData({
                                    product: sp.product,
                                    costo: sp.costo,
                                    lead_time_dias: sp.lead_time_dias,
                                    min_lote: sp.min_lote || 1,
                                    descuento_pct: sp.descuento_pct || 0,
                                    preferente: sp.preferente,
                                  });
                                  setShowProductForm(true);
                                }}
                              >
                                Editar
                              </button>
                              <button
                                type="button"
                                className="btn btn-sm btn-outline-danger"
                                onClick={async () => {
                                  const result = await Swal.fire({
                                    title: '¿Estás seguro?',
                                    text: 'Esta acción no se puede deshacer',
                                    icon: 'warning',
                                    showCancelButton: true,
                                    confirmButtonColor: '#d33',
                                    cancelButtonColor: '#3085d6',
                                    confirmButtonText: 'Sí, eliminar',
                                    cancelButtonText: 'Cancelar',
                                  });
                                  if (result.isConfirmed) {
                                    try {
                                      await api.removeSupplierProduct(id, sp.product);
                                      Swal.fire({
                                        icon: 'success',
                                        title: '¡Éxito!',
                                        text: 'Producto eliminado exitosamente',
                                        timer: 2000,
                                        showConfirmButton: false,
                                      });
                                      loadSupplierProducts();
                                    } catch (error) {
                                      Swal.fire({
                                        icon: 'error',
                                        title: 'Error',
                                        text: error.response?.data?.error || 'Error al eliminar producto',
                                      });
                                    }
                                  }
                                }}
                              >
                                Eliminar
                              </button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </>
            )}

            <div className="d-flex justify-content-end gap-2">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate('/suppliers')}
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

export default SupplierForm;

