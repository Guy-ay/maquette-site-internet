import { cache } from 'react';
import type { ArticleItem, AirportSite } from '@/types';

// ============================================================
// REACT BEST PRACTICE : SERVER-CACHE-REACT & ASYNC-PARALLEL
// ============================================================

/**
 * Récupère un article par son slug avec déduplication React.cache()
 * Règle: server-cache-react (évite d'exécuter la même requête plusieurs fois lors d'un même rendu serveur)
 */
export const getArticleBySlug = cache(async (slug: string): Promise<ArticleItem | null> => {
  // Dans l'implémentation Next.js, interroge Prisma ou l'API NestJS
  // Projection stricte pour minimiser le payload sérialisé (Règle server-serialization)
  return null;
});

/**
 * Récupère simultanément les flux nécessaires à la page d'accueil
 * Règle: async-parallel (élimination des waterfalls avec Promise.all)
 */
export async function getHomePageData() {
  const [heroArticles, grandsDossiers, dernieresActus] = await Promise.all([
    fetchHeroArticles(),
    fetchGrandsDossiers(),
    fetchDernieresActualites(),
  ]);

  return {
    heroArticles,
    grandsDossiers,
    dernieresActus,
  };
}

// Fonctions d'accès aux données (simulées ou connectées à l'API)
async function fetchHeroArticles(): Promise<ArticleItem[]> {
  return [];
}

async function fetchGrandsDossiers(): Promise<ArticleItem[]> {
  return [];
}

async function fetchDernieresActualites(): Promise<ArticleItem[]> {
  return [];
}

