# Guide d'Optimisation Next.js App Router (Senior Guidelines)

Ce guide récapitule les meilleures stratégies pour obtenir des Core Web Vitals optimaux avec Next.js 14/15.

---

## 1. Séparation Stricte Server / Client

| Type de Composant | Quand l'utiliser | Caractéristiques |
| :--- | :--- | :--- |
| **Server Component** (défaut) | Fetch de données, accès direct à la BDD, secrets d'API, contenu textuel | 0 Ko de JS client, rendu sur le serveur |
| **Client Component** (`'use client'`) | Écoute d'événements (`onClick`, `onChange`), `useState`, `useEffect`, animations Framer Motion | Chargé dans le bundle client |

### Règle d'or :
Pousser les Client Components vers les nœuds feuilles de l'arbre DOM.

```tsx
// ❌ MAUVAIS : Tout le layout devient Client Component
'use client';
export default function DashboardLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  return (
    <div>
      <Sidebar isOpen={sidebarOpen} />
      <main>{children}</main>
    </div>
  );
}

// ✅ BON : Seul le toggle et la barre latérale dynamique sont Client
export default function DashboardLayout({ children }) {
  return (
    <div>
      <ClientSidebarWrapper />
      <main>{children}</main>
    </div>
  );
}
```

---

## 2. Optimisation des Images et Multimédia

Toujours utiliser `next/image` avec les dimensions intrinsèques :

```tsx
import Image from 'next/image';

// Image Hero prioritaire pour le LCP
<Image
  src="/hero.webp"
  alt="Illustration principale"
  width={1200}
  height={600}
  priority
  className="w-full h-auto object-cover"
/>

// Image sous la ligne de flottaison (lazy-load automatique)
<Image
  src="/thumb.webp"
  alt="Vignette"
  width={400}
  height={300}
  loading="lazy"
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
/>
```

---

## 3. Streaming et Suspense

Ne jamais faire attendre toute la page si une seule section est lente.

```tsx
import { Suspense } from 'react';

export default function ArticlePage({ params }: { params: { slug: string } }) {
  return (
    <article className="max-w-4xl mx-auto py-8">
      {/* Contenu principal immédiat */}
      <ArticleHeader slug={params.slug} />

      {/* Commentaires ou statistiques lentes streamés */}
      <Suspense fallback={<CommentsSkeleton />}>
        <AsyncCommentsSection slug={params.slug} />
      </Suspense>
    </article>
  );
}
```

