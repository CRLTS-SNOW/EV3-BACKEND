// frontend/src/components/Login.js
import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Swal from 'sweetalert2';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    if (user) {
      navigate('/products');
    }
  }, [user, navigate]);

  // Mostrar mensaje de sesión cerrada exitosamente
  useEffect(() => {
    const logoutParam = searchParams.get('logout');
    if (logoutParam === 'success') {
      Swal.fire({
        icon: 'success',
        title: 'Sesión cerrada con éxito',
        text: 'Has cerrado sesión correctamente. ¡Hasta pronto!',
        timer: 3000,
        showConfirmButton: true,
        confirmButtonColor: '#c00000',
        confirmButtonText: 'Entendido',
        customClass: {
          popup: 'swal2-popup-custom',
          title: 'swal2-title-custom',
          confirmButton: 'swal2-confirm-custom'
        },
        buttonsStyling: true,
      });
      // Limpiar el parámetro de la URL
      setSearchParams({});
    }
  }, [searchParams, setSearchParams]);

  // Mostrar mensaje cuando se cambia la contraseña desde Firebase
  useEffect(() => {
    const passwordChanged = searchParams.get('passwordChanged');
    if (passwordChanged === 'true') {
      Swal.fire({
        icon: 'success',
        title: 'Contraseña cambiada exitosamente',
        html: `
          <p>Tu contraseña ha sido restablecida correctamente.</p>
          <p class="mt-3">Ahora puedes iniciar sesión con tu nueva contraseña.</p>
        `,
        timer: 4000,
        showConfirmButton: true,
        confirmButtonColor: '#c00000',
        confirmButtonText: 'Entendido',
        customClass: {
          popup: 'swal2-popup-custom',
          title: 'swal2-title-custom',
          confirmButton: 'swal2-confirm-custom'
        },
        buttonsStyling: true,
      });
      // Limpiar el parámetro de la URL
      setSearchParams({});
    }
  }, [searchParams, setSearchParams]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validar campos con SweetAlert2
    if (!username.trim()) {
      Swal.fire({
        icon: 'warning',
        title: 'Campo requerido',
        text: 'Por favor, ingresa tu usuario o email',
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

    if (!password.trim()) {
      Swal.fire({
        icon: 'warning',
        title: 'Campo requerido',
        text: 'Por favor, ingresa tu contraseña',
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
      const result = await login(username, password);
      if (result.success) {
        Swal.fire({
          icon: 'success',
          title: '¡Bienvenido!',
          text: 'Has iniciado sesión exitosamente',
          timer: 1500,
          showConfirmButton: false,
          confirmButtonColor: '#c00000',
          customClass: {
            popup: 'swal2-popup-custom',
            title: 'swal2-title-custom',
          },
        });
        navigate('/products');
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Error de autenticación',
          text: result.error || 'Usuario o contraseña incorrectos',
          confirmButtonColor: '#c00000',
          confirmButtonText: 'Entendido',
          customClass: {
            popup: 'swal2-popup-custom',
            title: 'swal2-title-custom',
            confirmButton: 'swal2-confirm-custom'
          },
          buttonsStyling: true,
        });
      }
    } catch (error) {
      console.error('Error en handleSubmit:', error);
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.message || 'Ocurrió un error al iniciar sesión',
        confirmButtonColor: '#c00000',
        confirmButtonText: 'Entendido',
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
    <div className="login-container">
      <div className="card shadow-sm login-card" style={{ width: '100%', maxWidth: '400px', backgroundColor: '#fff', marginBottom: '20px' }}>
        <div className="card-body p-4 p-md-5">
          <div className="w-50 mx-auto mb-3">
            <img
              src="/logo.png"
              alt="Lili's Logo"
              className="img-fluid login-logo"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>
          <h2 className="card-title text-center mb-4" style={{ color: '#c00000' }}>Iniciar Sesión</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-floating mb-3">
              <input
                type="text"
                className="form-control"
                id="username"
                placeholder="Usuario o Email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={loading}
              />
              <label htmlFor="username">Usuario o Email</label>
            </div>

            <div className="form-floating mb-3">
              <input
                type="password"
                className="form-control"
                id="password"
                placeholder="Contraseña"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
              />
              <label htmlFor="password">Contraseña</label>
            </div>

            <button
              className="btn btn-primary w-100 btn-lg fs-5 fw-bold"
              type="submit"
              disabled={loading}
              style={{ backgroundColor: '#c00000', borderColor: '#d4af37', color: '#d4af37' }}
            >
              {loading ? 'Iniciando sesión...' : 'Entrar'}
            </button>
            
            <div className="text-center mt-3">
              <Link 
                to="/reset-password"
                className="text-decoration-underline" 
                style={{ fontSize: '0.9rem', color: '#c00000' }}
              >
                ¿Olvidaste tu contraseña?
              </Link>
            </div>
          </form>
        </div>
      </div>

      <div className="card shadow-sm" style={{ width: '100%', maxWidth: '400px', fontSize: '0.9em', backgroundColor: '#fff' }}>
        <div className="card-body">
          <h5 className="card-title text-center text-muted">Credenciales de Demo</h5>
          <ul className="list-group list-group-flush">
            <li className="list-group-item">
              <strong>Rol:</strong> Admin<br />
              <strong>User:</strong> admin / <strong>Pass:</strong> 123456
            </li>
            <li className="list-group-item">
              <strong>Rol:</strong> Operador de Bodega<br />
              <strong>User:</strong> bodeguero / <strong>Pass:</strong> 123456
            </li>
            <li className="list-group-item">
              <strong>Rol:</strong> Operador de Ventas<br />
              <strong>User:</strong> vendedor / <strong>Pass:</strong> 123456
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Login;

