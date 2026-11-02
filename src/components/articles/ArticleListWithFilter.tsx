'use client';

import React, { useState, useMemo } from 'react';
import type { ArticleItem, ArticleCategory } from '@/types';
import { ArticleCard } from './ArticleCard';

// ============================================================
// REACT BEST PRACTICE : RERENDER-DERIVED-STATE & RERENDER-MOVE-STATE-DOWN
// Règle 5.1 & 5.2 : Calcul direct de l'état dérivé pendant le rendu.
// ZÉRO useEffect pour synchroniser la liste filtrée !
// ============================================================

const CATEGORIES: { id: ArticleCategory | 'all'; label: string }[] = [
  { id: 'all', label: 'Toutes les actualités' },
  { id: 'aeroport', label: 'Aéroports' },
  { id: 'meteo', label: 'Météorologie' },
  { id: 'social', label: 'Jeunesse & Bourses' },
  { id: 'gouvernance', label: 'Gouvernance' },
  { id: 'cooperation', label: 'Coopération' },
  { id: 'publication', label: "L'Aérien" },
];

export interface ArticleListWithFilterProps {
  initialArticles: ArticleItem[];
}

export function ArticleListWithFilter({ initialArticles }: ArticleListWithFilterProps) {
  const [selectedCategory, setSelectedCategory] = useState<ArticleCategory | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // ✅ CORRECT (rerender-derived-state) : Calcul dérivé pur lors du rendu
  // useMemo protège les calculs si la collection dépasse plusieurs centaines d'articles
  const filteredArticles = useMemo(() => {
    const query = searchQuery.toLowerCase().trim();
    return initialArticles.filter((article) => {
      const matchesCategory =
        selectedCategory === 'all' || article.category === selectedCategory;
      const matchesSearch =
        !query ||
        article.title.toLowerCase().includes(query) ||
        article.excerpt.toLowerCase().includes(query);
      return matchesCategory && matchesSearch;
    });
  }, [initialArticles, selectedCategory, searchQuery]);

  return (
    <div className="space-y-8">
      {/* Barre de contrôle : Recherche et Filtres */}
      <div className="bg-white border border-neutral-200/80 rounded-2xl p-4 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Filtres par catégorie */}
        <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0 scrollbar-none">
          {CATEGORIES.map((cat) => {
            const isActive = selectedCategory === cat.id;
            return (
              <button
                key={cat.id}
                type="button"
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-3.5 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-orange-600 text-white shadow-sm'
                    : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                }`}
              >
                {cat.label}
              </button>
            );
          })}
        </div>

        {/* Champ de recherche */}
        <div className="relative w-full md:w-72">
          <input
            type="search"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Rechercher un article..."
            className="w-full h-10 pl-9 pr-4 text-xs bg-neutral-100 border border-transparent rounded-full focus:bg-white focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/20 transition-all"
          />
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400 text-xs">
            🔍
          </span>
        </div>
      </div>

      {/* Compteur de résultats */}
      <div className="text-xs font-semibold text-neutral-500 px-1">
        {filteredArticles.length} article{filteredArticles.length > 1 ? 's' : ''} trouvé{filteredArticles.length > 1 ? 's' : ''}
      </div>

      {/* Grille d'articles */}
      {filteredArticles.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredArticles.map((article, idx) => (
            <ArticleCard
              key={article.id}
              article={article}
              priority={idx < 3} // Règle LCP : fetchpriority élevé pour les 3 premières cartes
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-white border border-neutral-200 rounded-2xl p-8 space-y-2">
          <p className="text-sm font-bold text-neutral-800">Aucun article ne correspond à votre recherche</p>
          <p className="text-xs text-neutral-500">Essayez de modifier votre mot-clé ou réinitialisez les filtres.</p>
          <button
            type="button"
            onClick={() => {
              setSelectedCategory('all');
              setSearchQuery('');
            }}
            className="mt-4 px-4 py-2 text-xs font-bold text-orange-600 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors"
          >
            Réinitialiser les filtres
          </button>
        </div>
      )}
    </div>
  );
}

