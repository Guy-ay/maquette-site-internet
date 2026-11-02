# Optimisation des Bases de Données & Requêtes ORM (PostgreSQL & Prisma)

Ce document fournit les solutions concrètes pour auditer, détecter et éradiquer les goulots d'étranglement de bases de données relationnelles.

---

## 1. Éradication du Problème N+1

Le problème N+1 survient lorsqu'une requête initiale récupère N enregistrements, puis N requêtes additionnelles sont exécutées individuellement pour récupérer les relations.

### ❌ Mauvais (N+1 Requêtes)
```typescript
const articles = await prisma.article.findMany(); // 1 requête
for (const art of articles) {
  art.author = await prisma.user.findUnique({ where: { id: art.authorId } }); // N requêtes !
}
```

### ✅ Bon (1 Seule Requête JOIN)
```typescript
const articles = await prisma.article.findMany({
  include: {
    author: {
      select: { id: true, name: true, role: true }, // Projection stricte
    },
    category: true,
  },
});
```

---

## 2. Stratégie d'Indexation sous PostgreSQL

### A. Clés Étrangères (Foreign Keys)
Dans PostgreSQL, déclarer une clé étrangère n'indexe **pas** automatiquement la colonne. Si vous filtrez ou joignez souvent sur `authorId` ou `categoryId`, vous subirez un `Seq Scan` (balayage complet de table) à chaque jointure.

```prisma
model Article {
  id         String   @id @default(uuid())
  authorId   String
  categoryId String
  status     String

  @@index([authorId])
  @@index([categoryId])
}
```

### B. Index Partiels (Partial Indexes)
Si 95% des requêtes publiques ne ciblent que les articles ayant le statut `PUBLIE`, un index partiel est 10 fois plus petit et beaucoup plus rapide en cache RAM :

```sql
CREATE INDEX idx_articles_published 
ON articles (published_at DESC) 
WHERE status = 'PUBLIE';
```

---

## 3. Transactions et Isolation ACID

Toute opération métier modifiant plusieurs tables doit s'exécuter dans une transaction atomique :

```typescript
await prisma.$transaction(async (tx) => {
  // 1. Mettre à jour l'entité
  const doc = await tx.document.update({
    where: { id: docId },
    data: { isValidated: true },
  });

  // 2. Écrire le log d'audit
  await tx.auditLog.create({
    data: {
      userId: adminId,
      action: 'VALIDATE_DOCUMENT',
      resourceId: doc.id,
    },
  });
});
```

