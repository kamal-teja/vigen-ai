import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { adService } from '../services/adService';
import { useAuthStore } from '../store/authStore';
import { SkeletonRecentAds } from '../components/SkeletonLoader';
import Header from '../components/Header';
import {
  Zap,
  LogOut,
  Video,
  TrendingUp,
  Plus,
  Sparkles,
  PlayCircle,
  Clock,
  CheckCircle,
  XCircle,
  Loader
} from 'lucide-react';

export default function Dashboard() {
  const [ads, setAds] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const adsData = await adService.listAds();
      setAds(adsData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    const s = (status || '').toString().toUpperCase();
    switch (s) {
      case 'GENERATED':
        return <CheckCircle className="w-4 h-4" />;
      case 'FAILED':
        return <XCircle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const stats = {
    total: loading ? null : ads.length,
    inProgress: loading ? null : ads.filter((ad) => ad.status === 'IN_PROGRESS').length,
    generated: loading ? null : ads.filter((ad) => ad.status === 'GENERATED').length,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900">
      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)] pointer-events-none"></div>
      
      {/* Header */}
      <Header currentPage="Dashboard" />

      <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fadeIn">
        {/* Welcome Banner - Always visible */}
        <div className="mb-8 bg-gradient-to-r from-indigo-600/20 via-cyan-600/20 to-indigo-600/20 rounded-2xl p-8 border border-indigo-500/30 backdrop-blur-xl">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h2 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400 mb-2 font-['Space_Grotesk']">
                Welcome back, {user?.email?.split('@')[0] || 'Creator'}! 👋
              </h2>
              <p className="text-slate-300 text-lg">Create stunning video ads with AI in minutes</p>
            </div>
            <Link
              to="/ads/new"
              className="group flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-700 hover:to-cyan-600 text-white font-bold py-4 px-8 rounded-xl transition-all shadow-lg shadow-indigo-500/50 hover:shadow-xl hover:shadow-cyan-500/50 hover:scale-105"
            >
              <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform" />
              Create New Ad
            </Link>
          </div>
        </div>

        {/* Stats Cards - Always visible with loading spinners for numbers */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Total Ads */}
          <button
            onClick={() => navigate('/ads')}
            disabled={loading}
            className="relative overflow-hidden bg-gradient-to-br from-pink-600 to-rose-600 rounded-2xl shadow-lg shadow-pink-500/30 p-6 text-white transform hover:scale-105 transition-transform duration-300 cursor-pointer text-left group disabled:cursor-wait"
          >
            <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-indigo-400/8 opacity-60 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <Video className="w-10 h-10" />
                {stats.total === null ? (
                  <Loader className="w-8 h-8 animate-spin" />
                ) : (
                  <span className="text-3xl font-black">{stats.total}</span>
                )}
              </div>
              <h3 className="text-lg font-semibold mb-1">Total Ads</h3>
              <p className="text-pink-100 text-sm">Click to view all videos</p>
            </div>
          </button>

          {/* Ads In Progress */}
          <button
            onClick={() => navigate('/ads?status=in_progress')}
            disabled={loading}
            className="relative overflow-hidden bg-gradient-to-br from-indigo-600 to-blue-600 rounded-2xl shadow-lg shadow-indigo-500/30 p-6 text-white transform hover:scale-105 transition-transform duration-300 cursor-pointer text-left group disabled:cursor-wait"
          >
            <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-emerald-400/8 opacity-60 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <Clock className="w-10 h-10" />
                {stats.inProgress === null ? (
                  <Loader className="w-8 h-8 animate-spin" />
                ) : (
                  <span className="text-3xl font-black">{stats.inProgress}</span>
                )}
              </div>
              <h3 className="text-lg font-semibold mb-1">In Progress</h3>
              <p className="text-indigo-100 text-sm">Click to view generating ads</p>
            </div>
          </button>

          {/* Generated Ads */}
          <button
            onClick={() => navigate('/ads?status=generated')}
            disabled={loading}
            className="relative overflow-hidden bg-gradient-to-br from-emerald-600 to-teal-600 rounded-2xl shadow-lg shadow-emerald-500/30 p-6 text-white transform hover:scale-105 transition-transform duration-300 cursor-pointer text-left group disabled:cursor-wait"
          >
            <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-pink-400/8 opacity-60 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <TrendingUp className="w-10 h-10" />
                {stats.generated === null ? (
                  <Loader className="w-8 h-8 animate-spin" />
                ) : (
                  <span className="text-3xl font-black">{stats.generated}</span>
                )}
              </div>
              <h3 className="text-lg font-semibold mb-1">Generated</h3>
              <p className="text-emerald-100 text-sm">Click to view generated videos</p>
            </div>
          </button>
        </div>

        {/* Quick Actions */}
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl shadow-lg p-8 mb-8 border border-slate-700/50">
          <div className="flex items-center gap-2 mb-6">
            <Sparkles className="w-6 h-6 text-cyan-400" />
            <h2 className="text-2xl font-bold text-slate-100">Quick Actions</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Link
              to="/ads/new"
              className="group relative overflow-hidden bg-gradient-to-br from-pink-500/20 to-rose-500/20 hover:from-pink-500/30 hover:to-rose-500/30 rounded-xl p-6 transition-all duration-300 border-2 border-pink-500/30 hover:border-pink-400/50 hover:shadow-lg hover:shadow-pink-500/20"
            >
              <div className="flex flex-col items-center text-center">
                <div className="w-12 h-12 bg-gradient-to-br from-pink-600 to-rose-600 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform shadow-lg shadow-pink-500/50">
                  <PlayCircle className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-bold text-slate-100 mb-1">New Ad</h3>
                <p className="text-sm text-slate-400">Start a fresh creative brief</p>
              </div>
            </Link>

            <Link
              to="/ads"
              className="group relative overflow-hidden bg-gradient-to-br from-emerald-500/20 to-teal-500/20 hover:from-emerald-500/30 hover:to-teal-500/30 rounded-xl p-6 transition-all duration-300 border-2 border-emerald-500/30 hover:border-emerald-400/50 hover:shadow-lg hover:shadow-emerald-500/20"
            >
              <div className="flex flex-col items-center text-center">
                <div className="w-12 h-12 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform shadow-lg shadow-emerald-500/50">
                  <Video className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-bold text-slate-100 mb-1">View Ads</h3>
                <p className="text-sm text-slate-400">Manage your generated videos</p>
              </div>
            </Link>
          </div>
        </div>

        {/* Recent Ads */}
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl shadow-lg p-8 border border-slate-700/50">
          <h2 className="text-2xl font-bold text-slate-100 mb-6">Recent Ads</h2>
          {loading ? (
            <SkeletonRecentAds />
          ) : ads.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-indigo-500/30">
                <Video className="w-8 h-8 text-indigo-400" />
              </div>
              <p className="text-slate-400 mb-4">No ads created yet</p>
              <Link
                to="/ads/new"
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-700 hover:to-cyan-600 text-white font-semibold rounded-xl transition-all shadow-lg shadow-indigo-500/50 hover:shadow-xl hover:shadow-cyan-500/50"
              >
                <Plus className="w-5 h-5" />
                Create Your First Ad
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b-2 border-slate-700">
                    <th className="text-left py-4 px-4 font-semibold text-slate-300">Product</th>
                    <th className="text-left py-4 px-4 font-semibold text-slate-300">Description</th>
                    <th className="text-left py-4 px-4 font-semibold text-slate-300">Status</th>
                    <th className="text-left py-4 px-4 font-semibold text-slate-300">Created</th>
                    <th className="text-left py-4 px-4 font-semibold text-slate-300">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {ads.slice(0, 5).map((ad) => (
                    <tr key={ad.run_id || ad.id} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                      <td className="py-4 px-4 font-medium text-slate-200">{ad.name}</td>
                      <td className="py-4 px-4 text-slate-400 max-w-xs truncate">{ad.desc}</td>
                      <td className="py-4 px-4">
                        <span
                          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
                            ad.status === 'GENERATED'
                              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                              : ad.status === 'FAILED'
                              ? 'bg-red-500/10 text-red-400 border-red-500/30'
                              : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                          }`}
                        >
                          {getStatusIcon(ad.status)}
                          {ad.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-slate-400">
                        {new Date(ad.created_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </td>
                      <td className="py-4 px-4">
                        {ad.status === 'GENERATED' && (
                          <Link
                            to={`/ads/${ad.run_id || ad.id}/video`}
                            className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 rounded-lg text-sm font-medium hover:bg-indigo-500/30 transition-colors"
                          >
                            <PlayCircle className="w-4 h-4" />
                            View Video
                          </Link>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="relative mt-12 pb-8 text-center text-slate-500 text-sm">
        <p>🚀 Powered by Vigen AI • Built for Innovation</p>
      </footer>
    </div>
  );
}
