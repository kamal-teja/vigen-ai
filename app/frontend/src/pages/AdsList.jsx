import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { adService } from '../services/adService';
import { useAuthStore } from '../store/authStore';
import { SkeletonCard, SkeletonListItem, SkeletonStatCard } from '../components/SkeletonLoader';
import Header from '../components/Header';
import {
  Video,
  CheckCircle,
  Clock,
  XCircle,
  Search,
  Filter,
  Grid3x3,
  List,
  Play,
  Eye,
  Calendar,
  Sparkles,
  TrendingUp,
  Loader,
  AlertCircle,
  ChevronRight,
  ChevronDown,
  Home
} from 'lucide-react';

export default function AdsList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  
  const [ads, setAds] = useState([]);
  const [filteredAds, setFilteredAds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || 'all');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [sortBy, setSortBy] = useState('newest'); // 'newest', 'oldest', 'name'
  const [sortDropdownOpen, setSortDropdownOpen] = useState(false);

  useEffect(() => {
    loadAds();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [ads, searchQuery, statusFilter, sortBy]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (sortDropdownOpen && !event.target.closest('.sort-dropdown')) {
        setSortDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [sortDropdownOpen]);

  const loadAds = async () => {
    try {
      const adsData = await adService.listAds();
      setAds(adsData);
    } catch (error) {
      console.error('Error loading ads:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let result = [...ads];

    // Filter by status
    if (statusFilter !== 'all') {
      result = result.filter(ad => {
        if (statusFilter === 'in_progress') return ad.status === 'in_progress' || ad.status === 'IN_PROGRESS';
  if (statusFilter === 'generated') return ad.status === 'generated' || ad.status === 'GENERATED';
        if (statusFilter === 'failed') return ad.status === 'failed' || ad.status === 'FAILED';
        return true;
      });
    }

    // Filter by search query
    if (searchQuery) {
      result = result.filter(ad =>
        ad.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ad.desc.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Sort
    result.sort((a, b) => {
      if (sortBy === 'newest') {
        return new Date(b.created_at) - new Date(a.created_at);
      } else if (sortBy === 'oldest') {
        return new Date(a.created_at) - new Date(b.created_at);
      } else if (sortBy === 'name') {
        return a.name.localeCompare(b.name);
      }
      return 0;
    });

    setFilteredAds(result);
  };

  const handleStatusFilterChange = (status) => {
    setStatusFilter(status);
    if (status === 'all') {
      searchParams.delete('status');
    } else {
      searchParams.set('status', status);
    }
    setSearchParams(searchParams);
  };

  const getStatusBadge = (status) => {
    const normalizedStatus = status.toLowerCase();
    switch (normalizedStatus) {
  case 'generated':
        return {
          bg: 'bg-emerald-500/10',
          text: 'text-emerald-400 border-emerald-500/30',
          icon: <CheckCircle className="w-4 h-4" />,
          label: 'Generated'
        };
      case 'in_progress':
        return {
          bg: 'bg-blue-500/10',
          text: 'text-blue-400 border-blue-500/30',
          icon: <Clock className="w-4 h-4 animate-spin" />,
          label: 'In Progress'
        };
      case 'failed':
        return {
          bg: 'bg-red-500/10',
          text: 'text-red-400 border-red-500/30',
          icon: <XCircle className="w-4 h-4" />,
          label: 'Failed'
        };
      default:
        return {
          bg: 'bg-slate-500/10',
          text: 'text-slate-400 border-slate-500/30',
          icon: <AlertCircle className="w-4 h-4" />,
          label: 'Draft'
        };
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 48) return 'Yesterday';
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const handleAdClick = (ad) => {
  if (ad.status.toLowerCase() === 'generated') {
      navigate(`/ads/${ad.run_id}/video`);
    } else if (ad.status.toLowerCase() === 'in_progress') {
      navigate(`/ads/${ad.run_id}/progress`);
    } else {
      navigate(`/ads/${ad.run_id}/progress`);
    }
  };

  const stats = {
    total: loading ? null : ads.length,
    inProgress: loading ? null : ads.filter(ad => ad.status.toLowerCase() === 'in_progress').length,
    completed: loading ? null : ads.filter(ad => ad.status.toLowerCase() === 'generated').length,
    failed: loading ? null : ads.filter(ad => ad.status.toLowerCase() === 'failed').length
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900">
      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,black,transparent)] pointer-events-none"></div>
      
      {/* Header */}
      <Header currentPage="My Video Ads" />
      
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
            <span className="text-indigo-400 font-bold flex items-center gap-2 bg-indigo-500/10 px-4 py-2 rounded-lg border border-indigo-500/30">
              <Video className="w-5 h-5" />
              My Video Ads
            </span>
          </nav>
        </div>
      </div>

      {/* Header */}
      <div className="relative bg-slate-800/50 border-b border-slate-700/50 sticky top-0 z-40 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        </div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fadeIn">
        {/* Stats Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <button
            onClick={() => handleStatusFilterChange('all')}
            disabled={loading}
            className={`group relative p-5 rounded-xl border transition-all duration-300 text-left ${
              statusFilter === 'all'
                ? 'bg-indigo-500/20 border-indigo-500/50 shadow-lg shadow-indigo-500/20 scale-105'
                : 'bg-slate-800/50 border-slate-700/50 hover:border-indigo-500/30 hover:bg-slate-800/80 backdrop-blur-xl hover:scale-102'
            } ${loading ? 'cursor-wait' : 'cursor-pointer'}`}
          >
            <div className="flex flex-col">
              <div className="flex items-center justify-between mb-3">
                <div className={`p-2 rounded-lg transition-colors ${
                  statusFilter === 'all' 
                    ? 'bg-indigo-500/20' 
                    : 'bg-slate-700/50 group-hover:bg-indigo-500/10'
                }`}>
                  <Video className={`w-5 h-5 ${statusFilter === 'all' ? 'text-indigo-400' : 'text-slate-400 group-hover:text-indigo-400'}`} />
                </div>
                {stats.total === null ? (
                  <Loader className="w-8 h-8 animate-spin text-indigo-400" />
                ) : (
                  <span className={`text-3xl font-black transition-colors ${
                    statusFilter === 'all' ? 'text-indigo-400' : 'text-slate-100'
                  }`}>{stats.total}</span>
                )}
              </div>
              <p className={`text-sm font-semibold transition-colors ${
                statusFilter === 'all' ? 'text-indigo-300' : 'text-slate-400 group-hover:text-slate-300'
              }`}>Total Ads</p>
            </div>
          </button>

          <button
            onClick={() => handleStatusFilterChange('in_progress')}
            disabled={loading}
            className={`group relative p-5 rounded-xl border transition-all duration-300 text-left ${
              statusFilter === 'in_progress'
                ? 'bg-blue-500/20 border-blue-500/50 shadow-lg shadow-blue-500/20 scale-105'
                : 'bg-slate-800/50 border-slate-700/50 hover:border-blue-500/30 hover:bg-slate-800/80 backdrop-blur-xl hover:scale-102'
            } ${loading ? 'cursor-wait' : 'cursor-pointer'}`}
          >
            <div className="flex flex-col">
              <div className="flex items-center justify-between mb-3">
                <div className={`p-2 rounded-lg transition-colors ${
                  statusFilter === 'in_progress' 
                    ? 'bg-blue-500/20' 
                    : 'bg-slate-700/50 group-hover:bg-blue-500/10'
                }`}>
                  <Clock className={`w-5 h-5 ${statusFilter === 'in_progress' ? 'text-blue-400' : 'text-slate-400 group-hover:text-blue-400'}`} />
                </div>
                {stats.inProgress === null ? (
                  <Loader className="w-8 h-8 animate-spin text-blue-400" />
                ) : (
                  <span className={`text-3xl font-black transition-colors ${
                    statusFilter === 'in_progress' ? 'text-blue-400' : 'text-slate-100'
                  }`}>{stats.inProgress}</span>
                )}
              </div>
              <p className={`text-sm font-semibold transition-colors ${
                statusFilter === 'in_progress' ? 'text-blue-300' : 'text-slate-400 group-hover:text-slate-300'
              }`}>In Progress</p>
            </div>
          </button>

          <button
            onClick={() => handleStatusFilterChange('generated')}
            disabled={loading}
            className={`group relative p-5 rounded-xl border transition-all duration-300 text-left ${
              statusFilter === 'generated'
                ? 'bg-emerald-500/20 border-emerald-500/50 shadow-lg shadow-emerald-500/20 scale-105'
                : 'bg-slate-800/50 border-slate-700/50 hover:border-emerald-500/30 hover:bg-slate-800/80 backdrop-blur-xl hover:scale-102'
            } ${loading ? 'cursor-wait' : 'cursor-pointer'}`}
          >
            <div className="flex flex-col">
              <div className="flex items-center justify-between mb-3">
                <div className={`p-2 rounded-lg transition-colors ${
                  statusFilter === 'generated'
                    ? 'bg-emerald-500/20' 
                    : 'bg-slate-700/50 group-hover:bg-emerald-500/10'
                }`}>
                  <TrendingUp className={`w-5 h-5 ${statusFilter === 'generated' ? 'text-emerald-400' : 'text-slate-400 group-hover:text-emerald-400'}`} />
                </div>
                {stats.completed === null ? (
                  <Loader className="w-8 h-8 animate-spin text-emerald-400" />
                ) : (
                  <span className={`text-3xl font-black transition-colors ${
                    statusFilter === 'generated' ? 'text-emerald-400' : 'text-slate-100'
                  }`}>{stats.completed}</span>
                )}
              </div>
              <p className={`text-sm font-semibold transition-colors ${
                statusFilter === 'generated' ? 'text-emerald-300' : 'text-slate-400 group-hover:text-slate-300'
              }`}>Generated</p>
            </div>
          </button>

          <button
            onClick={() => handleStatusFilterChange('failed')}
            disabled={loading}
            className={`group relative p-5 rounded-xl border transition-all duration-300 text-left ${
              statusFilter === 'failed'
                ? 'bg-red-500/20 border-red-500/50 shadow-lg shadow-red-500/20 scale-105'
                : 'bg-slate-800/50 border-slate-700/50 hover:border-red-500/30 hover:bg-slate-800/80 backdrop-blur-xl hover:scale-102'
            } ${loading ? 'cursor-wait' : 'cursor-pointer'}`}
          >
            <div className="flex flex-col">
              <div className="flex items-center justify-between mb-3">
                <div className={`p-2 rounded-lg transition-colors ${
                  statusFilter === 'failed' 
                    ? 'bg-red-500/20' 
                    : 'bg-slate-700/50 group-hover:bg-red-500/10'
                }`}>
                  <XCircle className={`w-5 h-5 ${statusFilter === 'failed' ? 'text-red-400' : 'text-slate-400 group-hover:text-red-400'}`} />
                </div>
                {stats.failed === null ? (
                  <Loader className="w-8 h-8 animate-spin text-red-400" />
                ) : (
                  <span className={`text-3xl font-black transition-colors ${
                    statusFilter === 'failed' ? 'text-red-400' : 'text-slate-100'
                  }`}>{stats.failed}</span>
                )}
              </div>
              <p className={`text-sm font-semibold transition-colors ${
                statusFilter === 'failed' ? 'text-red-300' : 'text-slate-400 group-hover:text-slate-300'
              }`}>Failed</p>
            </div>
          </button>
        </div>

        {/* Search and Filters */}
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl shadow-lg p-4 mb-6 border border-slate-700/50 relative z-[100]">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search Bar */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search ads by name or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-slate-700/50 border border-slate-600 text-slate-100 placeholder-slate-400 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
              />
            </div>

            {/* Sort Dropdown */}
            <div className="relative sort-dropdown z-[9999]">
              <button
                onClick={() => setSortDropdownOpen(!sortDropdownOpen)}
                className="flex items-center justify-between gap-3 w-full pl-4 pr-4 py-3 bg-slate-700/50 border border-slate-600 text-slate-100 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all cursor-pointer hover:bg-slate-700/70 min-w-[140px]"
              >
                <span>
                  {sortBy === 'newest' ? 'Newest First' : 
                   sortBy === 'oldest' ? 'Oldest First' : 
                   'Name (A-Z)'}
                </span>
                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${sortDropdownOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {sortDropdownOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-slate-700 border border-slate-600 rounded-xl shadow-xl z-[9999] overflow-hidden">
                  <button
                    onClick={() => {
                      setSortBy('newest');
                      setSortDropdownOpen(false);
                    }}
                    className={`w-full px-4 py-3 text-left hover:bg-slate-600 transition-colors ${
                      sortBy === 'newest' ? 'bg-indigo-500/20 text-indigo-300' : 'text-slate-100'
                    }`}
                  >
                    Newest First
                  </button>
                  <button
                    onClick={() => {
                      setSortBy('oldest');
                      setSortDropdownOpen(false);
                    }}
                    className={`w-full px-4 py-3 text-left hover:bg-slate-600 transition-colors ${
                      sortBy === 'oldest' ? 'bg-indigo-500/20 text-indigo-300' : 'text-slate-100'
                    }`}
                  >
                    Oldest First
                  </button>
                  <button
                    onClick={() => {
                      setSortBy('name');
                      setSortDropdownOpen(false);
                    }}
                    className={`w-full px-4 py-3 text-left hover:bg-slate-600 transition-colors ${
                      sortBy === 'name' ? 'bg-indigo-500/20 text-indigo-300' : 'text-slate-100'
                    }`}
                  >
                    Name (A-Z)
                  </button>
                </div>
              )}
            </div>
            
            {/* View Toggle */}
            <div className="flex items-center gap-2 bg-slate-700/50 p-1 rounded-lg border border-slate-600/50">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-md transition-all ${
                  viewMode === 'grid'
                    ? 'bg-indigo-500/20 text-indigo-400 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Grid View"
              >
                <Grid3x3 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-md transition-all ${
                  viewMode === 'list'
                    ? 'bg-indigo-500/20 text-indigo-400 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="List View"
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Active Filters */}
          {(statusFilter !== 'all' || searchQuery) && (
            <div className="mt-4 pt-4 border-t border-slate-700 flex items-center gap-2 flex-wrap">
              <span className="text-sm font-semibold text-slate-300">Active Filters:</span>
              {statusFilter !== 'all' && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full text-sm font-medium">
                  Status: {statusFilter.replace('_', ' ')}
                  <button
                    onClick={() => handleStatusFilterChange('all')}
                    className="ml-1 hover:bg-indigo-500/30 rounded-full p-0.5"
                  >
                    ×
                  </button>
                </span>
              )}
              {searchQuery && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full text-sm font-medium">
                  Search: "{searchQuery}"
                  <button
                    onClick={() => setSearchQuery('')}
                    className="ml-1 hover:bg-indigo-500/30 rounded-full p-0.5"
                  >
                    ×
                  </button>
                </span>
              )}
              <button
                onClick={() => {
                  setSearchQuery('');
                  handleStatusFilterChange('all');
                }}
                className="text-sm text-cyan-400 hover:text-cyan-300 font-medium"
              >
                Clear All
              </button>
            </div>
          )}
        </div>

        {/* Ads Grid/List */}
        {loading ? (
          <div className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'space-y-4'
          }>
            {viewMode === 'grid' ? (
              <>
                <SkeletonCard />
                <SkeletonCard />
                <SkeletonCard />
                <SkeletonCard />
                <SkeletonCard />
                <SkeletonCard />
              </>
            ) : (
              <>
                <SkeletonListItem />
                <SkeletonListItem />
                <SkeletonListItem />
                <SkeletonListItem />
                <SkeletonListItem />
                <SkeletonListItem />
              </>
            )}
          </div>
        ) : filteredAds.length === 0 ? (
          <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl shadow-lg p-12 text-center border border-slate-700/50">
            <div className="w-20 h-20 bg-gradient-to-br from-purple-100 to-pink-100 rounded-3xl flex items-center justify-center mx-auto mb-4">
              <Video className="w-10 h-10 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              {searchQuery || statusFilter !== 'all' ? 'No ads found' : 'No ads yet'}
            </h3>
            <p className="text-gray-600 mb-6">
              {searchQuery || statusFilter !== 'all'
                ? 'Try adjusting your filters or search terms'
                : 'Create your first AI-powered video ad to get started'}
            </p>
            <Link
              to="/ads/new"
              className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-700 hover:to-cyan-600 text-white font-bold py-3 px-8 rounded-xl transition-all shadow-lg shadow-indigo-500/50 hover:shadow-xl hover:shadow-cyan-500/50"
            >
              <Sparkles className="w-5 h-5" />
              Create Your First Ad
            </Link>
          </div>
        ) : (
          <div
            className={
              viewMode === 'grid'
                ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
                : 'space-y-4'
            }
          >
            {filteredAds.map((ad) => {
              const badge = getStatusBadge(ad.status);

              if (viewMode === 'list') {
                return (
                  <button
                    key={ad.run_id}
                    onClick={() => handleAdClick(ad)}
                    className="w-full bg-slate-800/50 backdrop-blur-xl rounded-xl shadow-lg hover:shadow-2xl border border-slate-700/50 p-6 transition-all hover:scale-[1.02] text-left hover:border-indigo-500/50"
                  >
                    <div className="flex items-center gap-6">
                      <div className="flex-shrink-0 w-24 h-24 bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 rounded-xl flex items-center justify-center border border-indigo-500/30">
                        {ad.status.toLowerCase() === 'generated' ? (
                          <Play className="w-10 h-10 text-indigo-400" />
                        ) : (
                          <Video className="w-10 h-10 text-indigo-400" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4 mb-2">
                          <h3 className="text-lg font-bold text-slate-100 truncate">{ad.name}</h3>
                          <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border ${badge.bg} ${badge.text} flex-shrink-0`}>
                            {badge.icon}
                            {badge.label}
                          </span>
                        </div>
                        <p className="text-sm text-slate-400 line-clamp-2 mb-3">{ad.desc}</p>
                        <div className="flex items-center gap-4 text-xs text-slate-500">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {formatDate(ad.created_at)}
                          </span>
                          {ad.status.toLowerCase() === 'generated' && (
                            <span className="flex items-center gap-1 text-emerald-400 font-medium">
                              <Eye className="w-3 h-3" />
                              Ready to view
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </button>
                );
              }

              // Grid View
              return (
                <button
                  key={ad.run_id}
                  onClick={() => handleAdClick(ad)}
                  className="group bg-slate-800/50 backdrop-blur-xl rounded-2xl shadow-lg hover:shadow-2xl border border-slate-700/50 overflow-hidden transition-all hover:scale-105 text-left hover:border-indigo-500/50"
                >
                  {/* Thumbnail */}
                  <div className="relative h-48 bg-gradient-to-br from-indigo-500/20 via-cyan-500/20 to-indigo-500/20 flex items-center justify-center">
                    {ad.status.toLowerCase() === 'generated' ? (
                      <div className="relative">
                        <div className="w-20 h-20 bg-slate-700 rounded-full flex items-center justify-center shadow-lg shadow-indigo-500/50 group-hover:scale-110 transition-transform">
                          <Play className="w-10 h-10 text-indigo-400" />
                        </div>
                        <div className="absolute -top-1 -right-1 w-6 h-6 bg-emerald-500 rounded-full flex items-center justify-center">
                          <CheckCircle className="w-4 h-4 text-white" />
                        </div>
                      </div>
                    ) : ad.status.toLowerCase() === 'in_progress' ? (
                      <div className="relative">
                        <Loader className="w-12 h-12 text-indigo-400 animate-spin" />
                      </div>
                    ) : (
                      <Video className="w-12 h-12 text-indigo-400" />
                    )}
                    
                    {/* Status Badge */}
                    <div className="absolute top-3 right-3">
                      <span className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-bold border backdrop-blur-sm ${badge.bg} ${badge.text} shadow-md`}>
                        {badge.icon}
                        {badge.label}
                      </span>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-5">
                    <h3 className="text-lg font-bold text-slate-100 mb-2 truncate group-hover:text-indigo-400 transition-colors">
                      {ad.name}
                    </h3>
                    <p className="text-sm text-slate-400 line-clamp-2 mb-4">{ad.desc}</p>
                    
                    <div className="flex items-center justify-between pt-4 border-t border-slate-700">
                      <span className="flex items-center gap-1 text-xs text-slate-500">
                        <Calendar className="w-3 h-3" />
                        {formatDate(ad.created_at)}
                      </span>
                      {ad.status.toLowerCase() === 'generated' && (
                        <span className="flex items-center gap-1 text-xs text-emerald-400 font-semibold">
                          <Eye className="w-3 h-3" />
                          View Now
                        </span>
                      )}
                      {ad.status.toLowerCase() === 'in_progress' && (
                        <span className="flex items-center gap-1 text-xs text-blue-400 font-semibold">
                          <Clock className="w-3 h-3" />
                          Check Progress
                        </span>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
