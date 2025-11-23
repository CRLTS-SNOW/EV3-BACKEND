// frontend/src/components/suppliers/SupplierList.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import Swal from 'sweetalert2';
import * as XLSX from 'xlsx';

const SupplierList = () => {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const { isAdmin } = useAuth();

  useEffect(() => {
    loadSuppliers();
  }, []);

  const loadSuppliers = async () => {
    try {
      setLoading(true);
      const params = searchQuery ? { q: searchQuery } : {};
      const response = await api.getSuppliers(params);
      setSuppliers(response.data.results || response.data);
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al cargar proveedores',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadSuppliers();
  };

  const exportToExcel = async () => {
    try {
      setLoading(true);
      const params = searchQuery ? { q: searchQuery } : {};
      const response = await api.getSuppliers(params);
      const allSuppliers = Array.isArray(response.data) 
        ? response.data 
        : (response.data.results || []);
      
      if (allSuppliers.length === 0) {
        Swal.fire({
          icon: 'warning',
          title: 'Sin datos',
          text: 'No hay proveedores para exportar',
        });
        return;
      }
      
      const excelData = allSuppliers.map((supplier) => ({
        'RUT/NIF': String(supplier.rut_nif || ''),
        'Razón Social': String(supplier.razon_social || ''),
        'Nombre Fantasía': String(supplier.nombre_fantasia || ''),
        'Email': String(supplier.email || ''),
        'Teléfono': String(supplier.telefono || ''),
        'Estado': String(supplier.estado || ''),
      }));
      
      const ws = XLSX.utils.json_to_sheet(excelData, {
        header: ['RUT/NIF', 'Razón Social', 'Nombre Fantasía', 'Email', 'Teléfono', 'Estado'],
        skipHeader: false,
      });
      
      ws['!cols'] = [
        { wch: 15 }, // RUT/NIF
        { wch: 30 }, // Razón Social
        { wch: 25 }, // Nombre Fantasía
        { wch: 25 }, // Email
        { wch: 15 }, // Teléfono
        { wch: 12 }, // Estado
      ];
      
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Proveedores');
      
      const fecha = new Date();
      const fechaStr = fecha.getFullYear() + '-' + 
                      String(fecha.getMonth() + 1).padStart(2, '0') + '-' + 
                      String(fecha.getDate()).padStart(2, '0');
      const fileName = `Proveedores_${fechaStr}.xlsx`;
      
      XLSX.writeFile(wb, fileName);
      
      Swal.fire({
        icon: 'success',
        title: '¡Éxito!',
        text: `Se exportaron ${allSuppliers.length} proveedores a Excel`,
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
        <h1>Proveedores</h1>
        <div className="d-flex gap-2">
          <button
            onClick={exportToExcel}
            className="btn btn-success"
            disabled={loading}
          >
            <i className="bi bi-file-earmark-excel"></i> Exportar a Excel
          </button>
          {isAdmin() && (
            <Link to="/suppliers/new" className="btn btn-primary">
              <i className="bi bi-plus-circle"></i> Nuevo Proveedor
            </Link>
          )}
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
                  placeholder="Buscar por razón social, nombre, email o RUT..."
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
                  <th>Razón Social</th>
                  <th>Nombre Fantasía</th>
                  <th>Email</th>
                  <th>Teléfono</th>
                  <th>Estado</th>
                  {isAdmin() && <th>Acciones</th>}
                </tr>
              </thead>
              <tbody>
                {suppliers.length === 0 ? (
                  <tr>
                    <td colSpan={isAdmin() ? 6 : 5} className="text-center">
                      No se encontraron proveedores
                    </td>
                  </tr>
                ) : (
                  suppliers.map((supplier) => (
                    <tr key={supplier.id}>
                      <td>{supplier.razon_social || '-'}</td>
                      <td>{supplier.nombre_fantasia || '-'}</td>
                      <td>{supplier.email}</td>
                      <td>{supplier.telefono || '-'}</td>
                      <td>
                        <span className={`badge ${supplier.estado === 'ACTIVO' ? 'bg-success' : 'bg-danger'}`}>
                          {supplier.estado}
                        </span>
                      </td>
                      {isAdmin() && (
                        <td>
                          <Link
                            to={`/suppliers/${supplier.id}/edit`}
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
        </div>
      </div>
    </div>
  );
};

export default SupplierList;

