# Plan d'implémentation - Plateforme SODEXAM : Fondations Monorepo, Sécurité & Workflow de Validation Admin (Articles & Documents par Catégorie)

> **Pour l'agent :** SOUS-COMPÉTENCE REQUIS : Utiliser `executing-plans` pour implémenter ce plan tâche par tâche. Les étapes utilisent la syntaxe des cases à cocher (`- [ ]`) pour le suivi.

**Objectif :** Construire le socle du monorepo TypeScript SODEXAM (`packages/shared` et `apps/api`), incluant l'infrastructure Docker sécurisée, le schéma Prisma unifié (Catégories, Articles, Documents, Assets, AuditLog), la sanitization anti-XSS, le chiffrement AES-256-GCM et le moteur de workflow garantissant qu'aucun article ni document PDF ne soit visible ou téléchargeable publiquement sans validation explicite d'un administrateur et scan antivirus `CLEAN`.

**Architecture :** Monorepo `pnpm` partageant un contrat unique Zod (`packages/shared`) entre le backend NestJS (`apps/api`), le site public Mobile-First (`apps/web`) et le back-office (`apps/admin`). Toute publication suit une machine à états stricte (`BROUILLON` -> `EN_RELECTURE` -> `PUBLIE` / `REJETE` -> `ARCHIVE`) tracée dans `AuditLog`, avec quarantaine S3/MinIO tant que l'administrateur n'a pas validé le contenu.

**Stack Technique :** Node.js 22 LTS, pnpm 9, TypeScript 5.6, Zod 3.23, Prisma 5.20, PostgreSQL 16, Redis 7, ClamAV, MinIO (S3), Vitest 2.1, sanitize-html, Node.js `crypto` (AES-256-GCM).

## Contraintes Globales
- **Langage unique :** TypeScript en mode strict (`strict: true`, `noImplicitAny: true`, `strictNullChecks: true`).
- **Sécurité réseau Docker :** Tous les ports des services d'infrastructure (`postgres`, `redis`, `meilisearch`, `clamav`, `minio`) doivent être liés exclusivement à `127.0.0.1`.
- **Zéro fuite de document non validé :** Aucun document ou article dont le statut est différent de `PUBLIE` ou dont un fichier lié a un statut `ScanStatus` différent de `CLEAN` ne peut être retourné par les requêtes publiques.
- **Validation unique :** Les schémas Zod de `packages/shared` constituent l'unique source de vérité pour la validation des entrées.

---

## Découpage Global des Sous-Systèmes (3 Plans Autonomes)

Conformément aux bonnes pratiques pour un développeur seul, le projet complet est divisé en 3 plans séquentiels autonomes :
1. **Plan 1 (Ce document) — Fondations, Contrats Partagés Zod, Sécurité & Workflow de Validation Admin (Articles & Documents par Catégorie)** : Monorepo, Docker, Prisma, Services de sécurité et Moteur de publication/validation testé de bout en bout.
2. **Plan 2 — Authentification (JWT HttpOnly + 2FA TOTP), Upload Asynchrone (BullMQ + ClamAV + S3) & Back-Office (`apps/admin`)** : Interface d'administration et file de validation rapide sur mobile.
3. **Plan 3 — Site Public Mobile-First (`apps/web`), Visionneuse de Documents *L'Aérien* & PWA** : Intégration Next.js App Router des maquettes SODEXAM avec cache ISR On-Demand.

---

## Structure des Fichiers du Plan 1

| Fichier | Responsabilité |
|---|---|
| `package.json` | Configuration racine du monorepo et scripts de test globaux |
| `pnpm-workspace.yaml` | Déclaration des espaces de travail `apps/*` et `packages/*` |
| `tsconfig.base.json` | Configuration TypeScript stricte partagée |
| `infra/docker-compose.yml` | Services locaux isolés sur `127.0.0.1` avec limites mémoire ClamAV |
| `.env.example` | Modèle des variables d'environnement requises |
| `packages/shared/package.json` | Manifeste du package partagé `@sodexam/shared` |
| `packages/shared/src/workflow.ts` | Rôles RBAC, statuts et machine à états de validation Admin + contrôle `ScanStatus` |
| `packages/shared/src/schemas.ts` | Schémas Zod (`Category`, `Article`, `Document`, `Transition`) |
| `packages/shared/src/index.ts` | Point d'entrée public de `@sodexam/shared` |
| `apps/api/prisma/schema.prisma` | Modèle de données PostgreSQL complet (Catégories, Articles, Documents, Assets, Audit) |
| `apps/api/prisma/seed.ts` | Données initiales officielles SODEXAM (catégories fusionnées, compte admin) |
| `apps/api/src/common/sanitize.service.ts` | Nettoyage HTML liste blanche anti-XSS pour le contenu riche TipTap |
| `apps/api/src/common/crypto.service.ts` | Chiffrement et déchiffrement authentifié AES-256-GCM pour données sensibles (CERMA) |
| `apps/api/src/content/content-workflow.service.ts` | Logique métier de création par catégorie, validation Admin en cascade et filtrage public |

---

### Tâche 1 : Initialisation du Monorepo `pnpm`, Configuration TypeScript et Infrastructure Docker Sécurisée

**Fichiers :**
- Créer : `pnpm-workspace.yaml`
- Créer : `tsconfig.base.json`
- Créer : `package.json`
- Créer : `infra/docker-compose.yml`
- Créer : `.env.example`
- Tester : `packages/shared/tests/infra-config.spec.ts`

**Interfaces :**
- Consomme : Aucune (tâche fondatrice)
- Produit : Workspace `pnpm` fonctionnel, configuration TypeScript stricte et définition Docker Compose validée par test automatisé.

- [ ] **Étape 1 : Écrire le test qui échoue**
  Créer `packages/shared/package.json` :
  ```json
  {
    "name": "@sodexam/shared",
    "version": "1.0.0",
    "private": true,
    "type": "module",
    "main": "./src/index.ts",
    "types": "./src/index.ts",
    "scripts": {
      "test": "vitest run"
    },
    "dependencies": {
      "zod": "^3.23.8"
    },
    "devDependencies": {
      "@types/node": "^22.7.5",
      "typescript": "^5.6.3",
      "vitest": "^2.1.3",
      "yaml": "^2.6.0"
    }
  }
  ```

  Créer `packages/shared/tests/infra-config.spec.ts` :
  ```ts
  import { describe, it, expect } from 'vitest';
  import { readFileSync, existsSync } from 'node:fs';
  import { resolve } from 'node:path';
  import { parse } from 'yaml';

  const rootDir = resolve(__dirname, '../../..');

  describe('Infrastructure & Monorepo Security Configuration', () => {
    it('should define pnpm-workspace.yaml with apps/* and packages/*', () => {
      const workspacePath = resolve(rootDir, 'pnpm-workspace.yaml');
      expect(existsSync(workspacePath)).toBe(true);
      const content = parse(readFileSync(workspacePath, 'utf-8')) as { packages: string[] };
      expect(content.packages).toEqual(['apps/*', 'packages/*']);
    });

    it('should bind all Docker Compose service ports strictly to 127.0.0.1 and limit ClamAV memory', () => {
      const composePath = resolve(rootDir, 'infra/docker-compose.yml');
      expect(existsSync(composePath)).toBe(true);
      const compose = parse(readFileSync(composePath, 'utf-8')) as {
        services: Record<string, { ports?: string[]; mem_limit?: string }>;
      };

      const services = compose.services;
      expect(Object.keys(services)).toEqual(['db', 'redis', 'meili', 'clamav', 'minio']);

      for (const [serviceName, serviceConfig] of Object.entries(services)) {
        for (const portMapping of serviceConfig.ports ?? []) {
          expect(
            portMapping.startsWith('127.0.0.1:'),
            `Service ${serviceName} port ${portMapping} must be bound to 127.0.0.1`
          ).toBe(true);
        }
      }

      expect(services.clamav.mem_limit).toBe('2g');
    });
  });
  ```

- [ ] **Étape 2 : Lancer le test pour vérifier l'échec**
  Commande : `pnpm --filter @sodexam/shared test`
  Attendu : Échec car `pnpm-workspace.yaml` et `infra/docker-compose.yml` n'existent pas encore.

- [ ] **Étape 3 : Écrire l'implémentation minimale**
  Créer `pnpm-workspace.yaml` :
  ```yaml
  packages:
    - 'apps/*'
    - 'packages/*'
  ```

  Créer `tsconfig.base.json` :
  ```json
  {
    "compilerOptions": {
      "target": "ES2022",
      "module": "ESNext",
      "moduleResolution": "Bundler",
      "strict": true,
      "noImplicitAny": true,
      "strictNullChecks": true,
      "noUnusedLocals": true,
      "noUnusedParameters": true,
      "esModuleInterop": true,
      "skipLibCheck": true,
      "forceConsistentCasingInFileNames": true,
      "resolveJsonModule": true,
      "declaration": true
    }
  }
  ```

  Créer `package.json` à la racine :
  ```json
  {
    "name": "sodexam-monorepo",
    "version": "1.0.0",
    "private": true,
    "packageManager": "pnpm@9.12.2",
    "scripts": {
      "test": "pnpm -r test"
    }
  }
  ```

  Créer `infra/docker-compose.yml` :
  ```yaml
  services:
    db:
      image: postgres:16-alpine
      restart: unless-stopped
      environment:
        POSTGRES_USER: sodexam
        POSTGRES_PASSWORD: ${DB_PASSWORD}
        POSTGRES_DB: sodexam
      volumes:
        - pgdata:/var/lib/postgresql/data
      ports:
        - "127.0.0.1:5432:5432"
      healthcheck:
        test: ["CMD-SHELL", "pg_isready -U sodexam -d sodexam"]
        interval: 10s
        timeout: 5s
        retries: 5

    redis:
      image: redis:7-alpine
      restart: unless-stopped
      ports:
        - "127.0.0.1:6379:6379"
      healthcheck:
        test: ["CMD", "redis-cli", "ping"]
        interval: 10s
        timeout: 5s
        retries: 5

    meili:
      image: getmeili/meilisearch:v1.11
      restart: unless-stopped
      environment:
        MEILI_MASTER_KEY: ${MEILI_KEY}
        MEILI_NO_ANALYTICS: "true"
      ports:
        - "127.0.0.1:7700:7700"
      volumes:
        - meili:/meili_data

    clamav:
      image: clamav/clamav:stable
      restart: unless-stopped
      mem_limit: 2g
      ports:
        - "127.0.0.1:3310:3310"
      healthcheck:
        test: ["CMD", "/usr/local/bin/clamdcheck.sh"]
        interval: 60s
        timeout: 10s
        retries: 3

    minio:
      image: minio/minio:latest
      restart: unless-stopped
      command: server /data --console-address ":9001"
      environment:
        MINIO_ROOT_USER: ${S3_KEY}
        MINIO_ROOT_PASSWORD: ${S3_SECRET}
      ports:
        - "127.0.0.1:9000:9000"
        - "127.0.0.1:9001:9001"
      volumes:
        - minio:/data

  volumes:
    pgdata: {}
    meili: {}
    minio: {}
  ```

  Créer `.env.example` :
  ```dotenv
  DATABASE_URL=postgresql://sodexam:CHANGER_MOT_DE_PASSE@127.0.0.1:5432/sodexam
  DB_PASSWORD=CHANGER_MOT_DE_PASSE
  JWT_ACCESS_SECRET=remplacer_par_64_caracteres_hexadecimaux_aleatoires_minimum
  JWT_REFRESH_SECRET=remplacer_par_64_caracteres_hexadecimaux_differents_du_premier
  FIELD_ENCRYPTION_KEY=remplacer_par_32_octets_encodes_en_base64_pour_aes_256_gcm
  REVALIDATE_WEBHOOK_SECRET=remplacer_par_secret_partage_entre_api_et_nextjs_web
  MEILI_KEY=remplacer_par_cle_maitre_meilisearch_32_caracteres
  S3_ENDPOINT=http://127.0.0.1:9000
  S3_BUCKET_STAGING=sodexam-staging-private
  S3_BUCKET_PUBLIC=sodexam-public-validated
  S3_KEY=sodexam_minio_admin
  S3_SECRET=remplacer_par_secret_minio_robuste
  PUBLIC_SITE_URL=http://localhost:3000
  ADMIN_URL=http://localhost:3001
  ```

- [ ] **Étape 4 : Lancer le test pour vérifier la réussite**
  Commande : `pnpm --filter @sodexam/shared test packages/shared/tests/infra-config.spec.ts`
  Attendu : Réussite (2 tests PASS).

- [ ] **Étape 5 : Faire un commit**
  ```bash
  git add pnpm-workspace.yaml tsconfig.base.json package.json infra/docker-compose.yml .env.example packages/shared/package.json packages/shared/tests/infra-config.spec.ts
  git commit -m "chore(infra): initialise pnpm monorepo and 127.0.0.1 docker services"
  ```

---

### Tâche 2 : Machine à États du Workflow de Validation Admin et Sécurité Antivirus (`packages/shared/src/workflow.ts`)

**Fichiers :**
- Créer : `packages/shared/src/workflow.ts`
- Tester : `packages/shared/tests/workflow.spec.ts`

**Interfaces :**
- Consomme : Aucune dépendance externe
- Produit :
  - Types : `Role`, `ContentStatus`, `ScanStatus`, `CategoryScope`
  - Fonctions :
    - `canTransition(role: Role, from: ContentStatus, to: ContentStatus): boolean`
    - `assertPublicationAllowed(params: { role: Role; from: ContentStatus; to: ContentStatus; assetScanStatuses: ScanStatus[] }): { allowed: true } | { allowed: false; reason: string }`

- [ ] **Étape 1 : Écrire le test qui échoue**
  Créer `packages/shared/tests/workflow.spec.ts` :
  ```ts
  import { describe, it, expect } from 'vitest';
  import {
    ROLES,
    CONTENT_STATUSES,
    SCAN_STATUSES,
    canTransition,
    assertPublicationAllowed,
  } from '../src/workflow';

  describe('Editorial & Document Validation Workflow', () => {
    it('forbids REDACTEUR and EDITEUR from transitioning directly to PUBLIE', () => {
      expect(canTransition(ROLES.REDACTEUR, CONTENT_STATUSES.BROUILLON, CONTENT_STATUSES.PUBLIE)).toBe(false);
      expect(canTransition(ROLES.REDACTEUR, CONTENT_STATUSES.EN_RELECTURE, CONTENT_STATUSES.PUBLIE)).toBe(false);
      expect(canTransition(ROLES.EDITEUR, CONTENT_STATUSES.EN_RELECTURE, CONTENT_STATUSES.PUBLIE)).toBe(false);
    });

    it('allows REDACTEUR to submit BROUILLON to EN_RELECTURE', () => {
      expect(canTransition(ROLES.REDACTEUR, CONTENT_STATUSES.BROUILLON, CONTENT_STATUSES.EN_RELECTURE)).toBe(true);
    });

    it('allows ONLY ADMIN to validate EN_RELECTURE or BROUILLON to PUBLIE', () => {
      expect(canTransition(ROLES.ADMIN, CONTENT_STATUSES.EN_RELECTURE, CONTENT_STATUSES.PUBLIE)).toBe(true);
      expect(canTransition(ROLES.ADMIN, CONTENT_STATUSES.BROUILLON, CONTENT_STATUSES.PUBLIE)).toBe(true);
    });

    it('blocks ADMIN from publishing if any attached document or cover image is PENDING or INFECTED', () => {
      const pendingResult = assertPublicationAllowed({
        role: ROLES.ADMIN,
        from: CONTENT_STATUSES.EN_RELECTURE,
        to: CONTENT_STATUSES.PUBLIE,
        assetScanStatuses: [SCAN_STATUSES.CLEAN, SCAN_STATUSES.PENDING],
      });
      expect(pendingResult).toEqual({
        allowed: false,
        reason: 'Tous les fichiers joints doivent avoir passé le scan antivirus ClamAV (statut CLEAN) avant publication.',
      });

      const infectedResult = assertPublicationAllowed({
        role: ROLES.ADMIN,
        from: CONTENT_STATUSES.EN_RELECTURE,
        to: CONTENT_STATUSES.PUBLIE,
        assetScanStatuses: [SCAN_STATUSES.INFECTED],
      });
      expect(infectedResult.allowed).toBe(false);
    });

    it('allows ADMIN to publish when transition is valid and all attached assets are CLEAN', () => {
      const cleanResult = assertPublicationAllowed({
        role: ROLES.ADMIN,
        from: CONTENT_STATUSES.EN_RELECTURE,
        to: CONTENT_STATUSES.PUBLIE,
        assetScanStatuses: [SCAN_STATUSES.CLEAN, SCAN_STATUSES.CLEAN],
      });
      expect(cleanResult).toEqual({ allowed: true });
    });
  });
  ```

- [ ] **Étape 2 : Lancer le test pour vérifier l'échec**
  Commande : `pnpm --filter @sodexam/shared test packages/shared/tests/workflow.spec.ts`
  Attendu : Échec avec `"Cannot find module '../src/workflow'"`.

- [ ] **Étape 3 : Écrire l'implémentation minimale**
  Créer `packages/shared/src/workflow.ts` :
  ```ts
  export const ROLES = {
    REDACTEUR: 'REDACTEUR',
    EDITEUR: 'EDITEUR',
    ADMIN: 'ADMIN',
  } as const;

  export type Role = (typeof ROLES)[keyof typeof ROLES];

  export const CONTENT_STATUSES = {
    BROUILLON: 'BROUILLON',
    EN_RELECTURE: 'EN_RELECTURE',
    REJETE: 'REJETE',
    PUBLIE: 'PUBLIE',
    ARCHIVE: 'ARCHIVE',
  } as const;

  export type ContentStatus = (typeof CONTENT_STATUSES)[keyof typeof CONTENT_STATUSES];

  export const SCAN_STATUSES = {
    PENDING: 'PENDING',
    CLEAN: 'CLEAN',
    INFECTED: 'INFECTED',
  } as const;

  export type ScanStatus = (typeof SCAN_STATUSES)[keyof typeof SCAN_STATUSES];

  export const CATEGORY_SCOPES = {
    ARTICLE: 'ARTICLE',
    DOCUMENT: 'DOCUMENT',
    BOTH: 'BOTH',
  } as const;

  export type CategoryScope = (typeof CATEGORY_SCOPES)[keyof typeof CATEGORY_SCOPES];

  const TRANSITIONS: Record<ContentStatus, Partial<Record<Role, readonly ContentStatus[]>>> = {
    BROUILLON: {
      REDACTEUR: ['EN_RELECTURE'],
      EDITEUR: ['EN_RELECTURE'],
      ADMIN: ['EN_RELECTURE', 'PUBLIE'],
    },
    EN_RELECTURE: {
      EDITEUR: ['BROUILLON', 'REJETE'],
      ADMIN: ['PUBLIE', 'REJETE', 'BROUILLON'],
    },
    REJETE: {
      REDACTEUR: ['BROUILLON'],
      EDITEUR: ['BROUILLON'],
      ADMIN: ['BROUILLON'],
    },
    PUBLIE: {
      ADMIN: ['ARCHIVE', 'BROUILLON'],
    },
    ARCHIVE: {
      ADMIN: ['BROUILLON'],
    },
  };

  export function canTransition(role: Role, from: ContentStatus, to: ContentStatus): boolean {
    return TRANSITIONS[from]?.[role]?.includes(to) ?? false;
  }

  export function assertPublicationAllowed(params: {
    role: Role;
    from: ContentStatus;
    to: ContentStatus;
    assetScanStatuses: ScanStatus[];
  }): { allowed: true } | { allowed: false; reason: string } {
    const { role, from, to, assetScanStatuses } = params;

    if (!canTransition(role, from, to)) {
      return {
        allowed: false,
        reason: `Transition non autorisée de ${from} vers ${to} pour le rôle ${role}.`,
      };
    }

    if (to === CONTENT_STATUSES.PUBLIE) {
      const hasUncleanAsset = assetScanStatuses.some((status) => status !== SCAN_STATUSES.CLEAN);
      if (hasUncleanAsset) {
        return {
          allowed: false,
          reason:
            'Tous les fichiers joints doivent avoir passé le scan antivirus ClamAV (statut CLEAN) avant publication.',
        };
      }
    }

    return { allowed: true };
  }
  ```

- [ ] **Étape 4 : Lancer le test pour vérifier la réussite**
  Commande : `pnpm --filter @sodexam/shared test packages/shared/tests/workflow.spec.ts`
  Attendu : Réussite (5 tests PASS).

- [ ] **Étape 5 : Faire un commit**
  ```bash
  git add packages/shared/src/workflow.ts packages/shared/tests/workflow.spec.ts
  git commit -m "feat(shared): add RBAC editorial workflow state machine and ClamAV publication guard"
  ```

---

### Tâche 3 : Schémas Zod Unifiés (`Catégorie`, `Article`, `Document`, `Transition`) dans `packages/shared`

**Fichiers :**
- Créer : `packages/shared/src/schemas.ts`
- Créer : `packages/shared/src/index.ts`
- Tester : `packages/shared/tests/schemas.spec.ts`

**Interfaces :**
- Consomme : `CONTENT_STATUSES`, `CATEGORY_SCOPES` depuis `packages/shared/src/workflow.ts`
- Produit :
  - `CreateCategorySchema`, `CreateArticleSchema`, `CreateDocumentSchema`, `TransitionContentSchema`
  - Types inférés : `CreateCategoryInput`, `CreateArticleInput`, `CreateDocumentInput`, `TransitionContentInput`

- [ ] **Étape 1 : Écrire le test qui échoue**
  Créer `packages/shared/tests/schemas.spec.ts` :
  ```ts
  import { describe, it, expect } from 'vitest';
  import {
    CreateCategorySchema,
    CreateArticleSchema,
    CreateDocumentSchema,
    TransitionContentSchema,
  } from '../src/index';

  describe('Shared Zod Schemas (Articles, Documents, Categories)', () => {
    it('validates a well-formed SODEXAM category with hex color and slug', () => {
      const parsed = CreateCategorySchema.safeParse({
        name: 'Navigation Aérienne & Aéroports Régionaux',
        slug: 'navigation-aerienne-aeroports-regionaux',
        color: '#1E7A3C',
        scope: 'BOTH',
        order: 2,
      });
      expect(parsed.success).toBe(true);
    });

    it('rejects category with invalid slug or invalid hex color', () => {
      const invalid = CreateCategorySchema.safeParse({
        name: 'Météo',
        slug: 'Météo Avec Espaces!',
        color: 'orange',
        scope: 'BOTH',
      });
      expect(invalid.success).toBe(false);
    });

    it('validates a document attached to a category and optional article', () => {
      const doc = CreateDocumentSchema.safeParse({
        title: "Magazine L'Aérien N°84",
        slug: 'magazine-l-aerien-n84',
        description: 'Spécial inauguration du bâtiment Général Abdoulaye Coulibaly',
        issueNumber: 'N°84',
        publicationYear: 2026,
        categoryId: 'cat_aerien_01',
        fileAssetId: 'asset_pdf_84',
        coverAssetId: 'asset_cover_84',
      });
      expect(doc.success).toBe(true);
    });

    it('requires a rejectionReason of at least 10 characters when transitioning to REJETE', () => {
      const missingReason = TransitionContentSchema.safeParse({
        targetStatus: 'REJETE',
      });
      expect(missingReason.success).toBe(false);

      const validRejection = TransitionContentSchema.safeParse({
        targetStatus: 'REJETE',
        rejectionReason: 'Le document PDF joint ne correspond pas à la version finale signée.',
      });
      expect(validRejection.success).toBe(true);
    });

    it('allows transitioning to PUBLIE with cascadePublishDocuments flag', () => {
      const validPublish = TransitionContentSchema.safeParse({
        targetStatus: 'PUBLIE',
        cascadePublishDocuments: true,
      });
      expect(validPublish.success).toBe(true);
    });
  });
  ```

- [ ] **Étape 2 : Lancer le test pour vérifier l'échec**
  Commande : `pnpm --filter @sodexam/shared test packages/shared/tests/schemas.spec.ts`
  Attendu : Échec avec `"Cannot find module '../src/index'"`.

- [ ] **Étape 3 : Écrire l'implémentation minimale**
  Créer `packages/shared/src/schemas.ts` :
  ```ts
  import { z } from 'zod';
  import { CATEGORY_SCOPES, CONTENT_STATUSES } from './workflow';

  const slugRegex = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
  const hexColorRegex = /^#[0-9A-Fa-f]{6}$/;

  export const CreateCategorySchema = z.object({
    name: z.string().trim().min(3).max(120),
    slug: z.string().trim().regex(slugRegex, 'Slug invalide (minuscules, chiffres et tirets uniquement)'),
    description: z.string().trim().max(500).optional(),
    color: z.string().regex(hexColorRegex, 'Couleur hexadécimale requise (#RRGGBB)').default('#F26A21'),
    scope: z.enum([CATEGORY_SCOPES.ARTICLE, CATEGORY_SCOPES.DOCUMENT, CATEGORY_SCOPES.BOTH]).default('BOTH'),
    order: z.number().int().min(0).max(100).default(0),
  });

  export type CreateCategoryInput = z.infer<typeof CreateCategorySchema>;

  export const CreateArticleSchema = z.object({
    title: z.string().trim().min(5).max(220),
    slug: z.string().trim().regex(slugRegex, 'Slug invalide'),
    excerpt: z.string().trim().min(20).max(600),
    contentJson: z.record(z.string(), z.unknown()),
    rawHtml: z.string().min(1),
    categoryId: z.string().trim().min(1),
    coverAssetId: z.string().trim().min(1).optional(),
    isFeatured: z.boolean().default(false),
    attachedDocumentIds: z.array(z.string().trim().min(1)).default([]),
  });

  export type CreateArticleInput = z.infer<typeof CreateArticleSchema>;

  export const CreateDocumentSchema = z.object({
    title: z.string().trim().min(3).max(200),
    slug: z.string().trim().regex(slugRegex, 'Slug invalide'),
    description: z.string().trim().max(1000).optional(),
    issueNumber: z.string().trim().max(30).optional(),
    publicationYear: z.number().int().min(1997).max(2100),
    categoryId: z.string().trim().min(1),
    fileAssetId: z.string().trim().min(1),
    coverAssetId: z.string().trim().min(1).optional(),
    articleId: z.string().trim().min(1).optional(),
  });

  export type CreateDocumentInput = z.infer<typeof CreateDocumentSchema>;

  export const TransitionContentSchema = z
    .object({
      targetStatus: z.enum([
        CONTENT_STATUSES.BROUILLON,
        CONTENT_STATUSES.EN_RELECTURE,
        CONTENT_STATUSES.REJETE,
        CONTENT_STATUSES.PUBLIE,
        CONTENT_STATUSES.ARCHIVE,
      ]),
      rejectionReason: z.string().trim().min(10).max(1000).optional(),
      cascadePublishDocuments: z.boolean().default(false),
    })
    .superRefine((data, ctx) => {
      if (data.targetStatus === CONTENT_STATUSES.REJETE && !data.rejectionReason) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ['rejectionReason'],
          message: 'Un motif de rejet d’au moins 10 caractères est obligatoire.',
        });
      }
    });

  export type TransitionContentInput = z.infer<typeof TransitionContentSchema>;
  ```

  Créer `packages/shared/src/index.ts` :
  ```ts
  export * from './workflow';
  export * from './schemas';
  ```

- [ ] **Étape 4 : Lancer le test pour vérifier la réussite**
  Commande : `pnpm --filter @sodexam/shared test packages/shared/tests/schemas.spec.ts`
  Attendu : Réussite (5 tests PASS).

- [ ] **Étape 5 : Faire un commit**
  ```bash
  git add packages/shared/src/schemas.ts packages/shared/src/index.ts packages/shared/tests/schemas.spec.ts
  git commit -m "feat(shared): add unified Zod validation schemas for categories, articles and documents"
  ```

---

### Tâche 4 : Schéma Prisma Complet (`apps/api/prisma/schema.prisma`) et Catégories Initiales SODEXAM (`seed.ts`)

**Fichiers :**
- Créer : `apps/api/package.json`
- Créer : `apps/api/prisma/schema.prisma`
- Créer : `apps/api/src/prisma/seed-data.ts`
- Tester : `apps/api/tests/prisma-schema.spec.ts`

**Interfaces :**
- Consomme : `@sodexam/shared` (`CATEGORY_SCOPES`, `CreateCategorySchema`)
- Produit :
  - Schéma de base de données PostgreSQL complet (`User`, `Category`, `Article`, `Document`, `Asset`, `AuditLog`)
  - `INITIAL_SODEXAM_CATEGORIES` validé contre `CreateCategorySchema` (incluant la fusion *Navigation Aérienne & Aéroports Régionaux*)

- [ ] **Étape 1 : Écrire le test qui échoue**
  Créer `apps/api/package.json` :
  ```json
  {
    "name": "@sodexam/api",
    "version": "1.0.0",
    "private": true,
    "type": "module",
    "scripts": {
      "test": "vitest run"
    },
    "dependencies": {
      "@sodexam/shared": "workspace:*",
      "sanitize-html": "^2.13.1"
    },
    "devDependencies": {
      "@types/node": "^22.7.5",
      "@types/sanitize-html": "^2.13.0",
      "typescript": "^5.6.3",
      "vitest": "^2.1.3"
    }
  }
  ```

  Créer `apps/api/tests/prisma-schema.spec.ts` :
  ```ts
  import { describe, it, expect } from 'vitest';
  import { readFileSync, existsSync } from 'node:fs';
  import { resolve } from 'node:path';
  import { CreateCategorySchema } from '@sodexam/shared';
  import { INITIAL_SODEXAM_CATEGORIES } from '../src/prisma/seed-data';

  describe('Prisma Schema & Official SODEXAM Categories Seed', () => {
    it('defines all required models and composite indexes in schema.prisma', () => {
      const schemaPath = resolve(__dirname, '../prisma/schema.prisma');
      expect(existsSync(schemaPath)).toBe(true);
      const schema = readFileSync(schemaPath, 'utf-8');

      expect(schema).toContain('model User {');
      expect(schema).toContain('model Category {');
      expect(schema).toContain('model Article {');
      expect(schema).toContain('model Document {');
      expect(schema).toContain('model Asset {');
      expect(schema).toContain('model AuditLog {');
      expect(schema).toContain('@@index([status, categoryId, publishedAt(sort: Desc)])');
      expect(schema).toContain('@@index([status, categoryId, publicationYear(sort: Desc)])');
    });

    it('provides valid initial SODEXAM categories with merged Navigation Aérienne & Aéroports Régionaux', () => {
      expect(INITIAL_SODEXAM_CATEGORIES.length).toBeGreaterThanOrEqual(5);

      for (const category of INITIAL_SODEXAM_CATEGORIES) {
        const parsed = CreateCategorySchema.safeParse(category);
        expect(parsed.success, `Category ${category.slug} failed Zod validation`).toBe(true);
      }

      const slugs = INITIAL_SODEXAM_CATEGORIES.map((c) => c.slug);
      expect(slugs).toContain('navigation-aerienne-aeroports-regionaux');
      expect(slugs).toContain('magazine-l-aerien');
      expect(slugs).toContain('meteorologie-climat');
      expect(slugs).toContain('medecine-aeronautique-cerma');
    });
  });
  ```

- [ ] **Étape 2 : Lancer le test pour vérifier l'échec**
  Commande : `pnpm --filter @sodexam/api test apps/api/tests/prisma-schema.spec.ts`
  Attendu : Échec avec `"Cannot find module '../src/prisma/seed-data'"`.

- [ ] **Étape 3 : Écrire l'implémentation minimale**
  Créer `apps/api/prisma/schema.prisma` :
  ```prisma
  generator client {
    provider = "prisma-client-js"
  }

  datasource db {
    provider = "postgresql"
    url      = env("DATABASE_URL")
  }

  enum Role {
    REDACTEUR
    EDITEUR
    ADMIN
  }

  enum ContentStatus {
    BROUILLON
    EN_RELECTURE
    REJETE
    PUBLIE
    ARCHIVE
  }

  enum ScanStatus {
    PENDING
    CLEAN
    INFECTED
  }

  enum CategoryScope {
    ARTICLE
    DOCUMENT
    BOTH
  }

  model User {
    id               String     @id @default(cuid())
    email            String     @unique
    fullName         String
    passwordHash     String
    role             Role       @default(REDACTEUR)
    totpSecretEnc    String?
    isTotpEnabled    Boolean    @default(false)
    isActive         Boolean    @default(true)

    authoredArticles  Article[]  @relation("ArticleAuthor")
    validatedArticles Article[]  @relation("ArticleValidator")
    authoredDocs      Document[] @relation("DocAuthor")
    validatedDocs     Document[] @relation("DocValidator")
    auditLogs         AuditLog[]

    createdAt        DateTime   @default(now())
    updatedAt        DateTime   @updatedAt
  }

  model Category {
    id          String        @id @default(cuid())
    name        String
    slug        String        @unique
    description String?
    color       String        @default("#F26A21")
    scope       CategoryScope @default(BOTH)
    order       Int           @default(0)
    isActive    Boolean       @default(true)

    articles    Article[]
    documents   Document[]

    createdAt   DateTime      @default(now())
    updatedAt   DateTime      @updatedAt
  }

  model Article {
    id              String        @id @default(cuid())
    title           String
    slug            String        @unique
    excerpt         String        @db.Text
    contentJson     Json
    contentHtml     String        @db.Text
    coverAssetId    String?
    coverAsset      Asset?        @relation("ArticleCover", fields: [coverAssetId], references: [id])

    status          ContentStatus @default(BROUILLON)
    rejectionReason String?       @db.Text
    isFeatured      Boolean       @default(false)

    categoryId      String
    category        Category      @relation(fields: [categoryId], references: [id])

    authorId        String
    author          User          @relation("ArticleAuthor", fields: [authorId], references: [id])
    validatorId     String?
    validator       User?         @relation("ArticleValidator", fields: [validatorId], references: [id])
    publishedAt     DateTime?

    documents       Document[]

    createdAt       DateTime      @default(now())
    updatedAt       DateTime      @updatedAt

    @@index([status, categoryId, publishedAt(sort: Desc)])
  }

  model Document {
    id              String        @id @default(cuid())
    title           String
    slug            String        @unique
    description     String?       @db.Text
    issueNumber     String?
    publicationYear Int

    fileAssetId     String        @unique
    fileAsset       Asset         @relation("DocumentFile", fields: [fileAssetId], references: [id])
    coverAssetId    String?
    coverAsset      Asset?        @relation("DocumentCover", fields: [coverAssetId], references: [id])

    status          ContentStatus @default(BROUILLON)
    rejectionReason String?       @db.Text
    downloadCount   Int           @default(0)

    categoryId      String
    category        Category      @relation(fields: [categoryId], references: [id])

    articleId       String?
    article         Article?      @relation(fields: [articleId], references: [id], onDelete: SetNull)

    authorId        String
    author          User          @relation("DocAuthor", fields: [authorId], references: [id])
    validatorId     String?
    validator       User?         @relation("DocValidator", fields: [validatorId], references: [id])
    publishedAt     DateTime?

    createdAt       DateTime      @default(now())
    updatedAt       DateTime      @updatedAt

    @@index([status, categoryId, publicationYear(sort: Desc)])
  }

  model Asset {
    id             String     @id @default(cuid())
    originalName   String
    storageKey     String     @unique
    mimeType       String
    sizeBytes      Int
    sha256         String
    scanStatus     ScanStatus @default(PENDING)
    isPublic       Boolean    @default(false)

    articleCovers  Article[]  @relation("ArticleCover")
    documentFiles  Document?  @relation("DocumentFile")
    documentCovers Document[] @relation("DocumentCover")

    createdAt      DateTime   @default(now())
  }

  model AuditLog {
    id         String   @id @default(cuid())
    actorId    String
    actor      User     @relation(fields: [actorId], references: [id])
    action     String
    entityType String
    entityId   String
    metadata   Json
    ipAddress  String?
    createdAt  DateTime @default(now())

    @@index([entityType, entityId, createdAt(sort: Desc)])
  }
  ```

  Créer `apps/api/src/prisma/seed-data.ts` :
  ```ts
  import { CreateCategoryInput } from '@sodexam/shared';

  export const INITIAL_SODEXAM_CATEGORIES: CreateCategoryInput[] = [
    {
      name: 'Météorologie Nationale & Climat',
      slug: 'meteorologie-climat',
      description: 'Bulletins Vigiclim, stations synoptiques, radars Doppler et agrométéorologie.',
      color: '#F26A21',
      scope: 'BOTH',
      order: 1,
    },
    {
      name: 'Navigation Aérienne & Aéroports Régionaux',
      slug: 'navigation-aerienne-aeroports-regionaux',
      description:
        'Surveillance de l’espace aérien, radars, pistes et exploitation des plateformes aéroportuaires intérieures.',
      color: '#1E7A3C',
      scope: 'BOTH',
      order: 2,
    },
    {
      name: 'Médecine Aéronautique (CERMA)',
      slug: 'medecine-aeronautique-cerma',
      description: 'Expertise médicale du personnel navigant, examens d’aptitude OACI et prévention.',
      color: '#0284C7',
      scope: 'BOTH',
      order: 3,
    },
    {
      name: "Magazine L'Aérien",
      slug: 'magazine-l-aerien',
      description: 'Revue bimestrielle officielle de la SODEXAM téléchargeable en PDF après validation.',
      color: '#0F172A',
      scope: 'DOCUMENT',
      order: 4,
    },
    {
      name: 'Communiqués Officiels & Gouvernance',
      slug: 'communiques-officiels-gouvernance',
      description: 'Décisions du Conseil d’Administration, Direction Générale, RSE et partenariats stratégiques.',
      color: '#E11D48',
      scope: 'BOTH',
      order: 5,
    },
  ];
  ```

- [ ] **Étape 4 : Lancer le test pour vérifier la réussite**
  Commande : `pnpm --filter @sodexam/api test apps/api/tests/prisma-schema.spec.ts`
  Attendu : Réussite (2 tests PASS).

- [ ] **Étape 5 : Faire un commit**
  ```bash
  git add apps/api/package.json apps/api/prisma/schema.prisma apps/api/src/prisma/seed-data.ts apps/api/tests/prisma-schema.spec.ts
  git commit -m "feat(api): add Prisma schema for articles/documents workflow and official SODEXAM categories"
  ```

---

### Tâche 5 : Services de Sécurité (`SanitizeService` Anti-XSS TipTap & `CryptoService` AES-256-GCM)

**Fichiers :**
- Créer : `apps/api/src/common/sanitize.service.ts`
- Créer : `apps/api/src/common/crypto.service.ts`
- Tester : `apps/api/tests/security-services.spec.ts`

**Interfaces :**
- Consomme : Bibliothèque `sanitize-html` et module natif `node:crypto`
- Produit :
  - `SanitizeService.cleanArticleHtml(dirtyHtml: string): string`
  - `CryptoService.encrypt(plainText: string): string`
  - `CryptoService.decrypt(cipherPayload: string): string`

- [ ] **Étape 1 : Écrire le test qui échoue**
  Créer `apps/api/tests/security-services.spec.ts` :
  ```ts
  import { describe, it, expect } from 'vitest';
  import { randomBytes } from 'node:crypto';
  import { SanitizeService } from '../src/common/sanitize.service';
  import { CryptoService } from '../src/common/crypto.service';

  describe('Security Services: HTML Sanitization & Field Encryption', () => {
    it('strips malicious <script>, onerror handlers and javascript: URLs while preserving semantic article tags', () => {
      const sanitizer = new SanitizeService();
      const maliciousHtml = `
        <h2>Visite de l'Aéroport de San Pedro</h2>
        <p onclick="stealAdminCookie()">Rapport officiel <strong>SODEXAM</strong>.</p>
        <img src="https://sodexam.com/photo.jpg" onerror="fetch('https://evil.ci/hack')" alt="Tarmac" />
        <a href="javascript:alert(1)">Télécharger</a>
        <script>window.location='https://evil.ci'</script>
      `;

      const cleaned = sanitizer.cleanArticleHtml(maliciousHtml);
      expect(cleaned).toContain("<h2>Visite de l'Aéroport de San Pedro</h2>");
      expect(cleaned).toContain('<p>Rapport officiel <strong>SODEXAM</strong>.</p>');
      expect(cleaned).toContain('<img src="https://sodexam.com/photo.jpg" alt="Tarmac" />');
      expect(cleaned).not.toContain('script');
      expect(cleaned).not.toContain('onerror');
      expect(cleaned).not.toContain('onclick');
      expect(cleaned).not.toContain('javascript:');
    });

    it('encrypts and decrypts sensitive CERMA medical appointment fields using AES-256-GCM with unique IVs', () => {
      const keyBase64 = randomBytes(32).toString('base64');
      const cryptoService = new CryptoService(keyBase64);

      const secretMedicalNote = 'Visite médicale Classe 1 Pilote - Dossier #CI-2026-889';
      const encryptedA = cryptoService.encrypt(secretMedicalNote);
      const encryptedB = cryptoService.encrypt(secretMedicalNote);

      expect(encryptedA).not.toBe(secretMedicalNote);
      expect(encryptedA).not.toBe(encryptedB);
      expect(cryptoService.decrypt(encryptedA)).toBe(secretMedicalNote);
      expect(cryptoService.decrypt(encryptedB)).toBe(secretMedicalNote);
    });

    it('throws an integrity error if AES-256-GCM authentication tag is tampered with', () => {
      const keyBase64 = randomBytes(32).toString('base64');
      const cryptoService = new CryptoService(keyBase64);
      const encrypted = cryptoService.encrypt('Données confidentielles');
      const parts = encrypted.split(':');
      parts[2] = parts[2].slice(0, -2) + 'ff';

      expect(() => cryptoService.decrypt(parts.join(':'))).toThrow();
    });
  });
  ```

- [ ] **Étape 2 : Lancer le test pour vérifier l'échec**
  Commande : `pnpm --filter @sodexam/api test apps/api/tests/security-services.spec.ts`
  Attendu : Échec avec `"Cannot find module '../src/common/sanitize.service'"`.

- [ ] **Étape 3 : Écrire l'implémentation minimale**
  Créer `apps/api/src/common/sanitize.service.ts` :
  ```ts
  import sanitizeHtml from 'sanitize-html';

  export class SanitizeService {
    cleanArticleHtml(dirtyHtml: string): string {
      return sanitizeHtml(dirtyHtml, {
        allowedTags: [
          'h2',
          'h3',
          'h4',
          'p',
          'strong',
          'em',
          'u',
          'ul',
          'ol',
          'li',
          'blockquote',
          'a',
          'img',
          'table',
          'thead',
          'tbody',
          'tr',
          'th',
          'td',
          'br',
          'figure',
          'figcaption',
        ],
        allowedAttributes: {
          a: ['href', 'title', 'target', 'rel'],
          img: ['src', 'alt', 'title', 'width', 'height', 'loading'],
        },
        allowedSchemes: ['http', 'https', 'mailto', 'tel'],
        transformTags: {
          a: sanitizeHtml.simpleTransform('a', {
            rel: 'noopener noreferrer',
          }),
        },
      });
    }
  }
  ```

  Créer `apps/api/src/common/crypto.service.ts` :
  ```ts
  import { createCipheriv, createDecipheriv, randomBytes } from 'node:crypto';

  export class CryptoService {
    private readonly key: Buffer;

    constructor(base64Key: string) {
      this.key = Buffer.from(base64Key, 'base64');
      if (this.key.length !== 32) {
        throw new Error('FIELD_ENCRYPTION_KEY must be exactly 32 bytes encoded in base64 for AES-256-GCM.');
      }
    }

    encrypt(plainText: string): string {
      const iv = randomBytes(12);
      const cipher = createCipheriv('aes-256-gcm', this.key, iv);
      const encrypted = Buffer.concat([cipher.update(plainText, 'utf8'), cipher.final()]);
      const authTag = cipher.getAuthTag();

      return `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted.toString('hex')}`;
    }

    decrypt(cipherPayload: string): string {
      const parts = cipherPayload.split(':');
      if (parts.length !== 3) {
        throw new Error('Invalid encrypted payload format.');
      }
      const [ivHex, authTagHex, encryptedHex] = parts;
      const iv = Buffer.from(ivHex, 'hex');
      const authTag = Buffer.from(authTagHex, 'hex');
      const encrypted = Buffer.from(encryptedHex, 'hex');

      const decipher = createDecipheriv('aes-256-gcm', this.key, iv);
      decipher.setAuthTag(authTag);

      const decrypted = Buffer.concat([decipher.update(encrypted), decipher.final()]);
      return decrypted.toString('utf8');
    }
  }
  ```

- [ ] **Étape 4 : Lancer le test pour vérifier la réussite**
  Commande : `pnpm --filter @sodexam/api test apps/api/tests/security-services.spec.ts`
  Attendu : Réussite (3 tests PASS).

- [ ] **Étape 5 : Faire un commit**
  ```bash
  git add apps/api/src/common/sanitize.service.ts apps/api/src/common/crypto.service.ts apps/api/tests/security-services.spec.ts
  git commit -m "feat(security): add TipTap HTML sanitizer and AES-256-GCM field encryption service"
  ```

---

### Tâche 6 : Moteur Métier `ContentWorkflowService` (Articles & Documents par Catégorie, Validation Admin en Cascade, Visibilité Publique)

**Fichiers :**
- Créer : `apps/api/src/content/content-workflow.service.ts`
- Tester : `apps/api/tests/content-workflow.service.spec.ts`

**Interfaces :**
- Consomme :
  - `ROLES`, `CONTENT_STATUSES`, `SCAN_STATUSES`, `assertPublicationAllowed`, `CreateArticleSchema`, `CreateDocumentSchema`, `TransitionContentSchema` depuis `@sodexam/shared`
  - `SanitizeService` depuis `apps/api/src/common/sanitize.service.ts`
- Produit :
  - `ContentWorkflowService` avec :
    - `createDraftArticle(actorId, input)`
    - `createDraftDocument(actorId, input)`
    - `transitionArticleStatus(actor, articleId, transitionInput)` (avec validation en cascade des documents liés si l'Admin active `cascadePublishDocuments: true`, enregistrement dans `AuditLog` et déclenchement du callback de revalidation mobile ISR)
    - `transitionDocumentStatus(actor, documentId, transitionInput)`
    - `getPublicContentByCategory(categorySlug)` (retourne **uniquement** les articles et documents en statut `PUBLIE` dont tous les fichiers sont `CLEAN`)

- [ ] **Étape 1 : Écrire le test qui échoue**
  Créer `apps/api/tests/content-workflow.service.spec.ts` :
  ```ts
  import { describe, it, expect, beforeEach } from 'vitest';
  import { SanitizeService } from '../src/common/sanitize.service';
  import { ContentWorkflowService } from '../src/content/content-workflow.service';

  describe('ContentWorkflowService: Category Publishing & Admin Approval', () => {
    let service: ContentWorkflowService;
    let revalidatedTags: string[];

    beforeEach(() => {
      revalidatedTags = [];
      service = new ContentWorkflowService(new SanitizeService(), (tags) => {
        revalidatedTags.push(...tags);
      });

      service.seedCategory({
        id: 'cat_aerien',
        name: "Magazine L'Aérien",
        slug: 'magazine-l-aerien',
      });

      service.seedAsset({
        id: 'asset_pdf_clean',
        storageKey: 'staging/aerien-84.pdf',
        scanStatus: 'CLEAN',
      });

      service.seedAsset({
        id: 'asset_pdf_pending',
        storageKey: 'staging/aerien-85.pdf',
        scanStatus: 'PENDING',
      });
    });

    it('keeps newly created articles and documents invisible on the public category endpoint until ADMIN validation', () => {
      const doc = service.createDraftDocument('user_redacteur_1', {
        title: "Magazine L'Aérien N°84",
        slug: 'magazine-l-aerien-n84',
        publicationYear: 2026,
        categoryId: 'cat_aerien',
        fileAssetId: 'asset_pdf_clean',
      });

      const article = service.createDraftArticle('user_redacteur_1', {
        title: "Sortie officielle du Magazine L'Aérien N°84",
        slug: 'sortie-magazine-l-aerien-n84',
        excerpt: 'Découvrez le nouveau numéro consacré au siège Général Abdoulaye Coulibaly.',
        contentJson: { type: 'doc', content: [] },
        rawHtml: '<p>Contenu officiel<script>alert(1)</script></p>',
        categoryId: 'cat_aerien',
        isFeatured: true,
        attachedDocumentIds: [doc.id],
      });

      expect(article.contentHtml).toBe('<p>Contenu officiel</p>');
      expect(article.status).toBe('BROUILLON');
      expect(doc.status).toBe('BROUILLON');

      // Vérifie qu'aucun article ni document non validé n'est exposé au public
      const publicBefore = service.getPublicContentByCategory('magazine-l-aerien');
      expect(publicBefore.articles).toHaveLength(0);
      expect(publicBefore.documents).toHaveLength(0);

      // Le rédacteur soumet en relecture
      service.transitionArticleStatus(
        { id: 'user_redacteur_1', role: 'REDACTEUR' },
        article.id,
        { targetStatus: 'EN_RELECTURE', cascadePublishDocuments: false }
      );

      // Toujours invisible pour le public en statut EN_RELECTURE
      expect(service.getPublicContentByCategory('magazine-l-aerien').articles).toHaveLength(0);

      // L'administrateur valide l'article ET les documents joints en cascade
      const validated = service.transitionArticleStatus(
        { id: 'user_admin_1', role: 'ADMIN' },
        article.id,
        { targetStatus: 'PUBLIE', cascadePublishDocuments: true }
      );

      expect(validated.status).toBe('PUBLIE');
      expect(validated.validatorId).toBe('user_admin_1');
      expect(validated.publishedAt).toBeInstanceOf(Date);

      // Désormais disponible publiquement dans la catégorie !
      const publicAfter = service.getPublicContentByCategory('magazine-l-aerien');
      expect(publicAfter.articles).toHaveLength(1);
      expect(publicAfter.documents).toHaveLength(1);
      expect(publicAfter.documents[0].validatorId).toBe('user_admin_1');

      // Vérifie que le cache mobile Next.js ISR a été invalidé
      expect(revalidatedTags).toContain('category:magazine-l-aerien');

      // Vérifie la trace d'audit
      const logs = service.getAuditLogs();
      expect(logs.some((l) => l.action === 'ARTICLE_TRANSITION_PUBLIE' && l.actorId === 'user_admin_1')).toBe(true);
    });

    it('prevents ADMIN from validating a document whose PDF has not finished ClamAV scan', () => {
      const pendingDoc = service.createDraftDocument('user_redacteur_1', {
        title: "Magazine L'Aérien N°85",
        slug: 'magazine-l-aerien-n85',
        publicationYear: 2026,
        categoryId: 'cat_aerien',
        fileAssetId: 'asset_pdf_pending',
      });

      expect(() =>
        service.transitionDocumentStatus(
          { id: 'user_admin_1', role: 'ADMIN' },
          pendingDoc.id,
          { targetStatus: 'PUBLIE', cascadePublishDocuments: false }
        )
      ).toThrow(/ClamAV/);
    });
  });
  ```

- [ ] **Étape 2 : Lancer le test pour vérifier l'échec**
  Commande : `pnpm --filter @sodexam/api test apps/api/tests/content-workflow.service.spec.ts`
  Attendu : Échec avec `"Cannot find module '../src/content/content-workflow.service'"`.

- [ ] **Étape 3 : Écrire l'implémentation minimale**
  Créer `apps/api/src/content/content-workflow.service.ts` :
  ```ts
  import {
    Role,
    ContentStatus,
    ScanStatus,
    CONTENT_STATUSES,
    SCAN_STATUSES,
    CreateArticleSchema,
    CreateArticleInput,
    CreateDocumentSchema,
    CreateDocumentInput,
    TransitionContentSchema,
    TransitionContentInput,
    assertPublicationAllowed,
  } from '@sodexam/shared';
  import { SanitizeService } from '../common/sanitize.service';

  export interface CategoryRecord {
    id: string;
    name: string;
    slug: string;
  }

  export interface AssetRecord {
    id: string;
    storageKey: string;
    scanStatus: ScanStatus;
    isPublic: boolean;
  }

  export interface ArticleRecord {
    id: string;
    title: string;
    slug: string;
    excerpt: string;
    contentJson: Record<string, unknown>;
    contentHtml: string;
    categoryId: string;
    coverAssetId?: string;
    status: ContentStatus;
    rejectionReason?: string;
    isFeatured: boolean;
    authorId: string;
    validatorId?: string;
    publishedAt?: Date;
    attachedDocumentIds: string[];
  }

  export interface DocumentRecord {
    id: string;
    title: string;
    slug: string;
    description?: string;
    issueNumber?: string;
    publicationYear: number;
    categoryId: string;
    fileAssetId: string;
    coverAssetId?: string;
    articleId?: string;
    status: ContentStatus;
    rejectionReason?: string;
    authorId: string;
    validatorId?: string;
    publishedAt?: Date;
  }

  export interface AuditLogEntry {
    actorId: string;
    action: string;
    entityType: 'ARTICLE' | 'DOCUMENT';
    entityId: string;
    metadata: Record<string, unknown>;
    createdAt: Date;
  }

  export class ContentWorkflowService {
    private categories = new Map<string, CategoryRecord>();
    private assets = new Map<string, AssetRecord>();
    private articles = new Map<string, ArticleRecord>();
    private documents = new Map<string, DocumentRecord>();
    private auditLogs: AuditLogEntry[] = [];

    constructor(
      private readonly sanitizeService: SanitizeService,
      private readonly onRevalidateTags: (tags: string[]) => void = () => {}
    ) {}

    seedCategory(category: CategoryRecord): void {
      this.categories.set(category.id, category);
    }

    seedAsset(asset: { id: string; storageKey: string; scanStatus: ScanStatus }): void {
      this.assets.set(asset.id, { ...asset, isPublic: false });
    }

    createDraftArticle(authorId: string, rawInput: CreateArticleInput): ArticleRecord {
      const input = CreateArticleSchema.parse(rawInput);
      if (!this.categories.has(input.categoryId)) {
        throw new Error(`Catégorie introuvable : ${input.categoryId}`);
      }

      const id = `art_${this.articles.size + 1}`;
      const sanitizedHtml = this.sanitizeService.cleanArticleHtml(input.rawHtml);

      const record: ArticleRecord = {
        id,
        title: input.title,
        slug: input.slug,
        excerpt: input.excerpt,
        contentJson: input.contentJson,
        contentHtml: sanitizedHtml,
        categoryId: input.categoryId,
        coverAssetId: input.coverAssetId,
        status: CONTENT_STATUSES.BROUILLON,
        isFeatured: input.isFeatured,
        authorId,
        attachedDocumentIds: input.attachedDocumentIds,
      };

      this.articles.set(id, record);
      return record;
    }

    createDraftDocument(authorId: string, rawInput: CreateDocumentInput): DocumentRecord {
      const input = CreateDocumentSchema.parse(rawInput);
      if (!this.categories.has(input.categoryId)) {
        throw new Error(`Catégorie introuvable : ${input.categoryId}`);
      }
      if (!this.assets.has(input.fileAssetId)) {
        throw new Error(`Fichier Asset introuvable : ${input.fileAssetId}`);
      }

      const id = `doc_${this.documents.size + 1}`;
      const record: DocumentRecord = {
        id,
        title: input.title,
        slug: input.slug,
        description: input.description,
        issueNumber: input.issueNumber,
        publicationYear: input.publicationYear,
        categoryId: input.categoryId,
        fileAssetId: input.fileAssetId,
        coverAssetId: input.coverAssetId,
        articleId: input.articleId,
        status: CONTENT_STATUSES.BROUILLON,
        authorId,
      };

      this.documents.set(id, record);
      return record;
    }

    transitionDocumentStatus(
      actor: { id: string; role: Role },
      documentId: string,
      rawTransition: TransitionContentInput
    ): DocumentRecord {
      const transition = TransitionContentSchema.parse(rawTransition);
      const doc = this.documents.get(documentId);
      if (!doc) {
        throw new Error(`Document introuvable : ${documentId}`);
      }

      const assetStatuses: ScanStatus[] = [];
      const fileAsset = this.assets.get(doc.fileAssetId);
      if (fileAsset) assetStatuses.push(fileAsset.scanStatus);
      if (doc.coverAssetId) {
        const coverAsset = this.assets.get(doc.coverAssetId);
        if (coverAsset) assetStatuses.push(coverAsset.scanStatus);
      }

      const check = assertPublicationAllowed({
        role: actor.role,
        from: doc.status,
        to: transition.targetStatus,
        assetScanStatuses: assetStatuses,
      });

      if (!check.allowed) {
        throw new Error(check.reason);
      }

      const previousStatus = doc.status;
      doc.status = transition.targetStatus;
      doc.rejectionReason = transition.rejectionReason;

      if (transition.targetStatus === CONTENT_STATUSES.PUBLIE) {
        doc.validatorId = actor.id;
        doc.publishedAt = new Date();
        if (fileAsset) fileAsset.isPublic = true;
      }

      this.auditLogs.push({
        actorId: actor.id,
        action: `DOCUMENT_TRANSITION_${transition.targetStatus}`,
        entityType: 'DOCUMENT',
        entityId: doc.id,
        metadata: { from: previousStatus, to: transition.targetStatus },
        createdAt: new Date(),
      });

      const category = this.categories.get(doc.categoryId);
      if (category && transition.targetStatus === CONTENT_STATUSES.PUBLIE) {
        this.onRevalidateTags(['documents', `category:${category.slug}`]);
      }

      return doc;
    }

    transitionArticleStatus(
      actor: { id: string; role: Role },
      articleId: string,
      rawTransition: TransitionContentInput
    ): ArticleRecord {
      const transition = TransitionContentSchema.parse(rawTransition);
      const article = this.articles.get(articleId);
      if (!article) {
        throw new Error(`Article introuvable : ${articleId}`);
      }

      const assetStatuses: ScanStatus[] = [];
      if (article.coverAssetId) {
        const cover = this.assets.get(article.coverAssetId);
        if (cover) assetStatuses.push(cover.scanStatus);
      }

      const check = assertPublicationAllowed({
        role: actor.role,
        from: article.status,
        to: transition.targetStatus,
        assetScanStatuses: assetStatuses,
      });

      if (!check.allowed) {
        throw new Error(check.reason);
      }

      const previousStatus = article.status;
      article.status = transition.targetStatus;
      article.rejectionReason = transition.rejectionReason;

      if (transition.targetStatus === CONTENT_STATUSES.PUBLIE) {
        article.validatorId = actor.id;
        article.publishedAt = new Date();

        if (transition.cascadePublishDocuments) {
          for (const docId of article.attachedDocumentIds) {
            const attachedDoc = this.documents.get(docId);
            if (attachedDoc && attachedDoc.status !== CONTENT_STATUSES.PUBLIE) {
              this.transitionDocumentStatus(actor, docId, {
                targetStatus: CONTENT_STATUSES.PUBLIE,
                cascadePublishDocuments: false,
              });
            }
          }
        }
      }

      this.auditLogs.push({
        actorId: actor.id,
        action: `ARTICLE_TRANSITION_${transition.targetStatus}`,
        entityType: 'ARTICLE',
        entityId: article.id,
        metadata: {
          from: previousStatus,
          to: transition.targetStatus,
          cascadePublishDocuments: transition.cascadePublishDocuments,
        },
        createdAt: new Date(),
      });

      const category = this.categories.get(article.categoryId);
      if (category && transition.targetStatus === CONTENT_STATUSES.PUBLIE) {
        this.onRevalidateTags(['articles', `category:${category.slug}`]);
      }

      return article;
    }

    getPublicContentByCategory(categorySlug: string): {
      category: CategoryRecord;
      articles: ArticleRecord[];
      documents: DocumentRecord[];
    } {
      const category = Array.from(this.categories.values()).find((c) => c.slug === categorySlug);
      if (!category) {
        throw new Error(`Catégorie introuvable : ${categorySlug}`);
      }

      const publishedArticles = Array.from(this.articles.values()).filter(
        (a) => a.categoryId === category.id && a.status === CONTENT_STATUSES.PUBLIE && Boolean(a.validatorId)
      );

      const publishedDocuments = Array.from(this.documents.values()).filter((d) => {
        if (d.categoryId !== category.id || d.status !== CONTENT_STATUSES.PUBLIE || !d.validatorId) {
          return false;
        }
        const asset = this.assets.get(d.fileAssetId);
        return asset?.scanStatus === SCAN_STATUSES.CLEAN && asset.isPublic === true;
      });

      return {
        category,
        articles: publishedArticles,
        documents: publishedDocuments,
      };
    }

    getAuditLogs(): AuditLogEntry[] {
      return [...this.auditLogs];
    }
  }
  ```

- [ ] **Étape 4 : Lancer le test pour vérifier la réussite**
  Commande : `pnpm --filter @sodexam/api test apps/api/tests/content-workflow.service.spec.ts`
  Attendu : Réussite (2 tests PASS).

- [ ] **Étape 5 : Faire un commit**
  ```bash
  git add apps/api/src/content/content-workflow.service.ts apps/api/tests/content-workflow.service.spec.ts
  git commit -m "feat(api): implement category content workflow with admin cascade approval and public isolation"
  ```

