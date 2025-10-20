import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { adService } from '../services/adService';
import Header from '../components/Header';
import {
  Video,
  Sparkles,
  MessageSquare,
  Play,
  Zap,
  TrendingUp,
  Home,
  ChevronRight,
} from 'lucide-react';

export default function CreateAd() {
  const [formData, setFormData] = useState({
    productName: '',
    productDesc: '',
  });
  const [statusMessage, setStatusMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setStatusMessage('');

    // Validate form data
    if (!formData.productName.trim()) {
      setError('Product name is required');
      return;
    }

    if (!formData.productDesc.trim()) {
      setError('Product description is required');
      return;
    }

    if (formData.productDesc.trim().length < 10) {
      setError('Product description must be at least 10 characters long');
      return;
    }

    setLoading(true);

    try {
      setStatusMessage('Creating ad...');
      const adData = {
        name: formData.productName,
        desc: formData.productDesc,
      };

      const result = await adService.createAd(adData);
      const runId = result.run_id;

      setStatusMessage('Ad created successfully! Redirecting...');
      
      // Navigate immediately to progress page
      setTimeout(() => {
        navigate(`/ads/${runId}/progress`);
      }, 500);
      
    } catch (err) {
      console.error('Create ad failed', err);
      const detail = err.response?.data?.detail || err.message || 'Failed to create ad. Please try again.';
      setError(detail);
      setLoading(false);
    }
  };

  const aspectRatioOptions = [
    { value: '9:16', label: 'Vertical (9:16)', icon: '📱', desc: 'TikTok, Instagram Reels' },
    { value: '16:9', label: 'Horizontal (16:9)', icon: '🖥️', desc: 'YouTube, Website' },
    { value: '1:1', label: 'Square (1:1)', icon: '⬜', desc: 'Instagram Feed' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900">
      <Header currentPage="Create Ad" />
      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,black,transparent)] pointer-events-none"></div>
      
      {/* Elegant Breadcrumb Navigation */}
      <div className="relative border-b border-slate-700/50 bg-slate-800/30 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
          <nav className="flex items-center gap-3 text-base">
            <Link 
              to="/dashboard" 
              className="flex items-center gap-2 text-slate-400 hover:text-indigo-400 transition-colors group"
            >
              <Home className="w-5 h-5 group-hover:scale-110 transition-transform" />
              <span className="font-medium">Dashboard</span>
            </Link>
            <ChevronRight className="w-5 h-5 text-slate-600" />
            <Link 
              to="/ads" 
              className="flex items-center gap-2 text-slate-400 hover:text-indigo-400 transition-colors group"
            >
              <Video className="w-5 h-5 group-hover:scale-110 transition-transform" />
              <span className="font-medium">My Video Ads</span>
            </Link>
            <ChevronRight className="w-5 h-5 text-slate-600" />
            <span className="text-indigo-400 font-bold flex items-center gap-2 bg-indigo-500/10 px-4 py-2 rounded-lg border border-indigo-500/30">
              <Sparkles className="w-5 h-5" />
              Create Ad
            </span>
          </nav>
        </div>
      </div>

      <div className="relative max-w-5xl mx-auto px-4 pb-8 pt-8 animate-fadeIn">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-indigo-600 to-cyan-500 rounded-xl shadow-lg shadow-indigo-500/50 mb-4">
            <Video className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400 mb-3 font-['Space_Grotesk']">
            Create Video Ad
          </h1>
          <p className="text-slate-400 text-lg flex items-center justify-center gap-2">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            AI-powered video generation in seconds
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-slate-700/50">
          {error && (
            <div className="bg-red-500/10 border-l-4 border-red-500 text-red-400 px-4 py-3 rounded-lg mb-6 flex items-center gap-2 backdrop-blur-sm">
              <span className="text-xl">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Section 1: Product Information */}
            <div>
              <h3 className="text-xl font-bold text-slate-100 mb-6 flex items-center gap-2">
                <Zap className="w-6 h-6 text-indigo-400" />
                Product Information
              </h3>
              <div className="space-y-6">
                {/* Product Name */}
                <div>
                  <label className="flex items-center gap-2 text-slate-300 text-sm font-bold mb-3">
                    <TrendingUp className="w-4 h-4 text-indigo-400" />
                    Product Name *
                  </label>
                  <input
                    type="text"
                    name="productName"
                    value={formData.productName}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 text-slate-100 placeholder-slate-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-base"
                    placeholder="e.g., AcmePay"
                    required
                    disabled={loading}
                  />
                </div>

                {/* Product Description */}
                <div>
                  <label className="flex items-center gap-2 text-slate-300 text-sm font-bold mb-3">
                    <MessageSquare className="w-4 h-4 text-indigo-400" />
                    Product Description *
                  </label>
                  <textarea
                    name="productDesc"
                    value={formData.productDesc}
                    onChange={handleChange}
                    className={`w-full px-4 py-3 bg-slate-700/50 border ${
                      formData.productDesc.length > 0 && formData.productDesc.length < 10 
                        ? 'border-red-500' 
                        : 'border-slate-600'
                    } text-slate-100 placeholder-slate-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-base resize-none`}
                    rows="4"
                    placeholder="e.g., UPI payments with instant rewards and cashback on every transaction"
                    required
                    disabled={loading}
                  />
                  <div className="flex justify-between items-center mt-2">
                    <p className="text-xs text-slate-400">Describe your product's key features and benefits</p>
                    <p className={`text-xs ${
                      formData.productDesc.length < 10 ? 'text-red-400' : 'text-slate-400'
                    }`}>
                      {formData.productDesc.length}/10 min
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 pt-6 border-t border-slate-700">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-700 hover:to-cyan-600 text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-500/50 hover:shadow-xl hover:shadow-cyan-500/50 relative overflow-hidden group"
              >
                <span className="relative z-10 flex items-center justify-center gap-2">
                  {loading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      {statusMessage || 'Creating ad...'}
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      Generate Video Ad
                    </>
                  )}
                </span>
                <div className="absolute inset-0 bg-slate-900/30 opacity-0 group-hover:opacity-80 transition-opacity"></div>
              </button>
              
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                disabled={loading}
                className="flex-1 bg-slate-700/50 hover:bg-slate-700 text-slate-200 font-bold py-4 px-6 rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed border border-slate-600"
              >
                Cancel
              </button>
            </div>
            {statusMessage && !loading && (
              <p className="text-sm text-cyan-400 mt-3 text-center">{statusMessage}</p>
            )}
          </form>
        </div>

        {/* Help Text */}
        <div className="mt-8 text-center text-sm text-slate-400">
          <p className="flex items-center justify-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            Your ad generation will start immediately after submission and you'll see progress updates
          </p>
        </div>
      </div>
    </div>
  );
}
