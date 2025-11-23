// frontend/src/components/supplier-orders/SupplierOrderDetail.js
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Swal from 'sweetalert2';

const SupplierOrderDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    loadOrder();
  }, [id]);

  const loadOrder = async () => {
    try {
      const response = await api.getSupplierOrder(id);
      setOrder(response.data);
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al cargar la orden',
      });
      navigate('/supplier-orders');
    } finally {
      setLoading(false);
    }
  };

  const handleReceive = async () => {
    const result = await Swal.fire({
      title: '¿Confirmar recepción?',
      text: '¿Deseas marcar esta orden como recibida?',
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#c00000',
      cancelButtonColor: '#6c757d',
      confirmButtonText: 'Sí, recibir',
      cancelButtonText: 'Cancelar',
    });

    if (result.isConfirmed) {
      setProcessing(true);
      try {
        await api.receiveOrder(id);
        Swal.fire({
          icon: 'success',
          title: '¡Éxito!',
          text: 'Orden recibida exitosamente',
        });
        loadOrder();
      } catch (error) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error.response?.data?.error || 'Error al recibir la orden',
        });
      } finally {
        setProcessing(false);
      }
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
    return date.toLocaleDateString('es-CL');
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

  if (!order) {
    return <div>Orden no encontrada</div>;
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Orden #{order.id}</h1>
        <div>
          {order.status === 'PENDING' && (
            <button
              className="btn btn-success me-2"
              onClick={handleReceive}
              disabled={processing}
            >
              {processing ? 'Procesando...' : 'Recibir Orden'}
            </button>
          )}
          <button className="btn btn-secondary" onClick={() => navigate('/supplier-orders')}>
            Volver
          </button>
        </div>
      </div>

      <div className="card mb-3">
        <div className="card-body">
          <h5 className="card-title">Información de la Orden</h5>
          <div className="row">
            <div className="col-md-6">
              <p><strong>Proveedor:</strong> {order.supplier_name}</p>
              <p><strong>Bodega:</strong> {order.warehouse_name || '-'}</p>
              <p><strong>Zona:</strong> {order.zone_name || '-'}</p>
            </div>
            <div className="col-md-6">
              <p><strong>Fecha:</strong> {formatDate(order.order_date)}</p>
              <p><strong>Estado:</strong> 
                <span
                  className={`badge ms-2 ${
                    order.status === 'RECEIVED'
                      ? 'bg-success'
                      : order.status === 'CANCELLED'
                      ? 'bg-danger'
                      : 'bg-warning'
                  }`}
                >
                  {order.status}
                </span>
              </p>
              <p><strong>Total:</strong> {formatCurrency(order.total_amount)}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <h5 className="card-title">Productos</h5>
          {order.items && order.items.length > 0 ? (
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
                {order.items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.product_name}</td>
                    <td>{item.product_sku}</td>
                    <td>{item.quantity}</td>
                    <td>{formatCurrency(item.unit_price)}</td>
                    <td>{formatCurrency(item.subtotal)}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr>
                  <th colSpan="4">Total</th>
                  <th>{formatCurrency(order.total_amount)}</th>
                </tr>
              </tfoot>
            </table>
          ) : (
            <p className="text-muted">No hay productos en esta orden</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default SupplierOrderDetail;

