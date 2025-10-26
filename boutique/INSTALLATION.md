# 🚀 Installation de la Boutique en Ligne

## ✅ Ce qui a été créé

### 📁 Structure Backend (Complète)

```
boutique/
├── backend/
│   ├── models/
│   │   ├── __init__.py          ✅ Créé
│   │   ├── customer.py          ✅ Créé (StoreCustomer)
│   │   ├── order.py             ✅ Créé (StoreOrder, StoreOrderItem)
│   │   └── payment.py           ✅ Créé (StorePayment)
│   ├── schemas/
│   │   ├── __init__.py          ✅ Créé
│   │   ├── customer.py          ✅ Créé (Register, Login, etc.)
│   │   ├── product.py           ✅ Créé (ProductList, ProductDetail)
│   │   ├── cart.py              ✅ Créé (CartItem, CartResponse)
│   │   ├── order.py             ✅ Créé (OrderCreate, OrderResponse)
│   │   └── payment.py           ✅ Créé (PaymentInitiate, etc.)
│   ├── routers/
│   │   ├── __init__.py          ✅ Créé
│   │   ├── products.py          ✅ Créé (API produits publique)
│   │   ├── customers.py         ✅ Créé (Authentification)
│   │   ├── cart.py              ✅ Créé (Validation panier)
│   │   ├── orders.py            ✅ Créé (Gestion commandes)
│   │   └── payments.py          ✅ Créé (Paiements Mobile Money)
│   └── utils/
│       ├── __init__.py          ✅ Créé
│       ├── auth.py              ✅ Créé (JWT pour clients)
│       └── payment.py           ✅ Créé (Intégrations paiement)
├── init_store_db.py             ✅ Créé (Script initialisation DB)
├── README.md                    ✅ Créé (Documentation complète)
└── INSTALLATION.md              ✅ Créé (Ce fichier)
```

### 🔧 Modifications dans l'application principale

1. **main.py**
   - ✅ Import CORSMiddleware
   - ✅ Configuration CORS pour domaine boutique
   - ✅ Import et enregistrement des routers boutique

2. **app/database.py**
   - ✅ Import des modèles boutique pour création tables

## 🎯 Prochaines étapes

### 1. Initialiser les tables de la boutique

```bash
# Se connecter au conteneur Docker
docker exec -it powerclasss_app bash

# Initialiser les tables
python boutique/init_store_db.py

# Sortir du conteneur
exit
```

### 2. Redémarrer l'application

```bash
docker compose up -d --build
```

### 3. Tester l'API

```bash
# Tester l'endpoint des produits
curl http://localhost:8000/api/store/products

# Devrait retourner une liste de produits (vide au début)
```

### 4. Configurer les variables d'environnement

Ajouter dans `.env` :

```env
# Domaine de la boutique (pour CORS)
STORE_DOMAIN=http://localhost:3000

# JWT Secret pour les clients
JWT_SECRET_KEY=votre-secret-key-change-moi-en-production-svp

# Orange Money (optionnel pour l'instant)
ORANGE_MONEY_API_URL=
ORANGE_MONEY_MERCHANT_KEY=

# MTN Mobile Money (optionnel pour l'instant)
MTN_MOMO_API_URL=
MTN_MOMO_API_KEY=
MTN_MOMO_SUBSCRIPTION_KEY=
```

### 5. Créer le Frontend Next.js

```bash
cd /opt/powerclasss/boutique

# Créer le projet Next.js
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --app \
  --use-npm \
  --no-src-dir \
  --import-alias "@/*"

cd frontend

# Installer les dépendances
npm install axios framer-motion lucide-react
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install @radix-ui/react-select @radix-ui/react-toast
npm install class-variance-authority clsx tailwind-merge

# Créer le fichier de config API
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

## 📡 API Endpoints Disponibles

### Produits (Public - Pas d'authentification)
- `GET /api/store/products` - Liste des produits avec filtres
- `GET /api/store/products/{id}` - Détail d'un produit
- `GET /api/store/products/categories/list` - Liste des catégories
- `GET /api/store/products/featured/list` - Produits en vedette

### Clients (Authentification)
- `POST /api/store/customers/register` - Inscription
- `POST /api/store/customers/login` - Connexion
- `GET /api/store/customers/me` - Profil (authentifié)
- `PUT /api/store/customers/me` - Modifier profil (authentifié)

### Panier (Public)
- `POST /api/store/cart/validate` - Valider un panier
- `POST /api/store/cart/check-availability/{product_id}` - Vérifier stock

### Commandes (Authentifié)
- `POST /api/store/orders` - Créer une commande
- `GET /api/store/orders` - Liste des commandes du client
- `GET /api/store/orders/{id}` - Détail d'une commande
- `POST /api/store/orders/{id}/cancel` - Annuler une commande

### Paiements (Authentifié)
- `POST /api/store/payments/initiate` - Initier un paiement
- `POST /api/store/payments/verify` - Vérifier le statut
- `GET /api/store/payments/{reference}` - Détail paiement

## 🧪 Tests de l'API

### 1. Lister les produits

```bash
curl http://localhost:8000/api/store/products
```

### 2. Créer un compte client

```bash
curl -X POST http://localhost:8000/api/store/customers/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123",
    "first_name": "Test",
    "last_name": "User",
    "phone": "+225 07 00 00 00 00"
  }'
```

### 3. Se connecter

```bash
curl -X POST http://localhost:8000/api/store/customers/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123"
  }'
```

Copier le `access_token` retourné.

### 4. Créer une commande (avec token)

```bash
curl -X POST http://localhost:8000/api/store/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer VOTRE_TOKEN_ICI" \
  -d '{
    "items": [
      {
        "product_id": 1,
        "quantity": 2
      }
    ],
    "shipping_address": {
      "first_name": "Test",
      "last_name": "User",
      "email": "test@example.com",
      "phone": "+225 07 00 00 00 00",
      "address": "123 Rue Test",
      "city": "Abidjan",
      "country": "Côte d'\''Ivoire"
    },
    "payment_method": "orange_money"
  }'
```

## 🎨 Design du Frontend

### Palette de couleurs (même que l'app de gestion)

```css
:root {
  --primary: #1f2937;      /* Gris foncé */
  --secondary: #4e73df;    /* Bleu */
  --success: #1cc88a;      /* Vert */
  --warning: #f6c23e;      /* Jaune */
  --danger: #e74a3b;       /* Rouge */
  --gold: #ffd700;         /* Or (logo) */
}
```

### Pages à créer

1. **Page d'accueil** (`app/page.tsx`)
   - Hero section avec animation
   - Produits en vedette
   - Catégories
   - Call-to-action

2. **Catalogue** (`app/products/page.tsx`)
   - Grille de produits
   - Filtres (catégorie, prix, stock)
   - Recherche
   - Pagination

3. **Détail produit** (`app/products/[id]/page.tsx`)
   - Images produit
   - Description
   - Prix
   - Bouton "Ajouter au panier"
   - Stock disponible

4. **Panier** (`app/cart/page.tsx`)
   - Liste des articles
   - Quantités modifiables
   - Sous-total
   - Bouton "Commander"

5. **Checkout** (`app/checkout/page.tsx`)
   - Formulaire adresse
   - Récapitulatif commande
   - Choix méthode paiement
   - Validation

6. **Compte client** (`app/account/page.tsx`)
   - Profil
   - Commandes
   - Adresses

## 🔐 Sécurité

### Backend
- ✅ JWT pour authentification
- ✅ CORS configuré
- ✅ Validation Pydantic
- ✅ Hashage bcrypt
- ✅ Protection SQL injection (ORM)

### Frontend (à implémenter)
- 🔒 Token en localStorage
- 🔒 HTTPS en production
- 🔒 Validation inputs
- 🔒 Sanitization

## 📊 Base de données

### Nouvelles tables créées

1. **store_customers** - Clients de la boutique
2. **store_orders** - Commandes
3. **store_order_items** - Articles des commandes
4. **store_payments** - Paiements

### Relations

```
store_customers
    ↓ (1:N)
store_orders
    ↓ (1:N)
store_order_items → products (référence)
    ↑
store_payments (1:1)
```

## 🚀 Déploiement

### Backend
Déjà déployé avec l'application principale.

### Frontend
```bash
cd frontend
vercel --prod
```

Ou Netlify, Cloudflare Pages, etc.

## 📝 Checklist

- [x] Créer la structure backend
- [x] Créer les modèles de données
- [x] Créer les schémas Pydantic
- [x] Créer les routers API
- [x] Configurer CORS
- [x] Créer la documentation
- [ ] Initialiser les tables DB
- [ ] Tester l'API
- [ ] Créer le frontend Next.js
- [ ] Implémenter les pages
- [ ] Ajouter les animations
- [ ] Configurer les paiements
- [ ] Déployer

## 🆘 Dépannage

### Erreur CORS
Vérifier que `STORE_DOMAIN` est correctement configuré dans `.env`.

### Tables non créées
Exécuter `python boutique/init_store_db.py` dans le conteneur Docker.

### API ne répond pas
Vérifier les logs : `docker logs powerclasss_app`

## 📞 Support

Pour toute question, vérifier :
1. Les logs Docker
2. La documentation API (Swagger) : http://localhost:8000/docs
3. Le fichier README.md

---

**Prochaine étape** : Initialiser les tables et créer le frontend ! 🎉
