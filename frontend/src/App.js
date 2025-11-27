import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Services from './components/Services';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import AdminPanel from './components/AdminPanel';
import AdminAppointments from './components/AdminAppointments';
import GuestAppointment from './components/GuestAppointment';
import CustomerAppointment from './components/CustomerAppointment';
import Appointments from './components/Appointments';
import './App.css';

// Компонент для захисту маршрутів
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div className="text-center">Завантаження...</div>;
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />;
};

// Компонент для захисту адміністративних маршрутів
const AdminRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();
  
  if (loading) {
    return <div className="text-center">Завантаження...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  // Перевіряємо чи користувач є адміністратором
  if (!user?.is_staff) {
    return <Navigate to="/dashboard" />;
  }
  
  return children;
};

function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <Router>
          <div className="App">
            <Navbar />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/services" element={<Services />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/admin" element={
                <AdminRoute>
                  <AdminPanel />
                </AdminRoute>
              } />
              <Route path="/admin-appointments" element={
                <AdminRoute>
                  <AdminAppointments />
                </AdminRoute>
              } />
              <Route path="/guest-appointment" element={<GuestAppointment />} />
              <Route path="/appointment" element={
                <ProtectedRoute>
                  <CustomerAppointment />
                </ProtectedRoute>
              } />
              <Route path="/appointments" element={
                <ProtectedRoute>
                  <Appointments />
                </ProtectedRoute>
              } />
            </Routes>
            <ToastContainer position="top-right" autoClose={3000} />
          </div>
        </Router>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App; 