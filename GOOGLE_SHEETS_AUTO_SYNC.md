# Synchronisation Automatique Google Sheets

## Vue d'ensemble

L'application supporte maintenant la **synchronisation bidirectionnelle** avec Google Sheets :
- ✅ **Import** : Importer des produits depuis Google Sheets vers l'application
- ✅ **Export automatique** : Mettre à jour le stock dans Google Sheets après chaque vente

## Configuration

### 1. Variables d'environnement requises

```env
# Credentials Google Sheets (obligatoire)
GOOGLE_SHEETS_CREDENTIALS_PATH=/opt/powerclasss/credentials/google-sheets-credentials.json

# Configuration du spreadsheet (obligatoire)
GOOGLE_SHEETS_SPREADSHEET_ID=1VHMujdZw-iPs28pz1rC9Ol72T9l9YTW6Wr9j5ujEsXQ
GOOGLE_SHEETS_WORKSHEET_NAME=Les produits

# Activer la synchronisation automatique (optionnel, par défaut: false)
GOOGLE_SHEETS_AUTO_SYNC=true
```

### 2. Permissions Google Sheets

⚠️ **Important** : Les permissions du Service Account doivent être mises à jour pour permettre l'**écriture** :

1. **Créer un nouveau fichier de credentials** avec les permissions en écriture
2. **OU** Partager le Google Sheet avec le service account en tant qu'**Éditeur** (pas seulement Lecteur)

Pour vérifier l'email du service account :
```bash
cat /opt/powerclasss/credentials/symbolic-folio-470422-v3-71562b79a03f.json | grep client_email
```

Ensuite, dans Google Sheets :
- Cliquer sur **Partager**
- Ajouter l'email du service account
- Sélectionner **Éditeur** comme niveau d'accès
- Cliquer sur **Envoyer**

## Fonctionnement

### Synchronisation automatique

Quand `GOOGLE_SHEETS_AUTO_SYNC=true`, le stock est automatiquement mis à jour dans Google Sheets après :

1. **Création de facture** : Le stock des produits vendus est décrémenté dans Google Sheets
2. **Mise à jour de facture** : Le stock est ajusté en conséquence
3. **Vente quotidienne** : Le stock est mis à jour automatiquement

### Synchronisation manuelle

Vous pouvez aussi synchroniser manuellement tous les stocks vers Google Sheets :

```bash
# Via API
curl -X POST http://votre-domaine:8000/api/google-sheets/sync-stock-to-sheets \
  -H "Authorization: Bearer VOTRE_TOKEN"
```

## Logs et monitoring

Les logs de synchronisation apparaissent dans les logs de l'application :

```bash
# Docker
docker compose logs -f app | grep -i "google\|sync\|stock"

# Exemples de logs
✅ Stock mis à jour dans Google Sheets: 85002031591 → 15
⚠️ Produit non trouvé dans Google Sheets: 1234567890
❌ Erreur lors de la mise à jour du stock dans Google Sheets: Permission denied
```

## Comportement

### Produits avec code-barres

✅ Seuls les produits ayant un **code-barres** sont synchronisés avec Google Sheets
- Le code-barres sert d'identifiant unique pour retrouver le produit dans le sheet
- Si un produit n'a pas de code-barres, il ne sera pas synchronisé

### Produits non trouvés

⚠️ Si un produit vendu n'existe pas dans le Google Sheet :
- Un avertissement est loggué
- La vente est enregistrée normalement dans l'application
- Aucune erreur ne bloque la transaction

### Gestion des erreurs

🛡️ La synchronisation Google Sheets est **non-bloquante** :
- Si la synchronisation échoue, la vente est quand même enregistrée
- Les erreurs sont loguées mais n'interrompent pas le processus
- Vous pouvez relancer une synchronisation manuelle plus tard

## Cas d'usage

### Scenario 1 : Vente en magasin

```
1. Client achète un iPhone 14 Pro (quantité: 1)
2. Facture créée dans l'application
3. Stock dans l'application: 5 → 4
4. ✅ Stock dans Google Sheets: 5 → 4 (automatique)
```

### Scenario 2 : Synchronisation en masse

```bash
# Synchroniser tous les stocks vers Google Sheets
POST /api/google-sheets/sync-stock-to-sheets

# Réponse
{
  "success": true,
  "message": "Synchronisation des stocks terminée: 42 mis à jour, 3 non trouvés, 0 erreurs",
  "stats": {
    "total": 45,
    "updated": 42,
    "not_found": 3,
    "errors": 0
  }
}
```

## Troubleshooting

### Erreur : "Permission denied"

**Cause** : Le service account n'a pas les droits d'écriture

**Solution** :
1. Ouvrir le Google Sheet
2. Partager avec l'email du service account en tant qu'**Éditeur**
3. Relancer la synchronisation

### Erreur : "Produit non trouvé"

**Cause** : Le code-barres du produit n'existe pas dans le Google Sheet

**Solutions** :
1. Vérifier que le produit a bien un code-barres dans l'application
2. Vérifier que ce code-barres existe dans la colonne "Code-barres produit" du Google Sheet
3. Importer d'abord le produit depuis Google Sheets avec `/api/google-sheets/sync`

### La synchronisation ne se déclenche pas

**Vérifications** :
```bash
# 1. Vérifier que la variable est activée
docker compose exec app env | grep GOOGLE_SHEETS_AUTO_SYNC
# Devrait afficher: GOOGLE_SHEETS_AUTO_SYNC=true

# 2. Vérifier les logs
docker compose logs app | grep "sync"

# 3. Tester la connexion
curl -X POST http://localhost:8000/api/google-sheets/test-connection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  -d '{"spreadsheet_id": "VOTRE_ID"}'
```

## Performance

### Impact sur les performances

- La synchronisation est **asynchrone** et n'ajoute qu'environ **100-300ms** par produit vendu
- Pas d'impact significatif sur l'expérience utilisateur
- Les requêtes vers Google Sheets sont limitées par les quotas Google (100 requêtes/100 secondes/utilisateur)

### Optimisations possibles

Pour de gros volumes de ventes :
1. Désactiver la synchronisation automatique (`GOOGLE_SHEETS_AUTO_SYNC=false`)
2. Utiliser une synchronisation planifiée (cron) toutes les heures/jour
3. Implémenter une file d'attente (queue) pour les mises à jour

## API Endpoints

### Synchroniser les stocks vers Google Sheets

```http
POST /api/google-sheets/sync-stock-to-sheets
Authorization: Bearer {token}
```

**Réponse** :
```json
{
  "success": true,
  "message": "Synchronisation des stocks terminée: 42 mis à jour, 3 non trouvés, 0 erreurs",
  "stats": {
    "total": 45,
    "updated": 42,
    "not_found": 3,
    "errors": 0,
    "error_details": []
  }
}
```

### Importer les produits depuis Google Sheets

```http
POST /api/google-sheets/sync
Content-Type: application/json
Authorization: Bearer {token}

{
  "spreadsheet_id": "1VHMujdZw-iPs28pz1rC9Ol72T9l9YTW6Wr9j5ujEsXQ",
  "worksheet_name": "Les produits",
  "update_existing": false
}
```

## Sécurité

### Bonnes pratiques

✅ **À faire** :
- Limiter les permissions du service account au strict minimum (éditeur sur ce sheet uniquement)
- Utiliser un service account dédié pour cette intégration
- Surveiller les logs pour détecter des comportements anormaux
- Faire des sauvegardes régulières du Google Sheet

❌ **À éviter** :
- Donner des droits "Propriétaire" au service account
- Partager le fichier credentials avec d'autres applications
- Activer la synchronisation automatique sans avoir testé d'abord

## Support

Pour toute question ou problème :
1. Consulter les logs : `docker compose logs -f app`
2. Vérifier la configuration dans `/opt/powerclasss/.env`
3. Tester la connexion avec l'endpoint `/api/google-sheets/test-connection`
4. Consulter `GOOGLE_SHEETS_SETUP.md` pour la configuration initiale
