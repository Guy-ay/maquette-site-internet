'use client';

import React, { useState, useEffect, useRef } from 'react';

// ============================================================
// REACT BEST PRACTICE : JS-PASSIVE-LISTENERS & RAF-THROTTLING
// Règle 7 : Écouteur passif + requestAnimationFrame pour un scroll 60/120 FPS
// ============================================================

export interface ArticleReadingViewProps {
  children: React.ReactNode;
}

export function ArticleReadingView({ children }: ArticleReadingViewProps) {
  const [readingProgress, setReadingProgress] = useState(0);
  const [fontSize, setFontSize] = useState(16);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const toastTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const articleRef = useRef<HTMLDivElement>(null);

  // Barre de progression de lecture optimisée rAF
  useEffect(() => {
    let ticking = false;

    const handleScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          if (articleRef.current) {
            const rect = articleRef.current.getBoundingClientRect();
            const total = articleRef.current.offsetHeight - window.innerHeight;
            if (total > 0) {
              const current = -rect.top;
              const percent = Math.min(100, Math.max(0, (current / total) * 100));
              setReadingProgress(percent);
            }
          }
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    if (toastTimeoutRef.current) clearTimeout(toastTimeoutRef.current);
    toastTimeoutRef.current = setTimeout(() => {
      setToastMessage(null);
    }, 3000);
  };

  const copyLink = () => {
    if (typeof window !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      showToast('Lien copié dans le presse-papier !');
    }
  };

  return (
    <div ref={articleRef} className="relative">
      {/* Barre de progression fixe */}
      <div
        className="fixed top-0 left-0 h-1 bg-orange-600 z-50 transition-all duration-75 pointer-events-none"
        style={{ width: `${readingProgress}%` }}
        aria-hidden="true"
      />

      {/* Barre d'outils de confort & partage */}
      <div className="my-6 p-3 bg-neutral-50 border border-neutral-200/80 rounded-xl flex items-center justify-between gap-4 flex-wrap text-xs">
        <div className="flex items-center gap-2">
          <span className="font-bold text-neutral-500 uppercase tracking-wider text-[11px]">
            Taille du texte :
          </span>
          <button
            type="button"
            onClick={() => setFontSize((s) => Math.max(14, s - 1))}
            className="w-7 h-7 rounded border border-neutral-200 bg-white font-bold hover:border-orange-500 hover:text-orange-600"
            title="Réduire la police"
          >
            A-
          </button>
          <button
            type="button"
            onClick={() => setFontSize((s) => Math.min(22, s + 1))}
            className="w-7 h-7 rounded border border-neutral-200 bg-white font-bold hover:border-orange-500 hover:text-orange-600"
            title="Agrandir la police"
          >
            A+
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={copyLink}
            className="px-3 py-1.5 rounded-lg border border-neutral-200 bg-white font-semibold text-neutral-700 hover:border-orange-500 hover:text-orange-600 flex items-center gap-1.5 transition-colors"
          >
            <span>🔗 Copier le lien</span>
          </button>
          <button
            type="button"
            onClick={() => window.print()}
            className="px-3 py-1.5 rounded-lg border border-neutral-200 bg-white font-semibold text-neutral-700 hover:border-orange-500 hover:text-orange-600 flex items-center gap-1.5 transition-colors"
          >
            <span>🖨️ Imprimer</span>
          </button>
        </div>
      </div>

      {/* Contenu avec fontSize dynamique */}
      <div style={{ fontSize: `${fontSize}px` }} className="article-dynamic-body">
        {children}
      </div>

      {/* Toast Notification (Sonner-style) */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-neutral-900 text-white px-4 py-2.5 rounded-xl shadow-2xl border border-neutral-800 text-xs font-semibold flex items-center gap-2 animate-bounce">
          <span className="text-emerald-400">✓</span>
          <span>{toastMessage}</span>
        </div>
      )}
    </div>
  );
}

