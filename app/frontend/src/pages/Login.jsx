import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/authService';
import { useAuthStore } from '../store/authStore';
import { Sparkles, Mail, Lock, Zap } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const { token, user } = await authService.login(email, password);
      setAuth(user, token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900">
      {/* Animated background grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#4f46e520_1px,transparent_1px),linear-gradient(to_bottom,#4f46e520_1px,transparent_1px)] bg-[size:4rem_4rem]"></div>
      
      {/* Animated glow effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-20 w-96 h-96 bg-indigo-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-cyan-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="relative z-10 w-full max-w-md px-6">
        {/* Logo/Brand Section */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-indigo-600 to-cyan-500 rounded-2xl shadow-xl shadow-indigo-500/50 mb-6 animate-pulse">
            <Zap className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-black mb-4 pb-2 font-['Space_Grotesk'] bg-gradient-to-r from-indigo-400 via-cyan-400 to-indigo-400 bg-clip-text text-transparent leading-tight">
            Vigen AI
          </h1>
          <p className="text-slate-400 text-lg flex items-center justify-center gap-2">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            Transform Ideas into Viral Videos
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-slate-800/80 backdrop-blur-xl rounded-3xl shadow-2xl shadow-indigo-500/10 p-8 border border-slate-700/50">
          <h2 className="text-2xl font-bold text-slate-100 mb-6 text-center">
            Welcome Back! 👋
          </h2>
          
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-xl mb-6 flex items-center gap-2">
              <span className="text-xl">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Input */}
            <div>
              <label className="block text-slate-300 text-sm font-semibold mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-slate-700/50 border border-slate-600 text-slate-100 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all placeholder-slate-400"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            {/* Password Input */}
            <div>
              <label className="block text-slate-300 text-sm font-semibold mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-slate-700/50 border border-slate-600 text-slate-100 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all placeholder-slate-400"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-700 hover:to-cyan-600 text-white font-bold py-3 px-4 rounded-xl transition-all duration-300 transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-500/50 hover:shadow-xl hover:shadow-cyan-500/50 relative overflow-hidden group"
            >
              <span className="relative z-10 flex items-center justify-center gap-2">
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Logging in...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5" />
                    Log In
                  </>
                )}
              </span>
              <div className="absolute inset-0 bg-slate-900/30 opacity-0 group-hover:opacity-80 transition-opacity"></div>
            </button>
          </form>

          {/* Register Link */}
          <div className="mt-6 text-center">
            <p className="text-slate-400">
              Don't have an account?{' '}
              <Link 
                to="/register" 
                className="text-cyan-400 hover:text-cyan-300 font-bold hover:underline transition-all"
              >
                Create one now →
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center mt-6 text-slate-400 text-sm">
          🚀 Built for Innovation • Powered by AI
        </p>
      </div>
    </div>
  );
}
