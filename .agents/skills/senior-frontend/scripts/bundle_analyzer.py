#!/usr/bin/env python3
"""
Analyseur de dépendances et de bundle pour projets frontend React/Next.js.
Détecte les paquets lourds, obsolètes ou sujets aux fuites de performance.
Usage:
    python bundle_analyzer.py [project_dir] [--verbose]
"""

import sys
import os
import json
import argparse

HEAVY_LIBRARIES = {
    "moment": "Remplacer par 'date-fns' (modulaire) ou l'API native Intl.DateTimeFormat.",
    "lodash": "Préférer les méthodes ES6+ natives ou importer spécifiquement 'lodash-es/function'.",
    "rxjs": "Souvent trop volumineux si utilisé uniquement pour de simples flux d'événements.",
    "@material-ui/core": "Privilégier Tailwind CSS ou shadcn/ui pour éviter un runtime CSS-in-JS lourd.",
    "styled-components": "CSS-in-JS à l'exécution dégrade le temps de rendu et bloque le streaming RSC.",
    "@emotion/react": "Runtime CSS-in-JS déconseillé avec Next.js App Router.",
    "xlsx": "Très lourd dans le bundle client. À exécuter côté serveur ou charger via next/dynamic.",
    "pdfjs-dist": "Bibliothèque volumineuse. Doit impérativement être chargée dynamiquement.",
    "chart.js": "Considérer des alternatives légères ou charger dynamiquement sans SSR."
}

def analyze_package_json(filepath, verbose=False):
    print(f"🔍 Analyse du fichier : {filepath}\n")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Erreur de lecture de {filepath} : {e}")
        return

    deps = data.get("dependencies", {})
    dev_deps = data.get("devDependencies", {})
    all_deps = {**deps, **dev_deps}

    warnings = []
    recommendations = []

    for pkg, version in deps.items():
        if pkg in HEAVY_LIBRARIES:
            warnings.append((pkg, version, HEAVY_LIBRARIES[pkg]))

    # Détection de configurations recommandées
    has_next = "next" in deps
    has_tailwind = "tailwindcss" in all_deps
    has_typescript = "typescript" in all_deps

    print(f"📦 Total dépendances de production : {len(deps)}")
    print(f"🛠️  Total dépendances de dev : {len(dev_deps)}")
    print(f"⚡ Stack détectée : Next.js={has_next}, TypeScript={has_typescript}, Tailwind={has_tailwind}\n")

    if warnings:
        print("⚠️  PAQUETS VOLUMINEUX OU SOUS-OPTIMAUX DÉTECTÉS :")
        for pkg, ver, advice in warnings:
            print(f"  • {pkg} ({ver})")
            print(f"    👉 Recommandation : {advice}\n")
    else:
        print("✅ Aucun paquet critique lourd identifié dans les dépendances directes.")

    # Recommandations Next.js
    if has_next:
        print("💡 CONSEILS NEXT.JS APP ROUTER :")
        print("  1. Vérifiez que 'optimizePackageImports' est activé dans next.config.js pour vos bibliothèques d'icônes.")
        print("  2. Utilisez '@next/bundle-analyzer' pour visualiser les chunks de build :")
        print("     ANALYZE=true pnpm build")
        print("  3. Utilisez 'next/dynamic' pour tout composant de plus de 30 Ko non critique au premier rendu.")

def main():
    parser = argparse.ArgumentParser(description="Analyseur de bundle et dépendances frontend")
    parser.add_argument("dir", nargs="?", default=".", help="Répertoire racine du projet")
    parser.add_argument("--verbose", action="store_true", help="Afficher les détails de chaque dépendance")
    args = parser.parse_args()

    pkg_path = os.path.join(args.dir, "package.json")
    if not os.path.isfile(pkg_path):
        # Chercher récursivement dans les sous-dossiers
        found = False
        for root, dirs, files in os.walk(args.dir):
            if "node_modules" in dirs:
                dirs.remove("node_modules")
            if "package.json" in files:
                analyze_package_json(os.path.join(root, "package.json"), args.verbose)
                found = True
        if not found:
            print("ℹ️ Aucun package.json trouvé dans ce répertoire.")
    else:
        analyze_package_json(pkg_path, args.verbose)

if __name__ == "__main__":
    main()

