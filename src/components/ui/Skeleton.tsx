import React from 'react';

// ============================================================
// REACT BEST PRACTICE : SKELETON POUR SUSPENSE BOUNDARIES
// Règle: async-suspense-boundaries
// ============================================================

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={`animate-pulse bg-neutral-200/80 rounded-lg ${className || ''}`}
      aria-hidden="true"
    />
  );
}

export function ArticleCardSkeleton() {
  return (
    <div className="bg-white border border-neutral-200 rounded-2xl p-2 space-y-3">
      <Skeleton className="w-full h-48 rounded-xl" />
      <div className="p-3 space-y-2">
        <Skeleton className="w-24 h-4" />
        <Skeleton className="w-full h-6" />
        <Skeleton className="w-3/4 h-6" />
        <Skeleton className="w-1/2 h-4 mt-2" />
      </div>
    </div>
  );
}

export function ArticleGridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, idx) => (
        <ArticleCardSkeleton key={idx} />
      ))}
    </div>
  );
}

