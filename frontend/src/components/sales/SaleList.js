// frontend/src/components/sales/SaleList.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import Swal from 'sweetalert2';
import * as XLSX from 'xlsx';

const SaleList = () => {
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    client_id: '',
    user_id: '',
    date_from: '',
    date_to: '',
    total_min: '',
    total_max: '',
  });
  const [orderBy, setOrderBy] = useState('-sale_date'); // Por defecto: más reciente primero
  const [clients, setClients] = useState([]);
  const [users, setUsers] = useState([]);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadClients();
    loadUsers();
    loadSales();
  }, []);

  const loadClients = async () => {
    try {
      const response = await api.getClients();
      setClients(response.data.results || response.data || []);
    } catch (error) {
      console.error('Error al cargar clientes:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await api.getUsers();
      setUsers(response.data.results || response.data || []);
    } catch (error) {
      console.error('Error al cargar usuarios:', error);
    }
  };

  const loadSales = async () => {
    try {
      setLoading(true);
      const params = {};
      
      if (searchQuery) {
        params.q = searchQuery;
      }
      
      // Agregar filtros
      if (filters.client_id) params.client_id = filters.client_id;
      if (filters.user_id) params.user_id = filters.user_id;
      if (filters.date_from) params.date_from = filters.date_from;
      if (filters.date_to) params.date_to = filters.date_to;
      if (filters.total_min) params.total_min = filters.total_min;
      if (filters.total_max) params.total_max = filters.total_max;
      
      // Agregar ordenamiento
      if (orderBy) params.order_by = orderBy;
      
      const response = await api.getSales(params);
      // Manejar diferentes formatos de respuesta
      if (Array.isArray(response.data)) {
        setSales(response.data);
      } else if (response.data.results) {
        setSales(response.data.results);
      } else {
        setSales([]);
      }
    } catch (error) {
      console.error('Error al cargar ventas:', error);
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al cargar ventas: ' + (error.response?.data?.detail || error.message || 'Error desconocido'),
      });
      setSales([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadSales();
  };

  const handleFilterChange = (field, value) => {
    setFilters({ ...filters, [field]: value });
  };

  const handleApplyFilters = () => {
    loadSales();
  };

  const handleClearFilters = () => {
    setFilters({
      client_id: '',
      user_id: '',
      date_from: '',
      date_to: '',
      total_min: '',
      total_max: '',
    });
    setOrderBy('-sale_date'); // Resetear a orden por defecto
    setSearchQuery('');
    // Cargar sin filtros después de limpiar
    setTimeout(() => loadSales(), 100);
  };

  const handleOrderChange = (e) => {
    setOrderBy(e.target.value);
    // Recargar automáticamente cuando cambia el ordenamiento
    setTimeout(() => loadSales(), 100);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
    }).format(value || 0);
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-CL');
  };

  const exportToExcel = async () => {
    try {
      setLoading(true);
      const params = {};
      
      if (searchQuery) params.q = searchQuery;
      if (filters.client_id) params.client_id = filters.client_id;
      if (filters.user_id) params.user_id = filters.user_id;
      if (filters.date_from) params.date_from = filters.date_from;
      if (filters.date_to) params.date_to = filters.date_to;
      if (filters.total_min) params.total_min = filters.total_min;
      if (filters.total_max) params.total_max = filters.total_max;
      if (orderBy) params.order_by = orderBy;
      
      const response = await api.getSales(params);
      const allSales = Array.isArray(response.data) 
        ? response.data 
        : (response.data.results || []);
      
      if (allSales.length === 0) {
        Swal.fire({
          icon: 'warning',
          title: 'Sin datos',
          text: 'No hay ventas para exportar',
        });
        return;
      }
      
      const excelData = allSales.map((sale) => ({
        'ID': Number(sale.id || 0),
        'Cliente': String(sale.client_name || 'Cliente General'),
        'Usuario': String(sale.user_name || ''),
        'Fecha': formatDate(sale.sale_date),
        'Total': Number(sale.total_amount || 0),
      }));
      
      const ws = XLSX.utils.json_to_sheet(excelData, {
        header: ['ID', 'Cliente', 'Usuario', 'Fecha', 'Total'],
        skipHeader: false,
      });
      
      ws['!cols'] = [
        { wch: 8 },  // ID
        { wch: 25 }, // Cliente
        { wch: 20 }, // Usuario
        { wch: 12 }, // Fecha
        { wch: 15 }, // Total
      ];
      
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Ventas');
      
      const fecha = new Date();
      const fechaStr = fecha.getFullYear() + '-' + 
                      String(fecha.getMonth() + 1).padStart(2, '0') + '-' + 
                      String(fecha.getDate()).padStart(2, '0');
      const fileName = `Ventas_${fechaStr}.xlsx`;
      
      XLSX.writeFile(wb, fileName);
      
      Swal.fire({
        icon: 'success',
        title: '¡Éxito!',
        text: `Se exportaron ${allSales.length} ventas a Excel`,
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
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Ventas</h1>
        <div className="d-flex gap-2">
          <button
            onClick={exportToExcel}
            className="btn btn-success"
            disabled={loading}
          >
            <i className="bi bi-file-earmark-excel"></i> Exportar a Excel
          </button>
          <Link to="/sales/new" className="btn btn-primary">
            <i className="bi bi-plus-circle"></i> Nueva Venta
          </Link>
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <form onSubmit={handleSearch} className="mb-3">
            <div className="row g-3 align-items-end">
              <div className="col-md-6">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Buscar por ID, cliente o usuario..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <div className="col-md-3">
                <label className="form-label">Ordenar por</label>
                <select
                  className="form-select"
                  value={orderBy}
                  onChange={handleOrderChange}
                >
                  <option value="-sale_date">Más reciente primero</option>
                  <option value="sale_date">Más antiguo primero</option>
                  <option value="-total_amount">Mayor precio primero</option>
                  <option value="total_amount">Menor precio primero</option>
                  <option value="-id">ID más alto primero</option>
                  <option value="id">ID más bajo primero</option>
                </select>
              </div>
              <div className="col-md-1">
                <button type="submit" className="btn btn-primary w-100">
                  Buscar
                </button>
              </div>
              <div className="col-md-2">
                <button
                  type="button"
                  className="btn btn-outline-secondary w-100"
                  onClick={() => setShowFilters(!showFilters)}
                >
                  <i className="bi bi-funnel"></i> {showFilters ? 'Ocultar' : 'Filtros'}
                </button>
              </div>
            </div>
          </form>

          {showFilters && (
            <div className="card bg-light mb-3">
              <div className="card-body">
                <h6 className="card-title mb-3">Filtros Avanzados</h6>
                <div className="row g-3">
                  <div className="col-md-3">
                    <label className="form-label">Cliente</label>
                    <select
                      className="form-select"
                      value={filters.client_id}
                      onChange={(e) => handleFilterChange('client_id', e.target.value)}
                    >
                      <option value="">Todos los clientes</option>
                      {clients.map((client) => (
                        <option key={client.id} value={client.id}>
                          {client.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="col-md-3">
                    <label className="form-label">Usuario</label>
                    <select
                      className="form-select"
                      value={filters.user_id}
                      onChange={(e) => handleFilterChange('user_id', e.target.value)}
                    >
                      <option value="">Todos los usuarios</option>
                      {users.map((user) => (
                        <option key={user.id} value={user.id}>
                          {user.username} {user.first_name ? `(${user.first_name} ${user.last_name})` : ''}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="col-md-2">
                    <label className="form-label">Fecha Desde</label>
                    <input
                      type="date"
                      className="form-control"
                      value={filters.date_from}
                      onChange={(e) => handleFilterChange('date_from', e.target.value)}
                    />
                  </div>
                  <div className="col-md-2">
                    <label className="form-label">Fecha Hasta</label>
                    <input
                      type="date"
                      className="form-control"
                      value={filters.date_to}
                      onChange={(e) => handleFilterChange('date_to', e.target.value)}
                    />
                  </div>
                  <div className="col-md-2">
                    <label className="form-label">Total Mínimo</label>
                    <input
                      type="number"
                      className="form-control"
                      placeholder="0"
                      value={filters.total_min}
                      onChange={(e) => handleFilterChange('total_min', e.target.value)}
                      min="0"
                    />
                  </div>
                  <div className="col-md-2">
                    <label className="form-label">Total Máximo</label>
                    <input
                      type="number"
                      className="form-control"
                      placeholder="0"
                      value={filters.total_max}
                      onChange={(e) => handleFilterChange('total_max', e.target.value)}
                      min="0"
                    />
                  </div>
                </div>
                <div className="row mt-3">
                  <div className="col-12">
                    <button
                      type="button"
                      className="btn btn-primary me-2"
                      onClick={handleApplyFilters}
                    >
                      <i className="bi bi-check-circle"></i> Aplicar Filtros
                    </button>
                    <button
                      type="button"
                      className="btn btn-outline-secondary"
                      onClick={handleClearFilters}
                    >
                      <i className="bi bi-x-circle"></i> Limpiar Filtros
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Cliente</th>
                  <th>Usuario</th>
                  <th>Fecha</th>
                  <th>Total</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {sales.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="text-center">
                      No se encontraron ventas
                    </td>
                  </tr>
                ) : (
                  sales.map((sale) => (
                    <tr key={sale.id}>
                      <td>#{sale.id}</td>
                      <td>{sale.client_name || 'Cliente General'}</td>
                      <td>{sale.user_name}</td>
                      <td>{formatDate(sale.sale_date)}</td>
                      <td>{formatCurrency(sale.total_amount)}</td>
                      <td>
                        <Link
                          to={`/sales/${sale.id}`}
                          className="btn btn-sm btn-outline-primary"
                        >
                          Ver Detalle
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SaleList;

