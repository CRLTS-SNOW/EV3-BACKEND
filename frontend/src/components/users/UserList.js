// frontend/src/components/users/UserList.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import Swal from 'sweetalert2';
import * as XLSX from 'xlsx';

const UserList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const params = searchQuery ? { q: searchQuery } : {};
      const response = await api.getUsers(params);
      setUsers(response.data.results || response.data);
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al cargar usuarios',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadUsers();
  };

  const exportToExcel = async () => {
    try {
      setLoading(true);
      const params = searchQuery ? { q: searchQuery } : {};
      const response = await api.getUsers(params);
      const allUsers = Array.isArray(response.data) 
        ? response.data 
        : (response.data.results || []);
      
      if (allUsers.length === 0) {
        Swal.fire({
          icon: 'warning',
          title: 'Sin datos',
          text: 'No hay usuarios para exportar',
        });
        return;
      }
      
      const excelData = allUsers.map((user) => ({
        'Usuario': String(user.username || ''),
        'Nombre': String(user.profile?.nombre_completo || user.first_name || ''),
        'Email': String(user.email || ''),
        'Rol': String(user.profile?.role_display || user.profile?.role || ''),
        'Estado': String(user.is_active ? 'Activo' : 'Inactivo'),
        'Teléfono': String(user.profile?.phone || ''),
      }));
      
      const ws = XLSX.utils.json_to_sheet(excelData, {
        header: ['Usuario', 'Nombre', 'Email', 'Rol', 'Estado', 'Teléfono'],
        skipHeader: false,
      });
      
      ws['!cols'] = [
        { wch: 15 }, // Usuario
        { wch: 25 }, // Nombre
        { wch: 25 }, // Email
        { wch: 15 }, // Rol
        { wch: 12 }, // Estado
        { wch: 15 }, // Teléfono
      ];
      
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Usuarios');
      
      const fecha = new Date();
      const fechaStr = fecha.getFullYear() + '-' + 
                      String(fecha.getMonth() + 1).padStart(2, '0') + '-' + 
                      String(fecha.getDate()).padStart(2, '0');
      const fileName = `Usuarios_${fechaStr}.xlsx`;
      
      XLSX.writeFile(wb, fileName);
      
      Swal.fire({
        icon: 'success',
        title: '¡Éxito!',
        text: `Se exportaron ${allUsers.length} usuarios a Excel`,
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

  const handleDelete = async (id, username) => {
    const result = await Swal.fire({
      title: '¿Estás seguro?',
      text: `¿Deseas eliminar al usuario ${username}?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#c00000',
      cancelButtonColor: '#6c757d',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar',
    });

    if (result.isConfirmed) {
      try {
        await api.deleteUser(id);
        Swal.fire({
          icon: 'success',
          title: '¡Éxito!',
          text: 'Usuario eliminado exitosamente',
        });
        loadUsers();
      } catch (error) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'Error al eliminar usuario',
        });
      }
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
        <h1>Usuarios</h1>
        <div className="d-flex gap-2">
          <button
            onClick={exportToExcel}
            className="btn btn-success"
            disabled={loading}
          >
            <i className="bi bi-file-earmark-excel"></i> Exportar a Excel
          </button>
          <Link to="/users/new" className="btn btn-primary">
            <i className="bi bi-plus-circle"></i> Nuevo Usuario
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
                  placeholder="Buscar por usuario, email o nombre..."
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
                  <th>Usuario</th>
                  <th>Nombre</th>
                  <th>Email</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="text-center">
                      No se encontraron usuarios
                    </td>
                  </tr>
                ) : (
                  users.map((user) => (
                    <tr key={user.id}>
                      <td>{user.username}</td>
                      <td>{user.profile?.nombre_completo || user.first_name || '-'}</td>
                      <td>{user.email || '-'}</td>
                      <td>{user.profile?.role_display || '-'}</td>
                      <td>
                        <span className={`badge ${user.is_active ? 'bg-success' : 'bg-danger'}`}>
                          {user.is_active ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td>
                        <Link
                          to={`/users/${user.id}/edit`}
                          className="btn btn-sm btn-outline-primary me-2"
                        >
                          Editar
                        </Link>
                        <button
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => handleDelete(user.id, user.username)}
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
        </div>
      </div>
    </div>
  );
};

export default UserList;

