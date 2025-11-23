// frontend/src/utils/validators.js

/**
 * Validadores reutilizables para formularios React
 */

// Validar email
export const validateEmail = (email) => {
  if (!email) return 'El email es requerido';
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) return 'El email no tiene un formato válido';
  if (email.length > 254) return 'El email no puede tener más de 254 caracteres';
  return '';
};

// Validar teléfono chileno
export const validatePhone = (phone) => {
  if (!phone) return '';
  const phoneClean = phone.replace(/[\s\-\(\)\.]/g, '');
  const chilePhoneRegex = /^(\+?56)?9\d{8}$/;
  if (!chilePhoneRegex.test(phoneClean)) {
    return 'El teléfono debe ser formato chileno (ej: +56912345678 o 912345678)';
  }
  if (phone.length > 30) return 'El teléfono no puede tener más de 30 caracteres';
  return '';
};

// Validar URL
export const validateUrl = (url) => {
  if (!url) return '';
  const urlRegex = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
  if (!urlRegex.test(url)) return 'La URL no es válida (ej: https://www.ejemplo.cl)';
  if (url.length > 255) return 'La URL no puede tener más de 255 caracteres';
  return '';
};

// Validar RUT/NIF chileno
export const validateRutNif = (rutNif) => {
  if (!rutNif) return 'El RUT/NIF es requerido';
  if (rutNif.length > 20) return 'El RUT/NIF no puede tener más de 20 caracteres';
  // Formato básico: permite números, puntos, guiones y K
  const rutRegex = /^[\d\.\-kK]+$/;
  if (!rutRegex.test(rutNif)) return 'El RUT/NIF contiene caracteres inválidos';
  return '';
};

// Validar username
export const validateUsername = (username) => {
  if (!username) return 'El usuario es requerido';
  if (username.length < 3) return 'El usuario debe tener al menos 3 caracteres';
  if (username.length > 150) return 'El usuario no puede tener más de 150 caracteres';
  const usernameRegex = /^[a-zA-Z0-9_]+$/;
  if (!usernameRegex.test(username)) return 'El usuario solo puede contener letras, números y guiones bajos';
  return '';
};

// Validar contraseña
export const validatePassword = (password) => {
  if (!password) return 'La contraseña es requerida';
  if (password.length < 8) return 'La contraseña debe tener al menos 8 caracteres';
  return '';
};

// Validar número positivo
export const validatePositiveNumber = (value, fieldName = 'El valor') => {
  if (value === '' || value === null || value === undefined) return '';
  const num = parseFloat(value);
  if (isNaN(num)) return `${fieldName} debe ser un número válido`;
  if (num < 0) return `${fieldName} no puede ser negativo`;
  return '';
};

// Validar número mayor que cero
export const validatePositiveNumberGreaterThanZero = (value, fieldName = 'El valor') => {
  if (value === '' || value === null || value === undefined) return '';
  const num = parseFloat(value);
  if (isNaN(num)) return `${fieldName} debe ser un número válido`;
  if (num <= 0) return `${fieldName} debe ser mayor que cero`;
  return '';
};

// Validar máximo de caracteres
export const validateMaxLength = (value, maxLength, fieldName = 'El campo') => {
  if (!value) return '';
  if (value.length > maxLength) {
    return `${fieldName} no puede tener más de ${maxLength} caracteres`;
  }
  return '';
};

// Validar campo requerido
export const validateRequired = (value, fieldName = 'Este campo') => {
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    return `${fieldName} es requerido`;
  }
  return '';
};

// Validar fecha
export const validateDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return 'La fecha no es válida';
  return '';
};

// Validar fecha futura
export const validateFutureDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return 'La fecha no es válida';
  if (date <= new Date()) return 'La fecha debe ser futura';
  return '';
};

// Validar fecha pasada
export const validatePastDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return 'La fecha no es válida';
  if (date >= new Date()) return 'La fecha debe ser pasada';
  return '';
};

// Validar porcentaje (0-100)
export const validatePercentage = (value) => {
  if (value === '' || value === null || value === undefined) return '';
  const num = parseFloat(value);
  if (isNaN(num)) return 'Debe ser un número válido';
  if (num < 0 || num > 100) return 'El porcentaje debe estar entre 0 y 100';
  return '';
};

// Validar SKU/EAN
export const validateSkuEan = (value) => {
  if (!value) return '';
  if (value.length > 50) return 'El código no puede tener más de 50 caracteres';
  const skuRegex = /^[A-Z0-9\-_]+$/i;
  if (!skuRegex.test(value)) return 'El código solo puede contener letras, números, guiones y guiones bajos';
  return '';
};

