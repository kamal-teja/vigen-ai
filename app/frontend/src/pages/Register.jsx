import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/authService';
import { Sparkles, Mail, Lock, User, Zap, Check } from 'lucide-react';

export default function Register() {
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      await authService.register(email, fullName, password);
      navigate('/login', { state: { message: 'Registration successful! Please login.' } });
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900">
      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)]"></div>
      
      {/* Animated glow orbs */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 -left-20 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-cyan-600/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="relative z-10 w-full max-w-md px-6">
        {/* Logo/Brand Section */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-indigo-600 to-cyan-500 rounded-2xl shadow-xl shadow-indigo-500/50 mb-6">
            <Zap className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400 mb-4 pb-2 font-['Space_Grotesk'] leading-tight">
            Vigen AI
          </h1>
          <p className="text-slate-300 text-lg flex items-center justify-center gap-2">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            Join the Video Revolution
          </p>
        </div>

        {/* Register Card */}
        <div className="bg-slate-800/80 backdrop-blur-xl rounded-3xl shadow-2xl shadow-slate-950/50 p-8 border border-slate-700/50">
          <h2 className="text-2xl font-bold text-slate-100 mb-2 text-center">
            Create Your Account ✨
          </h2>
          <p className="text-slate-400 text-center mb-6">Start creating amazing videos today</p>
          
          {error && (
            <div className="bg-red-500/10 border-l-4 border-red-500 text-red-400 px-4 py-3 rounded-lg mb-6 flex items-center gap-2 backdrop-blur-sm">
              <span className="text-xl">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name Input */}
            <div>
              <label className="block text-slate-300 text-sm font-semibold mb-2">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-slate-700/50 border border-slate-600 text-slate-100 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all placeholder-slate-400"
                  placeholder="John Doe"
                  required
                />
              </div>
            </div>

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
              {password && (
                <p className={`text-xs mt-1 ${password.length >= 8 ? 'text-green-400' : 'text-slate-400'}`}>
                  {password.length >= 8 ? '✓' : '○'} At least 8 characters
                </p>
              )}
            </div>

            {/* Confirm Password Input */}
            <div>
              <label className="block text-slate-300 text-sm font-semibold mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-slate-700/50 border border-slate-600 text-slate-100 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all placeholder-slate-400"
                  placeholder="••••••••"
                  required
                />
              </div>
              {confirmPassword && (
                <p className={`text-xs mt-1 ${password === confirmPassword ? 'text-green-400' : 'text-red-400'}`}>
                  {password === confirmPassword ? '✓ Passwords match' : '✗ Passwords do not match'}
                </p>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-700 hover:to-cyan-600 text-white font-bold py-3 px-4 rounded-xl transition-all duration-300 transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-500/50 hover:shadow-xl hover:shadow-cyan-500/50 relative overflow-hidden group mt-6"
            >
              <span className="relative z-10 flex items-center justify-center gap-2">
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Creating Account...
                  </>
                ) : (
                  <>
                    <Check className="w-5 h-5" />
                    Create Account
                  </>
                )}
              </span>
              <div className="absolute inset-0 bg-slate-900/30 opacity-0 group-hover:opacity-80 transition-opacity"></div>
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-slate-400">
              Already have an account?{' '}
              <Link 
                to="/login" 
                className="text-cyan-400 hover:text-cyan-300 font-bold hover:underline transition-all"
              >
                Log in →
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center mt-6 text-slate-400 text-sm">
          🚀 Built for Innovation • Powered by AI
        </p>
        <p className="text-center mt-6 text-purple-100 text-sm">
          🚀 Built for Innovation • Powered by AI
        </p>
      </div>
    </div>
  );
}
