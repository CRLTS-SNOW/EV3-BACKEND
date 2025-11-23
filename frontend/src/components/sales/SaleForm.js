// frontend/src/components/sales/SaleForm.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Swal from 'sweetalert2';

const SaleForm = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [allProducts, setAllProducts] = useState([]);
  const [searching, setSearching] = useState(false);
  const [loadingProducts, setLoadingProducts] = useState(true);
  const [cart, setCart] = useState([]);
  const [clients, setClients] = useState([]);
  const [selectedClient, setSelectedClient] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadClients();
    loadAllProducts();
  }, []);

  const loadClients = async () => {
    try {
      const response = await api.getClients();
      setClients(response.data.results || response.data);
    } catch (error) {
      console.error('Error al cargar clientes:', error);
    }
  };

  const loadAllProducts = async (page = 1) => {
    try {
      setLoadingProducts(true);
      const response = await api.getAllProductsForSale(page, 50);
      if (response.data.status === 'success') {
        setAllProducts(response.data.products || []);
        setTotalPages(response.data.total_pages || 1);
        setCurrentPage(response.data.page || 1);
      }
    } catch (error) {
      console.error('Error al cargar productos:', error);
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al cargar productos',
      });
    } finally {
      setLoadingProducts(false);
    }
  };

  const searchProducts = async () => {
    if (searchQuery.length < 2) {
      setProducts([]);
      setSearching(false);
      return;
    }
    setSearching(true);
    try {
      const response = await api.searchProductsForSale(searchQuery);
      // Manejar diferentes formatos de respuesta
      if (response.data.status === 'success' && response.data.products) {
        setProducts(response.data.products);
      } else if (Array.isArray(response.data)) {
        setProducts(response.data);
      } else if (response.data.results) {
        setProducts(response.data.results);
      } else {
        setProducts([]);
      }
    } catch (error) {
      console.error('Error al buscar productos:', error);
      console.error('Error response:', error.response);
      setProducts([]);
      // No mostrar error al usuario, solo limpiar resultados
    } finally {
      setSearching(false);
    }
  };

  useEffect(() => {
    if (searchQuery.length >= 2) {
      const timeoutId = setTimeout(() => {
        searchProducts();
      }, 300);
      return () => clearTimeout(timeoutId);
    } else {
      setProducts([]);
      setSearching(false);
    }
  }, [searchQuery]);

  // Filtrar productos cuando cambia searchQuery
  useEffect(() => {
    if (searchQuery.length === 0) {
      setProducts([]);
    }
  }, [searchQuery]);

  const addToCart = (product) => {
    const existingItem = cart.find((item) => item.id === product.id);
    if (existingItem) {
      setCart(
        cart.map((item) =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        )
      );
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
    setSearchQuery('');
    setProducts([]);
  };

  const updateQuantity = (productId, quantity) => {
    if (quantity <= 0) {
      setCart(cart.filter((item) => item.id !== productId));
    } else {
      setCart(
        cart.map((item) =>
          item.id === productId ? { ...item, quantity } : item
        )
      );
    }
  };

  const getTotal = () => {
    return cart.reduce((total, item) => {
      return total + parseFloat(item.price || 0) * item.quantity;
    }, 0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (cart.length === 0) {
      Swal.fire({
        icon: 'warning',
        title: 'Carrito vacío',
        text: 'Agrega productos al carrito antes de procesar la venta',
      });
      return;
    }

    setLoading(true);
    try {
      const saleData = {
        client_id: selectedClient || null,
        cart: cart.map((item) => ({
          id: item.id,
          quantity: item.quantity,
        })),
      };
      await api.createSale(saleData);
      Swal.fire({
        icon: 'success',
        title: '¡Éxito!',
        text: 'Venta procesada exitosamente',
      });
      navigate('/sales');
    } catch (error) {
      console.error('Error al procesar venta:', error);
      console.error('Error response:', error.response);
      
      let errorMessage = 'Error al procesar la venta';
      
      if (error.response) {
        if (error.response.data?.errors) {
          errorMessage = Array.isArray(error.response.data.errors) 
            ? error.response.data.errors.join('<br>')
            : error.response.data.errors;
        } else if (error.response.data?.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.data?.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.status === 500) {
          errorMessage = 'Error interno del servidor. Por favor, contacte al administrador.';
        } else if (error.response.status === 403) {
          errorMessage = 'No tienes permisos para realizar ventas.';
        }
      }
      
      Swal.fire({
        icon: 'error',
        title: 'Error',
        html: errorMessage,
      });
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
    }).format(value || 0);
  };

  return (
    <div>
      <h1>Nueva Venta</h1>
      <div className="row">
        <div className="col-md-8">
          <div className="card mb-3">
            <div className="card-body">
              <h5 className="card-title">Buscar Productos</h5>
              <div className="position-relative">
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
              <div className="mt-3">
                {searchQuery.length >= 2 ? (
                  // Mostrar resultados de búsqueda
                  searching ? (
                    <div className="text-center py-3">
                      <div className="spinner-border spinner-border-sm text-primary" role="status">
                        <span className="visually-hidden">Buscando...</span>
                      </div>
                      <small className="d-block mt-2 text-muted">Buscando productos...</small>
                    </div>
                  ) : products.length > 0 ? (
                    <div className="table-responsive" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                      <table className="table table-hover">
                        <thead>
                          <tr>
                            <th>SKU</th>
                            <th>Nombre</th>
                            <th>Stock</th>
                            <th>Precio</th>
                            <th>Acción</th>
                          </tr>
                        </thead>
                        <tbody>
                          {products.map((product) => (
                            <tr 
                              key={product.id}
                              className={product.stock === 0 ? 'table-secondary' : ''}
                              style={{ cursor: product.stock > 0 ? 'pointer' : 'not-allowed' }}
                              onClick={() => product.stock > 0 && addToCart(product)}
                            >
                              <td>{product.sku}</td>
                              <td>
                                <strong>{product.name}</strong>
                              </td>
                              <td>
                                <span className={`badge ${product.stock > 0 ? 'bg-success' : 'bg-danger'}`}>
                                  {product.stock}
                                </span>
                              </td>
                              <td>{formatCurrency(product.price)}</td>
                              <td>
                                {product.stock > 0 ? (
                                  <button
                                    className="btn btn-sm btn-primary"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      addToCart(product);
                                    }}
                                  >
                                    Agregar
                                  </button>
                                ) : (
                                  <span className="badge bg-danger">Sin Stock</span>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="alert alert-info mb-0">
                      <small>No se encontraron productos con "{searchQuery}"</small>
                    </div>
                  )
                ) : (
                  // Mostrar lista completa de productos
                  loadingProducts ? (
                    <div className="text-center py-3">
                      <div className="spinner-border spinner-border-sm text-primary" role="status">
                        <span className="visually-hidden">Cargando...</span>
                      </div>
                      <small className="d-block mt-2 text-muted">Cargando productos...</small>
                    </div>
                  ) : allProducts.length > 0 ? (
                    <>
                      <div className="table-responsive" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                        <table className="table table-hover">
                          <thead>
                            <tr>
                              <th>SKU</th>
                              <th>Nombre</th>
                              <th>Stock</th>
                              <th>Precio</th>
                              <th>Acción</th>
                            </tr>
                          </thead>
                          <tbody>
                            {allProducts.map((product) => (
                              <tr 
                                key={product.id}
                                className={product.stock === 0 ? 'table-secondary' : ''}
                                style={{ cursor: product.stock > 0 ? 'pointer' : 'not-allowed' }}
                                onClick={() => product.stock > 0 && addToCart(product)}
                              >
                                <td>{product.sku}</td>
                                <td>
                                  <strong>{product.name}</strong>
                                </td>
                                <td>
                                  <span className={`badge ${product.stock > 0 ? 'bg-success' : 'bg-danger'}`}>
                                    {product.stock}
                                  </span>
                                </td>
                                <td>{formatCurrency(product.price)}</td>
                                <td>
                                  {product.stock > 0 ? (
                                    <button
                                      className="btn btn-sm btn-primary"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        addToCart(product);
                                      }}
                                    >
                                      Agregar
                                    </button>
                                  ) : (
                                    <span className="badge bg-danger">Sin Stock</span>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      {totalPages > 1 && (
                        <nav className="mt-3">
                          <ul className="pagination justify-content-center">
                            <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                              <button
                                className="page-link"
                                onClick={() => currentPage > 1 && loadAllProducts(currentPage - 1)}
                                disabled={currentPage === 1}
                              >
                                Anterior
                              </button>
                            </li>
                            <li className="page-item disabled">
                              <span className="page-link">
                                Página {currentPage} de {totalPages}
                              </span>
                            </li>
                            <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                              <button
                                className="page-link"
                                onClick={() => currentPage < totalPages && loadAllProducts(currentPage + 1)}
                                disabled={currentPage === totalPages}
                              >
                                Siguiente
                              </button>
                            </li>
                          </ul>
                        </nav>
                      )}
                    </>
                  ) : (
                    <div className="alert alert-info mb-0">
                      <small>No hay productos disponibles</small>
                    </div>
                  )
                )}
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Carrito</h5>
              {cart.length === 0 ? (
                <p className="text-muted">El carrito está vacío</p>
              ) : (
                <table className="table">
                  <thead>
                    <tr>
                      <th>Producto</th>
                      <th>Cantidad</th>
                      <th>Precio</th>
                      <th>Subtotal</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cart.map((item) => (
                      <tr key={item.id}>
                        <td>{item.name}</td>
                        <td>
                          <input
                            type="number"
                            className="form-control form-control-sm"
                            style={{ width: '80px' }}
                            value={item.quantity}
                            onChange={(e) =>
                              updateQuantity(item.id, parseInt(e.target.value))
                            }
                            min="1"
                          />
                        </td>
                        <td>{formatCurrency(item.price)}</td>
                        <td>
                          {formatCurrency(parseFloat(item.price || 0) * item.quantity)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr>
                      <th colSpan="3">Total</th>
                      <th>{formatCurrency(getTotal())}</th>
                    </tr>
                  </tfoot>
                </table>
              )}
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Información de Venta</h5>
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label">Cliente (Opcional)</label>
                  <select
                    className="form-select"
                    value={selectedClient}
                    onChange={(e) => setSelectedClient(e.target.value)}
                  >
                    <option value="">Cliente General</option>
                    {clients.map((client) => (
                      <option key={client.id} value={client.id}>
                        {client.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="mb-3">
                  <strong>Total: {formatCurrency(getTotal())}</strong>
                </div>
                <div className="d-grid gap-2">
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading || cart.length === 0}
                  >
                    {loading ? 'Procesando...' : 'Procesar Venta'}
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => navigate('/sales')}
                  >
                    Cancelar
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SaleForm;

