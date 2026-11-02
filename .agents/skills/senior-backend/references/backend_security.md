# Sécurité Backend & Défense en Profondeur (OWASP & Hardening)

Ce guide récapitule les contrôles de sécurité indispensables pour toute API en production.

---

## 1. Prévention des Failles IDOR (Insecure Direct Object Reference)

### ❌ Vulnérable (IDOR)
L'identifiant de la ressource est pris aveuglément sans contrôler l'appartenance :
```typescript
@Delete(':id')
async deleteDocument(@Param('id') id: string) {
  return this.prisma.document.delete({ where: { id } }); // N'importe qui peut supprimer n'importe quel document !
}
```

### ✅ Sécurisé (Contrôle d'accès strict)
```typescript
@Delete(':id')
async deleteDocument(@Param('id') id: string, @CurrentUser() user: RequestUser) {
  const doc = await this.prisma.document.findUnique({ where: { id } });
  if (!doc) throw new NotFoundException('Document non trouvé');

  // Vérification de la propriété ou du rôle ADMIN
  if (doc.authorId !== user.id && user.role !== 'ADMIN') {
    throw new ForbiddenException("Vous n'êtes pas autorisé à supprimer ce document.");
  }

  return this.prisma.document.delete({ where: { id } });
}
```

---

## 2. En-têtes de Sécurité HTTP (Helmet)

Activer systématiquement Helmet dans l'API principale :
```typescript
import helmet from 'helmet';

app.use(helmet({
  contentSecurityPolicy: true,
  crossOriginEmbedderPolicy: true,
  dnsPrefetchControl: { allow: false },
  frameguard: { action: 'deny' },
  hidePoweredBy: true,
  hsts: { maxAge: 31536000, includeSubDomains: true, preload: true },
}));
```

---

## 3. Chiffrement au Repos des Données Sensibles (AES-256-GCM)

Pour les données personnelles ou médicales (ex: CERMA) :
```typescript
import { createCipheriv, createDecipheriv, randomBytes } from 'crypto';

const ALGORITHM = 'aes-256-gcm';

export function encryptData(text: string, key: Buffer) {
  const iv = randomBytes(12);
  const cipher = createCipheriv(ALGORITHM, key, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  const tag = cipher.getAuthTag().toString('hex');
  return `${iv.toString('hex')}:${tag}:${encrypted}`;
}
```

