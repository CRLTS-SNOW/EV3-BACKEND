// frontend/src/components/products/ProductList.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import Swal from 'sweetalert2';
import * as XLSX from 'xlsx';

const ProductList = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const { isAdmin } = useAuth();

  // Debounce para la búsqueda en tiempo real
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
      // Resetear a la primera página cuando cambia la búsqueda
      if (page !== 1) {
        setPage(1);
      }
    }, 500); // Esperar 500ms después de que el usuario deje de escribir

    return () => clearTimeout(timer);
  }, [searchQuery]);

  useEffect(() => {
    loadProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedSearchQuery, sortBy, page]);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const params = {};
      
      // Solo agregar parámetros si tienen valor
      if (debouncedSearchQuery && debouncedSearchQuery.trim()) {
        params.q = debouncedSearchQuery.trim();
      }
      if (sortBy) {
        params.sort = sortBy;
      }
      if (page && page > 1) {
        params.page = page;
      }
      
      const response = await api.getProducts(params);
      
      // Manejar diferentes formatos de respuesta
      if (Array.isArray(response.data)) {
        setProducts(response.data);
        setTotalPages(1);
      } else if (response.data.results) {
        setProducts(response.data.results);
        if (response.data.count !== undefined) {
          setTotalPages(Math.ceil(response.data.count / 20));
        } else {
          setTotalPages(1);
        }
      } else {
        setProducts([]);
        setTotalPages(1);
      }
    } catch (error) {
      console.error('Error al cargar productos:', error);
      console.error('Error response:', error.response);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.error || 
                          error.message || 
                          'Error al cargar productos';
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: errorMessage,
      });
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    // La búsqueda ya se ejecuta automáticamente con el debounce
    setPage(1);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
    }).format(value || 0);
  };

  const exportToExcel = async () => {
    try {
      // Cargar todos los productos sin paginación para exportar
      const params = {};
      
      if (debouncedSearchQuery && debouncedSearchQuery.trim()) {
        params.q = debouncedSearchQuery.trim();
      }
      if (sortBy) {
        params.sort = sortBy;
      }
      
      // Cargar todos los productos (sin límite de página)
      const response = await api.getProducts(params);
      const allProducts = Array.isArray(response.data) 
        ? response.data 
        : (response.data.results || []);
      
      if (allProducts.length === 0) {
        Swal.fire({
          icon: 'warning',
          title: 'Sin datos',
          text: 'No hay productos para exportar',
        });
        return;
      }
      
      // Preparar datos para Excel con formato correcto
      const excelData = allProducts.map((product) => ({
        'SKU': String(product.sku || ''),
        'Nombre': String(product.name || ''),
        'Categoría': String(product.categoria || ''),
        'Stock': Number(product.total_stock || 0),
        'Precio Venta': Number(product.precio_venta || 0),
      }));
      
      // Crear workbook y worksheet
      const ws = XLSX.utils.json_to_sheet(excelData, {
        header: ['SKU', 'Nombre', 'Categoría', 'Stock', 'Precio Venta'],
        skipHeader: false,
      });
      
      // Ajustar ancho de columnas
      ws['!cols'] = [
        { wch: 15 }, // SKU
        { wch: 30 }, // Nombre
        { wch: 15 }, // Categoría
        { wch: 10 }, // Stock
        { wch: 15 }, // Precio Venta
      ];
      
      // Crear workbook con opciones explícitas
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Inventario');
      
      // Generar nombre de archivo con fecha (formato más compatible)
      const fecha = new Date();
      const fechaStr = fecha.getFullYear() + '-' + 
                      String(fecha.getMonth() + 1).padStart(2, '0') + '-' + 
                      String(fecha.getDate()).padStart(2, '0');
      const fileName = `Inventario_${fechaStr}.xlsx`;
      
      // Escribir archivo con tipo explícito (sin opciones adicionales que puedan causar problemas)
      XLSX.writeFile(wb, fileName);
      
      Swal.fire({
        icon: 'success',
        title: '¡Éxito!',
        text: `Se exportaron ${allProducts.length} productos a Excel`,
        timer: 2000,
        showConfirmButton: false,
      });
    } catch (error) {
      console.error('Error al exportar a Excel:', error);
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al exportar a Excel: ' + (error.message || 'Error desconocido'),
      });
    }
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Inventario</h1>
        <div className="d-flex gap-2">
          <button 
            onClick={exportToExcel} 
            className="btn btn-success"
            disabled={loading}
          >
            <i className="bi bi-file-earmark-excel"></i> Exportar a Excel
          </button>
          {isAdmin() && (
            <Link to="/products/new" className="btn btn-primary">
              <i className="bi bi-plus-circle"></i> Nuevo Producto
            </Link>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="mb-3">
            <div className="row g-3">
              <div className="col-md-10">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Buscar por nombre, SKU o proveedor... (búsqueda en tiempo real)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                {searchQuery && (
                  <small className="text-muted">Buscando: "{searchQuery}"</small>
                )}
              </div>
              <div className="col-md-2">
                <select
                  className="form-select"
                  value={sortBy}
                  onChange={(e) => {
                    setSortBy(e.target.value);
                    setPage(1);
                  }}
                >
                  <option value="name">Nombre A-Z</option>
                  <option value="-name">Nombre Z-A</option>
                  <option value="stock">Stock Menor</option>
                  <option value="-stock">Stock Mayor</option>
                  <option value="price">Precio Menor</option>
                  <option value="-price">Precio Mayor</option>
                </select>
              </div>
            </div>
          </div>

          {loading && (
            <div className="d-flex justify-content-center mb-3">
              <div className="spinner-border spinner-border-sm" role="status">
                <span className="visually-hidden">Cargando...</span>
              </div>
            </div>
          )}
          
          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Nombre</th>
                  <th>Categoría</th>
                  <th>Stock</th>
                  <th>Precio Venta</th>
                  {isAdmin() && <th>Acciones</th>}
                </tr>
              </thead>
              <tbody>
                {!loading && products.length === 0 ? (
                  <tr>
                    <td colSpan={isAdmin() ? 6 : 5} className="text-center">
                      No se encontraron productos
                    </td>
                  </tr>
                ) : (
                  products.map((product) => (
                    <tr key={product.id}>
                      <td>{product.sku}</td>
                      <td>
                        <Link to={`/products/${product.id}/edit`}>{product.name}</Link>
                      </td>
                      <td>{product.categoria}</td>
                      <td>{product.total_stock || 0}</td>
                      <td>{formatCurrency(product.precio_venta)}</td>
                      {isAdmin() && (
                        <td>
                          <Link
                            to={`/products/${product.id}/edit`}
                            className="btn btn-sm btn-outline-primary"
                          >
                            Editar
                          </Link>
                        </td>
                      )}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (() => {
            // Calcular qué páginas mostrar (máximo 7 páginas visibles)
            const getPageNumbers = () => {
              const delta = 2; // Páginas a mostrar a cada lado de la actual
              const range = [];
              const rangeWithDots = [];

              // Calcular el rango de páginas a mostrar (excluyendo primera y última)
              const start = Math.max(2, page - delta);
              const end = Math.min(totalPages - 1, page + delta);
              
              for (let i = start; i <= end; i++) {
                range.push(i);
              }

              // Agregar primera página
              rangeWithDots.push(1);

              // Agregar puntos suspensivos si hay gap entre página 1 y el rango
              if (start > 2) {
                rangeWithDots.push('...');
              }

              // Agregar páginas del rango (evitar duplicar página 1)
              range.forEach(i => {
                if (i !== 1) {
                  rangeWithDots.push(i);
                }
              });

              // Agregar puntos suspensivos si hay gap entre el rango y última página
              if (end < totalPages - 1) {
                rangeWithDots.push('...');
              }

              // Agregar última página (evitar duplicar si ya está en el rango)
              if (totalPages !== 1 && !range.includes(totalPages)) {
                rangeWithDots.push(totalPages);
              }

              return rangeWithDots;
            };

            const pageNumbers = getPageNumbers();

            return (
              <nav>
                <ul className="pagination justify-content-center">
                  <li className={`page-item ${page === 1 ? 'disabled' : ''}`}>
                    <button
                      className="page-link"
                      onClick={() => setPage(page - 1)}
                      disabled={page === 1}
                    >
                      Anterior
                    </button>
                  </li>
                  {pageNumbers.map((pageNum, index) => {
                    if (pageNum === '...') {
                      return (
                        <li key={`ellipsis-${index}`} className="page-item disabled">
                          <span className="page-link">...</span>
                        </li>
                      );
                    }
                    return (
                      <li
                        key={pageNum}
                        className={`page-item ${page === pageNum ? 'active' : ''}`}
                      >
                        <button
                          className="page-link"
                          onClick={() => setPage(pageNum)}
                        >
                          {pageNum}
                        </button>
                      </li>
                    );
                  })}
                  <li className={`page-item ${page === totalPages ? 'disabled' : ''}`}>
                    <button
                      className="page-link"
                      onClick={() => setPage(page + 1)}
                      disabled={page === totalPages}
                    >
                      Siguiente
                    </button>
                  </li>
                </ul>
              </nav>
            );
          })()}
        </div>
      </div>
    </div>
  );
};

export default ProductList;

