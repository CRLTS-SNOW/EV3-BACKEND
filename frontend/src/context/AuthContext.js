// frontend/src/context/AuthContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verificar si el usuario está autenticado al cargar la app
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await api.getCurrentUser();
      setUser(response.data);
    } catch (error) {
      // 401 es esperado cuando no hay usuario autenticado, no mostrar error en consola
      if (error.response?.status !== 401 && error.response?.status !== 403) {
        console.error('Error al verificar autenticación:', error);
      }
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      console.log('Intentando login con:', username);
      const loginResponse = await api.login(username, password);
      console.log('Respuesta del login:', loginResponse);
      
      // El login devuelve los datos del usuario directamente
      if (loginResponse && loginResponse.data) {
        console.log('Usuario autenticado:', loginResponse.data);
        setUser(loginResponse.data);
        return { success: true };
      } else {
        // Si no viene en la respuesta, obtener el usuario actual
        console.log('Obteniendo usuario actual...');
        const response = await api.getCurrentUser();
        setUser(response.data);
        return { success: true };
      }
    } catch (error) {
      console.error('Error completo en login:', error);
      console.error('Error response:', error.response);
      console.error('Error data:', error.response?.data);
      
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.detail ||
                          error.message || 
                          'Error al iniciar sesión';
      
      return {
        success: false,
        error: errorMessage,
      };
    }
  };

  const logout = async () => {
    try {
      await api.logout();
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    } finally {
      setUser(null);
      // Agregar parámetro para indicar que se cerró sesión exitosamente
      window.location.href = '/login?logout=success';
    }
  };

  const isAdmin = () => {
    return user?.is_superuser || user?.profile?.role === 'admin';
  };

  const isBodega = () => {
    return user?.profile?.role === 'bodega';
  };

  const isVentas = () => {
    return user?.profile?.role === 'ventas';
  };

  const canAccessSuppliers = () => {
    return isAdmin() || isBodega();
  };

  const canAccessSales = () => {
    return isAdmin() || isVentas();
  };

  const value = {
    user,
    loading,
    login,
    logout,
    checkAuth,
    isAdmin,
    isBodega,
    isVentas,
    canAccessSuppliers,
    canAccessSales,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

