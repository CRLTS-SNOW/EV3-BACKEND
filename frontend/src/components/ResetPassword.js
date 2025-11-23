// frontend/src/components/ResetPassword.js
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import Swal from 'sweetalert2';

const ResetPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validar campo vacío con SweetAlert2
    if (!email.trim()) {
      Swal.fire({
        icon: 'warning',
        title: 'Campo requerido',
        text: 'Por favor, ingresa tu correo electrónico',
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
      await api.resetPassword(email);
      
      Swal.fire({
        icon: 'success',
        title: '¡Código enviado!',
        html: `
          <p>Se ha enviado un código de verificación al correo <strong>${email}</strong>.</p>
          <p class="mt-3"><strong>Revisa tu bandeja de entrada y la carpeta de spam.</strong></p>
          <p class="text-muted small mt-2">
            El correo puede tardar unos minutos en llegar. Haz clic en el enlace del correo para continuar.
          </p>
        `,
        confirmButtonText: 'Entendido',
        confirmButtonColor: '#c00000',
        width: '600px',
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
      console.error('Error al restablecer contraseña:', error);
      
      // Mostrar mensaje genérico por seguridad (no revelar si el correo existe o no)
      const errorMessage = error.response?.data?.error || 'Correo electrónico inválido';
      
      Swal.fire({
        icon: 'error',
        title: 'Correo inválido',
        html: `
          <p>El correo electrónico ingresado es inválido o no está registrado en el sistema.</p>
          <p class="mt-3">Por favor, verifica que hayas ingresado el correo correcto.</p>
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
          <h2 className="card-title text-center mb-4">Restablecer Contraseña</h2>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label htmlFor="email" className="form-label">Correo Electrónico:</label>
              <input
                type="email"
                className="form-control"
                id="email"
                placeholder="Ingresa tu correo electrónico"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
              />
              <small className="form-text text-muted">
                Te enviaremos un enlace para restablecer tu contraseña.
              </small>
            </div>
            
            <div className="d-grid gap-2">
              <button 
                type="submit" 
                className="btn btn-primary" 
                disabled={loading}
              >
                {loading ? 'Enviando...' : 'Enviar Enlace'}
              </button>
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

export default ResetPassword;

