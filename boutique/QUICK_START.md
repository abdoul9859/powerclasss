# ⚡ Quick Start - Boutique en Ligne

## 🚀 Démarrage Rapide (5 minutes)

### 1. Initialiser les tables (2 min)

```bash
# Dans le terminal
docker exec -it powerclasss_app python boutique/init_store_db.py
docker compose restart
```

### 2. Tester l'API (1 min)

```bash
# Lister les produits
curl http://localhost:8000/api/store/products

# Voir la documentation interactive
open http://localhost:8000/docs
```

### 3. Créer un compte test (2 min)

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

✅ **Votre API boutique est opérationnelle !**

## 📱 Créer le Frontend (30 min)

### Option 1 : Démarrage rapide

```bash
cd /opt/powerclasss/boutique

# Créer le projet
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --app \
  --use-npm

cd frontend

# Installer les dépendances
npm install axios framer-motion lucide-react react-hot-toast

# Créer le fichier de config
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Démarrer
npm run dev
```

Ouvrir http://localhost:3000

### Option 2 : Clone un template (recommandé)

```bash
# TODO: Créer un template Next.js complet
# Pour l'instant, suivre Option 1 et copier les exemples de FRONTEND_EXAMPLES.md
```

## 📚 Documentation

- **README.md** - Vue d'ensemble complète
- **INSTALLATION.md** - Installation détaillée
- **FRONTEND_EXAMPLES.md** - Exemples de code frontend
- **SUMMARY.md** - Résumé de ce qui a été créé

## 🎯 Endpoints Principaux

### Produits (Public)
```bash
GET /api/store/products                    # Liste
GET /api/store/products/{id}               # Détail
GET /api/store/products/categories/list    # Catégories
```

### Clients
```bash
POST /api/store/customers/register         # Inscription
POST /api/store/customers/login            # Connexion
GET  /api/store/customers/me               # Profil
```

### Commandes (Authentifié)
```bash
POST /api/store/orders                     # Créer
GET  /api/store/orders                     # Liste
GET  /api/store/orders/{id}                # Détail
```

## 🔐 Authentification

```typescript
// 1. S'inscrire ou se connecter
const response = await axios.post('/api/store/customers/login', {
  email: 'test@example.com',
  password: 'Password123'
});

// 2. Sauvegarder le token
const token = response.data.access_token;
localStorage.setItem('token', token);

// 3. Utiliser le token
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

## 🛒 Flow Complet

```
1. Client visite la boutique
   ↓
2. Parcourt les produits
   ↓
3. Ajoute au panier (localStorage)
   ↓
4. Va au checkout
   ↓
5. S'inscrit/Se connecte
   ↓
6. Remplit l'adresse
   ↓
7. Choisit le paiement
   ↓
8. Valide la commande (POST /api/store/orders)
   ↓
9. Initie le paiement (POST /api/store/payments/initiate)
   ↓
10. Paie via Mobile Money
   ↓
11. Reçoit confirmation
```

## 🎨 Design System

### Couleurs
```css
--primary: #1f2937      /* Gris foncé */
--secondary: #4e73df    /* Bleu */
--success: #1cc88a      /* Vert */
--warning: #f6c23e      /* Jaune */
--danger: #e74a3b       /* Rouge */
--gold: #ffd700         /* Or */
```

### Composants à créer
- [ ] Header avec logo et panier
- [ ] ProductCard avec image et prix
- [ ] CartDrawer (panier latéral)
- [ ] CheckoutForm (formulaire commande)
- [ ] OrderCard (carte commande)
- [ ] Footer

## 💡 Tips

### Performance
- Utiliser `next/image` pour les images
- Implémenter le lazy loading
- Mettre en cache les produits

### UX
- Ajouter des animations fluides (Framer Motion)
- Feedback visuel (toasts)
- Loading states
- Error handling

### SEO
- Metadata pour chaque page
- Sitemap
- Schema.org markup
- Open Graph tags

## 🐛 Dépannage

### API ne répond pas
```bash
docker logs powerclasss_app
```

### CORS Error
Vérifier `.env` :
```env
STORE_DOMAIN=http://localhost:3000
```

### Token invalide
```typescript
localStorage.removeItem('token');
// Se reconnecter
```

## 📞 Aide

### Documentation API
http://localhost:8000/docs

### Logs
```bash
docker logs -f powerclasss_app
```

### Base de données
```bash
docker exec -it powerclasss_db psql -U koyeb-adm -d testgeek
```

## ✅ Checklist

- [ ] Tables initialisées
- [ ] API testée
- [ ] Frontend créé
- [ ] Authentification fonctionne
- [ ] Panier fonctionne
- [ ] Commande fonctionne
- [ ] Paiement configuré
- [ ] Design finalisé
- [ ] Tests effectués
- [ ] Déployé

## 🚀 Déploiement

### Backend
Déjà déployé avec l'app principale.

### Frontend
```bash
cd frontend
vercel --prod
```

Configurer le domaine :
```
boutique.votredomaine.com → Vercel
```

## 🎉 C'est parti !

Vous avez tout ce qu'il faut pour créer une boutique en ligne moderne et professionnelle !

**Prochaine étape** : Créer le frontend Next.js avec les exemples de `FRONTEND_EXAMPLES.md`

Bon développement ! 🛍️✨
