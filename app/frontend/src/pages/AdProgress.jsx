import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { adService } from '../services/adService';
import Header from '../components/Header';
import {
  CheckCircle,
  Loader,
  XCircle,
  Sparkles,
  FileText,
  MessageSquare,
  Video,
  Music,
  Scissors,
  Home,
  ChevronRight,
  Clock
} from 'lucide-react';

export default function AdProgress() {
  const { runId } = useParams();
  const navigate = useNavigate();
  const [ad, setAd] = useState(null);
  const [crewStatus, setCrewStatus] = useState(null);
  const [progressStep, setProgressStep] = useState(-1);  // Start with -1 to show 0% initially
  const [isStepActive, setIsStepActive] = useState(false);
  const [polling, setPolling] = useState(true);
  const [error, setError] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  const progressSteps = [
    { 
      id: 1, 
      name: 'Script Generation', 
      icon: FileText, 
      description: 'AI is writing your compelling ad script',
      statusKey: 'script_generation_status',
      color: 'purple'
    },
    { 
      id: 2, 
      name: 'Script Review', 
      icon: MessageSquare, 
      description: 'Reviewing and optimizing the script',
      statusKey: 'script_evaluation_status',
      color: 'blue'
    },
    { 
      id: 3, 
      name: 'Video Creation', 
      icon: Video, 
      description: 'Generating stunning video content',
      statusKey: 'video_generation_status',
      color: 'pink'
    },
    { 
      id: 4, 
      name: 'Audio Production', 
      icon: Music, 
      description: 'Creating voiceover and background music',
      statusKey: 'audio_generation_status',
      color: 'green'
    },
    { 
      id: 5, 
      name: 'Final Editing', 
      icon: Scissors, 
      description: 'Your video is complete and ready!',
      statusKey: 'editing_status',
      color: 'orange'
    }
  ];

  useEffect(() => {
    loadAdDetails();
    startPolling();

    return () => {
      // Cleanup polling on unmount
      if (window.pollInterval) {
        clearInterval(window.pollInterval);
      }
    };
  }, [runId]);

  const loadAdDetails = async () => {
    try {
      const adData = await adService.getAd(runId);
      setAd(adData);
    } catch (err) {
      console.error('Failed to load ad details', err);
      setError('Failed to load advertisement details.');
    }
  };

  const startPolling = () => {
    // Initial check
    checkStatus();

    // Poll every 5 seconds
    window.pollInterval = setInterval(() => {
      checkStatus();
    }, 5000);
  };

  const checkStatus = async () => {
    try {
      const statusResult = await adService.getAdStatus(runId);
      const crewStatusData = statusResult.crew_status;
      
      // Only update progress if we have valid crew status data
      if (!crewStatusData) {
        // Keep the initial state (-1) if no data is available yet
        return;
      }

      setCrewStatus(crewStatusData);

      // Calculate current progress step
      let currentStep = 0;
      let isCurrentStepActive = false;
      
      const statusData = [
        { status: crewStatusData.script_generation_status, isCompleted: crewStatusData.script_generation_status === "COMPLETED" },
        { status: crewStatusData.script_evaluation_status, isCompleted: crewStatusData.script_evaluation_status === "COMPLETED" },
        { status: crewStatusData.video_generation_status, isCompleted: crewStatusData.video_generation_status === "COMPLETED" },
        { status: crewStatusData.audio_generation_status, isCompleted: crewStatusData.audio_generation_status === "COMPLETED" },
        { 
          status: crewStatusData.editing_status, 
          isCompleted: crewStatusData.editing_status === "COMPLETED" && crewStatusData.final_video_uri != null 
        }
      ];

      // Check if any status actually has a value (not null/undefined)
      const hasAnyStatusValue = statusData.some(item => 
        item.status && item.status !== null && item.status !== undefined
      );

      // If no status values exist yet, don't update progress (keep at -1)
      if (!hasAnyStatusValue) {
        return;
      }

      // Find the current step
      let hasAnyProgress = false;
      for (let i = 0; i < statusData.length; i++) {
        if (statusData[i].isCompleted) {
          currentStep = i;
          hasAnyProgress = true;
        } else if (statusData[i].status === "IN_PROGRESS" || statusData[i].status === "RUNNING") {
          currentStep = i;
          isCurrentStepActive = true;
          hasAnyProgress = true;
          break;
        } else {
          break;
        }
      }

      // If no progress has been made, set to -1 to indicate 0% progress
      if (!hasAnyProgress) {
        currentStep = -1;
        isCurrentStepActive = false;
      }

      setProgressStep(currentStep);
      setIsStepActive(isCurrentStepActive);

      // Check if any step failed
      const hasFailed = [
        crewStatusData.script_generation_status === "FAILED",
        crewStatusData.script_evaluation_status === "FAILED",
        crewStatusData.video_generation_status === "FAILED",
        crewStatusData.audio_generation_status === "FAILED",
        crewStatusData.editing_status === "FAILED"
      ].some(failed => failed);

      if (hasFailed) {
        clearInterval(window.pollInterval);
        setPolling(false);
        setError('Video generation failed. One or more steps encountered an error.');
        
        // Update ad status to failed
        try {
          await adService.updateAd(runId, { status: 'FAILED' });
        } catch (updateErr) {
          console.error('Failed to update ad status:', updateErr);
        }
        return;
      }

      // Check if all steps completed
      const allCompleted = (
        crewStatusData.script_generation_status === "COMPLETED" &&
        crewStatusData.script_evaluation_status === "COMPLETED" &&
        crewStatusData.video_generation_status === "COMPLETED" &&
        crewStatusData.audio_generation_status === "COMPLETED" &&
        crewStatusData.editing_status === "COMPLETED" &&
        crewStatusData.final_video_uri != null
      );
      
      if (allCompleted) {
        clearInterval(window.pollInterval);
        setPolling(false);
        
  // Update ad status to GENERATED with video URL
          try {
          await adService.updateAd(runId, {
            status: 'GENERATED',
            final_video_uri: crewStatusData.final_video_uri
          });
          
          setIsComplete(true);
          
          // Show success message briefly, then redirect to video detail page
          setTimeout(() => {
            navigate(`/ads/${runId}/video`);
          }, 2500); // 2.5 second delay for visual feedback
        } catch (err) {
          console.error('Failed to complete ad:', err);
          setError('Video generation completed but failed to update status. Please refresh the page.');
        }
      }
    } catch (err) {
      console.error('Status check failed', err);
      setError('Failed to check generation status. Please refresh the page.');
    }
  };

  const getStepStatus = (step) => {
    if (!crewStatus) {
      return 'pending';
    }

    const status = crewStatus[step.statusKey];

    // Special handling for final step (Final Editing)
    if (step.id === 5) {
      // Final Editing is completed only when both editing is done AND final video is available
      if (status === 'COMPLETED' && crewStatus.final_video_uri) return 'completed';
      // Final Editing is active if editing is in progress OR if all previous steps are done
      if (status === 'IN_PROGRESS' || status === 'STARTED' || status === 'RUNNING') return 'active';
      if (status === 'FAILED') return 'failed';
      
      // Check if this step should be active based on previous steps being completed
      const allPreviousCompleted = 
        crewStatus.script_generation_status === 'COMPLETED' &&
        crewStatus.script_evaluation_status === 'COMPLETED' &&
        crewStatus.video_generation_status === 'COMPLETED' &&
        crewStatus.audio_generation_status === 'COMPLETED';
      return allPreviousCompleted ? 'active' : 'pending';
    }
    
    // Check if this step is completed
    if (status === 'COMPLETED') return 'completed';
    
    // Check if this step is currently running
    if (status === 'IN_PROGRESS' || status === 'STARTED' || status === 'RUNNING') return 'active';
    
    // Check if this step has failed
    if (status === 'FAILED') return 'failed';
    
    // Check if this step should be active based on previous steps being completed
    if (step.id === 1) {
      // First step is active if not completed and no status yet
      return !status || status === 'PENDING' ? 'active' : 'pending';
    }
    
    // For other steps, check if the previous step is completed
    const prevStep = progressSteps[step.id - 2]; // id is 1-based, array is 0-based
    if (prevStep) {
      const prevStatus = crewStatus[prevStep.statusKey];
      if (prevStatus === 'COMPLETED' && (!status || status === 'PENDING')) {
        return 'active';
      }
    }
    
    return 'pending';
  };

  const getColorClasses = (color, status) => {
    const colors = {
      purple: {
        bg: 'bg-purple-500',
        text: 'text-purple-600',
        light: 'bg-purple-100',
        ring: 'ring-purple-200'
      },
      blue: {
        bg: 'bg-blue-500',
        text: 'text-blue-600',
        light: 'bg-blue-100',
        ring: 'ring-blue-200'
      },
      pink: {
        bg: 'bg-pink-500',
        text: 'text-pink-600',
        light: 'bg-pink-100',
        ring: 'ring-pink-200'
      },
      green: {
        bg: 'bg-green-500',
        text: 'text-green-600',
        light: 'bg-green-100',
        ring: 'ring-green-200'
      },
      orange: {
        bg: 'bg-orange-500',
        text: 'text-orange-600',
        light: 'bg-orange-100',
        ring: 'ring-orange-200'
      },
      emerald: {
        bg: 'bg-emerald-500',
        text: 'text-emerald-600',
        light: 'bg-emerald-100',
        ring: 'ring-emerald-200'
      }
    };

    return colors[color] || colors.purple;
  };

  if (error && !isComplete) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 py-8">
        {/* Grid pattern overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)] pointer-events-none"></div>
        
        <div className="relative max-w-4xl mx-auto px-4">
          <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl shadow-2xl p-8 text-center border border-slate-700/50">
            <div className="w-12 h-12 bg-red-500/20 rounded-xl flex items-center justify-center mx-auto mb-6 border border-red-500/30">
              <XCircle className="w-6 h-6 text-red-400" />
            </div>
            <h1 className="text-3xl font-bold text-slate-100 mb-4">Generation Failed</h1>
            <p className="text-slate-400 mb-8 max-w-md mx-auto">{error}</p>
            <div className="flex gap-4 justify-center flex-wrap">
              <button
                onClick={() => window.location.reload()}
                className="bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-700 hover:to-cyan-600 text-white font-bold py-3 px-8 rounded-xl transition-all shadow-lg shadow-indigo-500/50"
              >
                Retry
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

  // Success view - show briefly before redirecting
  if (isComplete) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 flex items-center justify-center">
        {/* Grid pattern overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)] pointer-events-none"></div>
        
        <div className="relative text-center px-4">
          {/* Success Icon */}
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-full shadow-xl shadow-emerald-500/50 mb-6 animate-bounce">
            <CheckCircle className="w-8 h-8 text-white" />
          </div>
          
          {/* Success Message */}
          <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent mb-4 animate-pulse">
            🎉 Video Successfully Generated!
          </h1>
          <p className="text-xl text-slate-300 mb-2">
            Your ad for <span className="font-bold text-cyan-400">{ad?.name}</span> is ready
          </p>
          <p className="text-lg text-slate-400 flex items-center justify-center gap-2">
            <Sparkles className="w-5 h-5 text-cyan-400 animate-spin" />
            Redirecting to video player...
          </p>
        </div>
      </div>
    );
  }

  // Progress wizard view
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900">
      <Header currentPage="Video Progress" />
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
              <Clock className="w-5 h-5" />
              Progress
            </span>
          </nav>
        </div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fadeIn">

        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-indigo-600 to-cyan-500 rounded-xl shadow-lg shadow-indigo-500/50 mb-4">
            <Sparkles className="w-6 h-6 text-white animate-pulse" />
          </div>
          <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400 mb-3 font-['Space_Grotesk']">
            Creating Your Video Ad
          </h1>
          <p className="text-lg text-slate-300">
            AI is working its magic on <span className="font-bold text-indigo-400">{ad?.name}</span>
          </p>
        </div>

        {/* Horizontal Progress Steps */}
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl shadow-2xl p-8 md:p-12 mb-8 border border-slate-700/50">
          {/* Progress Bar */}
          <div className="mb-12">
            <div className="relative px-6">
              {/* Container for steps */}
              <div className="flex items-center justify-between relative">
                {/* Background progress line - connects between step circles */}
                <div className="absolute top-6 h-1 bg-slate-700 rounded-full" style={{ left: '24px', right: '24px', zIndex: 0 }}></div>
                
                {/* Animated progress line */}
                <div 
                  className="absolute top-6 h-1 bg-gradient-to-r from-indigo-500 to-cyan-500 rounded-full transition-all duration-1000 ease-out shadow-lg shadow-indigo-500/50"
                  style={{ 
                    left: '24px',
                    width: progressStep < 0 ? '0%' : 
                           progressStep >= progressSteps.length - 1 && !isStepActive ? 'calc(100% - 48px)' :
                           isStepActive ? 
                             `calc((100% - 48px) * ${progressStep} / ${progressSteps.length - 1})` :
                             `calc((100% - 48px) * ${progressStep + 1} / ${progressSteps.length - 1})`,
                    zIndex: 1
                  }}
                ></div>

              {/* Step circles */}
              {progressSteps.map((step, index) => {
                const status = getStepStatus(step);
                const StepIcon = step.icon;
                const isActive = status === 'active';
                const isCompleted = status === 'completed';
                const isFailed = status === 'failed';
                
                // Debug logging
                if (process.env.NODE_ENV === 'development') {
                  console.log(`Step ${step.id} (${step.name}):`, {
                    statusKey: step.statusKey,
                    crewStatusValue: crewStatus?.[step.statusKey],
                    calculatedStatus: status,
                    isActive,
                    isCompleted,
                    isFailed
                  });
                }

                return (
                  <div key={step.id} className="flex flex-col items-center relative" style={{ zIndex: 2 }}>
                    {/* Circle with animated ring for active state */}
                    <div className="relative">
                      {/* Animated spinning ring for active state */}
                      {isActive && (
                        <>
                          {/* Outer rotating ring */}
                          <div className="absolute inset-0 -m-2 w-16 h-16 rounded-full border-4 border-transparent border-t-cyan-400 border-r-indigo-400 animate-spin"></div>
                          {/* Pulsing glow */}
                          <div className="absolute inset-0 -m-1 w-14 h-14 rounded-full bg-gradient-to-br from-indigo-500/30 to-cyan-500/30 animate-pulse"></div>
                        </>
                      )}
                      
                      {/* Main circle */}
                      <div
                        className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-500 transform relative ${
                          isCompleted
                            ? 'bg-gradient-to-br from-emerald-500 to-teal-500 scale-110 shadow-xl shadow-emerald-500/50'
                            : isActive
                            ? 'bg-gradient-to-br from-indigo-500 to-cyan-500 scale-110 shadow-xl shadow-indigo-500/50'
                            : isFailed
                            ? 'bg-gradient-to-br from-red-500 to-pink-500 scale-110'
                            : 'bg-slate-700 scale-100 border-2 border-slate-600'
                        }`}
                      >
                        {isFailed ? (
                          <XCircle className="w-6 h-6 text-white" />
                        ) : (
                          <StepIcon className={`w-6 h-6 ${
                            isCompleted ? 'text-white' :
                            isActive ? 'text-white animate-pulse' : 
                            'text-slate-400'
                          }`} />
                        )}
                      </div>
                    </div>

                    {/* Label */}
                    <div className="mt-4 text-center min-w-[100px] max-w-[120px]">
                      <p className={`text-xs font-bold mb-1 transition-colors ${
                        isCompleted ? 'text-emerald-400' :
                        isActive ? 'text-indigo-400' :
                        isFailed ? 'text-red-400' :
                        'text-slate-500'
                      }`}>
                        {step.name}
                      </p>
                      {isActive && (
                        <p className="text-xs text-cyan-400 animate-pulse font-semibold">
                          Running...
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
              </div>
            </div>
          </div>

          {/* Current Step Details */}
          <div className="bg-slate-900/50 rounded-2xl p-6 border border-slate-700/50">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/50">
                {progressStep >= 0 && progressSteps[progressStep] && React.createElement(progressSteps[progressStep].icon, { className: "w-6 h-6 text-white" })}
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-slate-100">
                  {progressStep >= 0 ? (progressSteps[progressStep]?.name || 'Running...') : 'Getting Ready...'}
                </h3>
                <p className="text-sm text-slate-400">
                  {progressStep >= 0 ? (progressSteps[progressStep]?.description || 'AI is working...') : 'Preparing to start video generation...'}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Loader className="w-5 h-5 text-indigo-400 animate-spin" />
                <span className="text-sm font-semibold text-slate-300">
                  Step {progressStep >= 0 ? progressStep + 1 : 1} of {progressSteps.length}
                </span>
              </div>
            </div>

            {/* Progress percentage */}
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-slate-400">Overall Progress</span>
                <span className="text-sm font-bold text-indigo-400">
                  {progressStep < 0 ? 0 :
                   isStepActive ? 
                    Math.round(((progressStep + 0.5) / progressSteps.length) * 100) :
                    Math.round(((progressStep + 1) / progressSteps.length) * 100)
                  }%
                </span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-cyan-500 h-2 rounded-full transition-all duration-1000 ease-out shadow-lg shadow-indigo-500/30"
                  style={{ 
                    width: `${progressStep < 0 ? 0 :
                      isStepActive ? 
                        ((progressStep + 0.5) / progressSteps.length) * 100 :
                        ((progressStep + 1) / progressSteps.length) * 100
                    }%` 
                  }}
                ></div>
              </div>
            </div>
          </div>

          {/* Ad Details */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-900/30 rounded-xl p-4 border border-slate-700/30">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Product Name</p>
              <p className="text-slate-200 font-medium">{ad?.name}</p>
            </div>
            <div className="bg-slate-900/30 rounded-xl p-4 border border-slate-700/30">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Description</p>
              <p className="text-slate-200 font-medium truncate">{ad?.desc}</p>
            </div>
          </div>

          {/* Info Text */}
          <div className="mt-6 text-center">
            <p className="text-sm text-slate-400 flex items-center justify-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              This usually takes 2-5 minutes. You can safely close this page and come back later.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
