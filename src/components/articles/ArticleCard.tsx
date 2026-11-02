import React from 'react';
import type { ArticleItem } from '@/types';

// ============================================================
// REACT BEST PRACTICE : RENDERING-CONTENT-VISIBILITY & CLS
// Règles: rendering-content-visibility, aspect-ratio explicite, image lazy-loading
// ============================================================

export interface ArticleCardProps {
  article: ArticleItem;
  priority?: boolean;
}

export function ArticleCard({ article, priority = false }: ArticleCardProps) {
  return (
    <article
      className="group bg-white rounded-2xl border border-neutral-200/80 p-2 shadow-sm hover:shadow-md hover:border-orange-500/40 transition-all duration-200 flex flex-col h-full"
      style={{
        contentVisibility: 'auto',
        containIntrinsicSize: '0 420px',
      }}
    >
      <div className="relative overflow-hidden rounded-xl bg-neutral-100 aspect-[16/10]">
        <img
          src={article.coverImage}
          alt={article.title}
          loading={priority ? undefined : 'lazy'}
          fetchPriority={priority ? 'high' : 'auto'}
          decoding="async"
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <span className="absolute top-3 left-3 px-3 py-1 text-xs font-bold uppercase tracking-wider rounded-full bg-white/90 backdrop-blur-sm text-orange-600 shadow-sm">
          {article.categoryLabel}
        </span>
      </div>

      <div className="p-4 flex flex-col flex-grow">
        <div className="flex items-center gap-3 text-xs text-neutral-500 mb-2">
          <span>{article.publishedAt}</span>
          <span>•</span>
          <span>{article.readTimeMinutes} min de lecture</span>
        </div>

        <h3 className="text-base font-bold text-neutral-900 group-hover:text-orange-600 transition-colors line-clamp-2 mb-2">
          {article.title}
        </h3>

        <p className="text-xs text-neutral-600 line-clamp-3 mb-4 flex-grow">
          {article.excerpt}
        </p>

        <a
          href={`/actualites/${article.slug}`}
          className="inline-flex items-center gap-1.5 text-xs font-bold text-orange-600 hover:text-orange-700 mt-auto"
        >
          <span>Lire l'article</span>
          <span aria-hidden="true">→</span>
        </a>
      </div>
    </article>
  );
}

