#!/usr/bin/env python3
"""
Échafaudeur de structure modulaire frontend pour fonctionnalités ou applications React/Next.js.
Usage:
    python frontend_scaffolder.py <feature_name> [--base-dir <path>] [--features auth,api,ui]
"""

import os
import sys
import argparse

def scaffold_feature(name, base_dir="src/features", features=None):
    feature_dir = os.path.join(base_dir, name)
    subdirs = [
        "components",
        "hooks",
        "services",
        "types",
        "utils"
    ]

    for sd in subdirs:
        os.makedirs(os.path.join(feature_dir, sd), exist_ok=True)

    # 1. Types
    types_file = os.path.join(feature_dir, "types", "index.ts")
    with open(types_file, "w", encoding="utf-8") as f:
        f.write(f"""export interface {name.capitalize()}Item {{
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
}}

export interface {name.capitalize()}State {{
  items: {name.capitalize()}Item[];
  isLoading: boolean;
  error: string | null;
}}
""")

    # 2. Service API
    api_file = os.path.join(feature_dir, "services", f"{name}Api.ts")
    with open(api_file, "w", encoding="utf-8") as f:
        f.write(f"""import {{ {name.capitalize()}Item }} from '../types';

export async function fetch{name.capitalize()}Items(): Promise<{name.capitalize()}Item[]> {{
  const response = await fetch('/api/{name}');
  if (!response.ok) {{
    throw new Error('Erreur lors de la récupération des données {name}');
  }}
  return response.json();
}}
""")

    # 3. Hook
    hook_file = os.path.join(feature_dir, "hooks", f"use{name.capitalize()}.ts")
    with open(hook_file, "w", encoding="utf-8") as f:
        f.write(f"""'use client';

import {{ useState, useEffect }} from 'react';
import {{ {name.capitalize()}Item }} from '../types';
import {{ fetch{name.capitalize()}Items }} from '../services/{name}Api';

export function use{name.capitalize()}() {{
  const [items, setItems] = useState<{name.capitalize()}Item[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {{
    let isMounted = true;
    fetch{name.capitalize()}Items()
      .then(data => {{
        if (isMounted) setItems(data);
      }})
      .catch(err => {{
        if (isMounted) setError(err.message);
      }})
      .finally(() => {{
        if (isMounted) setIsLoading(false);
      }});

    return () => {{
      isMounted = false;
    }};
  }}, []);

  return {{ items, isLoading, error }};
}}
""")

    # 4. Composant Principal
    comp_file = os.path.join(feature_dir, "components", f"{name.capitalize()}List.tsx")
    with open(comp_file, "w", encoding="utf-8") as f:
        f.write(f"""'use client';

import React from 'react';
import {{ use{name.capitalize()} }} from '../hooks/use{name.capitalize()}';

export function {name.capitalize()}List() {{
  const {{ items, isLoading, error }} = use{name.capitalize()}();

  if (isLoading) {{
    return (
      <div className="flex items-center justify-center p-8 text-neutral-500 animate-pulse">
        Chargement des données...
      </div>
    );
  }}

  if (error) {{
    return (
      <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
        {{error}}
      </div>
    );
  }}

  if (items.length === 0) {{
    return (
      <div className="p-8 text-center text-neutral-400">
        Aucun élément disponible.
      </div>
    );
  }}

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {{items.map(item => (
        <div key={{item.id}} className="p-4 bg-white border border-neutral-200 rounded-xl shadow-sm hover:border-neutral-300 transition">
          <h3 className="font-semibold text-neutral-900">{{item.title}}</h3>
        </div>
      ))}}
    </div>
  );
}}
""")

    # 5. Point d'entrée public index.ts
    index_file = os.path.join(feature_dir, "index.ts")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(f"""export * from './components/{name.capitalize()}List';
export * from './hooks/use{name.capitalize()}';
export * from './types';
""")

    print(f"✅ Fonctionnalité '{name}' échafaudée avec succès dans : {feature_dir}")

def main():
    parser = argparse.ArgumentParser(description="Échafaudeur de fonctionnalité frontend modulaire")
    parser.add_argument("name", help="Nom de la fonctionnalité (ex: billing, analytics, notifications)")
    parser.add_argument("--base-dir", default="src/features", help="Répertoire de base")
    parser.add_argument("--features", default="api,hooks,ui", help="Fonctionnalités à activer")
    args = parser.parse_args()

    scaffold_feature(args.name, args.base_dir, args.features)

if __name__ == "__main__":
    main()

