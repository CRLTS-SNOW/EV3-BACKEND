// frontend/src/components/users/UserForm.js
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Swal from 'sweetalert2';
import { useAuth } from '../../context/AuthContext';
import {
  validateRequired,
  validateMaxLength,
  validateEmail,
  validatePhone,
  validateUsername,
  validatePassword
} from '../../utils/validators';

const UserForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const isEdit = !!id;
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [warehouses, setWarehouses] = useState([]);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    password_confirm: '',
    is_active: true,
    profile: {
      role: 'ventas',
      nombres: '',
      apellidos: '',
      phone: '',
      mfa_habilitado: false,
      estado: 'ACTIVO',
      area: '',
      observaciones: '',
    },
  });

  useEffect(() => {
    if (isEdit) {
      loadUser();
    }
  }, [id]);

  const loadUser = async () => {
    try {
      const response = await api.getUser(id);
      const profile = response.data.profile || {};
      setFormData({
        username: response.data.username,
        email: response.data.email || '',
        first_name: response.data.first_name || profile.nombres || '',
        last_name: response.data.last_name || profile.apellidos || '',
        password: '',
        is_active: response.data.is_active !== undefined ? response.data.is_active : true,
        profile: {
          role: profile.role || 'ventas',
          nombres: profile.nombres || response.data.first_name || '',
          apellidos: profile.apellidos || response.data.last_name || '',
          phone: profile.phone || '',
          mfa_habilitado: profile.mfa_habilitado || false,
          estado: profile.estado || 'ACTIVO',
          area: profile.area || '',
          observaciones: profile.observaciones || '',
          ultimo_acceso: profile.ultimo_acceso || null,
          sesiones_activas: profile.sesiones_activas || 0,
        },
      });
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al cargar el usuario',
      });
      navigate('/users');
    }
  };

  // Validaciones usando validadores reutilizables
  const validateField = (name, value) => {
    let error = '';
    
    switch (name) {
      case 'username':
        error = validateUsername(value);
        break;
      case 'email':
        error = validateEmail(value);
        break;
      case 'password':
        error = validatePassword(value);
        break;
      case 'password_confirm':
        if (!isEdit && formData.password && value !== formData.password) {
          error = 'Las contraseñas no coinciden';
        }
        break;
      case 'profile.phone':
        error = validatePhone(value);
        break;
      case 'profile.nombres':
        error = validateRequired(value, 'Los nombres');
        if (!error) error = validateMaxLength(value, 100, 'Los nombres');
        break;
      case 'profile.apellidos':
        error = validateRequired(value, 'Los apellidos');
        if (!error) error = validateMaxLength(value, 100, 'Los apellidos');
        break;
      case 'profile.area':
        if (value) error = validateMaxLength(value, 100, 'El área/unidad');
        break;
      case 'profile.observaciones':
        if (value) error = validateMaxLength(value, 500, 'Las observaciones');
        break;
      default:
        break;
    }
    
    return error;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    // Validar campo en tiempo real
    const error = validateField(name, value);
    setErrors({
      ...errors,
      [name]: error,
    });
    
    if (name.startsWith('profile.')) {
      const profileField = name.replace('profile.', '');
      setFormData({
        ...formData,
        profile: {
          ...formData.profile,
          [profileField]: value,
        },
      });
    } else {
      setFormData({
        ...formData,
        [name]: value,
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Validar campos principales usando validadores reutilizables
    newErrors.username = validateField('username', formData.username);
    newErrors.email = validateField('email', formData.email);
    
    if (!isEdit) {
      newErrors.password = validateField('password', formData.password);
      newErrors.password_confirm = validateField('password_confirm', formData.password_confirm);
    }
    
    // Validar campos del perfil
    newErrors['profile.phone'] = validateField('profile.phone', formData.profile.phone);
    newErrors['profile.nombres'] = validateField('profile.nombres', formData.profile.nombres);
    newErrors['profile.apellidos'] = validateField('profile.apellidos', formData.profile.apellidos);
    newErrors['profile.area'] = validateField('profile.area', formData.profile.area);
    newErrors['profile.observaciones'] = validateField('profile.observaciones', formData.profile.observaciones);
    
    setErrors(newErrors);
    
    // Verificar si hay errores
    return Object.values(newErrors).every(error => error === '');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validar formulario antes de enviar
    if (!validateForm()) {
      Swal.fire({
        icon: 'error',
        title: 'Error de validación',
        text: 'Por favor, corrige los errores en el formulario antes de guardar',
      });
      return;
    }
    
    setLoading(true);

    try {
      // Preparar datos en el formato que espera Django
      const submitData = {
        username: formData.username,
        email: formData.email,
        first_name: formData.first_name,
        last_name: formData.last_name,
        is_active: formData.is_active,
        // Campos del perfil como campos planos (no anidados)
        role: formData.profile.role,
        nombres: formData.profile.nombres,
        apellidos: formData.profile.apellidos,
        phone: formData.profile.phone,
        estado: formData.profile.estado || 'ACTIVO',
        mfa_habilitado: formData.profile.mfa_habilitado || false,
        area: formData.profile.area || '',
        observaciones: formData.profile.observaciones || '',
      };

      if (isEdit) {
        await api.updateUser(id, submitData);
        Swal.fire({
          icon: 'success',
          title: '¡Éxito!',
          text: 'Usuario actualizado exitosamente',
        });
      } else {
        // Para crear, incluir la contraseña
        submitData.password = formData.password;
        await api.createUser(submitData);
        Swal.fire({
          icon: 'success',
          title: '¡Éxito!',
          text: 'Usuario creado exitosamente',
        });
      }
      navigate('/users');
    } catch (error) {
      console.error('Error al guardar usuario:', error);
      let errorMessage = 'Error al guardar usuario';
      
      if (error.response?.data) {
        // Si hay errores del formulario Django
        if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (typeof error.response.data === 'object') {
          // Formatear errores del formulario
          const errors = [];
          for (const [key, value] of Object.entries(error.response.data)) {
            if (Array.isArray(value)) {
              errors.push(`${key}: ${value.join(', ')}`);
            } else if (typeof value === 'string') {
              errors.push(`${key}: ${value}`);
            } else {
              errors.push(`${key}: ${JSON.stringify(value)}`);
            }
          }
          // Mapear errores a campos del formulario para mostrar en los campos
          const formErrors = {};
          for (const [key, value] of Object.entries(error.response.data)) {
            const errorText = Array.isArray(value) ? value.join(', ') : (typeof value === 'string' ? value : JSON.stringify(value));
            if (key === 'phone') {
              formErrors['profile.phone'] = errorText;
            } else if (key.startsWith('profile.')) {
              formErrors[key] = errorText;
            } else {
              formErrors[key] = errorText;
            }
          }
          setErrors(formErrors);
          
          errorMessage = errors.length > 0 ? errors.join('\n') : 'Error al guardar usuario';
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      Swal.fire({
        icon: 'error',
        title: 'Error de validación',
        html: `<div style="text-align: left;">${errorMessage.split('\n').map(e => `<div>${e}</div>`).join('')}</div>`,
        width: '600px',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>{isEdit ? 'Editar Usuario' : 'Nuevo Usuario'}</h1>
      <div className="card">
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Usuario *</label>
                <input
                  type="text"
                  className={`form-control ${errors.username ? 'is-invalid' : ''}`}
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  disabled={isEdit}
                  minLength={3}
                  maxLength={150}
                  pattern="[a-zA-Z0-9_]+"
                />
                {errors.username && (
                  <div className="invalid-feedback">{errors.username}</div>
                )}
                {!errors.username && (
                  <small className="form-text text-muted">Mínimo 3 caracteres, solo letras, números y guiones bajos</small>
                )}
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Email *</label>
                <input
                  type="email"
                  className={`form-control ${errors.email ? 'is-invalid' : ''}`}
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  maxLength={150}
                />
                {errors.email && (
                  <div className="invalid-feedback">{errors.email}</div>
                )}
              </div>
            </div>

            {!isEdit && (
              <div className="row">
                <div className="col-md-6 mb-3">
                  <label className="form-label">Contraseña *</label>
                  <input
                    type="password"
                    className={`form-control ${errors.password ? 'is-invalid' : ''}`}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required={!isEdit}
                    minLength={8}
                  />
                  {errors.password && (
                    <div className="invalid-feedback">{errors.password}</div>
                  )}
                  <small className="form-text text-muted">Mínimo 8 caracteres</small>
                </div>
                <div className="col-md-6 mb-3">
                  <label className="form-label">Confirmar Contraseña *</label>
                  <input
                    type="password"
                    className={`form-control ${errors.password_confirm ? 'is-invalid' : ''}`}
                    name="password_confirm"
                    value={formData.password_confirm}
                    onChange={handleChange}
                    required={!isEdit}
                  />
                  {errors.password_confirm && (
                    <div className="invalid-feedback">{errors.password_confirm}</div>
                  )}
                </div>
              </div>
            )}

            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Nombres</label>
                <input
                  type="text"
                  className={`form-control ${errors['profile.nombres'] ? 'is-invalid' : ''}`}
                  name="profile.nombres"
                  value={formData.profile.nombres}
                  onChange={handleChange}
                  maxLength={100}
                />
                {errors['profile.nombres'] && (
                  <div className="invalid-feedback">{errors['profile.nombres']}</div>
                )}
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Apellidos *</label>
                <input
                  type="text"
                  className={`form-control ${errors['profile.apellidos'] ? 'is-invalid' : ''}`}
                  name="profile.apellidos"
                  value={formData.profile.apellidos}
                  onChange={handleChange}
                  maxLength={100}
                  required
                />
                {errors['profile.apellidos'] && (
                  <div className="invalid-feedback">{errors['profile.apellidos']}</div>
                )}
              </div>
            </div>

            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Teléfono</label>
                <input
                  type="tel"
                  className={`form-control ${errors['profile.phone'] ? 'is-invalid' : ''}`}
                  name="profile.phone"
                  value={formData.profile.phone}
                  onChange={handleChange}
                  placeholder="+56912345678"
                />
                {errors['profile.phone'] && (
                  <div className="invalid-feedback">{errors['profile.phone']}</div>
                )}
                {!errors['profile.phone'] && (
                  <small className="form-text text-muted">Formato chileno (ej: +56912345678 o 912345678)</small>
                )}
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Rol *</label>
                <select
                  className={`form-select ${errors['profile.role'] ? 'is-invalid' : ''}`}
                  name="profile.role"
                  value={formData.profile.role}
                  onChange={handleChange}
                  required
                  disabled={formData.username === 'admin'}
                >
                  <option value="admin">Administrador</option>
                  <option value="bodega">Operador de Bodega</option>
                  <option value="ventas">Operador de Ventas</option>
                  <option value="auditor">Auditor</option>
                  <option value="operador">Operador</option>
                </select>
                {errors['profile.role'] && (
                  <div className="invalid-feedback">{errors['profile.role']}</div>
                )}
                {formData.username === 'admin' && (
                  <small className="form-text text-muted">El usuario admin no puede cambiar su rol</small>
                )}
              </div>
            </div>
            
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Estado *</label>
                <select
                  className={`form-select ${errors['profile.estado'] ? 'is-invalid' : ''}`}
                  name="profile.estado"
                  value={formData.profile.estado}
                  onChange={handleChange}
                  required
                >
                  <option value="ACTIVO">Activo</option>
                  <option value="BLOQUEADO">Bloqueado</option>
                  <option value="INACTIVO">Inactivo</option>
                </select>
                {errors['profile.estado'] && (
                  <div className="invalid-feedback">{errors['profile.estado']}</div>
                )}
              </div>
            </div>

            <div className="row">
              <div className="col-md-12 mb-3">
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="profile.mfa_habilitado"
                    checked={formData.profile.mfa_habilitado}
                    onChange={handleChange}
                  />
                  <label className="form-check-label">MFA Habilitado</label>
                </div>
              </div>
            </div>

            {isEdit && (
              <div className="row mb-3">
                <div className="col-md-6">
                  <label className="form-label">Último Acceso</label>
                  <input
                    type="text"
                    className="form-control"
                    value={formData.profile.ultimo_acceso 
                      ? new Date(formData.profile.ultimo_acceso).toLocaleString('es-CL')
                      : 'Nunca'}
                    disabled
                    readOnly
                  />
                  <small className="form-text text-muted">Solo lectura</small>
                </div>
                <div className="col-md-6">
                  <label className="form-label">Sesiones Activas</label>
                  <input
                    type="number"
                    className="form-control"
                    value={formData.profile.sesiones_activas || 0}
                    disabled
                    readOnly
                  />
                  <small className="form-text text-muted">Solo lectura</small>
                </div>
              </div>
            )}

            <h5 className="mt-4 mb-3">Metadatos</h5>
            <div className="row">
              <div className="col-md-12 mb-3">
                <label className="form-label">Área/Unidad</label>
                <input
                  type="text"
                  className={`form-control ${errors['profile.area'] ? 'is-invalid' : ''}`}
                  name="profile.area"
                  value={formData.profile.area}
                  onChange={handleChange}
                  maxLength={100}
                  placeholder="Área o unidad del usuario"
                />
                {errors['profile.area'] && (
                  <div className="invalid-feedback">{errors['profile.area']}</div>
                )}
              </div>
            </div>

            <div className="row">
              <div className="col-12 mb-3">
                <label className="form-label">Observaciones</label>
                <textarea
                  className={`form-control ${errors['profile.observaciones'] ? 'is-invalid' : ''}`}
                  name="profile.observaciones"
                  value={formData.profile.observaciones}
                  onChange={handleChange}
                  rows={3}
                  maxLength={500}
                  placeholder="Observaciones adicionales"
                />
                {errors['profile.observaciones'] && (
                  <div className="invalid-feedback">{errors['profile.observaciones']}</div>
                )}
                <small className="form-text text-muted">
                  {formData.profile.observaciones.length}/500 caracteres
                </small>
              </div>
            </div>

            <div className="d-flex justify-content-end gap-2">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate('/users')}
              >
                Cancelar
              </button>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Guardando...' : 'Guardar'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UserForm;

