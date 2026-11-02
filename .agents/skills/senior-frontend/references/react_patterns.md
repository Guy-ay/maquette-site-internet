# Motifs d'Architecture et Conception React (React Patterns)

Ce guide de référence détaille les motifs de conception préconisés par les développeurs frontend seniors pour créer des applications React scalables et découplées.

---

## 1. Compound Components (Composants Composés)

Permet de créer des composants multi-éléments partageant un état implicite sans prop drilling (ex: Tabs, Accordion, Select, Modal).

```tsx
'use client';

import React, { createContext, useContext, useState } from 'react';

interface TabsContextType {
  activeTab: string;
  setActiveTab: (id: string) => void;
}

const TabsContext = createContext<TabsContextType | null>(null);

export function Tabs({ defaultValue, children }: { defaultValue: string; children: React.ReactNode }) {
  const [activeTab, setActiveTab] = useState(defaultValue);
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs-container">{children}</div>
    </TabsContext.Provider>
  );
}

export function TabList({ children }: { children: React.ReactNode }) {
  return <div className="flex border-b border-neutral-200 gap-2">{children}</div>;
}

export function TabTrigger({ value, children }: { value: string; children: React.ReactNode }) {
  const ctx = useContext(TabsContext);
  if (!ctx) throw new Error('TabTrigger doit être utilisé dans Tabs');
  const isActive = ctx.activeTab === value;
  return (
    <button
      onClick={() => ctx.setActiveTab(value)}
      className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
        isActive ? 'border-orange-500 text-orange-600' : 'border-transparent text-neutral-600 hover:text-neutral-900'
      }`}
    >
      {children}
    </button>
  );
}

export function TabContent({ value, children }: { value: string; children: React.ReactNode }) {
  const ctx = useContext(TabsContext);
  if (!ctx) throw new Error('TabContent doit être utilisé dans Tabs');
  if (ctx.activeTab !== value) return null;
  return <div className="py-4">{children}</div>;
}
```

---

## 2. Inversion de Contrôle : Conteneurs et Children (`children as props`)

Évite les cascades de re-rendus dans les composants parents ayant des états à forte fréquence (scroll, resize, animations).

```tsx
// Le composant wrapper écoute le scroll ou le resize, mais n'entraîne PAS le re-rendu de {children}
export function ScrollFadeContainer({ children }: { children: React.ReactNode }) {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="relative">
      <div style={{ opacity: Math.max(0, 1 - scrollY / 300) }} className="sticky top-0 h-1 bg-orange-500" />
      {children}
    </div>
  );
}
```

---

## 3. Polymorphic Components (`as` Prop Pattern)

Permet de modifier l'élément HTML sous-jacent (ex: un bouton rendu sous forme de lien `<a>` ou balise `<button>`).

```tsx
type AsProp<C extends React.ElementType> = {
  as?: C;
};

type PropsToOmit<C extends React.ElementType, P> = keyof (AsProp<C> & P);

type PolymorphicComponentProp<
  C extends React.ElementType,
  Props = {}
> = React.PropsWithChildren<Props & AsProp<C>> &
  Omit<React.ComponentPropsWithoutRef<C>, PropsToOmit<C, Props>>;

export function Typography<C extends React.ElementType = 'p'>({
  as,
  children,
  className,
  ...props
}: PolymorphicComponentProp<C, { className?: string }>) {
  const Component = as || 'p';
  return (
    <Component className={className} {...props}>
      {children}
    </Component>
  );
}
```

