// frontend/src/components/movements/MovementForm.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Swal from 'sweetalert2';
import {
  validateRequired,
  validateMaxLength,
  validatePositiveNumberGreaterThanZero
} from '../../utils/validators';

const MovementForm = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [zones, setZones] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [products, setProducts] = useState([]);
  const [allProducts, setAllProducts] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [loadingProducts, setLoadingProducts] = useState(true);
  const [originZones, setOriginZones] = useState([]);
  const [destinationZones, setDestinationZones] = useState([]);
  const [loadingOriginZones, setLoadingOriginZones] = useState(false);
  const [loadingDestinationZones, setLoadingDestinationZones] = useState(false);
  const [formData, setFormData] = useState({
    fecha: '',
    tipo: 'ingreso',
    product: '',
    supplier: '',
    warehouse: '',
    origin_warehouse: '',
    destination_warehouse: '',
    origin_zone: '',
    destination_zone: '',
    cantidad: '1', // Valor por defecto: 1
    lote: '',
    serie: '',
    fecha_vencimiento: '',
    doc_referencia: '',
    motivo: '',
    observaciones: '',
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    loadZones();
    loadWarehouses();
    loadSuppliers();
    loadAllProducts();
    // Establecer fecha actual por defecto
    const now = new Date();
    const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16);
    setFormData(prev => ({ ...prev, fecha: localDateTime }));
  }, []);

  // Establecer valores por defecto cuando se cargan las bodegas y zonas
  useEffect(() => {
    if (warehouses.length > 0 && !formData.warehouse && !formData.origin_warehouse && !formData.destination_warehouse) {
      // Buscar "Bodega Central" como primera opción, si no existe usar la primera
      const defaultWarehouse = warehouses.find(w => w.name.toLowerCase().includes('central')) || warehouses[0];
      if (defaultWarehouse) {
        setFormData(prev => ({ ...prev, warehouse: defaultWarehouse.id.toString() }));
      }
    }
  }, [warehouses]);

  useEffect(() => {
    if (zones.length > 0 && !formData.destination_zone && formData.tipo !== 'transferencia') {
      // Buscar zona de "Ventas" o "Despacho" como primera opción, si no existe usar la primera
      const defaultZone = zones.find(z => 
        z.name.toLowerCase().includes('venta') || 
        z.name.toLowerCase().includes('despacho') ||
        z.name.toLowerCase().includes('principal')
      ) || zones[0];
      if (defaultZone) {
        setFormData(prev => ({ ...prev, destination_zone: defaultZone.id.toString() }));
      }
    }
  }, [zones, formData.tipo]);

  // Establecer zona origen por defecto cuando se selecciona bodega origen
  useEffect(() => {
    if (formData.origin_warehouse && originZones.length > 0 && !formData.origin_zone) {
      const defaultOriginZone = originZones.find(z => 
        z.name.toLowerCase().includes('principal') ||
        z.name.toLowerCase().includes('almacén')
      ) || originZones[0];
      if (defaultOriginZone) {
        setFormData(prev => ({ ...prev, origin_zone: defaultOriginZone.id.toString() }));
      }
    }
  }, [formData.origin_warehouse, originZones]);

  // Establecer zona destino por defecto cuando se selecciona bodega destino
  useEffect(() => {
    if (formData.destination_warehouse && destinationZones.length > 0 && !formData.destination_zone) {
      const defaultDestinationZone = destinationZones.find(z => 
        z.name.toLowerCase().includes('principal') ||
        z.name.toLowerCase().includes('almacén') ||
        z.name.toLowerCase().includes('recepcion')
      ) || destinationZones[0];
      if (defaultDestinationZone) {
        setFormData(prev => ({ ...prev, destination_zone: defaultDestinationZone.id.toString() }));
      }
    }
  }, [formData.destination_warehouse, destinationZones]);

  // Establecer zona por defecto cuando se selecciona bodega (para ingreso/salida)
  useEffect(() => {
    if (formData.warehouse && zones.length > 0) {
      // Filtrar zonas de la bodega seleccionada
      // Las zonas pueden tener warehouse como ID o como objeto
      const warehouseZones = zones.filter(z => {
        const zoneWarehouseId = typeof z.warehouse === 'object' ? z.warehouse?.id : z.warehouse;
        return zoneWarehouseId === parseInt(formData.warehouse);
      });
      if (warehouseZones.length > 0) {
        if (formData.tipo === 'ingreso' && !formData.destination_zone) {
          const defaultZone = warehouseZones.find(z => 
            z.name.toLowerCase().includes('recepcion') ||
            z.name.toLowerCase().includes('principal') ||
            z.name.toLowerCase().includes('almacén')
          ) || warehouseZones[0];
          if (defaultZone) {
            setFormData(prev => ({ ...prev, destination_zone: defaultZone.id.toString() }));
          }
        } else if (formData.tipo === 'salida' && !formData.origin_zone) {
          const defaultZone = warehouseZones.find(z => 
            z.name.toLowerCase().includes('despacho') ||
            z.name.toLowerCase().includes('venta') ||
            z.name.toLowerCase().includes('principal')
          ) || warehouseZones[0];
          if (defaultZone) {
            setFormData(prev => ({ ...prev, origin_zone: defaultZone.id.toString() }));
          }
        }
      }
    }
  }, [formData.warehouse, zones, formData.tipo]);

  useEffect(() => {
    if (searchQuery.length >= 2) {
      const timeoutId = setTimeout(() => {
        searchProducts();
      }, 300);
      return () => clearTimeout(timeoutId);
    } else {
      setProducts([]);
    }
  }, [searchQuery]);

  // Filtrar productos cuando cambia searchQuery
  useEffect(() => {
    if (searchQuery.length === 0) {
      setProducts([]);
    }
  }, [searchQuery]);

  const loadZones = async () => {
    try {
      const response = await api.getAllZones();
      // La respuesta puede venir como {zones: [...]} o {results: [...]} o directamente como array
      const zonesList = response.data.zones || response.data.results || response.data || [];
      setZones(Array.isArray(zonesList) ? zonesList : []);
    } catch (error) {
      console.error('Error al cargar zonas:', error);
    }
  };

  const loadWarehouses = async () => {
    try {
      const response = await api.getWarehouses();
      const warehousesList = response.data.results || response.data || [];
      setWarehouses(warehousesList);
      
      // Establecer bodega por defecto si no hay ninguna seleccionada
      if (warehousesList.length > 0 && !formData.warehouse && !formData.origin_warehouse && !formData.destination_warehouse) {
        // Buscar "Bodega Central" como primera opción, si no existe usar la primera
        const defaultWarehouse = warehousesList.find(w => 
          w.name.toLowerCase().includes('central')
        ) || warehousesList[0];
        if (defaultWarehouse) {
          setFormData(prev => ({ ...prev, warehouse: defaultWarehouse.id.toString() }));
        }
      }
    } catch (error) {
      console.error('Error al cargar bodegas:', error);
    }
  };

  const loadSuppliers = async () => {
    try {
      const response = await api.getSuppliers();
      const suppliersList = response.data.results || response.data || [];
      setSuppliers(suppliersList.filter(s => s.estado === 'ACTIVO'));
    } catch (error) {
      console.error('Error al cargar proveedores:', error);
    }
  };

  const loadAllProducts = async () => {
    try {
      setLoadingProducts(true);
      const response = await api.getProducts({ page_size: 100 });
      const productsList = Array.isArray(response.data) 
        ? response.data 
        : (response.data.results || []);
      setAllProducts(productsList.filter(p => p.is_active));
    } catch (error) {
      console.error('Error al cargar productos:', error);
    } finally {
      setLoadingProducts(false);
    }
  };

  const searchProducts = async () => {
    if (searchQuery.length < 2) {
      setProducts([]);
      return;
    }
    setSearching(true);
    try {
      const response = await api.getProducts({ q: searchQuery });
      const productsList = Array.isArray(response.data) 
        ? response.data 
        : (response.data.results || []);
      setProducts(productsList.filter(p => p.is_active));
    } catch (error) {
      console.error('Error al buscar productos:', error);
      setProducts([]);
    } finally {
      setSearching(false);
    }
  };

  const selectProduct = (product) => {
    setFormData(prev => ({ ...prev, product: product.id }));
    setSearchQuery('');
    setProducts([]);
  };

  const validateField = (name, value) => {
    let error = '';
    
    switch (name) {
      case 'fecha':
        error = validateRequired(value, 'La fecha');
        break;
      case 'product':
        error = validateRequired(value, 'El producto');
        break;
      case 'cantidad':
        error = validateRequired(value, 'La cantidad');
        if (!error) {
          const numValue = parseFloat(value);
          if (isNaN(numValue) || numValue <= 0) {
            error = 'La cantidad debe ser un número mayor que cero';
          } else if (!Number.isInteger(numValue)) {
            error = 'La cantidad debe ser un número entero';
          }
        }
        break;
      case 'destination_zone':
        if (formData.tipo !== 'ajuste') {
          error = validateRequired(value, 'La zona destino');
        }
        break;
      case 'origin_warehouse':
        if (formData.tipo === 'transferencia') {
          error = validateRequired(value, 'La bodega origen');
        }
        break;
      case 'destination_warehouse':
        if (formData.tipo === 'transferencia') {
          error = validateRequired(value, 'La bodega destino');
        }
        break;
      case 'origin_zone':
        if (formData.tipo === 'transferencia' || formData.tipo === 'salida') {
          error = validateRequired(value, 'La zona origen');
        }
        break;
      case 'warehouse':
        if (formData.tipo === 'ingreso' || formData.tipo === 'salida') {
          error = validateRequired(value, 'La bodega');
        }
        break;
      case 'supplier':
        // Opcional pero recomendado para ingresos
        break;
      case 'lote':
        if (value && value.length > 100) error = 'El lote no puede tener más de 100 caracteres';
        break;
      case 'serie':
        if (value && value.length > 100) error = 'La serie no puede tener más de 100 caracteres';
        break;
      case 'doc_referencia':
        if (value && value.length > 100) error = 'El documento de referencia no puede tener más de 100 caracteres';
        break;
      case 'motivo':
        if (formData.tipo === 'ajuste' || formData.tipo === 'devolucion') {
          error = validateRequired(value, 'El motivo');
          if (!error && value.length > 1000) error = 'El motivo no puede tener más de 1000 caracteres';
        } else if (value && value.length > 1000) {
          error = 'El motivo no puede tener más de 1000 caracteres';
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

  const loadZonesByWarehouse = async (warehouseId, setZonesCallback, setLoadingCallback) => {
    if (!warehouseId) {
      setZonesCallback([]);
      return;
    }
    setLoadingCallback(true);
    try {
      const response = await api.getZonesByWarehouse(warehouseId);
      const zonesList = response.data.results || response.data || [];
      setZonesCallback(zonesList.filter(z => z.is_active !== false));
    } catch (error) {
      console.error('Error al cargar zonas:', error);
      setZonesCallback([]);
    } finally {
      setLoadingCallback(false);
    }
  };

  const handleChange = async (e) => {
    const { name, value } = e.target;
    
    // Validar campo en tiempo real
    const error = validateField(name, value);
    setErrors({
      ...errors,
      [name]: error,
    });
    
    const newFormData = {
      ...formData,
      [name]: value,
    };
    
    // Si cambia la bodega origen, cargar sus zonas
    if (name === 'origin_warehouse') {
      newFormData.origin_zone = ''; // Limpiar zona origen
      await loadZonesByWarehouse(value, setOriginZones, setLoadingOriginZones);
    }
    
    // Si cambia la bodega destino, cargar sus zonas
    if (name === 'destination_warehouse') {
      newFormData.destination_zone = ''; // Limpiar zona destino
      await loadZonesByWarehouse(value, setDestinationZones, setLoadingDestinationZones);
    }
    
    // Si cambia el tipo de movimiento, limpiar campos relacionados
    if (name === 'tipo') {
      if (value !== 'transferencia') {
        newFormData.origin_warehouse = '';
        newFormData.destination_warehouse = '';
        newFormData.origin_zone = '';
        newFormData.destination_zone = '';
        setOriginZones([]);
        setDestinationZones([]);
      }
      if (value !== 'ingreso' && value !== 'salida') {
        newFormData.warehouse = '';
      }
    }
    
    setFormData(newFormData);
  };

  const validateForm = () => {
    const newErrors = {};
    
    newErrors.fecha = validateField('fecha', formData.fecha);
    newErrors.product = validateField('product', formData.product);
    newErrors.cantidad = validateField('cantidad', formData.cantidad);
    
    // Validaciones según tipo de movimiento
    if (formData.tipo === 'transferencia') {
      newErrors.origin_warehouse = validateField('origin_warehouse', formData.origin_warehouse);
      newErrors.destination_warehouse = validateField('destination_warehouse', formData.destination_warehouse);
      newErrors.origin_zone = validateField('origin_zone', formData.origin_zone);
      newErrors.destination_zone = validateField('destination_zone', formData.destination_zone);
      if (formData.origin_zone === formData.destination_zone) {
        newErrors.destination_zone = 'La zona destino debe ser diferente a la zona origen';
      }
      if (formData.origin_warehouse && formData.destination_warehouse && formData.origin_warehouse === formData.destination_warehouse) {
        if (formData.origin_zone === formData.destination_zone) {
          newErrors.destination_zone = 'La zona destino debe ser diferente a la zona origen';
        }
      }
    } else if (formData.tipo === 'ingreso' || formData.tipo === 'salida') {
      newErrors.warehouse = validateField('warehouse', formData.warehouse);
      if (formData.tipo === 'ingreso') {
        newErrors.destination_zone = validateField('destination_zone', formData.destination_zone);
      } else {
        newErrors.origin_zone = validateField('origin_zone', formData.origin_zone);
      }
    } else if (formData.tipo === 'ajuste') {
      newErrors.destination_zone = validateField('destination_zone', formData.destination_zone);
    } else if (formData.tipo === 'devolucion') {
      newErrors.destination_zone = validateField('destination_zone', formData.destination_zone);
    }
    
    // Validar motivo para ajustes y devoluciones (requerido)
    if (formData.tipo === 'ajuste' || formData.tipo === 'devolucion') {
      newErrors.motivo = validateField('motivo', formData.motivo);
    }
    
    // Validar campos opcionales
    newErrors.lote = validateField('lote', formData.lote);
    newErrors.serie = validateField('serie', formData.serie);
    newErrors.doc_referencia = validateField('doc_referencia', formData.doc_referencia);
    newErrors.observaciones = validateField('observaciones', formData.observaciones);
    
    setErrors(newErrors);
    
    return Object.values(newErrors).every(error => error === '');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      // Mostrar campos faltantes de forma clara
      const missingFields = [];
      if (errors.fecha) missingFields.push('Fecha');
      if (errors.product) missingFields.push('Producto');
      if (errors.cantidad) missingFields.push('Cantidad');
      
      // Campos según tipo de movimiento
      if (formData.tipo === 'transferencia') {
        if (errors.origin_warehouse) missingFields.push('Bodega Origen');
        if (errors.destination_warehouse) missingFields.push('Bodega Destino');
        if (errors.origin_zone) missingFields.push('Zona Origen');
        if (errors.destination_zone) missingFields.push('Zona Destino');
      } else if (formData.tipo === 'ingreso') {
        if (errors.warehouse) missingFields.push('Bodega');
        if (errors.destination_zone) missingFields.push('Zona Destino');
      } else if (formData.tipo === 'salida') {
        if (errors.warehouse) missingFields.push('Bodega');
        if (errors.origin_zone) missingFields.push('Zona Origen');
      } else if (formData.tipo === 'ajuste' || formData.tipo === 'devolucion') {
        if (errors.destination_zone) missingFields.push('Zona Destino');
        if (errors.motivo) missingFields.push('Motivo');
      }
      
      const errorMessage = missingFields.length > 0 
        ? `Por favor, complete los siguientes campos requeridos:\n\n${missingFields.map(f => `• ${f}`).join('\n')}`
        : 'Por favor, corrige los errores en el formulario antes de guardar';
      
      Swal.fire({
        icon: 'error',
        title: 'Campos requeridos faltantes',
        html: errorMessage.split('\n').map(line => `<div style="text-align: left; margin: 5px 0;">${line}</div>`).join(''),
        width: '500px',
      });
      return;
    }
    
    setLoading(true);

    try {
      // Preparar datos para enviar
      const dataToSend = {
        fecha: formData.fecha || new Date().toISOString(),
        tipo: formData.tipo,
        product: parseInt(formData.product),
        cantidad: parseInt(formData.cantidad) || 0,
        destination_zone: formData.destination_zone ? parseInt(formData.destination_zone) : null,
        origin_zone: formData.origin_zone ? parseInt(formData.origin_zone) : null,
        supplier: formData.supplier ? parseInt(formData.supplier) : null,
        warehouse: formData.warehouse ? parseInt(formData.warehouse) : null,
        // Para transferencias, también podemos enviar las bodegas si están disponibles
        ...(formData.tipo === 'transferencia' && formData.origin_warehouse && {
          origin_warehouse: parseInt(formData.origin_warehouse)
        }),
        ...(formData.tipo === 'transferencia' && formData.destination_warehouse && {
          destination_warehouse: parseInt(formData.destination_warehouse)
        }),
        lote: formData.lote || null,
        serie: formData.serie || null,
        fecha_vencimiento: formData.fecha_vencimiento || null,
        doc_referencia: formData.doc_referencia || null,
        motivo: formData.motivo || null,
        observaciones: formData.observaciones || null,
      };
      
      // Debug: mostrar qué se está enviando
      console.log('Datos a enviar:', dataToSend);
      
      await api.createMovement(dataToSend);
      Swal.fire({
        icon: 'success',
        title: '¡Éxito!',
        text: 'Movimiento creado exitosamente',
      });
      navigate('/movements');
    } catch (error) {
      console.error('Error al crear movimiento:', error);
      let errorMessage = 'Error al crear movimiento';
      if (error.response?.data) {
        if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (typeof error.response.data === 'object') {
          // Mostrar errores de validación de forma más clara
          const fieldErrors = [];
          Object.keys(error.response.data).forEach(field => {
            const fieldMessages = Array.isArray(error.response.data[field]) 
              ? error.response.data[field] 
              : [error.response.data[field]];
            fieldMessages.forEach(msg => {
              // Traducir nombres de campos a español
              const fieldNames = {
                'fecha': 'Fecha',
                'tipo': 'Tipo de Movimiento',
                'product': 'Producto',
                'cantidad': 'Cantidad',
                'origin_warehouse': 'Bodega Origen',
                'destination_warehouse': 'Bodega Destino',
                'origin_zone': 'Zona Origen',
                'destination_zone': 'Zona Destino',
                'warehouse': 'Bodega',
                'supplier': 'Proveedor',
                'motivo': 'Motivo',
              };
              const fieldName = fieldNames[field] || field;
              fieldErrors.push(`${fieldName}: ${msg}`);
            });
          });
          errorMessage = fieldErrors.length > 0 ? fieldErrors.join('\n') : 'Error de validación';
        }
      }
      Swal.fire({
        icon: 'error',
        title: 'Error de validación',
        html: errorMessage.split('\n').map(line => `<div>${line}</div>`).join(''),
        width: '600px',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Nuevo Movimiento</h1>
      <div className="card">
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            {/* Datos del Movimiento */}
            <h5 className="mb-3">Datos del Movimiento</h5>
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Fecha *</label>
                <input
                  type="datetime-local"
                  className={`form-control ${errors.fecha ? 'is-invalid' : ''}`}
                  name="fecha"
                  value={formData.fecha}
                  onChange={handleChange}
                  required
                />
                {errors.fecha && (
                  <div className="invalid-feedback">{errors.fecha}</div>
                )}
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Tipo de Movimiento *</label>
                <select
                  className="form-select"
                  name="tipo"
                  value={formData.tipo}
                  onChange={handleChange}
                  required
                >
                  <option value="ingreso">Ingreso</option>
                  <option value="salida">Salida</option>
                  <option value="ajuste">Ajuste</option>
                  <option value="devolucion">Devolución</option>
                  <option value="transferencia">Transferencia</option>
                </select>
              </div>
            </div>

            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Producto *</label>
                {formData.product && (
                  <div className="alert alert-info py-2 mb-2">
                    <small>
                      <strong>Producto seleccionado:</strong>{' '}
                      {allProducts.find(p => p.id === parseInt(formData.product))?.sku || ''} -{' '}
                      {allProducts.find(p => p.id === parseInt(formData.product))?.name || ''}
                      <button
                        type="button"
                        className="btn btn-sm btn-link p-0 ms-2"
                        onClick={() => setFormData(prev => ({ ...prev, product: '' }))}
                      >
                        Cambiar
                      </button>
                    </small>
                  </div>
                )}
                {!formData.product && (
                  <>
                    <div className="position-relative mb-2">
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Escribe para buscar productos por nombre o SKU..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        autoComplete="off"
                      />
                      {searching && (
                        <div className="position-absolute top-50 end-0 translate-middle-y pe-3">
                          <div className="spinner-border spinner-border-sm text-primary" role="status">
                            <span className="visually-hidden">Buscando...</span>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {/* Lista de productos */}
                    <div className="mt-2">
                      {searchQuery.length >= 2 ? (
                        // Mostrar resultados de búsqueda
                        searching ? (
                          <div className="text-center py-2">
                            <div className="spinner-border spinner-border-sm text-primary" role="status">
                              <span className="visually-hidden">Buscando...</span>
                            </div>
                            <small className="d-block mt-2 text-muted">Buscando productos...</small>
                          </div>
                        ) : products.length > 0 ? (
                          <div className="table-responsive border rounded" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                            <table className="table table-hover mb-0">
                              <thead className="table-light sticky-top">
                                <tr>
                                  <th>SKU</th>
                                  <th>Nombre</th>
                                  <th>Categoría</th>
                                  <th>Acción</th>
                                </tr>
                              </thead>
                              <tbody>
                                {products.map((product) => (
                                  <tr 
                                    key={product.id}
                                    style={{ cursor: 'pointer' }}
                                    onClick={() => selectProduct(product)}
                                  >
                                    <td>{product.sku}</td>
                                    <td><strong>{product.name}</strong></td>
                                    <td>{product.categoria || '-'}</td>
                                    <td>
                                      <button
                                        type="button"
                                        className="btn btn-sm btn-primary"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          selectProduct(product);
                                        }}
                                      >
                                        Seleccionar
                                      </button>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        ) : (
                          <div className="alert alert-info mb-0 py-2">
                            <small>No se encontraron productos con "{searchQuery}"</small>
                          </div>
                        )
                      ) : (
                        // Mostrar lista completa de productos
                        loadingProducts ? (
                          <div className="text-center py-2">
                            <div className="spinner-border spinner-border-sm text-primary" role="status">
                              <span className="visually-hidden">Cargando...</span>
                            </div>
                            <small className="d-block mt-2 text-muted">Cargando productos...</small>
                          </div>
                        ) : allProducts.length > 0 ? (
                          <div className="table-responsive border rounded" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                            <table className="table table-hover mb-0">
                              <thead className="table-light sticky-top">
                                <tr>
                                  <th>SKU</th>
                                  <th>Nombre</th>
                                  <th>Categoría</th>
                                  <th>Acción</th>
                                </tr>
                              </thead>
                              <tbody>
                                {allProducts.map((product) => (
                                  <tr 
                                    key={product.id}
                                    style={{ cursor: 'pointer' }}
                                    onClick={() => selectProduct(product)}
                                  >
                                    <td>{product.sku}</td>
                                    <td><strong>{product.name}</strong></td>
                                    <td>{product.categoria || '-'}</td>
                                    <td>
                                      <button
                                        type="button"
                                        className="btn btn-sm btn-primary"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          selectProduct(product);
                                        }}
                                      >
                                        Seleccionar
                                      </button>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        ) : (
                          <div className="alert alert-warning mb-0 py-2">
                            <small>No hay productos disponibles</small>
                          </div>
                        )
                      )}
                    </div>
                  </>
                )}
                {errors.product && (
                  <div className="invalid-feedback d-block">{errors.product}</div>
                )}
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Cantidad *</label>
                <input
                  type="number"
                  step="1"
                  min="1"
                  className={`form-control ${errors.cantidad ? 'is-invalid' : ''}`}
                  name="cantidad"
                  value={formData.cantidad}
                  onChange={handleChange}
                  placeholder="Ingrese la cantidad"
                  required
                />
                {errors.cantidad && (
                  <div className="invalid-feedback">{errors.cantidad}</div>
                )}
                <small className="form-text text-muted">Ingrese la cantidad de productos (números enteros)</small>
              </div>
            </div>

            <div className="row">
              {(formData.tipo === 'ingreso' || formData.tipo === 'salida') && (
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
              )}
              {formData.tipo === 'ingreso' && (
                <div className="col-md-6 mb-3">
                  <label className="form-label">Proveedor</label>
                  <select
                    className="form-select"
                    name="supplier"
                    value={formData.supplier}
                    onChange={handleChange}
                  >
                    <option value="">Seleccionar...</option>
                    {suppliers.map((supplier) => (
                      <option key={supplier.id} value={supplier.id}>
                        {supplier.razon_social}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {/* Sección de Transferencia - Más intuitiva */}
            {formData.tipo === 'transferencia' && (
              <>
                <hr className="my-4" />
                <div className="alert alert-info mb-3">
                  <strong><i className="bi bi-info-circle"></i> Campos requeridos para Transferencia:</strong>
                  <ul className="mb-0 mt-2">
                    <li>Bodega Origen y Zona Origen (de dónde sale el producto)</li>
                    <li>Bodega Destino y Zona Destino (a dónde va el producto)</li>
                    <li>Las zonas deben ser diferentes</li>
                  </ul>
                </div>
                <h5 className="mb-3">
                  <i className="bi bi-arrow-left-right"></i> Transferencia entre Bodegas
                </h5>
                <div className="row">
                  <div className="col-md-6">
                    <div className="card border-primary">
                      <div className="card-header bg-primary text-white">
                        <strong><i className="bi bi-box-arrow-up"></i> Origen</strong>
                      </div>
                      <div className="card-body">
                        <div className="mb-3">
                          <label className="form-label">Bodega Origen *</label>
                          <select
                            className={`form-select ${errors.origin_warehouse ? 'is-invalid' : ''}`}
                            name="origin_warehouse"
                            value={formData.origin_warehouse}
                            onChange={handleChange}
                            required
                          >
                            <option value="">Seleccionar bodega...</option>
                            {warehouses.map((warehouse) => (
                              <option key={warehouse.id} value={warehouse.id}>
                                {warehouse.name}
                              </option>
                            ))}
                          </select>
                          {errors.origin_warehouse && (
                            <div className="invalid-feedback">{errors.origin_warehouse}</div>
                          )}
                        </div>
                        <div className="mb-0">
                          <label className="form-label">Zona Origen *</label>
                          {loadingOriginZones ? (
                            <div className="text-center py-2">
                              <div className="spinner-border spinner-border-sm text-primary" role="status">
                                <span className="visually-hidden">Cargando...</span>
                              </div>
                            </div>
                          ) : (
                            <select
                              className={`form-select ${errors.origin_zone ? 'is-invalid' : ''}`}
                              name="origin_zone"
                              value={formData.origin_zone}
                              onChange={handleChange}
                              required
                              disabled={!formData.origin_warehouse}
                            >
                              <option value="">
                                {formData.origin_warehouse ? 'Seleccionar zona...' : 'Primero seleccione la bodega'}
                              </option>
                              {originZones.map((zone) => (
                                <option key={zone.id} value={zone.id}>
                                  {zone.name}
                                </option>
                              ))}
                            </select>
                          )}
                          {errors.origin_zone && (
                            <div className="invalid-feedback">{errors.origin_zone}</div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="card border-success">
                      <div className="card-header bg-success text-white">
                        <strong><i className="bi bi-box-arrow-in-down"></i> Destino</strong>
                      </div>
                      <div className="card-body">
                        <div className="mb-3">
                          <label className="form-label">Bodega Destino *</label>
                          <select
                            className={`form-select ${errors.destination_warehouse ? 'is-invalid' : ''}`}
                            name="destination_warehouse"
                            value={formData.destination_warehouse}
                            onChange={handleChange}
                            required
                          >
                            <option value="">Seleccionar bodega...</option>
                            {warehouses.map((warehouse) => (
                              <option key={warehouse.id} value={warehouse.id}>
                                {warehouse.name}
                              </option>
                            ))}
                          </select>
                          {errors.destination_warehouse && (
                            <div className="invalid-feedback">{errors.destination_warehouse}</div>
                          )}
                        </div>
                        <div className="mb-0">
                          <label className="form-label">Zona Destino *</label>
                          {loadingDestinationZones ? (
                            <div className="text-center py-2">
                              <div className="spinner-border spinner-border-sm text-success" role="status">
                                <span className="visually-hidden">Cargando...</span>
                              </div>
                            </div>
                          ) : (
                            <select
                              className={`form-select ${errors.destination_zone ? 'is-invalid' : ''}`}
                              name="destination_zone"
                              value={formData.destination_zone}
                              onChange={handleChange}
                              required
                              disabled={!formData.destination_warehouse}
                            >
                              <option value="">
                                {formData.destination_warehouse ? 'Seleccionar zona...' : 'Primero seleccione la bodega'}
                              </option>
                              {destinationZones.map((zone) => (
                                <option key={zone.id} value={zone.id}>
                                  {zone.name}
                                </option>
                              ))}
                            </select>
                          )}
                          {errors.destination_zone && (
                            <div className="invalid-feedback">{errors.destination_zone}</div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                {formData.origin_warehouse && formData.destination_warehouse && formData.origin_warehouse === formData.destination_warehouse && (
                  <div className="alert alert-warning mt-3">
                    <i className="bi bi-exclamation-triangle"></i> Está transfiriendo dentro de la misma bodega. 
                    Asegúrese de seleccionar zonas diferentes.
                  </div>
                )}
              </>
            )}
            
            {/* Zonas para otros tipos de movimiento */}
            <div className="row">
              {(formData.tipo === 'ingreso' || formData.tipo === 'ajuste' || formData.tipo === 'devolucion') && (
                <div className="col-md-6 mb-3">
                  <label className="form-label">Zona Destino *</label>
                  <select
                    className={`form-select ${errors.destination_zone ? 'is-invalid' : ''}`}
                    name="destination_zone"
                    value={formData.destination_zone}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Seleccionar...</option>
                    {zones.map((zone) => (
                      <option key={zone.id} value={zone.id}>
                        {zone.name}
                      </option>
                    ))}
                  </select>
                  {errors.destination_zone && (
                    <div className="invalid-feedback">{errors.destination_zone}</div>
                  )}
                </div>
              )}
              {formData.tipo === 'salida' && (
                <div className="col-md-6 mb-3">
                  <label className="form-label">Zona Origen *</label>
                  <select
                    className={`form-select ${errors.origin_zone ? 'is-invalid' : ''}`}
                    name="origin_zone"
                    value={formData.origin_zone}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Seleccionar...</option>
                    {zones.map((zone) => (
                      <option key={zone.id} value={zone.id}>
                        {zone.name}
                      </option>
                    ))}
                  </select>
                  {errors.origin_zone && (
                    <div className="invalid-feedback">{errors.origin_zone}</div>
                  )}
                </div>
              )}
            </div>

            {/* Control Avanzado */}
            <hr className="my-4" />
            <h5 className="mb-3">Control Avanzado</h5>
            <div className="row">
              <div className="col-md-4 mb-3">
                <label className="form-label">Número de Lote</label>
                <input
                  type="text"
                  className={`form-control ${errors.lote ? 'is-invalid' : ''}`}
                  name="lote"
                  value={formData.lote}
                  onChange={handleChange}
                  maxLength={100}
                  placeholder="LOTE-12345"
                />
                {errors.lote && (
                  <div className="invalid-feedback">{errors.lote}</div>
                )}
                <small className="form-text text-muted">{formData.lote.length}/100 caracteres</small>
              </div>
              <div className="col-md-4 mb-3">
                <label className="form-label">Número de Serie</label>
                <input
                  type="text"
                  className={`form-control ${errors.serie ? 'is-invalid' : ''}`}
                  name="serie"
                  value={formData.serie}
                  onChange={handleChange}
                  maxLength={100}
                  placeholder="SER-12345"
                />
                {errors.serie && (
                  <div className="invalid-feedback">{errors.serie}</div>
                )}
                <small className="form-text text-muted">{formData.serie.length}/100 caracteres</small>
              </div>
              <div className="col-md-4 mb-3">
                <label className="form-label">Fecha de Vencimiento</label>
                <input
                  type="date"
                  className="form-control"
                  name="fecha_vencimiento"
                  value={formData.fecha_vencimiento}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Referencias/Observaciones */}
            <hr className="my-4" />
            <h5 className="mb-3">Referencias y Observaciones</h5>
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Documento de Referencia</label>
                <input
                  type="text"
                  className={`form-control ${errors.doc_referencia ? 'is-invalid' : ''}`}
                  name="doc_referencia"
                  value={formData.doc_referencia}
                  onChange={handleChange}
                  maxLength={100}
                  placeholder="OC-123, FAC-456, GUIA-789"
                />
                {errors.doc_referencia && (
                  <div className="invalid-feedback">{errors.doc_referencia}</div>
                )}
                <small className="form-text text-muted">{formData.doc_referencia.length}/100 caracteres</small>
              </div>
            </div>
            {(formData.tipo === 'ajuste' || formData.tipo === 'devolucion') && (
              <div className="mb-3">
                <label className="form-label">Motivo *</label>
                <textarea
                  className={`form-control ${errors.motivo ? 'is-invalid' : ''}`}
                  name="motivo"
                  rows="3"
                  value={formData.motivo}
                  onChange={handleChange}
                  maxLength={1000}
                  placeholder="Motivo del ajuste o devolución"
                />
                {errors.motivo && (
                  <div className="invalid-feedback">{errors.motivo}</div>
                )}
                <small className="form-text text-muted">{formData.motivo.length}/1000 caracteres</small>
              </div>
            )}
            <div className="mb-3">
              <label className="form-label">Observaciones</label>
              <textarea
                className={`form-control ${errors.observaciones ? 'is-invalid' : ''}`}
                name="observaciones"
                rows="3"
                value={formData.observaciones}
                onChange={handleChange}
                maxLength={1000}
                placeholder="Observaciones adicionales"
              />
              {errors.observaciones && (
                <div className="invalid-feedback">{errors.observaciones}</div>
              )}
              <small className="form-text text-muted">{formData.observaciones.length}/1000 caracteres</small>
            </div>

            <div className="d-flex justify-content-end gap-2">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate('/movements')}
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

export default MovementForm;


