---
name: senior-frontend
description: Compétence d'ingénierie frontend senior pour concevoir des applications web modernes et performantes avec React, Next.js, TypeScript et Tailwind CSS. Inclut la génération de composants modulaires, l'analyse de bundle, l'optimisation des performances, la gestion d'état et les revues de code frontend.
---

# Développeur Frontend Senior (Senior Frontend Skill)

Cette compétence équipe l'agent Antigravity des pratiques, motifs d'architecture et outils d'un **Ingénieur Frontend Senior** spécialisé dans l'écosystème moderne **React, Next.js (App Router), TypeScript et Tailwind CSS**.

Elle permet de structurer des interfaces utilisateur fluides, modulaires, accessibles (a11y) et scalables, tout en automatisant les tâches de génération de composants, d'analyse de performance et d'échafaudage de projets.

---

## Rôle
Lorsqu'elle est activée, cette compétence guide l'agent pour :
1. **Concevoir et développer des composants de qualité production** : typage TypeScript strict, accessibilité ARIA, gestion d'erreurs et variantes avec Tailwind CSS ou `class-variance-authority`.
2. **Architecturer les applications Next.js et React** : séparation propre Server/Client Components, hooks personnalisés réutilisables, gestion d'état robuste (Zustand, React Query/SWR, Context).
3. **Optimiser les performances et la taille du bundle** : audit des dépendances volumineuses, lazy-loading, mémorisation ciblée et respect des Core Web Vitals (LCP, INP, CLS).
4. **Mener des revues de code frontend rigoureuses** : détection des anti-patterns, des fuites de mémoire, des waterfalls réseau et de la dette technique.

---

## Quand l'utiliser
- Création, développement ou refactorisation de composants UI / UX.
- Configuration initiale ou scaffolding d'une application Next.js / React avec TypeScript et Tailwind CSS.
- Implémentation d'un système de design (Design System) ou de bibliothèques de composants.
- Audit et diagnostic de performance d'un bundle frontend.
- Revue de code (*code review*) axée sur la maintenabilité, l'accessibilité et la vélocité.

---

## Capacités et Outils Intégrés

La compétence intègre trois scripts d'automatisation dans son répertoire `scripts/` :

```text
.agents/skills/senior-frontend/
├── SKILL.md
├── scripts/
│   ├── component_generator.py   # Générateur de composants Client/Server, Hooks, Tests et Stories
│   ├── bundle_analyzer.py       # Analyseur de dépendances et de taille de bundle
│   └── frontend_scaffolder.py   # Générateur de structure de projet frontend moderne
└── references/
    ├── react_patterns.md        # Guide complet des motifs de conception React
    └── nextjs_optimization.md   # Guide d'optimisation Next.js App Router
```

### 1. Générateur de Composants (`component_generator.py`)
Génère instantanément des composants standardisés, typés et modulaires :
```bash
# Générer un composant Client React classique
python .agents/skills/senior-frontend/scripts/component_generator.py Button --dir src/components/ui

# Générer un Server Component asynchrone (Next.js)
python .agents/skills/senior-frontend/scripts/component_generator.py ProductCard --type server

# Générer un Hook personnalisé
python .agents/skills/senior-frontend/scripts/component_generator.py useDebounce --type hook

# Générer avec fichier de test et Storybook
python .agents/skills/senior-frontend/scripts/component_generator.py UserAvatar --with-test --with-story
```

### 2. Analyseur de Bundle (`bundle_analyzer.py`)
Vérifie la santé des dépendances dans `package.json` et signale les paquets obsolètes ou surdimensionnés (ex: `moment`, imports globaux `lodash`, barrel files géants) :
```bash
python .agents/skills/senior-frontend/scripts/bundle_analyzer.py .
```

### 3. Échafaudeur Frontend (`frontend_scaffolder.py`)
Initialise rapidement une arborescence moderne et modulaire pour une fonctionnalité ou une application :
```bash
python .agents/skills/senior-frontend/scripts/frontend_scaffolder.py dashboard --features auth,api
```

---

## Directives d'Ingénierie Frontend Senior

### A. Principes de Développement des Composants
1. **Composants atomiques et ciblés :** Un composant ne doit accomplir qu'une tâche bien définie. S'il dépasse 150-200 lignes, le scinder en sous-composants ou en hooks.
2. **Typage TypeScript strict :**
   - Toujours définir une interface claire pour les `Props` (ex: `interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>`).
   - Éviter `any` ; préférer `unknown`, les génériques ou les types discriminés pour les états multiples.
3. **Accessibilité (a11y) dès la conception :**
   - Utiliser des balises HTML sémantiques (`<button>`, `<main>`, `<article>`, `<nav>`).
   - Assurer les attributs ARIA appropriés (`aria-label`, `aria-expanded`, `aria-busy`).
   - Assurer une navigation complète au clavier (`Tab`, `Enter`, `Space`, `Escape`).

### B. Architecture Next.js & Server Components
- **Serveur par défaut :** Tous les composants de l'App Router sont des Server Components jusqu'à preuve du contraire.
- **Ajout de `'use client'` à la marge :** Ne déclarer `'use client'` que sur les composants interactifs feuilles (boutons, formulaires dynamiques, modales, toggles).
- **Inversion de contrôle :** Transmettre les Server Components comme `children` ou props aux Client Components conteneurs pour préserver le rendu côté serveur.

### C. Gestion d'État Pragmatique
- **État d'URL :** Pour les filtres, la pagination, les onglets et la recherche, synchroniser avec les paramètres d'URL (`searchParams`).
- **État serveur :** Utiliser SWR ou TanStack Query avec mise en cache et déduplication.
- **État client global :** Utiliser Zustand pour les états transversaux (panier, session UI, préférences) plutôt que de multiples React Contexts qui causent des re-rendus globaux.

---

## Instructions Pas-à-Pas pour l'Agent

Lorsqu'on vous demande de concevoir, auditer ou améliorer du code frontend :

1. **Analyser l'intention et le découpage :**
   - Identifier la frontière entre rendu statique/serveur et interactivité dynamique client.
   - Sélectionner les motifs de conception adéquats (Compound Components, Render Props, Custom Hooks).
2. **Appliquer les standards TypeScript et Tailwind :**
   - Définir les types et interfaces d'entrée/sortie.
   - Composer les classes utilitaires Tailwind avec cohérence (variantes responsives, états hover/focus-visible/disabled).
3. **Vérifier l'accessibilité et la résilience :**
   - Gérer les états : initial, chargement (*skeleton*), succès, vide (*empty state*) et erreur.
   - Garantir le focus visible au clavier.
4. **Optimiser les performances :**
   - Éviter les waterfalls et les imports bloquants.
   - Vérifier la stabilité du layout visuel (zéro décalage CLS).

---

## Exemples Concrets

### Exemple 1 : Composant Bouton Moderne et Accessible (Tailwind + CVA)
```tsx
import React, { forwardRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-lg text-sm font-semibold transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]',
  {
    variants: {
      variant: {
        primary: 'bg-orange-600 text-white hover:bg-orange-700 focus-visible:ring-orange-500 shadow-sm',
        secondary: 'bg-neutral-100 text-neutral-900 hover:bg-neutral-200 focus-visible:ring-neutral-400',
        outline: 'border border-neutral-300 bg-transparent hover:bg-neutral-50 text-neutral-800',
        ghost: 'hover:bg-neutral-100 text-neutral-700',
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        md: 'h-10 px-4 py-2',
        lg: 'h-12 px-6 text-base',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, isLoading, leftIcon, rightIcon, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        aria-busy={isLoading}
        className={cn(buttonVariants({ variant, size, className }))}
        {...props}
      >
        {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {!isLoading && leftIcon && <span className="mr-2">{leftIcon}</span>}
        <span>{children}</span>
        {!isLoading && rightIcon && <span className="ml-2">{rightIcon}</span>}
      </button>
    );
  }
);
Button.displayName = 'Button';
```

---

## Validation et Grille d'Évaluation

Une livraison frontend conforme à ce profil senior doit valider :
- [ ] Tous les composants sont strictement typés en TypeScript (zéro `any`).
- [ ] Aucun avertissement de console React (clés uniques dans les listes, labels accessibles).
- [ ] Le focus clavier (`focus-visible`) est visible et propre sur tous les éléments interactifs.
- [ ] Les états de chargement et d'erreur sont systématiquement prévus et soignés.
- [ ] Le code client (`'use client'`) est limité au strict minimum nécessaire.

