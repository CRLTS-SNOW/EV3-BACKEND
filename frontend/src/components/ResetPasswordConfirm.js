// frontend/src/components/ResetPasswordConfirm.js
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import api from '../services/api';
import Swal from 'sweetalert2';

const ResetPasswordConfirm = () => {
  const [oobCode, setOobCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    // Extraer el código OOB de la URL si viene como parámetro
    const codeFromUrl = searchParams.get('oobCode');
    if (codeFromUrl) {
      setOobCode(codeFromUrl);
    }
  }, [searchParams]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validaciones
    if (!oobCode.trim()) {
      Swal.fire({
        icon: 'warning',
        title: 'Campo requerido',
        text: 'Por favor, ingresa el código de verificación',
        confirmButtonColor: '#c00000',
        confirmButtonText: 'Entendido',
        customClass: {
          popup: 'swal2-popup-custom',
          title: 'swal2-title-custom',
          confirmButton: 'swal2-confirm-custom'
        },
        buttonsStyling: true,
      });
      return;
    }

    if (!newPassword.trim()) {
      Swal.fire({
        icon: 'warning',
        title: 'Campo requerido',
        text: 'Por favor, ingresa tu nueva contraseña',
        confirmButtonColor: '#c00000',
        confirmButtonText: 'Entendido',
        customClass: {
          popup: 'swal2-popup-custom',
          title: 'swal2-title-custom',
          confirmButton: 'swal2-confirm-custom'
        },
        buttonsStyling: true,
      });
      return;
    }

    if (newPassword.length < 6) {
      Swal.fire({
        icon: 'warning',
        title: 'Contraseña muy corta',
        text: 'La contraseña debe tener al menos 6 caracteres',
        confirmButtonColor: '#c00000',
        confirmButtonText: 'Entendido',
        customClass: {
          popup: 'swal2-popup-custom',
          title: 'swal2-title-custom',
          confirmButton: 'swal2-confirm-custom'
        },
        buttonsStyling: true,
      });
      return;
    }

    if (newPassword !== confirmPassword) {
      Swal.fire({
        icon: 'error',
        title: 'Las contraseñas no coinciden',
        text: 'Por favor, asegúrate de que ambas contraseñas sean iguales',
        confirmButtonColor: '#c00000',
        confirmButtonText: 'Entendido',
        customClass: {
          popup: 'swal2-popup-custom',
          title: 'swal2-title-custom',
          confirmButton: 'swal2-confirm-custom'
        },
        buttonsStyling: true,
      });
      return;
    }

    setLoading(true);

    try {
      await api.resetPasswordConfirm(oobCode, newPassword);
      
      Swal.fire({
        icon: 'success',
        title: '¡Contraseña cambiada exitosamente!',
        html: `
          <p>Tu contraseña ha sido restablecida correctamente.</p>
          <p class="mt-3">Ahora puedes iniciar sesión con tu nueva contraseña.</p>
        `,
        confirmButtonText: 'Ir al Login',
        confirmButtonColor: '#c00000',
        customClass: {
          popup: 'swal2-popup-custom',
          title: 'swal2-title-custom',
          confirmButton: 'swal2-confirm-custom'
        },
        buttonsStyling: true,
      }).then(() => {
        navigate('/login');
      });
    } catch (error) {
      console.error('Error al cambiar contraseña:', error);
      
      const errorMessage = error.response?.data?.error || 'Error al cambiar la contraseña. Por favor, intenta nuevamente.';
      
      Swal.fire({
        icon: 'error',
        title: 'Error',
        html: `
          <p>${errorMessage}</p>
          <p class="mt-3 text-muted small">Si el código ha expirado, solicita uno nuevo desde la página de restablecimiento de contraseña.</p>
        `,
        confirmButtonText: 'Entendido',
        confirmButtonColor: '#c00000',
        customClass: {
          popup: 'swal2-popup-custom',
          title: 'swal2-title-custom',
          confirmButton: 'swal2-confirm-custom'
        },
        buttonsStyling: true,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        backgroundColor: '#f8f9fa',
        padding: '20px',
      }}
    >
      <div className="card shadow-sm" style={{ width: '100%', maxWidth: '400px' }}>
        <div className="card-body p-4 p-md-5">
          <div className="w-50 mx-auto mb-3">
            <img
              src="/logo.png"
              alt="Lili's Logo"
              className="img-fluid"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>
          <h2 className="card-title text-center mb-4">Cambiar Contraseña</h2>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label htmlFor="oobCode" className="form-label">Código de Verificación:</label>
              <input
                type="text"
                className="form-control"
                id="oobCode"
                placeholder="Ingresa el código recibido por correo"
                value={oobCode}
                onChange={(e) => setOobCode(e.target.value)}
                disabled={loading}
              />
              <small className="form-text text-muted">
                Ingresa el código que recibiste en tu correo electrónico
              </small>
            </div>

            <div className="mb-3">
              <label htmlFor="newPassword" className="form-label">Nueva Contraseña:</label>
              <input
                type="password"
                className="form-control"
                id="newPassword"
                placeholder="Ingresa tu nueva contraseña"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                disabled={loading}
                minLength={6}
              />
              <small className="form-text text-muted">
                Mínimo 6 caracteres
              </small>
            </div>

            <div className="mb-3">
              <label htmlFor="confirmPassword" className="form-label">Confirmar Contraseña:</label>
              <input
                type="password"
                className="form-control"
                id="confirmPassword"
                placeholder="Confirma tu nueva contraseña"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading}
                minLength={6}
              />
            </div>
            
            <div className="d-grid gap-2">
              <button 
                type="submit" 
                className="btn btn-primary" 
                disabled={loading}
              >
                {loading ? 'Cambiando contraseña...' : 'Cambiar Contraseña'}
              </button>
              <Link 
                to="/reset-password" 
                className="btn btn-link"
                style={{ textDecoration: 'none', color: '#c00000' }}
              >
                Solicitar nuevo código
              </Link>
              <Link 
                to="/login" 
                className="btn btn-secondary"
                style={{ textDecoration: 'none' }}
              >
                Volver al Login
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ResetPasswordConfirm;

