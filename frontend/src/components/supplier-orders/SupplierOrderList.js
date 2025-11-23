// frontend/src/components/supplier-orders/SupplierOrderList.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import Swal from 'sweetalert2';
import * as XLSX from 'xlsx';

const SupplierOrderList = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const params = {};
      if (searchQuery) params.q = searchQuery;
      if (statusFilter) params.status = statusFilter;
      const response = await api.getSupplierOrders(params);
      setOrders(response.data.results || response.data);
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al cargar órdenes',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadOrders();
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
      if (statusFilter) params.status = statusFilter;
      const response = await api.getSupplierOrders(params);
      const allOrders = Array.isArray(response.data) 
        ? response.data 
        : (response.data.results || []);
      
      if (allOrders.length === 0) {
        Swal.fire({
          icon: 'warning',
          title: 'Sin datos',
          text: 'No hay órdenes para exportar',
        });
        return;
      }
      
      const excelData = allOrders.map((order) => ({
        'ID': Number(order.id || 0),
        'Proveedor': String(order.supplier_name || ''),
        'Fecha': formatDate(order.order_date),
        'Estado': String(order.status || ''),
        'Total': Number(order.total_amount || 0),
      }));
      
      const ws = XLSX.utils.json_to_sheet(excelData, {
        header: ['ID', 'Proveedor', 'Fecha', 'Estado', 'Total'],
        skipHeader: false,
      });
      
      ws['!cols'] = [
        { wch: 8 },  // ID
        { wch: 25 }, // Proveedor
        { wch: 12 }, // Fecha
        { wch: 15 }, // Estado
        { wch: 15 }, // Total
      ];
      
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Órdenes');
      
      const fecha = new Date();
      const fechaStr = fecha.getFullYear() + '-' + 
                      String(fecha.getMonth() + 1).padStart(2, '0') + '-' + 
                      String(fecha.getDate()).padStart(2, '0');
      const fileName = `Ordenes_Proveedores_${fechaStr}.xlsx`;
      
      XLSX.writeFile(wb, fileName);
      
      Swal.fire({
        icon: 'success',
        title: '¡Éxito!',
        text: `Se exportaron ${allOrders.length} órdenes a Excel`,
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
        <h1>Órdenes a Proveedores</h1>
        <div className="d-flex gap-2">
          <button
            onClick={exportToExcel}
            className="btn btn-success"
            disabled={loading}
          >
            <i className="bi bi-file-earmark-excel"></i> Exportar a Excel
          </button>
          <Link to="/supplier-orders/new" className="btn btn-primary">
            <i className="bi bi-plus-circle"></i> Nueva Orden
          </Link>
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <form onSubmit={handleSearch} className="mb-3">
            <div className="row g-3">
              <div className="col-md-6">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Buscar por ID o proveedor..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <div className="col-md-3">
                <select
                  className="form-select"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="">Todos los estados</option>
                  <option value="PENDING">Pendiente</option>
                  <option value="RECEIVED">Recibida</option>
                  <option value="CANCELLED">Cancelada</option>
                </select>
              </div>
              <div className="col-md-3">
                <button type="submit" className="btn btn-primary w-100">
                  Buscar
                </button>
              </div>
            </div>
          </form>

          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Proveedor</th>
                  <th>Fecha</th>
                  <th>Estado</th>
                  <th>Total</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {orders.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="text-center">
                      No se encontraron órdenes
                    </td>
                  </tr>
                ) : (
                  orders.map((order) => (
                    <tr key={order.id}>
                      <td>#{order.id}</td>
                      <td>{order.supplier_name}</td>
                      <td>{formatDate(order.order_date)}</td>
                      <td>
                        <span
                          className={`badge ${
                            order.status === 'RECEIVED'
                              ? 'bg-success'
                              : order.status === 'CANCELLED'
                              ? 'bg-danger'
                              : 'bg-warning'
                          }`}
                        >
                          {order.status}
                        </span>
                      </td>
                      <td>{formatCurrency(order.total_amount)}</td>
                      <td>
                        <Link
                          to={`/supplier-orders/${order.id}`}
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

export default SupplierOrderList;

