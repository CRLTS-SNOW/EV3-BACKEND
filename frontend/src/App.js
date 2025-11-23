// frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Login from './components/Login';
import ResetPassword from './components/ResetPassword';
import ResetPasswordConfirm from './components/ResetPasswordConfirm';
import ProductList from './components/products/ProductList';
import ProductForm from './components/products/ProductForm';
import SupplierList from './components/suppliers/SupplierList';
import SupplierForm from './components/suppliers/SupplierForm';
import UserList from './components/users/UserList';
import UserForm from './components/users/UserForm';
import SaleList from './components/sales/SaleList';
import SaleForm from './components/sales/SaleForm';
import SaleDetail from './components/sales/SaleDetail';
import MovementList from './components/movements/MovementList';
import MovementForm from './components/movements/MovementForm';
import SupplierOrderList from './components/supplier-orders/SupplierOrderList';
import SupplierOrderForm from './components/supplier-orders/SupplierOrderForm';
import SupplierOrderDetail from './components/supplier-orders/SupplierOrderDetail';
import 'bootstrap/dist/css/bootstrap.min.css';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
      </div>
    );
  }

  return user ? children : <Navigate to="/login" />;
};

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/products"
        element={
          <PrivateRoute>
            <ProductList />
          </PrivateRoute>
        }
      />
      <Route
        path="/products/new"
        element={
          <PrivateRoute>
            <ProductForm />
          </PrivateRoute>
        }
      />
      <Route
        path="/products/:id/edit"
        element={
          <PrivateRoute>
            <ProductForm />
          </PrivateRoute>
        }
      />
      <Route
        path="/suppliers"
        element={
          <PrivateRoute>
            <SupplierList />
          </PrivateRoute>
        }
      />
      <Route
        path="/suppliers/new"
        element={
          <PrivateRoute>
            <SupplierForm />
          </PrivateRoute>
        }
      />
      <Route
        path="/suppliers/:id/edit"
        element={
          <PrivateRoute>
            <SupplierForm />
          </PrivateRoute>
        }
      />
      <Route
        path="/users"
        element={
          <PrivateRoute>
            <UserList />
          </PrivateRoute>
        }
      />
      <Route
        path="/users/new"
        element={
          <PrivateRoute>
            <UserForm />
          </PrivateRoute>
        }
      />
      <Route
        path="/users/:id/edit"
        element={
          <PrivateRoute>
            <UserForm />
          </PrivateRoute>
        }
      />
      <Route
        path="/sales"
        element={
          <PrivateRoute>
            <SaleList />
          </PrivateRoute>
        }
      />
      <Route
        path="/sales/new"
        element={
          <PrivateRoute>
            <SaleForm />
          </PrivateRoute>
        }
      />
      <Route
        path="/sales/:id"
        element={
          <PrivateRoute>
            <SaleDetail />
          </PrivateRoute>
        }
      />
      <Route
        path="/movements"
        element={
          <PrivateRoute>
            <MovementList />
          </PrivateRoute>
        }
      />
      <Route
        path="/movements/new"
        element={
          <PrivateRoute>
            <MovementForm />
          </PrivateRoute>
        }
      />
      <Route
        path="/supplier-orders"
        element={
          <PrivateRoute>
            <SupplierOrderList />
          </PrivateRoute>
        }
      />
      <Route
        path="/supplier-orders/new"
        element={
          <PrivateRoute>
            <SupplierOrderForm />
          </PrivateRoute>
        }
      />
      <Route
        path="/supplier-orders/:id"
        element={
          <PrivateRoute>
            <SupplierOrderDetail />
          </PrivateRoute>
        }
      />
      <Route path="/" element={<Navigate to="/products" />} />
    </Routes>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/reset-password-confirm" element={<ResetPasswordConfirm />} />
            <Route
              path="/*"
              element={
                <PrivateRoute>
                  <Navbar />
                  <div className="container mt-4">
                    <AppRoutes />
                  </div>
                </PrivateRoute>
              }
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

