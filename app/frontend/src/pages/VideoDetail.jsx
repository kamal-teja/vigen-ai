import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { adService } from '../services/adService';
import { SkeletonVideoPlayer } from '../components/SkeletonLoader';
import Header from '../components/Header';
import {
  Play,
  Download,
  Video,
  CheckCircle,
  XCircle,
  Loader,
  Clock,
  Zap,
  FileText,
  Music,
  Scissors,
  Film,
  ChevronRight,
  Home,
  PlayCircle,
  Calendar,
  Tag
} from 'lucide-react';

export default function VideoDetail() {
  const { runId } = useParams();
  const navigate = useNavigate();
  const [videoUrl, setVideoUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [videoLoading, setVideoLoading] = useState(false);
  const [videoLoadAttempted, setVideoLoadAttempted] = useState(false);
  const [error, setError] = useState('');
  const [ad, setAd] = useState(null);
  const [polling, setPolling] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  const [crewStatus, setCrewStatus] = useState(null);

  useEffect(() => {
    loadAdDetails();
  }, [runId]);

  useEffect(() => {
    if (ad) {
      console.log('Ad loaded:', ad); // Debug log
      console.log('Ad status:', ad.status); // Debug log
      
  if (ad.status === 'GENERATED') {
        loadVideo();
      } else if (ad.status === 'IN_PROGRESS') {
        startPolling();
      } else if (ad.status === 'FAILED') {
        setError('Video generation failed. Please try creating a new ad.');
        setLoading(false);
      } else {
        setLoading(false);
      }
    }
  }, [ad]);

  const loadVideo = async () => {
    try {
      setVideoLoading(true);
      setVideoLoadAttempted(true);
      // Call the backend S3 endpoint to get presigned URL
      const response = await adService.getVideoUrl(runId);
      setVideoUrl(response.video_url);
      setLoading(false);
      setVideoLoading(false);
    } catch (err) {
      console.error('Failed to load video URL', err);
      setError('Failed to load video. Please try again.');
      setLoading(false);
      setVideoLoading(false);
    }
  };

  const startPolling = () => {
    setPolling(true);
    setProgressStep(1);

    const pollInterval = setInterval(async () => {
      try {
        const statusResult = await adService.getAdStatus(runId);
        const crewStatusData = statusResult.crew_status;
        setCrewStatus(crewStatusData);

        // Calculate progress step based on crew status
        let calculatedProgressStep = 0;

        const steps = [
          crewStatusData?.script_generation_status === "COMPLETED",
          crewStatusData?.script_evaluation_status === "COMPLETED",
          crewStatusData?.video_generation_status === "COMPLETED",
          crewStatusData?.audio_generation_status === "COMPLETED",
          crewStatusData?.editing_status === "COMPLETED",
          crewStatusData?.final_video_uri != null
        ];

        for (let i = 0; i < steps.length; i++) {
          if (steps[i]) {
            calculatedProgressStep = i + 1;
          } else {
            break;
          }
        }

        setProgressStep(calculatedProgressStep || 1);

        // Check if completed or failed
        const hasFailed = [
          crewStatusData?.script_generation_status === "FAILED",
          crewStatusData?.script_evaluation_status === "FAILED",
          crewStatusData?.video_generation_status === "FAILED",
          crewStatusData?.audio_generation_status === "FAILED",
          crewStatusData?.editing_status === "FAILED"
        ].some(failed => failed);

        const isCompleted = steps.every(step => step);

        if (hasFailed || isCompleted) {
          clearInterval(pollInterval);
          setPolling(false);

          if (isCompleted && crewStatusData?.final_video_uri) {
            // Update the advertisement with generated status and video URL
              try {
              await adService.updateAd(runId, {
                status: 'GENERATED',
                final_video_uri: crewStatusData.final_video_uri
              });
              // Reload ad details to get updated status
              await loadAdDetails();
            } catch (updateErr) {
              console.error('Failed to update ad status:', updateErr);
              setError('Video generation completed but failed to update status. Please refresh the page.');
            }
          } else if (hasFailed) {
            // Update status to failed
            try {
              await adService.updateAd(runId, { status: 'FAILED' });
              setError('Video generation failed. Please try creating a new ad.');
            } catch (updateErr) {
              console.error('Failed to update ad status:', updateErr);
              setError('Video generation failed. Please try creating a new ad.');
            }
          }
        }
      } catch (err) {
        console.error('Status polling failed', err);
        clearInterval(pollInterval);
        setPolling(false);
        setError('Failed to check ad status. Please refresh the page.');
      }
    }, 5000); // Poll every 5 seconds
  };

  const loadAdDetails = async () => {
    try {
      const adData = await adService.getAd(runId);
      setAd(adData);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load ad details', err);
      setError('Failed to load ad details.');
      setLoading(false);
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 py-8">
        {/* Grid pattern overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)] pointer-events-none"></div>
        
        <div className="relative max-w-4xl mx-auto px-4">
          <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl shadow-2xl p-8 text-center border border-slate-700/50">
            <div className="w-20 h-20 bg-red-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-red-500/30">
              <XCircle className="w-10 h-10 text-red-400" />
            </div>
            <h1 className="text-3xl font-bold text-slate-100 mb-3">Video Generation Failed</h1>
            <p className="text-slate-400 mb-8 max-w-md mx-auto">{error}</p>
            <div className="flex gap-4 justify-center flex-wrap">
              <button
                onClick={() => window.location.reload()}
                className="bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-700 hover:to-cyan-600 text-white font-bold py-3 px-8 rounded-xl transition-all shadow-lg shadow-indigo-500/50"
              >
                Try Again
              </button>
              <button
                onClick={() => navigate('/ads/new')}
                className="bg-slate-700/50 hover:bg-slate-700 text-slate-200 font-bold py-3 px-8 rounded-xl transition-all border border-slate-600"
              >
                Create New Ad
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show progress wizard if ad is in progress
  if (ad && ad.status === 'IN_PROGRESS') {
    const progressSteps = [
      { id: 1, name: 'Script Generation', icon: FileText, description: 'Creating compelling ad script' },
      { id: 2, name: 'Script Evaluation', icon: CheckCircle, description: 'Reviewing and optimizing script' },
      { id: 3, name: 'Video Generation', icon: Film, description: 'Generating video content' },
      { id: 4, name: 'Audio Generation', icon: Music, description: 'Creating voiceover and music' },
      { id: 5, name: 'Video Editing', icon: Scissors, description: 'Final editing and polishing' },
      { id: 6, name: 'Final Processing', icon: Video, description: 'Preparing final video file' }
    ];

    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8">
        {/* Header */}
        <div className="max-w-6xl mx-auto px-4 mb-6">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 font-medium transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Dashboard
          </Link>
        </div>

        <div className="max-w-4xl mx-auto px-4">
          {/* Progress Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 rounded-2xl mb-4">
              <Zap className="w-8 h-8 text-purple-600 animate-pulse" />
            </div>
            <h1 className="text-3xl font-black text-gray-900 mb-2 font-['Space_Grotesk']">
              Creating Your Video Ad
            </h1>
            <p className="text-gray-600 flex items-center justify-center gap-2">
              <Clock className="w-4 h-4" />
              AI is working on {ad?.name || 'your advertisement'}
            </p>
          </div>

          {/* Progress Wizard */}
          <div className="bg-slate-800/40 backdrop-blur-xl rounded-3xl shadow-xl p-8 mb-8 border border-slate-700/40">
            <div className="space-y-6">
              {progressSteps.map((step, index) => {
                const isCompleted = progressStep > step.id;
                const isCurrent = progressStep === step.id;
                const isPending = progressStep < step.id;
                
                // Check if this specific step is currently running
                let isRunning = false;
                if (crewStatus) {
                  const stepStatusKeys = [
                    'script_generation_status',
                    'script_evaluation_status', 
                    'video_generation_status',
                    'audio_generation_status',
                    'editing_status'
                  ];
                  
                  if (step.id <= 5) {
                    const stepStatus = crewStatus[stepStatusKeys[step.id - 1]];
                    isRunning = stepStatus === 'IN_PROGRESS' || stepStatus === 'STARTED' || stepStatus === 'RUNNING';
                  } else if (step.id === 6) {
                    // Final step is running if all previous are completed but no final video yet
                    isRunning = !crewStatus.final_video_uri && 
                      crewStatus.editing_status === 'COMPLETED';
                  }
                }

                let statusColor = 'text-slate-300';
                let bgColor = 'bg-slate-900/10';
                let borderColor = 'border-slate-700/40';

                if (isCompleted) {
                  statusColor = 'text-emerald-400';
                  bgColor = 'bg-emerald-500/10';
                  borderColor = 'border-emerald-500/30';
                } else if (isCurrent || isRunning) {
                  statusColor = 'text-indigo-400';
                  bgColor = 'bg-indigo-500/10';
                  borderColor = 'border-indigo-500/30';
                }

                return (
                  <div key={step.id} className={`flex items-center gap-4 p-4 rounded-xl border-2 transition-all duration-300 ${borderColor} ${bgColor}`}>
                    {/* Circle with animated ring for current/running step */}
                    <div className="flex-shrink-0 relative">
                      {/* Animated spinning ring for current/running step */}
                      {(isCurrent || isRunning) && (
                        <>
                          {/* Outer rotating ring */}
                          <div className="absolute inset-0 -m-2 w-16 h-16 rounded-full border-4 border-transparent border-t-cyan-400 border-r-indigo-400 animate-spin"></div>
                          {/* Pulsing glow */}
                          <div className="absolute inset-0 -m-1 w-14 h-14 rounded-full bg-gradient-to-br from-indigo-500/30 to-cyan-500/30 animate-pulse"></div>
                        </>
                      )}
                      
                      {/* Main circle */}
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center relative ${
                        isCompleted 
                          ? 'bg-gradient-to-br from-emerald-500 to-teal-500 shadow-lg shadow-emerald-500/50' 
                          : (isCurrent || isRunning)
                          ? 'bg-gradient-to-br from-indigo-500 to-cyan-500 shadow-lg shadow-indigo-500/50' 
                          : 'bg-slate-700'
                      }`}>
                        <step.icon className={`w-6 h-6 ${
                          isCompleted ? 'text-white' :
                          (isCurrent || isRunning) ? 'text-white animate-pulse' : 
                          'text-slate-400'
                        }`} />
                      </div>
                    </div>
                    
                    <div className="flex-grow">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`font-bold ${statusColor}`}>
                          Step {step.id}: {step.name}
                        </span>
                        {(isCurrent || isRunning) && (
                          <span className="text-xs text-cyan-400 font-semibold animate-pulse">Processing...</span>
                        )}
                      </div>
                      <p className="text-sm text-slate-400">{step.description}</p>
                      {crewStatus && (
                        <div className="mt-2 text-xs text-slate-500">
                          {step.id === 1 && crewStatus.script_generation_status && (
                            <span>Status: {crewStatus.script_generation_status}</span>
                          )}
                          {step.id === 2 && crewStatus.script_evaluation_status && (
                            <span>Status: {crewStatus.script_evaluation_status}</span>
                          )}
                          {step.id === 3 && crewStatus.video_generation_status && (
                            <span>Status: {crewStatus.video_generation_status}</span>
                          )}
                          {step.id === 4 && crewStatus.audio_generation_status && (
                            <span>Status: {crewStatus.audio_generation_status}</span>
                          )}
                          {step.id === 5 && crewStatus.editing_status && (
                            <span>Status: {crewStatus.editing_status}</span>
                          )}
                          {step.id === 6 && crewStatus.final_video_uri && (
                            <span>Final video ready</span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Progress Summary */}
              <div className="mt-8 p-4 bg-slate-900/30 rounded-xl border border-slate-700/40">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-slate-300">Overall Progress</span>
                <span className="font-bold text-indigo-400">{Math.round((progressStep / 6) * 100)}%</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-cyan-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${(progressStep / 6) * 100}%` }}
                ></div>
              </div>
              <p className="text-sm text-slate-400 mt-2">
                {polling ? 'Generating your video... This may take a few minutes.' : 'Processing complete!'}
              </p>
            </div>
          </div>

          {/* Ad Details */}
              <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl shadow-xl p-8 border border-slate-700/50">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Ad Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <p className="text-sm font-semibold text-gray-500 mb-1">Product Name</p>
                <p className="text-gray-900">{ad?.name}</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-500 mb-1">Description</p>
                <p className="text-gray-900">{ad?.desc}</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-500 mb-1">Status</p>
                <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                  In Progress
                </span>
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-500 mb-1">Created</p>
                <p className="text-gray-900">{ad?.created_at ? new Date(ad.created_at).toLocaleDateString() : 'N/A'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900">
      <Header currentPage="Video Details" />
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
              <PlayCircle className="w-5 h-5" />
              Video Detail
            </span>
          </nav>
        </div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fadeIn">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Video Player - Takes 2 columns */}
          <div className="lg:col-span-2">
            <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl shadow-2xl p-6 border border-slate-700/50">
              {/* Video Title */}
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-slate-100 mb-2 flex items-center gap-3">
                  <Tag className="w-6 h-6 text-indigo-400" />
                  {loading || !ad ? (
                    <span className="relative inline-block h-8 w-64 bg-slate-700/50 rounded overflow-hidden">
                      <span className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-slate-600/50 to-transparent"></span>
                    </span>
                  ) : (
                    ad.name
                  )}
                </h2>
                {loading || !ad ? (
                  <div className="space-y-2">
                    <span className="relative block h-4 w-full bg-slate-700/50 rounded overflow-hidden">
                      <span className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-slate-600/50 to-transparent"></span>
                    </span>
                    <span className="relative block h-4 w-3/4 bg-slate-700/50 rounded overflow-hidden">
                      <span className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-slate-600/50 to-transparent"></span>
                    </span>
                  </div>
                ) : (
                  <p className="text-slate-400 leading-relaxed">{ad.desc}</p>
                )}
              </div>

              {/* Video Player */}
              <div className="aspect-video bg-slate-900 rounded-xl overflow-hidden shadow-2xl shadow-slate-950/50 border border-slate-700/50 mb-6">
                {videoLoading ? (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="text-center">
                      <Loader className="w-16 h-16 mx-auto mb-4 text-indigo-400 animate-spin" />
                      <p className="text-slate-400 text-lg">Loading video...</p>
                      <p className="text-slate-500 text-sm mt-2">Generating presigned URL</p>
                    </div>
                  </div>
                ) : videoUrl ? (
                  <video
                    controls
                    className="w-full h-full"
                    controlsList="nodownload"
                  >
                    <source src={videoUrl} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                ) : !videoLoadAttempted || loading ? (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="text-center">
                      <Video className="w-16 h-16 mx-auto mb-4 text-slate-400 opacity-50" />
                      <p className="text-slate-400 text-lg">Preparing video player...</p>
                      <p className="text-slate-500 text-sm mt-2">Please wait</p>
                    </div>
                  </div>
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="text-center text-slate-400">
                      <XCircle className="w-16 h-16 mx-auto mb-4 text-red-400 opacity-75" />
                      <p className="text-red-400">Video not available</p>
                      <p className="text-slate-500 text-sm mt-2">Failed to load video content</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => window.open(videoUrl, '_blank')}
                  disabled={videoLoading || !videoUrl}
                  className={`flex-1 min-w-[200px] flex items-center justify-center gap-2 ${
                    videoLoading || !videoUrl
                      ? 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-700 hover:to-cyan-600 text-white shadow-lg shadow-indigo-500/50 hover:shadow-xl hover:shadow-cyan-500/50 hover:scale-105'
                  } font-bold py-3 px-6 rounded-xl transition-all`}
                >
                  {videoLoading ? (
                    <Loader className="w-5 h-5 animate-spin" />
                  ) : (
                    <Download className="w-5 h-5" />
                  )}
                  Download Video
                </button>
                {/* Share removed: presigned URLs are temporary and not suitable for direct sharing */}
              </div>
            </div>
          </div>

          {/* Sidebar - Video Details */}
          <div className="lg:col-span-1 space-y-6">
            {/* Video Information Card */}
            <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl shadow-lg p-6 border border-slate-700/50">
              <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-400" />
                Video Information
              </h3>
              <div className="space-y-4">
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Status</p>
                  {loading || !ad ? (
                    <span className="relative inline-block h-7 w-32 bg-slate-700/50 rounded-full overflow-hidden">
                      <span className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-slate-600/50 to-transparent"></span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-full text-sm font-semibold">
                      <CheckCircle className="w-4 h-4" />
                      {ad.status?.replace('_', ' ').toUpperCase()}
                    </span>
                  )}
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Created On</p>
                  {loading || !ad ? (
                    <span className="relative block h-5 w-48 bg-slate-700/50 rounded overflow-hidden">
                      <span className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-slate-600/50 to-transparent"></span>
                    </span>
                  ) : (
                    <p className="text-slate-200 flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-slate-400" />
                      {ad.created_at ? new Date(ad.created_at).toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                      }) : 'N/A'}
                    </p>
                  )}
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Video ID</p>
                  {loading || !ad ? (
                    <span className="relative block h-4 w-full bg-slate-700/50 rounded overflow-hidden">
                      <span className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-slate-600/50 to-transparent"></span>
                    </span>
                  ) : (
                    <p className="text-slate-400 font-mono text-xs truncate">{runId}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Quick Actions Card */}
            <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl shadow-lg p-6 border border-slate-700/50">
              <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-cyan-400" />
                Quick Actions
              </h3>
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/ads/new')}
                  className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-semibold py-3 px-4 rounded-xl transition-all shadow-lg shadow-emerald-500/30"
                >
                  <Play className="w-5 h-5" />
                  Create Another Ad
                </button>
                <button
                  onClick={() => navigate('/ads')}
                  className="w-full flex items-center justify-center gap-2 bg-slate-700/50 hover:bg-slate-700 text-slate-200 font-semibold py-3 px-4 rounded-xl transition-all border border-slate-600"
                >
                  <Video className="w-5 h-5" />
                  View All Ads
                </button>
              </div>
            </div>

            {/* Stats Card */}
            <div className="bg-gradient-to-br from-indigo-500/10 to-cyan-500/10 backdrop-blur-xl rounded-2xl shadow-lg p-6 border border-indigo-500/30">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-cyan-500 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-500/50">
                  <Zap className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h4 className="font-bold text-slate-100">AI Powered</h4>
                  <p className="text-xs text-slate-400">Generated with Vigen AI</p>
                </div>
              </div>
              <p className="text-sm text-slate-300 leading-relaxed">
                This video was created using cutting-edge AI technology to deliver professional-quality results in minutes.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}