# Configuration de l'intégration Google Sheets

Ce guide vous explique comment configurer l'intégration Google Sheets pour importer automatiquement vos produits.

## Étape 1 : Créer un Service Account Google

1. Accédez à la [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez l'API Google Sheets :
   - Dans le menu, allez à **APIs & Services** > **Library**
   - Recherchez "Google Sheets API"
   - Cliquez sur **Enable**
4. Créez un Service Account :
   - Allez à **APIs & Services** > **Credentials**
   - Cliquez sur **Create Credentials** > **Service Account**
   - Donnez un nom à votre service account (ex: "powerclasss-sheets-sync")
   - Cliquez sur **Create and Continue**
   - Sélectionnez le rôle **Editor** (ou un rôle personnalisé avec les permissions nécessaires)
   - Cliquez sur **Done**

## Étape 2 : Télécharger le fichier de credentials JSON

1. Dans la liste des Service Accounts, cliquez sur le service account que vous venez de créer
2. Allez dans l'onglet **Keys**
3. Cliquez sur **Add Key** > **Create new key**
4. Sélectionnez le format **JSON**
5. Cliquez sur **Create** - le fichier sera téléchargé automatiquement

## Étape 3 : Configurer le fichier de credentials sur le serveur

### Option 1 : Via le fichier .env (Recommandé)

1. Copiez le fichier JSON téléchargé sur votre serveur VPS dans un endroit sécurisé (ex: `/opt/powerclasss/credentials/`)

```bash
# Créer le dossier pour les credentials
mkdir -p /opt/powerclasss/credentials

# Copier le fichier (remplacez le chemin par le vôtre)
scp chemin/vers/votre-service-account.json user@votre-vps:/opt/powerclasss/credentials/google-sheets-credentials.json

# Sécuriser les permissions
chmod 600 /opt/powerclasss/credentials/google-sheets-credentials.json
```

2. Modifiez le fichier `.env` de votre application :

```bash
nano /opt/powerclasss/.env
```

3. Ajoutez ces lignes :

```env
# Configuration Google Sheets
GOOGLE_SHEETS_CREDENTIALS_PATH=/opt/powerclasss/credentials/google-sheets-credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=votre_spreadsheet_id_ici
GOOGLE_SHEETS_WORKSHEET_NAME=Tableau1
```

### Option 2 : Via Docker Compose (si vous utilisez Docker)

Modifiez votre `docker-compose.yml` :

```yaml
services:
  app:
    # ... autres configurations ...
    volumes:
      - ./credentials:/app/credentials:ro  # Montage en lecture seule
    environment:
      - GOOGLE_SHEETS_CREDENTIALS_PATH=/app/credentials/google-sheets-credentials.json
      - GOOGLE_SHEETS_SPREADSHEET_ID=votre_spreadsheet_id_ici
      - GOOGLE_SHEETS_WORKSHEET_NAME=Tableau1
```

Puis reconstruisez et redémarrez :

```bash
docker compose down
docker compose up -d --build
```

## Étape 4 : Partager votre Google Sheet avec le Service Account

1. Ouvrez votre Google Sheet
2. Cliquez sur le bouton **Partager** (en haut à droite)
3. Copiez l'adresse email du service account (se trouve dans le fichier JSON, champ `client_email`)
   - Elle ressemble à : `powerclasss-sheets-sync@votre-projet.iam.gserviceaccount.com`
4. Collez cette adresse dans le champ de partage
5. Sélectionnez **Lecteur** comme niveau d'accès (lecture seule suffit)
6. Cliquez sur **Envoyer**

## Étape 5 : Obtenir l'ID de votre Google Sheet

L'ID du Google Sheet se trouve dans l'URL :

```
https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit
```

Par exemple, dans cette URL :
```
https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j/edit
```

L'ID est : `1a2b3c4d5e6f7g8h9i0j`

## Étape 6 : Préparer votre Google Sheet

Assurez-vous que votre Google Sheet a les colonnes suivantes (exactement comme indiqué) :

| Colonne | Description | Obligatoire |
|---------|-------------|-------------|
| Nom du produit | Nom du produit | Oui |
| Categorie | Catégorie du produit | Non |
| Etat | État (neuf, occasion, venant) | Non |
| Marque | Marque du produit | Non |
| Modele | Modèle du produit | Non |
| Prix d'achat (FCFA) | Prix d'achat unitaire | Non |
| Prix en gros (FCFA) | Prix de vente en gros | Non |
| Prix unitaire (FCFA) | Prix de vente unitaire | Oui |
| Code-barres produit | Code-barres unique | Non |
| Quantite en stock | Quantité disponible | Non |
| Description | Description détaillée | Non |
| Notes | Notes additionnelles | Non |
| Lieu ou Image du produit | Chemin vers l'image | Non |

**Important :** La première ligne doit contenir les en-têtes de colonnes exactement comme indiqué ci-dessus.

### Exemple de Google Sheet

```
| Nom du produit | Categorie | Etat | Marque | Modele | Prix d'achat (FCFA) | Prix en gros (FCFA) | Prix unitaire (FCFA) | Code-barres produit | Quantite en stock | Description |
|----------------|-----------|------|--------|--------|---------------------|---------------------|---------------------|---------------------|-------------------|-------------|
| iPhone 14 Pro  | Smartphones | neuf | Apple | iPhone 14 Pro | 450000 | 480000 | 500000 | 1234567890123 | 5 | iPhone 14 Pro 256GB |
| MacBook Pro M2 | Ordinateurs | neuf | Apple | MacBook Pro | 850000 | 900000 | 950000 | 9876543210987 | 3 | MacBook Pro M2 16" |
```

## Étape 7 : Utiliser l'interface de synchronisation

1. Connectez-vous à votre application
2. Accédez à la page de synchronisation : `/google-sheets-sync`
3. Saisissez l'ID de votre Google Sheet
4. Cliquez sur **Tester la Connexion** pour vérifier que tout fonctionne
5. Cliquez sur **Synchroniser** pour importer les produits

### Options de synchronisation

- **Nom de la feuille** : Par défaut "Tableau1", changez-le si votre onglet a un nom différent
- **Mettre à jour les produits existants** : Si coché, les produits existants (identifiés par leur code-barres) seront mis à jour. Sinon, ils seront ignorés.

## Dépannage

### Erreur : "Les credentials Google Sheets ne sont pas configurés"

- Vérifiez que le fichier JSON est bien présent au chemin spécifié dans `GOOGLE_SHEETS_CREDENTIALS_PATH`
- Vérifiez les permissions du fichier : `ls -l /opt/powerclasss/credentials/google-sheets-credentials.json`
- Vérifiez que la variable d'environnement est bien définie : `env | grep GOOGLE_SHEETS`

### Erreur : "Impossible de s'authentifier avec Google Sheets API"

- Vérifiez que l'API Google Sheets est bien activée dans la console Google Cloud
- Vérifiez que le fichier JSON contient les bonnes informations
- Vérifiez que le Service Account a les permissions nécessaires

### Erreur : "Permission denied" ou "Spreadsheet not found"

- Vérifiez que vous avez bien partagé le Google Sheet avec l'email du service account
- Vérifiez que l'ID du spreadsheet est correct
- Vérifiez que le service account a au moins un accès en lecture

### Les produits ne s'importent pas correctement

- Vérifiez que les noms de colonnes sont exactement comme indiqué (respectez la casse et les espaces)
- Vérifiez que vos données sont dans la bonne feuille (vérifiez le nom de l'onglet)
- Consultez les détails des erreurs dans l'interface de synchronisation

## Sécurité

- **Ne commitez JAMAIS** le fichier JSON des credentials dans Git
- Ajoutez `credentials/` dans votre `.gitignore`
- Limitez les permissions du fichier JSON : `chmod 600`
- Utilisez des rôles IAM avec le minimum de permissions nécessaires
- Rotez régulièrement les clés du service account

## Support

Pour toute question ou problème, consultez les logs de l'application :

```bash
# Si vous utilisez Docker
docker compose logs -f app

# Si vous exécutez l'application directement
tail -f /var/log/powerclasss/app.log
```
