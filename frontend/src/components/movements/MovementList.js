// frontend/src/components/movements/MovementList.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import Swal from 'sweetalert2';
import * as XLSX from 'xlsx';

const MovementList = () => {
  const [movements, setMovements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadMovements();
  }, []);

  const loadMovements = async () => {
    try {
      setLoading(true);
      const params = searchQuery ? { q: searchQuery } : {};
      const response = await api.getMovements(params);
      setMovements(response.data.results || response.data);
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al cargar movimientos',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadMovements();
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('es-CL');
  };

  const exportToExcel = async () => {
    try {
      setLoading(true);
      const params = searchQuery ? { q: searchQuery } : {};
      const response = await api.getMovements(params);
      const allMovements = Array.isArray(response.data) 
        ? response.data 
        : (response.data.results || []);
      
      if (allMovements.length === 0) {
        Swal.fire({
          icon: 'warning',
          title: 'Sin datos',
          text: 'No hay movimientos para exportar',
        });
        return;
      }
      
      const excelData = allMovements.map((movement) => ({
        'Fecha': formatDate(movement.fecha || movement.created_at),
        'Tipo': String(movement.tipo || movement.movement_type || ''),
        'Producto': String(movement.product_name || ''),
        'SKU': String(movement.product_sku || ''),
        'Proveedor': String(movement.supplier_name || '-'),
        'Bodega': String(movement.warehouse_name || '-'),
        'Zona Origen': String(movement.origin_zone_name || '-'),
        'Zona Destino': String(movement.destination_zone_name || '-'),
        'Cantidad': Number(movement.quantity || movement.cantidad || 0),
        'Lote': String(movement.lote || '-'),
        'Serie': String(movement.serie || '-'),
        'Fecha Vencimiento': movement.fecha_vencimiento || '-',
        'Doc. Referencia': String(movement.doc_referencia || '-'),
        'Motivo': String(movement.motivo || movement.reason || '-'),
        'Observaciones': String(movement.observaciones || '-'),
        'Usuario': String(movement.user_name || '-'),
      }));
      
      const ws = XLSX.utils.json_to_sheet(excelData, {
        header: ['Fecha', 'Tipo', 'Producto', 'SKU', 'Proveedor', 'Bodega', 'Zona Origen', 'Zona Destino', 'Cantidad', 'Lote', 'Serie', 'Fecha Vencimiento', 'Doc. Referencia', 'Motivo', 'Observaciones', 'Usuario'],
        skipHeader: false,
      });
      
      ws['!cols'] = [
        { wch: 20 }, // Fecha
        { wch: 15 }, // Tipo
        { wch: 25 }, // Producto
        { wch: 15 }, // SKU
        { wch: 20 }, // Proveedor
        { wch: 20 }, // Bodega
        { wch: 20 }, // Zona Origen
        { wch: 20 }, // Zona Destino
        { wch: 12 }, // Cantidad
        { wch: 15 }, // Lote
        { wch: 15 }, // Serie
        { wch: 18 }, // Fecha Vencimiento
        { wch: 18 }, // Doc. Referencia
        { wch: 30 }, // Motivo
        { wch: 30 }, // Observaciones
        { wch: 20 }, // Usuario
      ];
      
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Movimientos');
      
      const fecha = new Date();
      const fechaStr = fecha.getFullYear() + '-' + 
                      String(fecha.getMonth() + 1).padStart(2, '0') + '-' + 
                      String(fecha.getDate()).padStart(2, '0');
      const fileName = `Movimientos_${fechaStr}.xlsx`;
      
      XLSX.writeFile(wb, fileName);
      
      Swal.fire({
        icon: 'success',
        title: '¡Éxito!',
        text: `Se exportaron ${allMovements.length} movimientos a Excel`,
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
        <h1>Movimientos de Productos</h1>
        <div className="d-flex gap-2">
          <button
            onClick={exportToExcel}
            className="btn btn-success"
            disabled={loading}
          >
            <i className="bi bi-file-earmark-excel"></i> Exportar a Excel
          </button>
          <Link to="/movements/new" className="btn btn-primary">
            <i className="bi bi-plus-circle"></i> Nuevo Movimiento
          </Link>
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <form onSubmit={handleSearch} className="mb-3">
            <div className="row g-3">
              <div className="col-md-10">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Buscar por producto..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <div className="col-md-2">
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
                  <th>Fecha</th>
                  <th>Tipo</th>
                  <th>Producto</th>
                  <th>SKU</th>
                  <th>Proveedor</th>
                  <th>Bodega</th>
                  <th>Zona Origen</th>
                  <th>Zona Destino</th>
                  <th>Cantidad</th>
                  <th>Lote</th>
                  <th>Serie</th>
                  <th>Doc. Ref.</th>
                  <th>Usuario</th>
                </tr>
              </thead>
              <tbody>
                {movements.length === 0 ? (
                  <tr>
                    <td colSpan="13" className="text-center">
                      No se encontraron movimientos
                    </td>
                  </tr>
                ) : (
                  movements.map((movement) => (
                    <tr key={movement.id}>
                      <td>{formatDate(movement.fecha || movement.created_at)}</td>
                      <td>
                        <span className={`badge bg-${
                          movement.tipo === 'ingreso' ? 'success' :
                          movement.tipo === 'salida' ? 'danger' :
                          movement.tipo === 'transferencia' ? 'info' :
                          movement.tipo === 'ajuste' ? 'warning' :
                          movement.tipo === 'devolucion' ? 'primary' : 'secondary'
                        }`}>
                          {movement.tipo || movement.movement_type || '-'}
                        </span>
                      </td>
                      <td>{movement.product_name || '-'}</td>
                      <td>{movement.product_sku || '-'}</td>
                      <td>{movement.supplier_name || '-'}</td>
                      <td>{movement.warehouse_name || '-'}</td>
                      <td>{movement.origin_zone_name || '-'}</td>
                      <td>{movement.destination_zone_name || '-'}</td>
                      <td>{movement.quantity || movement.cantidad || 0}</td>
                      <td>{movement.lote || '-'}</td>
                      <td>{movement.serie || '-'}</td>
                      <td>{movement.doc_referencia || '-'}</td>
                      <td>{movement.user_name || '-'}</td>
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

export default MovementList;

