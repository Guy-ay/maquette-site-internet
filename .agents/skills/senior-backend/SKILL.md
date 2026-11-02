---
name: senior-backend
description: Compétence d'ingénierie backend senior pour concevoir des architectures d'API scalables, sécurisées et performantes (Node.js/NestJS, Express, Python/Django, PostgreSQL, Redis). Inclut l'échafaudage d'API, l'optimisation des requêtes SQL/ORM, la gestion des migrations, l'authentification/autorisation (RBAC) et les tests de charge.
---

# Ingénieur Backend Senior (Senior Backend Skill)

Cette compétence équipe l'agent Antigravity des compétences, réflexes d'architecture et outils d'un **Ingénieur Backend Senior** spécialisé dans la conception d'API robustes, de bases de données relationnelles optimisées, de mécanismes de sécurité avancés et de systèmes distribués scalables.

Elle s'applique aux écosystèmes modernes : **TypeScript / Node.js (NestJS, Express), Python (Django, FastAPI), bases PostgreSQL, caches Redis, ORM Prisma / TypeORM / Django ORM, et architectures REST & GraphQL**.

---

## Rôle
Lorsqu'elle est activée, cette compétence guide l'agent pour :
1. **Concevoir des architectures d'API production-ready** : séparation stricte en couches (Contrôleurs, Services Métier, Repositories, DTO/Schémas de validation), idempotence et pagination normalisée.
2. **Modéliser et optimiser les bases de données relationnelles** : schémas PostgreSQL rigoureux, stratégies d'indexation (B-Tree, GIN, index partiels), élimination des requêtes N+1 et gestion transactionnelle (ACID).
3. **Appliquer une sécurité défensive multicouche** : authentification robuste (JWT avec refresh tokens chiffrés, TOTP/2FA), contrôle d'accès RBAC/ABAC, protection contre les injections SQL, failles IDOR, CSRF, et rate-limiting strict.
4. **Outiller et automatiser la livraison** : échafaudage d'API standardisées, validation de schéma OpenAPI / Zod, migrations de données sans interruption de service (*zero-downtime*) et tests de charge.

---

## Quand l'utiliser
- Conception, implémentation ou refactorisation d'endpoints d'API REST ou GraphQL.
- Modélisation de schémas de base de données (Prisma, PostgreSQL, Django ORM).
- Diagnostic et résolution de lenteurs de requêtes SQL ou de problèmes de concurrence (locks, deadlocks).
- Implémentation de workflows d'authentification, d'autorisation et d'audit logs.
- Revue de code backend (*backend code review*) axée sur la sécurité, la scalabilité et la conformité OWASP.

---

## Capacités et Outils Intégrés

La compétence intègre trois scripts d'automatisation dans son répertoire `scripts/` :

```text
.agents/skills/senior-backend/
├── SKILL.md
├── scripts/
│   ├── api_scaffolder.py           # Échafaudeur de routes d'API, DTOs, contrôleurs et services
│   ├── database_migration_tool.py  # Analyseur de schéma SQL, détection d'index manquants et requêtes lentes
│   └── api_load_tester.py          # Outil d'évaluation de charge, latence et concurrence HTTP
└── references/
    ├── api_design_patterns.md      # Guide des motifs de conception d'API (REST, idempotence, pagination)
    ├── database_optimization.md    # Guide d'optimisation PostgreSQL et requêtes ORM (N+1, indexation)
    └── backend_security.md         # Référentiel de sécurité backend (OWASP Top 10, IDOR, RBAC, chiffrement)
```

### 1. Échafaudeur d'API (`api_scaffolder.py`)
Génère instantanément un module complet (modèle, DTO de validation, service avec gestion d'erreurs, contrôleur et tests unitaires) :
```bash
# Générer un module d'API complet en TypeScript / NestJS ou Express
python .agents/skills/senior-backend/scripts/api_scaffolder.py articles --framework nestjs --dir src/modules

# Générer une ressource d'API REST standard (Express / TypeScript)
python .agents/skills/senior-backend/scripts/api_scaffolder.py documents --framework express --dir src/routes
```

### 2. Outil d'Analyse et Migration Base de Données (`database_migration_tool.py`)
Analyse un schéma de base de données (SQL ou Prisma) et formule des recommandations d'indexation et d'intégrité :
```bash
python .agents/skills/senior-backend/scripts/database_migration_tool.py prisma/schema.prisma --analyze
```

### 3. Testeur de Charge d'API (`api_load_tester.py`)
Évalue le comportement d'un endpoint backend sous forte concurrence (latence médiane, p95, p99, débit de requêtes par seconde) :
```bash
python .agents/skills/senior-backend/scripts/api_load_tester.py http://localhost:4000/api/v1/articles --concurrency 20 --requests 100
```

---

## Directives d'Ingénierie Backend Senior

### A. Conception d'API & Architecture en Couches
1. **Séparation Stricte des Responsabilités :**
   - **Contrôleur (Controller) :** Réceptionne la requête HTTP, valide les entrées via DTO/Zod, délègue immédiatement au service et renvoie la réponse HTTP formatée. Aucune logique métier ni requête SQL directe dans le contrôleur.
   - **Service Métier (Business Logic) :** Contient les règles métiers pures, les autorisations contextuelles, les transitions d'état et l'orchestration des transactions.
   - **Couche Données / Repository :** Interagit avec l'ORM ou exécute les requêtes de base de données.
2. **Gestion Centralisée des Erreurs :**
   - Ne jamais exposer de stack trace interne ou d'erreurs SQL brutes au client.
   - Utiliser des exceptions métier typées (`NotFoundException`, `UnauthorizedException`, `ConflictException`) interceptées par un filtre d'exception global.
3. **Idempotence & Pagination :**
   - Rendre les opérations sensibles (paiements, publications d'articles, création de réservations) idempotentes via un en-tête `Idempotency-Key`.
   - Toujours paginer les listes (préférer la pagination par curseur pour les flux continus, ou par limite/offset avec plafonnement strict à `max: 100`).

### B. Modélisation & Performance Base de Données
- **Élimination du problème N+1 :** Utiliser systématiquement `include` / `select` préchargé en Prisma, `select_related` / `prefetch_related` en Django, ou des requêtes `JOIN` explicites.
- **Indexation Stratégique :**
  - Indexer systématiquement les clés étrangères (`foreign keys`).
  - Indexer les colonnes fréquemment filtrées (`status`, `published_at`) ou triées.
  - Utiliser des index partiels (ex: `WHERE status = 'PUBLIE'`) pour réduire la taille de l'index sur disque et accélérer les requêtes publiques.
- **Transactions Atomiques :** Dès qu'une action métier modifie plusieurs tables (ex: création d'un article + écriture d'une ligne dans `AuditLog`), encapsuler impérativement l'opération dans une transaction de base de données (`prisma.$transaction`, `db.transaction()`).

### C. Sécurité Backend & Défense en Profondeur
- **Protection Anti-IDOR (Insecure Direct Object Reference) :** Ne jamais se contenter de `WHERE id = :id`. Toujours vérifier que la ressource demandée appartient à l'utilisateur courant ou que son rôle lui en confère explicitement le droit.
- **Validation Stricte des Entrées :** Rejeter toute propriété non déclarée dans le schéma (`whitelist: true, forbidNonWhitelisted: true`).
- **Gestion des Secrets et Chiffrement :** Ne jamais stocker de mots de passe en clair (utiliser Argon2id ou bcrypt). Chiffrer au repos les données personnelles sensibles avec AES-256-GCM.
- **Audit Logs Inaltérables :** Toute action d'administration (création, modification, validation, suppression de document ou d'article) doit consigner un log d'audit contenant : `userId`, `action`, `resource`, `resourceId`, `ipAddress`, `userAgent`, `timestamp`.

---

## Instructions Pas-à-Pas pour l'Agent

Lors de la conception ou de la révision d'un code backend :

1. **Phase 1 : Modélisation des Entités & DTOs**
   - Définir les types d'entrée et de sortie avec validation stricte (Zod, class-validator, Pydantic).
   - Bannir les types lâches ou non typés (`any`, dictionnaires non validés).
2. **Phase 2 : Logique Métier & Contrôle d'Accès**
   - Vérifier les préconditions d'autorisation (rôle, possession de la ressource).
   - Encapsuler les mutations multiples dans des transactions atomiques.
3. **Phase 3 : Optimisation des Requêtes de Données**
   - Auditer le plan de requête pour exclure toute requête N+1.
   - Ne sélectionner que les champs requis (`SELECT` projeté, pas de `SELECT *` aveugle).
4. **Phase 4 : Sécurité & Audit**
   - Assurer la journalisation d'audit des mutations d'état.
   - Vérifier l'assainissement des entrées et la prévention contre les dépassements de quota / DoS (Rate limiting).

---

## Exemples Concrets d'Application

### Exemple 1 : Service NestJS Sécurisé avec Transaction et Audit Log
```typescript
import { Injectable, NotFoundException, ForbiddenException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { PublishArticleDto } from './dto/publish-article.dto';
import { UserRole } from '@prisma/client';

@Injectable()
export class ArticlesService {
  constructor(private readonly prisma: PrismaService) {}

  async publishArticle(articleId: string, adminUser: { id: string; role: UserRole }, ipAddress: string) {
    if (adminUser.role !== UserRole.ADMIN) {
      throw new ForbiddenException('Seul un administrateur peut valider et publier un article.');
    }

    return await this.prisma.$transaction(async (tx) => {
      const article = await tx.article.findUnique({
        where: { id: articleId },
        select: { id: true, status: true, title: true },
      });

      if (!article) {
        throw new NotFoundException(`Article introuvable avec l'identifiant ${articleId}`);
      }

      // Transition d'état atomique
      const updatedArticle = await tx.article.update({
        where: { id: articleId },
        data: {
          status: 'PUBLIE',
          publishedAt: new Date(),
          validatorId: adminUser.id,
        },
      });

      // Traçabilité obligatoire dans les Audit Logs
      await tx.auditLog.create({
        data: {
          userId: adminUser.id,
          action: 'PUBLISH_ARTICLE',
          resource: 'Article',
          resourceId: article.id,
          details: { previousStatus: article.status, title: article.title },
          ipAddress,
        },
      });

      return updatedArticle;
    });
  }
}
```

---

## Validation et Grille d'Évaluation Backend

Une implémentation conforme à ce niveau senior doit valider :
- [ ] Les routes d'API filtrent et valident 100% des paramètres de requête (body, params, query).
- [ ] Les opérations de mutation multi-tables s'exécutent au sein d'une transaction atomique.
- [ ] Aucune boucle ne déclenche de requêtes SQL unitaires (éradication du problème N+1).
- [ ] Les contrôles d'autorisation vérifient l'identité et les droits spécifiques sur l'objet ciblé (anti-IDOR).
- [ ] Les actions d'administration et de validation génèrent une trace d'audit inaltérable.
- [ ] Les mots de passe et secrets sont hachés/chiffrés selon les standards cryptographiques actuels.

