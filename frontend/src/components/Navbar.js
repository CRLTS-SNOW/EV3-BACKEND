// frontend/src/components/Navbar.js
import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout, canAccessSuppliers, canAccessSales } = useAuth();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    };

    if (dropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [dropdownOpen]);

  const handleLogout = async () => {
    setDropdownOpen(false);
    await logout();
    // No necesitamos navigate aquí porque logout() ya redirige
  };

  const toggleDropdown = (e) => {
    e.preventDefault();
    setDropdownOpen(!dropdownOpen);
  };

  const getRoleDisplay = () => {
    if (user?.is_superuser) return 'Superusuario';
    if (user?.profile?.role) {
      const roles = {
        admin: 'Administrador',
        bodega: 'Operador de Bodega',
        ventas: 'Operador de Ventas',
        auditor: 'Auditor',
        operador: 'Operador',
      };
      return roles[user.profile.role] || user.profile.role;
    }
    return '';
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark">
      <div className="container-fluid">
        <Link className="navbar-brand" to="/products">
          <img
            src="/logo.png"
            alt="Lili's Logo"
            style={{ height: '40px', marginTop: '-5px', marginRight: '10px' }}
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
          <strong>Lili's Dulcería</strong>
        </Link>

        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            <li className="nav-item">
              <Link className="nav-link" to="/products">
                Inventario
              </Link>
            </li>

            {canAccessSuppliers() && (
              <li className="nav-item">
                <Link className="nav-link" to="/suppliers">
                  Proveedores
                </Link>
              </li>
            )}

            {canAccessSales() && (
              <li className="nav-item">
                <Link className="nav-link" to="/sales">
                  Ventas
                </Link>
              </li>
            )}

            {(user?.is_superuser || user?.profile?.role === 'admin' || user?.profile?.role === 'bodega') && (
              <li className="nav-item">
                <Link className="nav-link" to="/movements">
                  Movimientos
                </Link>
              </li>
            )}

            {user?.is_superuser || user?.profile?.role === 'admin' ? (
              <li className="nav-item">
                <Link className="nav-link" to="/users">
                  Usuarios
                </Link>
              </li>
            ) : null}
          </ul>

          <ul className="navbar-nav">
            <li className={`nav-item dropdown ${dropdownOpen ? 'show' : ''}`} ref={dropdownRef}>
              <a
                className="nav-link dropdown-toggle text-white"
                href="#"
                id="userDropdown"
                role="button"
                onClick={toggleDropdown}
                aria-expanded={dropdownOpen}
                style={{ cursor: 'pointer' }}
              >
                <strong>{user?.username}</strong>
                {getRoleDisplay() && ` (${getRoleDisplay()})`}
              </a>
              <ul className={`dropdown-menu dropdown-menu-end ${dropdownOpen ? 'show' : ''}`} aria-labelledby="userDropdown">
                <li>
                  <button
                    className="dropdown-item"
                    onClick={handleLogout}
                    style={{ background: 'none', border: 'none', width: '100%', textAlign: 'left', cursor: 'pointer' }}
                  >
                    <i className="bi bi-box-arrow-right"></i> Cerrar Sesión
                  </button>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

