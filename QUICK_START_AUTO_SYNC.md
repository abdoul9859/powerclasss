# Guide Rapide : Synchronisation Automatique Google Sheets

## 🎯 Problème résolu

Vous modifiez la quantité d'un produit dans Google Sheets, mais l'application ne se met pas à jour automatiquement.

## ✅ Solution implémentée

La synchronisation automatique bidirectionnelle est maintenant active :
- **Application → Google Sheets** : Mise à jour automatique après chaque vente
- **Google Sheets → Application** : Vérification automatique toutes les 10 minutes

## 🚀 Démarrage rapide

### 1. Accéder à l'interface

1. Connectez-vous à l'application
2. Allez dans **Paramètres** (icône engrenage)
3. Cliquez sur **Synchronisation Google Sheets**

### 2. Démarrer la synchronisation automatique

1. Sur la page de synchronisation, dans la section **"Synchronisation Automatique"**
2. Cliquez sur le bouton **"Démarrer"**
3. ✅ Vous verrez le statut passer à **"EN COURS"**

### 3. Vérifier que ça fonctionne

**Test rapide :**

1. Modifiez une quantité dans votre Google Sheet
2. Cliquez sur **"Synchroniser Maintenant"** (ou attendez 10 minutes)
3. Vérifiez que la quantité est mise à jour dans l'application

## 📊 Interface de contrôle

### Statut affiché

- **Statut** : Actif / Inactif
- **Intervalle** : 10 minutes (configurable)
- **Dernière sync** : Horodatage de la dernière synchronisation
- **Prochaine sync** : Quand aura lieu la prochaine synchronisation
- **Derniers résultats** : Nombre de produits mis à jour, créés, erreurs

### Boutons disponibles

- **Démarrer** : Lance la synchronisation automatique
- **Arrêter** : Arrête la synchronisation automatique
- **Synchroniser Maintenant** : Force une synchronisation immédiate
- **Actualiser le Statut** : Rafraîchit les informations affichées

## ⚙️ Configuration

### Variables d'environnement (déjà configurées)

```env
GOOGLE_SHEETS_CREDENTIALS_PATH=/opt/powerclasss/credentials/symbolic-folio-470422-v3-71562b79a03f.json
GOOGLE_SHEETS_SPREADSHEET_ID=1VHMujdZw-iPs28pz1rC9Ol72T9l9YTW6Wr9j5ujEsXQ
GOOGLE_SHEETS_WORKSHEET_NAME=Les produits
GOOGLE_SHEETS_AUTO_SYNC=true
GOOGLE_SHEETS_SYNC_INTERVAL=10  # En minutes
```

### Modifier l'intervalle de synchronisation

Pour changer l'intervalle (par exemple 5 minutes au lieu de 10) :

1. Éditez le fichier `.env` :
   ```bash
   nano /opt/powerclasss/.env
   ```

2. Modifiez la ligne :
   ```env
   GOOGLE_SHEETS_SYNC_INTERVAL=5
   ```

3. Redémarrez l'application :
   ```bash
   cd /opt/powerclasss
   docker compose restart app
   ```

4. Redémarrez la synchronisation automatique depuis l'interface

## 🔍 Vérification et logs

### Consulter les logs en temps réel

```bash
cd /opt/powerclasss
docker compose logs -f app | grep -i "sync\|google"
```

### Exemples de logs

```
🔄 Début de la synchronisation depuis Google Sheets...
✅ Produit mis à jour: iPhone 14 Pro - Quantité: 10 → 15
✅ Nouveau produit créé: Samsung Galaxy S24
✅ Synchronisation terminée: 3 mis à jour, 1 créés, 45 ignorés, 0 erreurs
```

## ⚠️ Points importants

### Code-barres obligatoire

Les produits **doivent avoir un code-barres** pour être synchronisés :
- Le code-barres sert d'identifiant unique
- Si un produit n'a pas de code-barres, il ne sera pas synchronisé

### Permissions Google Sheets

Le service account doit avoir les droits **Éditeur** sur le Google Sheet :
1. Ouvrir le Google Sheet
2. Cliquer sur **Partager**
3. Ajouter l'email du service account
4. Sélectionner **Éditeur**

### Synchronisation non-bloquante

- Les erreurs n'interrompent pas le processus
- Si un produit échoue, les autres continuent
- Toutes les erreurs sont loguées

## 🎬 Scénarios d'utilisation

### Scénario 1 : Mise à jour de quantité

```
1. Vous modifiez la quantité dans Google Sheets : 10 → 15
2. Après max 10 minutes (ou clic sur "Synchroniser Maintenant")
3. ✅ L'application détecte et applique le changement
```

### Scénario 2 : Ajout de nouveau produit

```
1. Vous ajoutez une nouvelle ligne dans Google Sheets
2. À la prochaine synchronisation
3. ✅ Le produit est créé dans l'application
```

### Scénario 3 : Vente en magasin

```
1. Vous vendez un produit (quantité: 1)
2. ✅ Stock dans l'application : 5 → 4 (immédiat)
3. ✅ Stock dans Google Sheets : 5 → 4 (immédiat)
```

## 🆘 Dépannage rapide

### La synchronisation ne démarre pas

**Vérifier** :
```bash
# 1. Vérifier les variables d'environnement
docker compose exec app env | grep GOOGLE_SHEETS

# 2. Vérifier que le fichier credentials existe
docker compose exec app ls -la /opt/powerclasss/credentials/

# 3. Consulter les logs
docker compose logs app | tail -50
```

### Les modifications ne sont pas détectées

**Solutions** :
1. Vérifier que la synchronisation est **active** (statut "EN COURS")
2. Cliquer sur **"Synchroniser Maintenant"** pour forcer
3. Vérifier que les produits ont un **code-barres**
4. Vérifier que le code-barres correspond entre Google Sheets et l'application

### Erreur "Permission denied"

**Solution** :
1. Partager le Google Sheet avec l'email du service account
2. Donner les droits **Éditeur** (pas seulement Lecteur)
3. Relancer la synchronisation

## 📚 Documentation complète

Pour plus de détails, consultez :
- `GOOGLE_SHEETS_BIDIRECTIONAL_SYNC.md` - Documentation complète
- `GOOGLE_SHEETS_AUTO_SYNC.md` - Synchronisation après vente
- `GOOGLE_SHEETS_SETUP.md` - Configuration initiale

## ✨ Résumé

✅ **Synchronisation bidirectionnelle automatique activée**
✅ **Interface de contrôle intuitive**
✅ **Logs détaillés pour le suivi**
✅ **Gestion robuste des erreurs**

Vous pouvez maintenant modifier vos quantités dans Google Sheets et elles seront automatiquement synchronisées dans l'application !
