import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { LogOut, User } from 'lucide-react';

export default function DashboardLayout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <img 
                src="https://customer-assets.emergentagent.com/job_1ccdb137-8865-4cb4-b134-9dea2c01f7a6/artifacts/klhc20tm_ChangaRed_Logo_IG_320x320%20-%20Editado.png" 
                alt="ChangaRed" 
                className="h-12"
                data-testid="dashboard-logo"
              />
              <div>
                <h2 className="font-heading font-bold text-lg">ChangaRed</h2>
                <p className="text-xs text-slate-600 capitalize">{user?.rol}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="font-semibold" data-testid="user-nombre">{user?.nombre}</p>
                <p className="text-sm text-slate-600">{user?.email}</p>
              </div>
              <Button variant="outline" onClick={handleLogout} data-testid="logout-button">
                <LogOut className="h-4 w-4 mr-2" />
                Salir
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {children}
      </main>
    </div>
  );
}