import React from 'react';
import { useAuthStore } from '../store/authStore';
import { Zap, LogOut } from 'lucide-react';

export default function Header({ currentPage = 'Dashboard' }) {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <header className="relative bg-slate-800/50 border-b border-slate-700/50 sticky top-0 z-50 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/50">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-black font-['Space_Grotesk'] bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                Vigen AI
              </h1>
              <p className="text-xs text-slate-400">Video Generation Platform</p>
            </div>
          </div>

          {/* User Menu */}
          <div className="flex items-center gap-4">
            <div className="hidden sm:block text-right">
              <p className="text-sm font-semibold text-slate-200">{user?.email || 'User'}</p>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 bg-slate-700/50 hover:bg-red-500/20 text-slate-300 hover:text-red-400 rounded-lg transition-all border border-slate-600 hover:border-red-500/50"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}