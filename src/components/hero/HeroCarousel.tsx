'use client';

import React, { useState, useEffect, useRef } from 'react';
import type { ArticleItem } from '@/types';

// ============================================================
// REACT BEST PRACTICE : RERENDER-MOVE-STATE-DOWN
// Règle 5.1 : L'état d'index du carrousel et son intervalle sont confinés
// dans ce composant feuille, évitant de re-rendre la page d'accueil entière.
// ============================================================

export interface HeroCarouselProps {
  slides: ArticleItem[];
  autoPlayIntervalMs?: number;
}

export function HeroCarousel({ slides, autoPlayIntervalMs = 6000 }: HeroCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const touchStartX = useRef<number | null>(null);

  useEffect(() => {
    if (isPaused || slides.length <= 1) return;

    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % slides.length);
    }, autoPlayIntervalMs);

    return () => clearInterval(timer);
  }, [isPaused, slides.length, autoPlayIntervalMs]);

  const currentSlide = slides[currentIndex];
  if (!currentSlide) return null;

  return (
    <div
      className="relative rounded-3xl overflow-hidden bg-neutral-900 border border-neutral-800 shadow-xl aspect-[16/9] md:aspect-[21/9]"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
      onTouchStart={(e) => {
        touchStartX.current = e.touches[0].clientX;
        setIsPaused(true);
      }}
      onTouchEnd={(e) => {
        if (touchStartX.current !== null) {
          const deltaX = e.changedTouches[0].clientX - touchStartX.current;
          if (deltaX > 50) {
            setCurrentIndex((prev) => (prev - 1 + slides.length) % slides.length);
          } else if (deltaX < -50) {
            setCurrentIndex((prev) => (prev + 1) % slides.length);
          }
        }
        setIsPaused(false);
      }}
    >
      {/* Image de fond avec transition douce */}
      <img
        src={currentSlide.coverImage}
        alt={currentSlide.title}
        fetchPriority="high"
        decoding="async"
        className="absolute inset-0 w-full h-full object-cover transition-opacity duration-700 ease-in-out"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-black/10" />

      {/* Contenu textuel */}
      <div className="absolute bottom-0 left-0 right-0 p-6 md:p-10 text-white space-y-3">
        <span className="inline-block px-3 py-1 text-xs font-bold uppercase tracking-wider rounded-full bg-orange-600 text-white shadow-md">
          {currentSlide.categoryLabel}
        </span>
        <h2 className="text-xl md:text-3xl font-extrabold line-clamp-2 leading-tight">
          {currentSlide.title}
        </h2>
        <p className="text-xs md:text-sm text-neutral-300 line-clamp-2 max-w-2xl">
          {currentSlide.excerpt}
        </p>
        <div className="pt-2">
          <a
            href={`/actualites/${currentSlide.slug}`}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-orange-600 hover:bg-orange-700 text-white font-bold text-xs shadow-lg transition-all active:scale-95"
          >
            <span>Lire le dossier</span>
            <span aria-hidden="true">→</span>
          </a>
        </div>
      </div>

      {/* Indicateurs (dots) */}
      <div className="absolute bottom-6 right-6 flex items-center gap-2 z-10">
        {slides.map((_, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => setCurrentIndex(idx)}
            aria-label={`Aller au slide ${idx + 1}`}
            className={`h-2 rounded-full transition-all ${
              idx === currentIndex ? 'w-6 bg-orange-500' : 'w-2 bg-white/40 hover:bg-white/80'
            }`}
          />
        ))}
      </div>
    </div>
  );
}

