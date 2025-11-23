// frontend/src/services/api.js
import axios from 'axios';

const API_BASE_URL = '/api';

// Configurar axios para incluir credenciales en todas las peticiones
axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

// Obtener el token CSRF de las cookies
const getCsrfToken = () => {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      return value;
    }
  }
  return null;
};

// Interceptor para agregar el token CSRF a las peticiones (solo si existe)
axios.interceptors.request.use(
  (config) => {
    // Si es una petición que requiere CSRF (POST, PUT, DELETE, PATCH)
    const method = config.method?.toUpperCase();
    if (method && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
      const csrfToken = getCsrfToken();
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de autenticación
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    // No redirigir automáticamente en rutas de login o si ya estamos en login
    if (error.response && error.response.status === 401) {
      const currentPath = window.location.pathname;
      if (currentPath !== '/login' && !error.config?.url?.includes('/login')) {
        // Solo redirigir si no estamos en login y no es una petición de login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Servicios API
export const api = {
  // Autenticación
  login: async (username, password) => {
    return axios.post(`${API_BASE_URL}/login/`, {
      username: username,
      password: password,
    }, {
      withCredentials: true,
    });
  },

  logout: async () => {
    // Llamar al endpoint de logout del backend para cerrar la sesión correctamente
    try {
      return await axios.post(`${API_BASE_URL}/logout/`, {}, {
        withCredentials: true,
      });
    } catch (error) {
      // Si falla, aún así continuamos con el logout del frontend
      console.error('Error al cerrar sesión en el backend:', error);
      return Promise.resolve();
    }
  },

  getCurrentUser: async () => {
    return axios.get(`${API_BASE_URL}/current-user/`);
  },

  resetPassword: async (email) => {
    return axios.post(`${API_BASE_URL}/reset-password/`, {
      email: email,
    });
  },

  resetPasswordConfirm: async (oobCode, newPassword) => {
    return axios.post(`${API_BASE_URL}/reset-password-confirm/`, {
      oobCode: oobCode,
      newPassword: newPassword,
    });
  },

  getWarehouses: async () => {
    return axios.get(`${API_BASE_URL}/warehouses/`);
  },

  // Productos
  getProducts: async (params = {}) => {
    return axios.get(`${API_BASE_URL}/products/`, { params });
  },

  getProduct: async (id) => {
    return axios.get(`${API_BASE_URL}/products/${id}/`);
  },

  createProduct: async (data) => {
    return axios.post(`${API_BASE_URL}/products/`, data);
  },

  updateProduct: async (id, data) => {
    return axios.put(`${API_BASE_URL}/products/${id}/`, data);
  },

  deleteProduct: async (id) => {
    return axios.delete(`${API_BASE_URL}/products/${id}/`);
  },

  // Proveedores
  getSuppliers: async (params = {}) => {
    return axios.get(`${API_BASE_URL}/suppliers/`, { params });
  },

  getSupplier: async (id) => {
    return axios.get(`${API_BASE_URL}/suppliers/${id}/`);
  },

  createSupplier: async (data) => {
    return axios.post(`${API_BASE_URL}/suppliers/`, data);
  },

  updateSupplier: async (id, data) => {
    return axios.put(`${API_BASE_URL}/suppliers/${id}/`, data);
  },
  
  // Productos asociados a proveedores
  getSupplierProducts: async (supplierId) => {
    return axios.get(`${API_BASE_URL}/suppliers/${supplierId}/products/`);
  },
  addSupplierProduct: async (supplierId, data) => {
    return axios.post(`${API_BASE_URL}/suppliers/${supplierId}/products/`, data);
  },
  updateSupplierProduct: async (supplierId, data) => {
    return axios.put(`${API_BASE_URL}/suppliers/${supplierId}/products/`, data);
  },
  removeSupplierProduct: async (supplierId, productId) => {
    return axios.delete(`${API_BASE_URL}/suppliers/${supplierId}/products/`, {
      data: { product: productId }
    });
  },

  deleteSupplier: async (id) => {
    return axios.delete(`${API_BASE_URL}/suppliers/${id}/`);
  },

  // Usuarios
  getUsers: async (params = {}) => {
    return axios.get(`${API_BASE_URL}/users/`, { params });
  },

  getUser: async (id) => {
    return axios.get(`${API_BASE_URL}/users/${id}/`);
  },

  createUser: async (data) => {
    return axios.post(`${API_BASE_URL}/users/`, data);
  },

  updateUser: async (id, data) => {
    return axios.put(`${API_BASE_URL}/users/${id}/`, data);
  },

  changeUserPassword: async (id, data) => {
    return axios.post(`${API_BASE_URL}/users/${id}/change_password/`, data);
  },

  changeOwnPassword: async (data) => {
    return axios.post(`${API_BASE_URL}/users/change-own-password/`, data);
  },

  deleteUser: async (id) => {
    return axios.delete(`${API_BASE_URL}/users/${id}/delete_user/`);
  },

  // Movimientos
  getMovements: async (params = {}) => {
    return axios.get(`${API_BASE_URL}/movements/`, { params });
  },

  createMovement: async (data) => {
    return axios.post(`${API_BASE_URL}/movements/`, data);
  },

  // Ventas
  getSales: async (params = {}) => {
    return axios.get(`${API_BASE_URL}/sales/`, { params });
  },

  getSale: async (id) => {
    return axios.get(`${API_BASE_URL}/sales/${id}/`);
  },

  createSale: async (data) => {
    return axios.post(`${API_BASE_URL}/sales/`, data);
  },

  // Órdenes a Proveedores
  getSupplierOrders: async (params = {}) => {
    return axios.get(`${API_BASE_URL}/supplier-orders/`, { params });
  },

  getSupplierOrder: async (id) => {
    return axios.get(`${API_BASE_URL}/supplier-orders/${id}/`);
  },

  createSupplierOrder: async (data) => {
    return axios.post(`${API_BASE_URL}/supplier-orders/`, data);
  },

  addItemToOrder: async (orderId, data) => {
    return axios.post(`${API_BASE_URL}/supplier-orders/${orderId}/add_item/`, data);
  },

  receiveOrder: async (orderId) => {
    return axios.post(`${API_BASE_URL}/supplier-orders/${orderId}/receive/`);
  },

  deleteOrderItem: async (orderId, itemId) => {
    return axios.delete(`${API_BASE_URL}/supplier-orders/${orderId}/items/${itemId}/`);
  },

  // Clientes
  getClients: async (params = {}) => {
    return axios.get(`${API_BASE_URL}/clients/`, { params });
  },

  // Bodegas y Zonas
  getWarehouses: async () => {
    return axios.get(`${API_BASE_URL}/warehouses/`);
  },

  getZones: async (params = {}) => {
    return axios.get(`${API_BASE_URL}/zones/`, { params });
  },

  // APIs adicionales (migradas a REST API)
  getProductStockInfo: async (productId) => {
    return axios.get(`${API_BASE_URL}/products/${productId}/`);
  },

  getAllZones: async () => {
    return axios.get(`${API_BASE_URL}/zones/`);
  },

  getZonesByWarehouse: async (warehouseId) => {
    return axios.get(`${API_BASE_URL}/zones/`, { params: { warehouse: warehouseId } });
  },

  getProductPrice: async (productId) => {
    const response = await axios.get(`${API_BASE_URL}/products/${productId}/`);
    return { data: { price: response.data.precio_venta } };
  },

  searchProductsForSale: async (query) => {
    return axios.get(`${API_BASE_URL}/search-products-for-sale/`, {
      params: { q: query },
    });
  },

  getAllProductsForSale: async (page = 1, pageSize = 50) => {
    return axios.get(`${API_BASE_URL}/all-products-for-sale/`, {
      params: { page, page_size: pageSize },
    });
  },
};

export default api;

