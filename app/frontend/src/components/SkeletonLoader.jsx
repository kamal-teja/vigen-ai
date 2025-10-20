import React from 'react';

// Shimmer animation
const shimmer = "before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_2s_infinite] before:bg-gradient-to-r before:from-transparent before:via-slate-700/50 before:to-transparent";

export const SkeletonCard = () => (
  <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl shadow-lg border border-slate-700/50 overflow-hidden">
    <div className={`relative h-48 bg-slate-700/50 ${shimmer} overflow-hidden`} />
    <div className="p-5 space-y-3">
      <div className={`relative h-6 bg-slate-700/50 rounded w-3/4 ${shimmer} overflow-hidden`} />
      <div className={`relative h-4 bg-slate-700/50 rounded w-full ${shimmer} overflow-hidden`} />
      <div className={`relative h-4 bg-slate-700/50 rounded w-5/6 ${shimmer} overflow-hidden`} />
      <div className="flex items-center justify-between pt-4 border-t border-slate-700">
        <div className={`relative h-3 bg-slate-700/50 rounded w-20 ${shimmer} overflow-hidden`} />
        <div className={`relative h-3 bg-slate-700/50 rounded w-16 ${shimmer} overflow-hidden`} />
      </div>
    </div>
  </div>
);

export const SkeletonListItem = () => (
  <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl shadow-lg border border-slate-700/50 p-6">
    <div className="flex items-center gap-6">
      <div className={`relative flex-shrink-0 w-24 h-24 bg-slate-700/50 rounded-xl ${shimmer} overflow-hidden`} />
      <div className="flex-1 space-y-3">
        <div className={`relative h-6 bg-slate-700/50 rounded w-1/2 ${shimmer} overflow-hidden`} />
        <div className={`relative h-4 bg-slate-700/50 rounded w-full ${shimmer} overflow-hidden`} />
        <div className={`relative h-4 bg-slate-700/50 rounded w-3/4 ${shimmer} overflow-hidden`} />
        <div className="flex items-center gap-4">
          <div className={`relative h-3 bg-slate-700/50 rounded w-20 ${shimmer} overflow-hidden`} />
          <div className={`relative h-3 bg-slate-700/50 rounded w-24 ${shimmer} overflow-hidden`} />
        </div>
      </div>
    </div>
  </div>
);

export const SkeletonStatCard = () => (
  <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700/50 p-5">
    <div className="flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <div className={`relative w-10 h-10 bg-slate-700/50 rounded-lg ${shimmer} overflow-hidden`} />
        <div className={`relative h-8 w-12 bg-slate-700/50 rounded ${shimmer} overflow-hidden`} />
      </div>
      <div className={`relative h-4 bg-slate-700/50 rounded w-20 ${shimmer} overflow-hidden`} />
    </div>
  </div>
);

export const SkeletonDashboardStats = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <SkeletonStatCard />
    <SkeletonStatCard />
    <SkeletonStatCard />
    <SkeletonStatCard />
  </div>
);

export const SkeletonRecentAds = () => (
  <div className="space-y-4">
    {[1, 2, 3].map((i) => (
      <div key={i} className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700/50 p-4">
        <div className="flex items-center gap-4">
          <div className={`relative w-16 h-16 bg-slate-700/50 rounded-xl ${shimmer} overflow-hidden`} />
          <div className="flex-1 space-y-2">
            <div className={`relative h-5 bg-slate-700/50 rounded w-1/3 ${shimmer} overflow-hidden`} />
            <div className={`relative h-4 bg-slate-700/50 rounded w-2/3 ${shimmer} overflow-hidden`} />
          </div>
          <div className={`relative w-20 h-6 bg-slate-700/50 rounded-full ${shimmer} overflow-hidden`} />
        </div>
      </div>
    ))}
  </div>
);

export const SkeletonVideoPlayer = () => (
  <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl shadow-2xl p-6 border border-slate-700/50">
    <div className="mb-6 space-y-3">
      <div className={`relative h-7 bg-slate-700/50 rounded w-1/2 ${shimmer} overflow-hidden`} />
      <div className={`relative h-5 bg-slate-700/50 rounded w-full ${shimmer} overflow-hidden`} />
    </div>
    <div className={`relative aspect-video bg-slate-700/50 rounded-xl ${shimmer} overflow-hidden mb-4`} />
    <div className="flex gap-3">
      <div className={`relative flex-1 h-12 bg-slate-700/50 rounded-xl ${shimmer} overflow-hidden`} />
      <div className={`relative w-12 h-12 bg-slate-700/50 rounded-xl ${shimmer} overflow-hidden`} />
    </div>
  </div>
);
