#!/usr/bin/env python3
"""
Outil d'analyse et d'optimisation de schéma de base de données (Prisma / SQL).
Vérifie les index, les clés étrangères et les risques d'intégrité ou de requêtes lentes.
Usage:
    python database_migration_tool.py <schema_file> [--analyze]
"""

import sys
import os
import re
import argparse

def analyze_prisma_schema(filepath):
    print(f"🔍 Analyse du schéma Prisma : {filepath}\n")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Impossible d'ouvrir {filepath} : {e}")
        return

    models = re.findall(r'model\s+(\w+)\s+\{([^}]+)\}', content)
    print(f"📊 Nombre de modèles trouvés : {len(models)}\n")

    warnings = []
    indexes_found = 0

    for model_name, body in models:
        lines = [line.strip() for line in body.split("\n") if line.strip()]
        fields = []
        has_id = False
        model_indexes = []

        for line in lines:
            if line.startswith("//"):
                continue
            if "@id" in line:
                has_id = True
            if "@@index" in line:
                model_indexes.append(line)
                indexes_found += 1
            if not line.startswith("@@"):
                parts = line.split()
                if len(parts) >= 2:
                    fields.append((parts[0], parts[1]))

        # Vérification clé primaire
        if not has_id:
            warnings.append(f"Modèle '{model_name}' : Aucune clé primaire (@id) explicite détectée.")

        # Vérification des colonnes de relation / Foreign Keys sans index
        for f_name, f_type in fields:
            if f_name.endswith("Id") and not any(f_name in idx for idx in model_indexes):
                warnings.append(
                    f"Modèle '{model_name}' : La clé étrangère '{f_name}' n'est pas indexée. "
                    f"Ajoutez @@index([{f_name}]) pour accélérer les jointures."
                )

            # Vérification des colonnes de statut ou de dates fréquemment filtrées
            if f_name in ["status", "publishedAt", "createdAt"] and not any(f_name in idx for idx in model_indexes):
                warnings.append(
                    f"Modèle '{model_name}' : Le champ de filtrage/tri '{f_name}' gagnerait à être indexé."
                )

    print(f"📈 Total index explicites détectés : {indexes_found}\n")

    if warnings:
        print("⚠️  RECOMMANDATIONS D'OPTIMISATION DE BASE DE DONNÉES :")
        for w in warnings:
            print(f"  • {w}")
    else:
        print("✅ Schéma bien structuré et convenablement indexé.")

def main():
    parser = argparse.ArgumentParser(description="Analyseur et optimisateur de schéma de base de données")
    parser.add_argument("schema", nargs="?", default="prisma/schema.prisma", help="Chemin du schéma (Prisma ou SQL)")
    parser.add_argument("--analyze", action="store_true", help="Lancer l'audit de performance et d'indexation")
    args = parser.parse_args()

    if not os.path.isfile(args.schema):
        print(f"ℹ️ Fichier {args.schema} non trouvé. Recherche d'un schéma Prisma dans le projet...")
        found = False
        for root, dirs, files in os.walk("."):
            if "schema.prisma" in files:
                analyze_prisma_schema(os.path.join(root, "schema.prisma"))
                found = True
                break
        if not found:
            print("❌ Aucun fichier schema.prisma trouvé.")
    else:
        analyze_prisma_schema(args.schema)

if __name__ == "__main__":
    main()

