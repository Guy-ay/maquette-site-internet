# Motifs de Conception d'API Backend (API Design Patterns)

Ce guide résume les standards industriels appliqués par les développeurs backend seniors pour concevoir des interfaces de programmation maintenables, cohérentes et résilientes.

---

## 1. Structure Uniforme des Réponses REST

Chaque réponse d'API doit suivre une enveloppe cohérente facilitant la consommation par les clients frontend et mobiles :

### Réponse Succès Unitaire
```json
{
  "success": true,
  "data": {
    "id": "art_98124",
    "title": "Inauguration de l'Aéroport de Korhogo",
    "status": "PUBLIE",
    "publishedAt": "2026-10-15T10:00:00.000Z"
  }
}
```

### Réponse Succès avec Pagination
```json
{
  "success": true,
  "data": [
    { "id": "art_1", "title": "Article 1" },
    { "id": "art_2", "title": "Article 2" }
  ],
  "meta": {
    "total": 45,
    "page": 1,
    "limit": 20,
    "totalPages": 3,
    "hasNextPage": true,
    "hasPrevPage": false
  }
}
```

### Réponse d'Erreur Standardisée (RFC 7807 Problem Details)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Les données fournies ne respectent pas le schéma requis.",
    "statusCode": 400,
    "details": [
      {
        "field": "title",
        "message": "Le titre ne doit pas être vide et faire moins de 255 caractères."
      }
    ],
    "timestamp": "2026-11-02T11:50:00.000Z",
    "path": "/api/v1/articles"
  }
}
```

---

## 2. Idempotence des Mutations Sensibles

Toute opération critique susceptible d'être rejouée lors d'une perte de connexion (validation de paiement, réservation, publication officielle) doit supporter l'en-tête `Idempotency-Key` :

```typescript
// Middleware ou Intercepteur d'Idempotence
const key = req.headers['idempotency-key'];
if (key) {
  const cachedResponse = await redis.get(`idemp:${key}`);
  if (cachedResponse) {
    return res.status(200).json(JSON.parse(cachedResponse));
  }
}
// Exécuter l'action, puis enregistrer le résultat avec expiration (ex: 24h)
await redis.set(`idemp:${key}`, JSON.stringify(result), 'EX', 86400);
```

---

## 3. Gestion des Versions d'API (Versioning)

- **Dans l'URI (recommandé) :** `/api/v1/articles`
- Déprécier les anciennes versions avec un en-tête `Sunset` et `Deprecation` :
  ```http
  Deprecation: @1793574300
  Sunset: Tue, 01 Dec 2026 00:00:00 GMT
  ```

