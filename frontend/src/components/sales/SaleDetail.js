// frontend/src/components/sales/SaleDetail.js
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Swal from 'sweetalert2';

const SaleDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [sale, setSale] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSale();
  }, [id]);

  const loadSale = async () => {
    try {
      const response = await api.getSale(id);
      setSale(response.data);
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al cargar la venta',
      });
      navigate('/sales');
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

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('es-CL');
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

  if (!sale) {
    return <div>Venta no encontrada</div>;
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Detalle de Venta #{sale.id}</h1>
        <button className="btn btn-secondary" onClick={() => navigate('/sales')}>
          Volver
        </button>
      </div>

      <div className="card mb-3">
        <div className="card-body">
          <h5 className="card-title">Información de la Venta</h5>
          <div className="row">
            <div className="col-md-6">
              <p><strong>Cliente:</strong> {sale.client_name || 'Cliente General'}</p>
              <p><strong>Usuario:</strong> {sale.user_name}</p>
            </div>
            <div className="col-md-6">
              <p><strong>Fecha:</strong> {formatDate(sale.sale_date)}</p>
              <p><strong>Total:</strong> {formatCurrency(sale.total_amount)}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <h5 className="card-title">Productos</h5>
          <table className="table">
            <thead>
              <tr>
                <th>Producto</th>
                <th>SKU</th>
                <th>Cantidad</th>
                <th>Precio Unitario</th>
                <th>Subtotal</th>
              </tr>
            </thead>
            <tbody>
              {sale.items?.map((item) => (
                <tr key={item.id}>
                  <td>{item.product_name}</td>
                  <td>{item.product_sku}</td>
                  <td>{item.quantity}</td>
                  <td>{formatCurrency(item.price_at_sale)}</td>
                  <td>{formatCurrency(item.subtotal)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <th colSpan="4">Total</th>
                <th>{formatCurrency(sale.total_amount)}</th>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  );
};

export default SaleDetail;

