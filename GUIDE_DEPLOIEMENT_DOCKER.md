# Guide Complet de Déploiement - Application powerclasss

## Vue d'ensemble
Ce guide vous accompagne étape par étape pour déployer votre application de gestion de stock sur un VPS Ubuntu en utilisant Docker et Docker Compose.

## Prérequis
- Un VPS Ubuntu 20.04+ avec accès root/sudo
- Un nom de domaine (optionnel mais recommandé)
- Connaissances de base en ligne de commande Linux

---

## Étape 1 : Préparation du VPS Ubuntu

### 1.1 Connexion au VPS
```bash
ssh root@VOTRE_IP_VPS
# ou
ssh utilisateur@VOTRE_IP_VPS
```

### 1.2 Mise à jour du système
```bash
# Mettre à jour les paquets
sudo apt update && sudo apt upgrade -y

# Installer les outils essentiels
sudo apt install -y curl wget git vim nano htop unzip
```

### 1.3 Configuration du firewall
```bash
# Activer UFW (Uncomplicated Firewall)
sudo ufw enable

# Autoriser SSH
sudo ufw allow ssh

# Autoriser HTTP et HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Autoriser le port 8000 (pour l'application)
sudo ufw allow 8000

# Vérifier le statut
sudo ufw status
```

---

## Étape 2 : Installation de Docker et Docker Compose

### 2.1 Installation de Docker
```bash
# Supprimer les anciennes versions
sudo apt remove -y docker docker-engine docker.io containerd runc

# Installer les dépendances
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Ajouter la clé GPG officielle de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Ajouter le repository Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Mettre à jour les paquets
sudo apt update

# Installer Docker
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Démarrer et activer Docker
sudo systemctl start docker
sudo systemctl enable docker

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER

# Vérifier l'installation
docker --version
```

### 2.2 Installation de Docker Compose
```bash
# Télécharger Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Rendre exécutable
sudo chmod +x /usr/local/bin/docker-compose

# Créer un lien symbolique
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Vérifier l'installation
docker-compose --version
```

### 2.3 Redémarrer la session
```bash
# Se déconnecter et se reconnecter pour appliquer les changements de groupe
exit
# Puis se reconnecter
ssh root@VOTRE_IP_VPS
```

---

## Étape 3 : Préparation de l'application

### 3.1 Cloner le projet
```bash
# Créer un répertoire pour l'application
sudo mkdir -p /opt/powerclasss
cd /opt/powerclasss

# Cloner le repository (remplacez par votre URL)
git clone https://github.com/VOTRE_USERNAME/powerclasss.git .

# Ou si vous avez déjà le code, le copier
# scp -r /chemin/vers/votre/projet/* root@VOTRE_IP:/opt/powerclasss/
```

### 3.2 Configuration des permissions
```bash
# Donner les bonnes permissions
sudo chown -R $USER:$USER /opt/powerclasss
chmod -R 755 /opt/powerclasss
```

---

## Étape 4 : Configuration de l'environnement

### 4.1 Créer le fichier .env
```bash
cd /opt/powerclasss
nano .env
```

Contenu du fichier `.env` :
```env
# Configuration de la base de données
DATABASE_URL=postgresql://postgres:123@db:5432/powerclasss_db
DB_SSLMODE=disable

# Configuration de l'application
HOST=0.0.0.0
PORT=8000
RELOAD=false

# Configuration de l'initialisation
INIT_DB_ON_STARTUP=true
SEED_DEFAULT_DATA=true

# Configuration des migrations (optionnel)
ENABLE_MIGRATIONS_WORKER=false

# Version des assets (pour le cache-busting)
ASSET_VERSION=production
```

### 4.2 Modifier docker-compose.yml pour la production
```bash
nano docker-compose.yml
```

Contenu optimisé pour la production :
```yaml
version: "3.9"

services:
  db:
    image: postgres:15-alpine
    container_name: powerclasss_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 123
      POSTGRES_DB: powerclasss_db
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: powerclasss_app
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://postgres:123@db:5432/powerclasss_db
      DB_SSLMODE: disable
      HOST: 0.0.0.0
      PORT: "8000"
      RELOAD: "false"
      INIT_DB_ON_STARTUP: "true"
      SEED_DEFAULT_DATA: "true"
      ENABLE_MIGRATIONS_WORKER: "false"
    ports:
      - "8000:8000"
    volumes:
      - ./static/uploads:/app/static/uploads
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  db_data:
```

---

## Étape 5 : Déploiement avec Docker

### 5.1 Construction et démarrage des conteneurs
```bash
cd /opt/powerclasss

# Construire les images
docker-compose build

# Démarrer les services
docker-compose up -d

# Vérifier le statut
docker-compose ps
```

### 5.2 Vérification des logs
```bash
# Voir les logs de l'application
docker-compose logs app

# Voir les logs de la base de données
docker-compose logs db

# Suivre les logs en temps réel
docker-compose logs -f app
```

### 5.3 Test de l'application
```bash
# Tester l'API
curl http://localhost:8000/api

# Tester l'interface web
curl http://localhost:8000/
```

---

## Étape 6 : Configuration du reverse proxy avec Nginx

### 6.1 Installation de Nginx
```bash
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 6.2 Configuration de Nginx
```bash
sudo nano /etc/nginx/sites-available/powerclasss
```

Contenu de la configuration :
```nginx
server {
    listen 80;
    server_name thegeektech.store www.thegeektech.store;

    # Redirection vers HTTPS (optionnel)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Gestion des fichiers statiques
    location /static/ {
        proxy_pass http://localhost:8000/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gestion des uploads
    location /static/uploads/ {
        proxy_pass http://localhost:8000/static/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 6.3 Activer la configuration
```bash
# Créer le lien symbolique
sudo ln -s /etc/nginx/sites-available/powerclasss /etc/nginx/sites-enabled/

# Supprimer la configuration par défaut
sudo rm /etc/nginx/sites-enabled/default

# Tester la configuration
sudo nginx -t

# Recharger Nginx
sudo systemctl reload nginx
```

---

## Étape 7 : Configuration SSL avec Let's Encrypt (Optionnel)

### 7.1 Installation de Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 7.2 Obtenir le certificat SSL
```bash
# Remplacer par votre domaine
sudo certbot --nginx -d thegeektech.store -d www.thegeektech.store
```

### 7.3 Vérification du renouvellement automatique
```bash
sudo certbot renew --dry-run
```

---

## Étape 8 : Configuration des sauvegardes

### 8.1 Script de sauvegarde de la base de données
```bash
sudo nano /opt/powerclasss/backup.sh
```

Contenu du script :
```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/opt/powerclasss/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="powerclasss_db"
DB_USER="postgres"
DB_PASSWORD="123"

# Créer le répertoire de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarder la base de données
docker exec powerclasss_db pg_dump -U $DB_USER -d $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Compresser la sauvegarde
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Supprimer les sauvegardes de plus de 7 jours
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

echo "Sauvegarde terminée: db_backup_$DATE.sql.gz"
```

### 8.2 Rendre le script exécutable
```bash
chmod +x /opt/powerclasss/backup.sh
```

### 8.3 Configurer la tâche cron
```bash
# Éditer le crontab
crontab -e

# Ajouter cette ligne pour une sauvegarde quotidienne à 2h du matin
0 2 * * * /opt/powerclasss/backup.sh >> /var/log/powerclasss-backup.log 2>&1
```

---

## Étape 9 : Monitoring et maintenance

### 9.1 Script de monitoring
```bash
sudo nano /opt/powerclasss/monitor.sh
```

Contenu du script :
```bash
#!/bin/bash

# Vérifier si les conteneurs sont en cours d'exécution
if ! docker ps | grep -q powerclasss_app; then
    echo "ALERTE: Le conteneur powerclasss_app n'est pas en cours d'exécution"
    # Redémarrer les services
    cd /opt/powerclasss
    docker-compose up -d
fi

if ! docker ps | grep -q powerclasss_db; then
    echo "ALERTE: Le conteneur powerclasss_db n'est pas en cours d'exécution"
    # Redémarrer les services
    cd /opt/powerclasss
    docker-compose up -d
fi

# Vérifier l'espace disque
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "ALERTE: Espace disque faible: ${DISK_USAGE}%"
fi

echo "Monitoring terminé à $(date)"
```

### 9.2 Rendre le script exécutable
```bash
chmod +x /opt/powerclasss/monitor.sh
```

### 9.3 Ajouter au crontab
```bash
crontab -e

# Ajouter cette ligne pour un monitoring toutes les 5 minutes
*/5 * * * * /opt/powerclasss/monitor.sh >> /var/log/powerclasss-monitor.log 2>&1
```

---

## Étape 10 : Commandes de gestion

### 10.1 Commandes Docker utiles
```bash
# Voir les conteneurs en cours d'exécution
docker ps

# Voir tous les conteneurs
docker ps -a

# Voir les logs
docker-compose logs -f

# Redémarrer les services
docker-compose restart

# Arrêter les services
docker-compose down

# Redémarrer avec reconstruction
docker-compose up -d --build

# Voir l'utilisation des ressources
docker stats
```

### 10.2 Commandes de maintenance
```bash
# Nettoyer les images Docker inutilisées
docker system prune -a

# Sauvegarder manuellement
/opt/powerclasss/backup.sh

# Vérifier l'espace disque
df -h

# Voir les logs de l'application
tail -f /var/log/powerclasss-monitor.log
```

---

## Étape 11 : Accès à l'application

### 11.1 URLs d'accès
- **Interface web** : `http://VOTRE_IP:8000` ou `http://thegeektech.store`
- **API** : `http://VOTRE_IP:8000/api` ou `http://thegeektech.store/api`

### 11.2 Comptes par défaut
- **Admin** : `admin` / `admin123`
- **Utilisateur** : `user` / `user123`

---

## Dépannage

### Problèmes courants

#### 1. L'application ne démarre pas
```bash
# Vérifier les logs
docker-compose logs app

# Vérifier la configuration
docker-compose config

# Redémarrer avec reconstruction
docker-compose down
docker-compose up -d --build
```

#### 2. Problème de base de données
```bash
# Vérifier les logs de la DB
docker-compose logs db

# Se connecter à la base de données
docker exec -it powerclasss_db psql -U postgres -d powerclasss_db
```

#### 3. Problème de permissions
```bash
# Corriger les permissions
sudo chown -R $USER:$USER /opt/powerclasss
chmod -R 755 /opt/powerclasss
```

#### 4. Problème de port
```bash
# Vérifier les ports utilisés
sudo netstat -tlnp | grep :8000

# Tuer un processus sur le port 8000
sudo fuser -k 8000/tcp
```

---

## Sécurité

### Recommandations de sécurité

1. **Changer les mots de passe par défaut**
2. **Configurer un firewall strict**
3. **Utiliser HTTPS en production**
4. **Mettre à jour régulièrement le système**
5. **Configurer des sauvegardes automatiques**
6. **Surveiller les logs**

### Commandes de sécurité
```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Vérifier les ports ouverts
sudo netstat -tlnp

# Vérifier les processus en cours
ps aux | grep powerclasss
```

---

## Conclusion

Votre application powerclasss est maintenant déployée sur votre VPS Ubuntu avec Docker ! 

### Points clés à retenir :
- L'application est accessible via `http://VOTRE_IP:8000` ou `http://thegeektech.store`
- Les données sont persistantes grâce aux volumes Docker
- Les sauvegardes sont automatiques
- Le monitoring est configuré
- Nginx fait office de reverse proxy

### Prochaines étapes :
1. Configurer votre nom de domaine
2. Mettre en place HTTPS
3. Personnaliser l'application selon vos besoins
4. Configurer des alertes de monitoring

Pour toute question ou problème, consultez les logs avec `docker-compose logs -f`.
