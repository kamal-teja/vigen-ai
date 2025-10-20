import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import CreateAd from './pages/CreateAd';
import AdProgress from './pages/AdProgress';
import AdsList from './pages/AdsList';
import VideoDetail from './pages/VideoDetail';
import './index.css';

function PrivateRoute({ children }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/ads/new"
          element={
            <PrivateRoute>
              <CreateAd />
            </PrivateRoute>
          }
        />
        <Route
          path="/ads"
          element={
            <PrivateRoute>
              <AdsList />
            </PrivateRoute>
          }
        />
        <Route
          path="/ads/:runId/progress"
          element={
            <PrivateRoute>
              <AdProgress />
            </PrivateRoute>
          }
        />
        <Route
          path="/ads/:runId/video"
          element={
            <PrivateRoute>
              <VideoDetail />
            </PrivateRoute>
          }
        />
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
