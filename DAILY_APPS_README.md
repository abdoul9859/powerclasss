# Applications Quotidiennes - Guide d'utilisation

## Vue d'ensemble

Deux nouvelles applications ont été ajoutées au système de gestion pour améliorer le suivi quotidien des activités :

1. **Demandes Quotidiennes des Clients** (`/daily-requests`)
2. **Ventes Quotidiennes** (`/daily-sales`)

## 1. Demandes Quotidiennes des Clients

### Fonctionnalités

- **Enregistrement des demandes** : Permet de noter les demandes des clients même si le produit n'est pas encore disponible
- **Gestion des clients** : 
  - Sélection d'un client existant dans la base de données
  - Création rapide d'un nouveau client via popup (nom et téléphone)
- **Suivi des statuts** :
  - `En attente` : Demande non encore traitée
  - `Satisfaite` : Demande honorée
  - `Annulée` : Demande annulée
- **Filtres et recherche** : Par client, produit, statut, date
- **Statistiques** : Taux de satisfaction, nombre de demandes par statut

### Utilisation

1. Accédez à **Ventes > Demandes Clients**
2. Cliquez sur **"Nouvelle Demande"**
3. Recherchez ou créez un client
4. Décrivez le produit demandé
5. Enregistrez la demande
6. Marquez comme "Satisfaite" quand le produit est livré

## 2. Ventes Quotidiennes

### Fonctionnalités

- **Ventes directes** : Enregistrement de ventes sans facture
- **Ventes liées aux factures** : Création automatique lors de la génération de factures
- **Gestion du stock** : Déduction automatique du stock lors des ventes
- **Méthodes de paiement** : Espèces, Mobile Money, Virement, Chèque
- **Filtres et recherche** : Par client, produit, méthode de paiement, date
- **Statistiques** : Montant total, vente moyenne, répartition par méthode de paiement

### Utilisation

#### Vente directe (sans facture)
1. Accédez à **Ventes > Ventes Quotidiennes**
2. Cliquez sur **"Nouvelle Vente"**
3. Recherchez ou créez un client
4. Recherchez ou saisissez un produit
5. Indiquez la quantité et le prix
6. Choisissez la méthode de paiement
7. Enregistrez la vente

#### Vente via facture
1. Créez une facture normalement
2. Les ventes quotidiennes sont automatiquement créées
3. Consultez-les dans **Ventes > Ventes Quotidiennes**

## Intégration avec le système existant

### Base de données

Nouvelles tables ajoutées :
- `daily_client_requests` : Demandes des clients
- `daily_sales` : Ventes quotidiennes

### Intégration automatique

- **Factures → Ventes quotidiennes** : Chaque facture créée génère automatiquement des entrées dans les ventes quotidiennes
- **Stock** : Les ventes quotidiennes déduisent automatiquement le stock des produits
- **Clients** : Réutilisation de la base de clients existante

## Migration

Pour ajouter ces fonctionnalités à une installation existante :

```bash
python migration_add_daily_apps.py
```

## Navigation

Les nouvelles applications sont accessibles via :
- **Menu principal > Ventes > Demandes Clients**
- **Menu principal > Ventes > Ventes Quotidiennes**

## Avantages

1. **Suivi amélioré** : Meilleure visibilité sur les demandes et ventes quotidiennes
2. **Flexibilité** : Ventes directes sans obligation de facturation
3. **Automatisation** : Intégration transparente avec le système de facturation
4. **Reporting** : Statistiques détaillées pour l'analyse des ventes
5. **Gestion du stock** : Mise à jour automatique du stock

## Notes techniques

- Les ventes quotidiennes sont automatiquement créées lors de la génération de factures
- Le stock est déduit automatiquement lors des ventes
- Les statistiques sont calculées en temps réel
- L'interface est responsive et compatible mobile
