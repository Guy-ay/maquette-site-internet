---
name: react-best-practices
description: Bonnes pratiques et optimisations de performance React et Next.js (Vercel Engineering) : élimination des waterfalls asynchrones, réduction de la taille des bundles, performance serveur et Server Actions, optimisation des re-rendus et architecture de composants moderne.
---

# Meilleures Pratiques React & Next.js (React Best Practices)

Ce guide opérationnel synthétise les directives d'ingénierie et d'optimisation de performance pour **React 18/19** et **Next.js (App Router)** établies par Vercel Engineering. Il fournit à l'agent et aux développeurs un référentiel strict classé par niveau d'impact (du plus critique au plus fin) pour concevoir, relire et refactoriser du code frontend hautement performant.

---

## Rôle
Lorsqu'elle est activée, cette compétence guide l'agent pour :
1. Auditer et éliminer tout goulet d'étranglement de performance (*waterfall*, re-rendu inutile, chargement bloquant).
2. Concevoir des composants React robustes, modulaires et faciles à maintenir.
3. Exploiter au maximum les capacités hybrides Server Components / Client Components.
4. Réduire au strict minimum l'empreinte JavaScript client (*bundle size*).

---

## Quand l'utiliser
- Création ou modification de composants React / Next.js.
- Implémentation du chargement de données (*data fetching*) côté serveur ou client.
- Revue de performance frontend et optimisation des Core Web Vitals (LCP, INP, CLS).
- Découpage et refactorisation de formulaires, tableaux de bord ou applications complexes.
- Utilisation de React Server Actions et mutations de données.

---

## Hiérarchie des Règles d'Optimisation par Niveau d'Impact

```text
Priorité 1 : CRITIQUE   ─── Élimination des Waterfalls Asynchrones (async-*)
Priorité 2 : CRITIQUE   ─── Optimisation de la Taille des Bundles (bundle-*)
Priorité 3 : ÉLEVÉE     ─── Performance Côté Serveur & Server Actions (server-*)
Priorité 4 : MOYENNE+   ─── Récupération de Données Client (client-*)
Priorité 5 : MOYENNE    ─── Optimisation des Re-rendus (rerender-*)
Priorité 6 : MOYENNE    ─── Performance de Rendu & DOM (rendering-*)
Priorité 7 : BASSE+     ─── Optimisations JavaScript (js-*)
Priorité 8 : BASSE      ─── Motifs Avancés & Architecture (advanced-*)
```

---

## 1. Priorité 1 : Élimination des Waterfalls Asynchrones (`async-*`) [CRITIQUE]

Un *waterfall* (cascade) survient lorsque des opérations asynchrones indépendantes sont exécutées séquentiellement au lieu d'être parallélisées, multipliant le temps d'attente réseau par le nombre d'appels.

### Règle 1.1 : Paralléliser les requêtes indépendantes avec `Promise.all` (`async-parallel`)
Ne jamais attendre consécutivement deux promesses qui ne dépendent pas l'une de l'autre.

```tsx
// ❌ INCORRECT : Cascade séquentielle bloquante
async function getDashboardData() {
  const user = await fetchUser();        // Attend 200ms
  const stats = await fetchStats();      // Attend encore 200ms -> Total = 400ms
  return { user, stats };
}

// ✅ CORRECT : Exécution concurrente immédiate
async function getDashboardData() {
  const [user, stats] = await Promise.all([
    fetchUser(),
    fetchStats()
  ]); // Total = max(200ms, 200ms) = 200ms
  return { user, stats };
}
```

### Règle 1.2 : Différer les `await` au moment strict de leur utilisation (`async-defer-await`)
Déclencher la promesse le plus tôt possible, mais ne l'`await`er que dans la branche conditionnelle qui la consomme.

```tsx
// ❌ INCORRECT : Await trop tôt avant condition
async function handleAction(shouldLog: boolean) {
  const logData = await fetchLogData(); // Bloque toujours
  if (!shouldLog) return null;
  return processLog(logData);
}

// ✅ CORRECT : Condition évaluée avant l'attente
async function handleAction(shouldLog: boolean) {
  if (!shouldLog) return null;
  const logData = await fetchLogData();
  return processLog(logData);
}
```

### Règle 1.3 : Utiliser les frontières Suspense pour diffuser le rendu (`async-suspense-boundaries`)
Ne pas bloquer toute une page pour une section lente. Utilisez `<Suspense>` pour afficher le squelette de la page instantanément et diffuser les sections plus lentes.

```tsx
// ✅ CORRECT : Découpage avec Suspense
export default function Page() {
  return (
    <div>
      <Header />
      <Suspense fallback={<StatsSkeleton />}>
        <AsyncStatsSection />
      </Suspense>
    </div>
  );
}
```

---

## 2. Priorité 2 : Optimisation de la Taille des Bundles (`bundle-*`) [CRITIQUE]

Le JavaScript client non nécessaire dégrade directement le TTI (*Time to Interactive*) et le LCP (*Largest Contentful Paint*), particulièrement sur mobile.

### Règle 2.1 : Éviter l'importation aveugle depuis des fichiers "Barrel" (`bundle-barrel-imports`)
Importer directement depuis les sous-modules spécifiques pour permettre un *tree-shaking* effectif.

```tsx
// ❌ INCORRECT : Import d'un barrel file géant
import { Check, ArrowRight, User } from 'lucide-react';

// ✅ CORRECT : Import direct du sous-fichier (ou configuration Next.js optimizePackageImports)
import Check from 'lucide-react/dist/esm/icons/check';
import ArrowRight from 'lucide-react/dist/esm/icons/arrow-right';
```

Dans `next.config.js` :
```js
module.exports = {
  experimental: {
    optimizePackageImports: ['lucide-react', '@headlessui/react', 'date-fns'],
  },
};
```

### Règle 2.2 : Charger dynamiquement les composants lourds ou sous conditions (`bundle-dynamic-imports`)
Tout composant lourd non visible lors du premier affichage (modales, éditeurs riches, graphiques, bibliothèques cartographiques) doit être fractionné via `next/dynamic` ou `React.lazy`.

```tsx
// ✅ CORRECT : Chargement dynamique à la demande
import dynamic from 'next/dynamic';

const RichTextEditor = dynamic(() => import('@/components/Editor'), {
  ssr: false,
  loading: () => <div className="h-64 animate-pulse bg-neutral-100 rounded-lg" />
});
```

---

## 3. Priorité 3 : Performance Côté Serveur & Server Actions (`server-*`) [ÉLEVÉE]

### Règle 3.1 : Authentifier et autoriser systématiquement dans les Server Actions (`server-auth-actions`)
Une Server Action est un endpoint public accessible par simple requête HTTP POST. Ne jamais supposer qu'elle est protégée simplement parce qu'elle est invoquée depuis un composant protégé.

```tsx
// ✅ CORRECT : Vérification d'autorisation systématique
'use server';

export async function deleteArticle(articleId: string) {
  const session = await getSession();
  if (!session || session.user.role !== 'ADMIN') {
    throw new Error('Non autorisé');
  }
  await db.article.delete({ where: { id: articleId } });
}
```

### Règle 3.2 : Minimiser la charge sérialisée Server Component -> Client Component (`server-serialization`)
Ne pas transmettre un objet Prisma/Base de données complet contenant 40 champs si le composant client n'affiche que le nom et l'identifiant.

```tsx
// ❌ INCORRECT : Sérialisation d'objets volumineux et secrets
<ClientCard user={rawDatabaseUser} />

// ✅ CORRECT : Projection stricte
<ClientCard user={{ id: user.id, name: user.name }} />
```

### Règle 3.3 : Dédupliquer les requêtes de données avec `React.cache()` (`server-cache-react`)
Pour éviter d'exécuter la même requête SQL ou API plusieurs fois au cours d'un même cycle de rendu serveur :

```tsx
import { cache } from 'react';

export const getCategoryById = cache(async (id: string) => {
  return await db.category.findUnique({ where: { id } });
});
```

---

## 4. Priorité 4 : Récupération de Données Côté Client (`client-*`) [MOYENNE+]

### Règle 4.1 : Déduplication automatique des requêtes avec SWR ou TanStack Query (`client-swr-dedup`)
Ne jamais utiliser de `useEffect` brut avec `fetch` pour synchroniser des données partagées.

```tsx
// ✅ CORRECT : Déduplication globale et cache automatique
import useSWR from 'swr';

export function useUserProfile() {
  const { data, error, isLoading } = useSWR('/api/profile', fetcher, {
    dedupingInterval: 5000,
  });
  return { user: data, error, isLoading };
}
```

---

## 5. Priorité 5 : Optimisation des Re-rendus (`rerender-*`) [MOYENNE]

### Règle 5.1 : Déplacer l'état au plus près de son utilisation (`rerender-move-state-down`)
Isoler les états locaux dans de petits sous-composants pour éviter que toute l'arborescence parente ne soit re-rendue.

```tsx
// ❌ INCORRECT : La saisie dans le filtre re-rend toute la liste
export function ProductPage() {
  const [query, setQuery] = useState('');
  return (
    <div>
      <input value={query} onChange={e => setQuery(e.target.value)} />
      <HeavyProductGrid />
    </div>
  );
}

// ✅ CORRECT : Composant de recherche isolé ou passage de la grille en children
export function ProductPage() {
  return (
    <div>
      <SearchInputContainer />
      <HeavyProductGrid />
    </div>
  );
}
```

### Règle 5.2 : Calculer les valeurs dérivées pendant le rendu (`rerender-derived-state`)
Ne jamais stocker un état qui peut être calculé directement à partir d'autres variables d'état ou de props. Bannir l'anti-pattern `useEffect(() => setFiltered(...), [items, filter])`.

```tsx
// ❌ INCORRECT : État dérivé synchronisé via useEffect
const [filteredItems, setFilteredItems] = useState([]);
useEffect(() => {
  setFilteredItems(items.filter(i => i.active));
}, [items]);

// ✅ CORRECT : Calcul direct (avec useMemo si la liste est volumineuse > 1 000 éléments)
const filteredItems = useMemo(() => {
  return items.filter(i => i.active);
}, [items]);
```

### Règle 5.3 : Utiliser la composition et la prop `children` (`rerender-children-as-props`)
Quand un composant parent gère un état d'animation ou de scroll, passer les composants lourds via la prop `children`. React ne les re-rendra pas lors de la mise à jour de l'état du conteneur.

---

## 6. Priorité 6 : Performance de Rendu & DOM (`rendering-*`) [MOYENNE]

### Règle 6.1 : Utiliser `content-visibility: auto` pour les longues listes (`rendering-content-visibility`)
Permet au navigateur d'ignorer le calcul du layout et du rendu des éléments hors-champ.

```css
.long-list-item {
  content-visibility: auto;
  contain-intrinsic-size: 0 80px; /* estimation de la hauteur */
}
```

### Règle 6.2 : Définir des dimensions explicites pour éliminer les décalages de mise en page (CLS)
Toujours spécifier `width` et `height` (ou le ratio `aspect-ratio`) sur les images et conteneurs multimédias. Utiliser le composant `<Image />` de Next.js avec `placeholder="blur"`.

---

## 7. Instructions Pas-à-Pas pour l'Agent

Lors de l'analyse ou de l'écriture de code React/Next.js, suivez cette procédure :

1. **Phase 1 : Audit des Waterfalls**
   - Repérer tous les `await` séquentiels dans les Server Components, routes API et Server Actions.
   - Regrouper avec `Promise.all` ou décomposer avec `<Suspense>`.
2. **Phase 2 : Contrôle des Dépendances & Imports**
   - Détecter les imports depuis des barrel files d'icônes ou de composants UI.
   - S'assurer que les bibliothèques lourdes sont chargées dynamiquement (`next/dynamic`).
3. **Phase 3 : Vérification des Frontières Server/Client**
   - Maintenir le maximum de composants en Server Components par défaut.
   - Ajouter `'use client'` uniquement là où l'interactivité (hooks, événements, animations directes) est obligatoire.
4. **Phase 4 : Nettoyage des Re-rendus**
   - Éliminer les `useEffect` redondants servant à calculer des états dérivés.
   - Déplacer l'état vers les composants feuilles.
5. **Phase 5 : Accessibilité et Core Web Vitals**
   - Valider la stabilité visuelle (CLS) et la réactivité au premier clic (INP).

---

## Exemples Concrets d'Application

### Exemple 1 : Page Tableau de Bord avec Données Multiples
**Demande :** « Créer la page d'accueil d'un tableau de bord affichant les statistiques, les alertes météo et la liste des derniers articles. »

**Application de la compétence :**
```tsx
import { Suspense } from 'react';
import dynamic from 'next/dynamic';
import { StatsCards } from '@/components/dashboard/StatsCards';
import { AlertsBanner } from '@/components/dashboard/AlertsBanner';
import { SkeletonGrid } from '@/components/ui/SkeletonGrid';

// Chargement différé du graphique interactif lourd
const InteractiveTrafficChart = dynamic(
  () => import('@/components/dashboard/TrafficChart'),
  { ssr: false, loading: () => <div className="h-72 animate-pulse bg-neutral-100" /> }
);

export default async function DashboardPage() {
  return (
    <main className="p-6 max-w-7xl mx-auto space-y-6">
      <AlertsBanner />
      
      {/* Rendu concurrent avec streaming Suspense */}
      <Suspense fallback={<SkeletonGrid count={4} />}>
        <StatsCards />
      </Suspense>

      <section className="bg-white rounded-xl border border-neutral-200 p-6">
        <h2 className="text-lg font-bold text-neutral-900 mb-4">Évolution du Trafic</h2>
        <InteractiveTrafficChart />
      </section>
    </main>
  );
}
```

---

## Validation et Critères de Conformité

Pour considérer qu'une implémentation respecte cette compétence :
- [ ] Aucun `await` consécutif indépendant n'est présent.
- [ ] Tout chargement de données lourd est encapsulé sous `<Suspense>` avec un fallback squelette.
- [ ] Aucun import géant de bibliothèque d'icônes n'est fait sans optimisation ciblée.
- [ ] Les formulaires et éléments interactifs isolent leur état local pour protéger les composants frères.
- [ ] Aucun `useEffect` n'est employé pour dupliquer ou dériver un état existant.
- [ ] Les Server Actions valident explicitement la session et les droits d'accès de l'utilisateur.

