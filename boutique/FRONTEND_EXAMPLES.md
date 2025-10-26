# 🎨 Exemples de Code Frontend - Next.js

## 📁 Structure recommandée

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── products/
│   ├── cart/
│   ├── checkout/
│   └── account/
├── components/
├── lib/
└── public/
```

## 🔧 Configuration API Client

### `lib/api.ts`

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
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

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### `lib/auth.ts`

```typescript
import api from './api';

export interface Customer {
  customer_id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  customer: Customer;
}

export const authService = {
  async register(data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone?: string;
  }): Promise<LoginResponse> {
    const response = await api.post('/api/store/customers/register', data);
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('customer', JSON.stringify(response.data.customer));
    return response.data;
  },

  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await api.post('/api/store/customers/login', {
      email,
      password,
    });
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('customer', JSON.stringify(response.data.customer));
    return response.data;
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('customer');
    window.location.href = '/';
  },

  getCustomer(): Customer | null {
    const customer = localStorage.getItem('customer');
    return customer ? JSON.parse(customer) : null;
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  },
};
```

### `lib/cart.ts`

```typescript
import api from './api';

export interface CartItem {
  product_id: number;
  product_name: string;
  product_image?: string;
  unit_price: number;
  quantity: number;
  subtotal: number;
}

export interface Cart {
  items: CartItem[];
  subtotal: number;
  shipping_cost: number;
  total: number;
  items_count: number;
}

export const cartService = {
  getCart(): CartItem[] {
    const cart = localStorage.getItem('cart');
    return cart ? JSON.parse(cart) : [];
  },

  addToCart(productId: number, quantity: number = 1) {
    const cart = this.getCart();
    const existingItem = cart.find((item) => item.product_id === productId);

    if (existingItem) {
      existingItem.quantity += quantity;
    } else {
      cart.push({
        product_id: productId,
        quantity,
      } as any);
    }

    localStorage.setItem('cart', JSON.stringify(cart));
  },

  removeFromCart(productId: number) {
    const cart = this.getCart().filter((item) => item.product_id !== productId);
    localStorage.setItem('cart', JSON.stringify(cart));
  },

  updateQuantity(productId: number, quantity: number) {
    const cart = this.getCart();
    const item = cart.find((item) => item.product_id === productId);
    if (item) {
      item.quantity = quantity;
      localStorage.setItem('cart', JSON.stringify(cart));
    }
  },

  async validateCart(): Promise<Cart> {
    const cart = this.getCart();
    const response = await api.post('/api/store/cart/validate', cart);
    return response.data;
  },

  clearCart() {
    localStorage.removeItem('cart');
  },

  getItemsCount(): number {
    return this.getCart().reduce((sum, item) => sum + item.quantity, 0);
  },
};
```

## 🏠 Page d'accueil

### `app/page.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import ProductCard from '@/components/ProductCard';
import { motion } from 'framer-motion';

export default function HomePage() {
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFeaturedProducts();
  }, []);

  const loadFeaturedProducts = async () => {
    try {
      const response = await api.get('/api/store/products/featured/list');
      setFeaturedProducts(response.data);
    } catch (error) {
      console.error('Erreur chargement produits:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-gray-900 to-gray-800 text-white py-20">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-5xl font-bold mb-4">
              Bienvenue sur notre boutique
            </h1>
            <p className="text-xl mb-8">
              Découvrez nos produits de qualité
            </p>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg text-lg font-semibold transition">
              Voir le catalogue
            </button>
          </motion.div>
        </div>
      </section>

      {/* Produits en vedette */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-8 text-center">
            Produits en vedette
          </h2>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="bg-gray-200 h-64 rounded-lg mb-4"></div>
                  <div className="bg-gray-200 h-4 rounded mb-2"></div>
                  <div className="bg-gray-200 h-4 rounded w-2/3"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {featuredProducts.map((product) => (
                <ProductCard key={product.product_id} product={product} />
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
```

## 🛍️ Composant ProductCard

### `components/ProductCard.tsx`

```typescript
'use client';

import { motion } from 'framer-motion';
import { ShoppingCart } from 'lucide-react';
import { cartService } from '@/lib/cart';
import { toast } from 'react-hot-toast';

interface Product {
  product_id: number;
  name: string;
  description?: string;
  price: number;
  image?: string;
  in_stock: boolean;
}

export default function ProductCard({ product }: { product: Product }) {
  const handleAddToCart = () => {
    cartService.addToCart(product.product_id, 1);
    toast.success('Produit ajouté au panier !');
  };

  return (
    <motion.div
      whileHover={{ y: -5 }}
      className="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer"
    >
      <div className="relative h-64 bg-gray-200">
        {product.image ? (
          <img
            src={product.image}
            alt={product.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            Pas d'image
          </div>
        )}
        {!product.in_stock && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <span className="text-white font-bold">Rupture de stock</span>
          </div>
        )}
      </div>

      <div className="p-4">
        <h3 className="font-semibold text-lg mb-2 truncate">{product.name}</h3>
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
          {product.description}
        </p>

        <div className="flex items-center justify-between">
          <span className="text-2xl font-bold text-gray-900">
            {product.price.toLocaleString()} F
          </span>

          <button
            onClick={handleAddToCart}
            disabled={!product.in_stock}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white p-2 rounded-lg transition"
          >
            <ShoppingCart size={20} />
          </button>
        </div>
      </div>
    </motion.div>
  );
}
```

## 🛒 Page Panier

### `app/cart/page.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { cartService, Cart } from '@/lib/cart';
import { Trash2, Plus, Minus } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function CartPage() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      const validatedCart = await cartService.validateCart();
      setCart(validatedCart);
    } catch (error) {
      console.error('Erreur chargement panier:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (productId: number, newQuantity: number) => {
    if (newQuantity < 1) return;
    cartService.updateQuantity(productId, newQuantity);
    await loadCart();
  };

  const removeItem = async (productId: number) => {
    cartService.removeFromCart(productId);
    await loadCart();
  };

  if (loading) {
    return <div className="container mx-auto px-4 py-8">Chargement...</div>;
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-3xl font-bold mb-4">Votre panier est vide</h1>
        <button
          onClick={() => router.push('/products')}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg"
        >
          Continuer mes achats
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Mon panier</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Liste des articles */}
        <div className="lg:col-span-2">
          {cart.items.map((item) => (
            <div
              key={item.product_id}
              className="bg-white rounded-lg shadow-md p-4 mb-4 flex items-center gap-4"
            >
              <img
                src={item.product_image || '/placeholder.png'}
                alt={item.product_name}
                className="w-24 h-24 object-cover rounded"
              />

              <div className="flex-1">
                <h3 className="font-semibold text-lg">{item.product_name}</h3>
                <p className="text-gray-600">{item.unit_price.toLocaleString()} F</p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                  className="p-1 hover:bg-gray-100 rounded"
                >
                  <Minus size={16} />
                </button>
                <span className="w-12 text-center font-semibold">
                  {item.quantity}
                </span>
                <button
                  onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                  className="p-1 hover:bg-gray-100 rounded"
                >
                  <Plus size={16} />
                </button>
              </div>

              <div className="text-right">
                <p className="font-bold text-lg">
                  {item.subtotal.toLocaleString()} F
                </p>
                <button
                  onClick={() => removeItem(item.product_id)}
                  className="text-red-600 hover:text-red-700 mt-2"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Récapitulatif */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6 sticky top-4">
            <h2 className="text-xl font-bold mb-4">Récapitulatif</h2>

            <div className="space-y-2 mb-4">
              <div className="flex justify-between">
                <span>Sous-total</span>
                <span>{cart.subtotal.toLocaleString()} F</span>
              </div>
              <div className="flex justify-between">
                <span>Livraison</span>
                <span>{cart.shipping_cost.toLocaleString()} F</span>
              </div>
              <div className="border-t pt-2 flex justify-between font-bold text-lg">
                <span>Total</span>
                <span>{cart.total.toLocaleString()} F</span>
              </div>
            </div>

            <button
              onClick={() => router.push('/checkout')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold transition"
            >
              Passer la commande
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
```

## 🎨 Tailwind Config

### `tailwind.config.js`

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1f2937',
        secondary: '#4e73df',
        success: '#1cc88a',
        warning: '#f6c23e',
        danger: '#e74a3b',
        gold: '#ffd700',
      },
    },
  },
  plugins: [],
};
```

## 📦 Package.json

```json
{
  "name": "boutique-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "^18",
    "react-dom": "^18",
    "axios": "^1.6.0",
    "framer-motion": "^10.16.0",
    "lucide-react": "^0.292.0",
    "react-hot-toast": "^2.4.1"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10",
    "postcss": "^8",
    "tailwindcss": "^3",
    "typescript": "^5"
  }
}
```

---

**Ces exemples vous donnent une base solide pour démarrer le frontend ! 🚀**
