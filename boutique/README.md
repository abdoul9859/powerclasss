# 🛍️ Boutique en Ligne - E-commerce Store

Boutique en ligne complète liée à l'application de gestion de stock POWERCLASSS.

## 📋 Architecture

### Backend (API)
- **FastAPI** - API REST publique
- **PostgreSQL** - Base de données partagée avec l'app de gestion
- **JWT** - Authentification des clients
- **Mobile Money** - Intégration Orange Money, MTN, Moov, Wave

### Frontend (À créer)
- **Next.js 14** - Framework React moderne
- **TailwindCSS** - Styling
- **Framer Motion** - Animations
- **shadcn/ui** - Composants UI

## 🚀 Installation Backend

### 1. Créer les tables de la boutique

```bash
cd /opt/powerclasss
python boutique/init_store_db.py
```

### 2. Configurer les variables d'environnement

Ajouter dans `.env` :

```env
# Domaine de la boutique (pour CORS)
STORE_DOMAIN=https://boutique.votredomaine.com

# JWT Secret pour les clients
JWT_SECRET_KEY=votre-secret-key-tres-securisee

# Orange Money (Côte d'Ivoire)
ORANGE_MONEY_API_URL=https://api.orange.com/orange-money-webpay/...
ORANGE_MONEY_MERCHANT_KEY=votre-merchant-key

# MTN Mobile Money
MTN_MOMO_API_URL=https://momodeveloper.mtn.com/collection/v1_0/requesttopay
MTN_MOMO_API_KEY=votre-api-key
MTN_MOMO_SUBSCRIPTION_KEY=votre-subscription-key
MTN_MOMO_ENVIRONMENT=sandbox  # ou production

# URLs de callback paiement
PAYMENT_RETURN_URL=https://boutique.votredomaine.com/payment/success
PAYMENT_CANCEL_URL=https://boutique.votredomaine.com/payment/cancel
PAYMENT_NOTIF_URL=https://api.votredomaine.com/api/store/payments/callback
```

### 3. Redémarrer l'application

```bash
docker compose up -d --build
```

## 📡 API Endpoints

### Produits (Public)
- `GET /api/store/products` - Liste des produits
- `GET /api/store/products/{id}` - Détail produit
- `GET /api/store/products/categories/list` - Liste des catégories
- `GET /api/store/products/featured/list` - Produits en vedette

### Clients (Authentification)
- `POST /api/store/customers/register` - Inscription
- `POST /api/store/customers/login` - Connexion
- `GET /api/store/customers/me` - Profil client
- `PUT /api/store/customers/me` - Modifier profil
- `POST /api/store/customers/change-password` - Changer mot de passe

### Panier
- `POST /api/store/cart/validate` - Valider le panier
- `POST /api/store/cart/check-availability/{product_id}` - Vérifier disponibilité

### Commandes (Authentifié)
- `POST /api/store/orders` - Créer une commande
- `GET /api/store/orders` - Liste des commandes
- `GET /api/store/orders/{id}` - Détail commande
- `POST /api/store/orders/{id}/cancel` - Annuler commande

### Paiements (Authentifié)
- `POST /api/store/payments/initiate` - Initier un paiement
- `POST /api/store/payments/verify` - Vérifier statut paiement
- `GET /api/store/payments/{reference}` - Détail paiement
- `POST /api/store/payments/callback` - Webhook provider (public)

## 🎨 Frontend - Next.js Store

### Créer le projet Next.js

```bash
cd /opt/powerclasss/boutique
npx create-next-app@latest frontend --typescript --tailwind --app --use-npm
cd frontend
```

### Installer les dépendances

```bash
npm install axios framer-motion lucide-react @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install -D @types/node
```

### Structure du projet

```
frontend/
├── app/
│   ├── layout.tsx              # Layout principal
│   ├── page.tsx                # Page d'accueil
│   ├── products/
│   │   ├── page.tsx            # Liste produits
│   │   └── [id]/page.tsx       # Détail produit
│   ├── cart/
│   │   └── page.tsx            # Panier
│   ├── checkout/
│   │   └── page.tsx            # Checkout
│   ├── account/
│   │   ├── page.tsx            # Compte client
│   │   ├── orders/page.tsx     # Commandes
│   │   └── profile/page.tsx    # Profil
│   └── auth/
│       ├── login/page.tsx      # Connexion
│       └── register/page.tsx   # Inscription
├── components/
│   ├── Header.tsx              # En-tête
│   ├── Footer.tsx              # Pied de page
│   ├── ProductCard.tsx         # Carte produit
│   ├── Cart.tsx                # Composant panier
│   └── ui/                     # Composants UI (shadcn)
├── lib/
│   ├── api.ts                  # Client API
│   ├── auth.ts                 # Gestion auth
│   └── cart.ts                 # Gestion panier
└── public/
    └── images/                 # Images statiques
```

### Configuration API

Créer `frontend/.env.local` :

```env
NEXT_PUBLIC_API_URL=https://api.votredomaine.com
```

### Exemple de client API

```typescript
// lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

## 🎨 Design & Couleurs

Utiliser les mêmes couleurs que l'application de gestion :

```css
:root {
  --primary: #1f2937;      /* Gris foncé */
  --secondary: #4e73df;    /* Bleu */
  --success: #1cc88a;      /* Vert */
  --warning: #f6c23e;      /* Jaune */
  --danger: #e74a3b;       /* Rouge */
  --gold: #ffd700;         /* Or (pour logo) */
}
```

## 🔐 Sécurité

### Backend
- ✅ JWT pour authentification clients
- ✅ CORS configuré pour domaine boutique
- ✅ Validation des données (Pydantic)
- ✅ Hashage des mots de passe (bcrypt)
- ✅ Protection contre les injections SQL (SQLAlchemy ORM)

### Frontend
- 🔒 Token stocké en localStorage
- 🔒 HTTPS obligatoire en production
- 🔒 Validation côté client
- 🔒 Sanitization des inputs

## 📦 Déploiement

### Backend (Déjà déployé avec l'app de gestion)
L'API de la boutique est automatiquement déployée avec l'application principale.

### Frontend (Vercel recommandé)

```bash
cd frontend
vercel --prod
```

Ou utiliser Netlify, Cloudflare Pages, etc.

### Configuration DNS

Pointer votre domaine boutique vers le frontend :
```
boutique.votredomaine.com → Vercel/Netlify
```

L'API reste sur le même domaine que l'app de gestion.

## 🧪 Tests

### Tester l'API

```bash
# Lister les produits
curl https://api.votredomaine.com/api/store/products

# Créer un compte
curl -X POST https://api.votredomaine.com/api/store/customers/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "password": "Password123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+225 07 00 00 00 00"
  }'
```

## 📱 Fonctionnalités

### Pour les clients
- ✅ Catalogue produits avec filtres
- ✅ Recherche avancée
- ✅ Panier persistant
- ✅ Comptes clients
- ✅ Historique commandes
- ✅ Suivi de commande
- ✅ Paiement Mobile Money
- ✅ Paiement à la livraison

### Pour l'admin (dans l'app de gestion)
- ✅ Gestion des commandes
- ✅ Suivi des paiements
- ✅ Gestion des clients e-commerce
- ✅ Statistiques de ventes en ligne

## 🆘 Support

Pour toute question ou problème :
1. Vérifier les logs : `docker logs powerclasss_app`
2. Vérifier la base de données
3. Tester les endpoints API

## 📝 TODO

- [ ] Créer le frontend Next.js
- [ ] Implémenter les pages principales
- [ ] Ajouter les animations
- [ ] Configurer les paiements Mobile Money
- [ ] Tester en production
- [ ] Ajouter les avis clients
- [ ] Implémenter la wishlist
- [ ] Ajouter les codes promo
- [ ] Optimiser le SEO
- [ ] Ajouter Google Analytics

## 🎉 Prochaines étapes

1. **Initialiser les tables** : `python boutique/init_store_db.py`
2. **Créer le frontend Next.js** (voir instructions ci-dessus)
3. **Configurer les paiements** (Orange Money, MTN, etc.)
4. **Déployer le frontend** sur Vercel
5. **Configurer le domaine** boutique.votredomaine.com

Bonne chance avec votre boutique en ligne ! 🚀
