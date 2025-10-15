# Intégration Google Sheets - Guide Rapide

## Vue d'ensemble

L'intégration Google Sheets permet d'importer automatiquement vos produits depuis un Google Spreadsheet vers votre application PowerClass. Cette fonctionnalité facilite la migration de données et la synchronisation avec des fichiers Excel/Google Sheets existants.

## Accès rapide

Une fois configuré, accédez à l'interface de synchronisation via :
- **URL**: `http://votre-domaine.com/google-sheets-sync`
- **Navigation**: Paramètres → Synchronisation Google Sheets

## Fonctionnalités

- ✅ Importation automatique des produits depuis Google Sheets
- ✅ Mapping automatique des colonnes vers le modèle de données
- ✅ Test de connexion avant synchronisation
- ✅ Mode de mise à jour des produits existants (par code-barres)
- ✅ Création automatique de mouvements de stock
- ✅ Rapport détaillé de synchronisation avec statistiques
- ✅ Gestion des erreurs avec logs détaillés

## Prérequis

1. **Service Account Google** avec accès à l'API Google Sheets
2. **Fichier JSON de credentials** du Service Account
3. **Google Spreadsheet** avec la structure de colonnes appropriée

## Configuration rapide (3 étapes)

### 1. Créer le Service Account Google

```bash
# Aller sur Google Cloud Console
https://console.cloud.google.com/

# Créer un projet ou sélectionner un existant
# Activer l'API Google Sheets
# Créer un Service Account avec le rôle "Editor"
# Télécharger le fichier JSON de credentials
```

### 2. Configurer les credentials sur le serveur

```bash
# Créer le dossier pour les credentials
mkdir -p /opt/powerclasss/credentials

# Copier le fichier JSON (depuis votre machine locale)
scp chemin/vers/votre-credentials.json user@votre-vps:/opt/powerclasss/credentials/google-sheets-credentials.json

# Sécuriser les permissions
chmod 600 /opt/powerclasss/credentials/google-sheets-credentials.json
```

Modifier le fichier `.env` :

```env
GOOGLE_SHEETS_CREDENTIALS_PATH=/opt/powerclasss/credentials/google-sheets-credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=votre_spreadsheet_id
GOOGLE_SHEETS_WORKSHEET_NAME=Tableau1
```

### 3. Partager le Google Sheet avec le Service Account

```bash
# Copier l'email du service account depuis le fichier JSON
# Exemple: powerclasss@mon-projet.iam.gserviceaccount.com

# Dans Google Sheets, cliquer sur "Partager"
# Coller l'email du service account
# Donner les droits de "Lecteur"
```

## Structure du Google Sheet

Votre Google Sheet doit contenir les colonnes suivantes (première ligne = en-têtes) :

| Colonne | Type | Obligatoire | Description |
|---------|------|-------------|-------------|
| `Nom du produit` | Texte | ✅ Oui | Nom du produit |
| `Categorie` | Texte | ⬜ Non | Catégorie du produit |
| `Etat` | Texte | ⬜ Non | État (neuf, occasion, venant) |
| `Marque` | Texte | ⬜ Non | Marque du produit |
| `Modele` | Texte | ⬜ Non | Modèle du produit |
| `Prix d'achat (FCFA)` | Nombre | ⬜ Non | Prix d'achat unitaire |
| `Prix en gros (FCFA)` | Nombre | ⬜ Non | Prix de vente en gros |
| `Prix unitaire (FCFA)` | Nombre | ✅ Oui | Prix de vente unitaire |
| `Code-barres produit` | Texte | ⬜ Non | Code-barres unique |
| `Quantite en stock` | Nombre | ⬜ Non | Quantité disponible |
| `Description` | Texte | ⬜ Non | Description détaillée |
| `Notes` | Texte | ⬜ Non | Notes additionnelles |
| `Lieu ou Image du produit` | Texte | ⬜ Non | Chemin vers l'image |

### Exemple de Google Sheet

```
| Nom du produit | Categorie | Etat | Marque | Modele | Prix d'achat (FCFA) | Prix en gros (FCFA) | Prix unitaire (FCFA) | Code-barres produit | Quantite en stock |
|----------------|-----------|------|--------|--------|---------------------|---------------------|---------------------|---------------------|-------------------|
| iPhone 14 Pro  | Smartphones | neuf | Apple | iPhone 14 Pro | 450 000 | 480 000 | 500 000 | 1234567890123 | 5 |
| MacBook Pro M2 | Ordinateurs | neuf | Apple | MacBook Pro | 850 000 | 900 000 | 950 000 | 9876543210987 | 3 |
```

**Important**: Les espaces dans les prix (ex: `450 000`) sont automatiquement gérés.

## Utilisation

### Via l'interface web

1. Connectez-vous à l'application
2. Accédez à `/google-sheets-sync`
3. Entrez l'ID de votre Google Sheet (trouvé dans l'URL)
4. Cliquez sur **Tester la Connexion** pour vérifier
5. Cliquez sur **Synchroniser** pour importer les produits

### Via l'API

```bash
# Tester la connexion
curl -X POST http://votre-domaine.com/api/google-sheets/test-connection \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"spreadsheet_id": "VOTRE_SPREADSHEET_ID"}'

# Synchroniser les produits
curl -X POST http://votre-domaine.com/api/google-sheets/sync \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "spreadsheet_id": "VOTRE_SPREADSHEET_ID",
    "worksheet_name": "Tableau1",
    "update_existing": false
  }'
```

## Options de synchronisation

### Mettre à jour les produits existants

- **Si coché** : Les produits existants (identifiés par leur code-barres) seront mis à jour avec les nouvelles données
- **Si décoché** : Les produits existants seront ignorés (pas de modification)

### Nom de la feuille

Par défaut `Tableau1`. Changez-le si votre onglet a un nom différent dans le Google Sheet.

## Résultats de synchronisation

Après chaque synchronisation, vous obtenez un rapport avec :

- **Total** : Nombre total de lignes dans le Google Sheet
- **Créés** : Nombre de nouveaux produits ajoutés
- **Mis à jour** : Nombre de produits modifiés (si l'option est activée)
- **Ignorés** : Nombre de produits déjà existants (si l'option de mise à jour est désactivée)
- **Erreurs** : Nombre d'erreurs rencontrées avec détails

## Architecture technique

### Fichiers créés

```
app/
├── services/
│   └── google_sheets_service.py    # Service d'intégration
├── routers/
│   └── google_sheets.py             # Routes API
templates/
└── google_sheets_sync.html          # Interface web
```

### API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/google-sheets/sync` | POST | Synchronise les produits |
| `/api/google-sheets/test-connection` | POST | Test la connexion |
| `/api/google-sheets/settings` | GET | Récupère la configuration |

### Dépendances ajoutées

```
gspread==6.0.0                # Client Google Sheets
google-auth==2.27.0           # Authentification Google
google-auth-oauthlib==1.2.0   # OAuth pour Google
google-auth-httplib2==0.2.0   # HTTP lib pour Google Auth
```

## Sécurité

### Bonnes pratiques

✅ **À FAIRE**:
- Stocker le fichier JSON dans un dossier sécurisé avec `chmod 600`
- Ajouter `credentials/` dans `.gitignore`
- Utiliser des rôles IAM avec le minimum de permissions
- Rotez régulièrement les clés du service account
- Donner uniquement les droits de "Lecteur" au service account

❌ **À NE PAS FAIRE**:
- Committer le fichier JSON dans Git
- Partager publiquement les credentials
- Donner des droits "Éditeur" au service account sur le Google Sheet
- Laisser le fichier JSON accessible en lecture par d'autres utilisateurs

### Vérifier la sécurité

```bash
# Vérifier les permissions du fichier credentials
ls -l /opt/powerclasss/credentials/google-sheets-credentials.json
# Devrait afficher: -rw------- (600)

# Vérifier que le dossier n'est pas dans Git
git check-ignore credentials/
# Devrait afficher: credentials/
```

## Dépannage

### Erreur: "Les credentials ne sont pas configurés"

**Solution**:
```bash
# Vérifier que le fichier existe
ls -l $GOOGLE_SHEETS_CREDENTIALS_PATH

# Vérifier la variable d'environnement
env | grep GOOGLE_SHEETS

# Redémarrer l'application
docker compose restart app
```

### Erreur: "Impossible de s'authentifier"

**Solution**:
- Vérifier que l'API Google Sheets est activée dans Google Cloud Console
- Vérifier que le fichier JSON est valide (ouvrir avec un éditeur de texte)
- Vérifier que le service account a les permissions nécessaires

### Erreur: "Spreadsheet not found"

**Solution**:
- Vérifier l'ID du spreadsheet (copier depuis l'URL)
- Vérifier que le Google Sheet est partagé avec l'email du service account
- Vérifier que le service account a au moins les droits de lecture

### Les colonnes ne sont pas reconnues

**Solution**:
- Vérifier que les noms de colonnes sont EXACTEMENT comme spécifié (respecter la casse)
- Vérifier qu'il n'y a pas d'espaces supplémentaires dans les noms de colonnes
- La première ligne doit contenir les en-têtes

### Les produits ne s'importent pas

**Solution**:
- Consulter les logs : `docker compose logs -f app`
- Vérifier le rapport de synchronisation dans l'interface pour voir les erreurs détaillées
- Vérifier que le nom de la feuille est correct
- Vérifier que les données sont dans le bon format (nombres pour les prix, etc.)

## Logs et monitoring

### Consulter les logs

```bash
# Logs en temps réel
docker compose logs -f app

# Logs récents (dernières 100 lignes)
docker compose logs --tail=100 app

# Filtrer par mot-clé
docker compose logs app | grep "google"
```

### Logs de synchronisation

Les logs incluent :
- Début et fin de synchronisation
- Nombre de produits traités
- Erreurs détaillées avec numéro de ligne
- Temps d'exécution

## Support et documentation

Pour plus d'informations, consultez :
- **Configuration détaillée** : `GOOGLE_SHEETS_SETUP.md`
- **Documentation du projet** : `CLAUDE.md`
- **Schéma de la base de données** : `app/database.py`

## Améliorations futures possibles

- [ ] Synchronisation automatique programmée (cron)
- [ ] Import de variantes de produits
- [ ] Import de plusieurs feuilles simultanément
- [ ] Export de produits vers Google Sheets
- [ ] Historique des synchronisations
- [ ] Notifications par email après synchronisation
- [ ] Validation des données avant import
- [ ] Preview des données avant import

## Contribution

Si vous rencontrez des bugs ou avez des suggestions d'amélioration, veuillez créer une issue ou une pull request sur le dépôt Git du projet.
