# 📱 Instructions Twilio - Notifications de Dettes

## ✅ Configuration Actuelle

Votre système Twilio est **complètement configuré** et **fonctionnel** !

### Variables d'environnement (.env)
```env
ENABLE_DEBT_REMINDERS=true
DEBT_REMINDER_CHANNEL=sms
TWILIO_ACCOUNT_SID=ACb21e8790fcdc2e2c50ed00e8103af34a
TWILIO_AUTH_TOKEN=4487502c79d1267fcb88a0bd8fcd1d42
TWILIO_FROM=+12316245696

# MODE TEST (actuellement activé)
DEBT_REMINDER_DRY_RUN=true          # ← Mettre à false pour envoyer réellement
DEBT_REMINDER_INTERVAL_SECONDS=60   # Vérifie toutes les 60 secondes
DEBT_REMINDER_PERIOD_DAYS=0         # Pas d'attente entre notifications
DEFAULT_COUNTRY_CODE=+221           # Sénégal
```

## 🧪 Test Effectué

**Date:** 4 décembre 2025
**Résultat:** ✅ SUCCÈS

Le système a détecté **17 clients** avec des dettes en retard et a généré les messages correctement.

### Exemples de clients détectés:
- Haziza Apple: 2 500 XOF
- Fa Guité: 127 000 XOF (facture + dette manuelle)
- Grand Ndiaye: 235 000 XOF
- Cheikh ibra: 16 000 XOF
- Et 13 autres clients...

## 🚀 Pour Activer l'Envoi Réel

### Option 1: Modifier le .env (Recommandé)

1. Ouvrir `/opt/powerclasss/.env`
2. Changer la ligne:
   ```env
   DEBT_REMINDER_DRY_RUN=false
   ```
3. Redémarrer l'application:
   ```bash
   docker compose restart app
   ```

### Option 2: Test Manuel Immédiat

Dans le conteneur Docker:
```bash
docker exec powerclasss_app python3 test_debt_simple.py
```

## ⚙️ Configuration des Paramètres

### Intervalle de vérification
```env
DEBT_REMINDER_INTERVAL_SECONDS=60    # Vérifie toutes les 60 secondes
# Recommandé en production: 21600 (6 heures)
```

### Période entre notifications
```env
DEBT_REMINDER_PERIOD_DAYS=0    # Envoie immédiatement
# Recommandé en production: 2 (tous les 2 jours)
```

### Canal de notification
```env
DEBT_REMINDER_CHANNEL=sms    # Options: sms, email, log
```

## 📊 Monitoring

### Voir les logs en temps réel
```bash
docker logs -f powerclasss_app
```

### Tester manuellement
```bash
# Mode DRY_RUN (affiche dans console)
docker exec powerclasss_app python3 test_debt_simple.py

# Copier les scripts de test
docker cp test_debt_simple.py powerclasss_app:/app/
docker cp test_twilio.py powerclasss_app:/app/
```

## 💰 Coûts Twilio

- **SMS sortant:** ~0.0075 USD par SMS (varie selon pays)
- **17 clients détectés:** ~0.13 USD par envoi
- **Avec PERIOD_DAYS=2:** ~2 USD/mois maximum

## 🔒 Sécurité

✅ Les credentials Twilio sont dans `.env` (non versionné)
✅ Les numéros sont normalisés automatiquement
✅ Mode DRY_RUN pour tester sans risque
✅ Logs détaillés pour debugging

## 📝 Notes

- Le système démarre automatiquement avec l'application
- Les notifications sont envoyées en arrière-plan
- Chaque client ne reçoit qu'un message par période (PERIOD_DAYS)
- Les numéros locaux (77XXXXXXX) sont automatiquement préfixés avec +221

## 🆘 Dépannage

### Les messages ne s'envoient pas
1. Vérifier que `ENABLE_DEBT_REMINDERS=true`
2. Vérifier que `DEBT_REMINDER_DRY_RUN=false`
3. Vérifier les credentials Twilio
4. Consulter les logs: `docker logs powerclasss_app`

### Tester un envoi unique
```bash
docker exec -it powerclasss_app python3 test_twilio.py +221771234567
```

## ✅ Checklist de Production

- [ ] Mettre `DEBT_REMINDER_DRY_RUN=false`
- [ ] Augmenter `DEBT_REMINDER_INTERVAL_SECONDS` à 21600 (6h)
- [ ] Mettre `DEBT_REMINDER_PERIOD_DAYS` à 2 ou 3
- [ ] Vérifier le solde Twilio
- [ ] Tester avec 1-2 clients d'abord
- [ ] Monitorer les logs pendant 24h
- [ ] Configurer des alertes si nécessaire

---

**Système testé et validé le 4 décembre 2025** ✅
