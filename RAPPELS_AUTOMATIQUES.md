# 🔔 Système de Rappels Automatiques - Tous les 3 Jours

## ⚙️ Configuration Actuelle

```env
ENABLE_DEBT_REMINDERS=true           # ✅ Système activé
DEBT_REMINDER_CHANNEL=sms            # ✅ Envoi par SMS
DEBT_REMINDER_DRY_RUN=true           # ⚠️  Mode test (mettre false pour production)
DEBT_REMINDER_INTERVAL_SECONDS=21600 # ✅ Vérifie toutes les 6 heures
DEBT_REMINDER_PERIOD_DAYS=3          # ✅ Rappel tous les 3 jours par client
```

## 🔄 Comment ça Fonctionne

### 1. **Vérification Automatique**
- L'application vérifie **toutes les 6 heures** (21600 secondes)
- Recherche les clients avec dettes en retard
- Compare avec la dernière date d'envoi

### 2. **Logique de Rappel par Client**
```
Jour 0  : Client a une dette → 📨 1er SMS envoyé
Jour 1  : Pas de rappel (< 3 jours)
Jour 2  : Pas de rappel (< 3 jours)
Jour 3  : 📨 2ème SMS envoyé (3 jours écoulés)
Jour 6  : 📨 3ème SMS envoyé (3 jours écoulés)
Jour 9  : 📨 4ème SMS envoyé (3 jours écoulés)
...
Jusqu'au paiement complet
```

### 3. **Arrêt Automatique**
Le système arrête d'envoyer des rappels quand :
- ✅ La facture est payée (`remaining_amount = 0`)
- ✅ La dette manuelle est soldée (`remaining_amount = 0`)
- ✅ Le statut passe à "paid"

## 📊 Exemple Concret

### Client: Fa Guité
**Dette totale:** 127 000 XOF
- Facture FAC-0096: 25 000 XOF (échéance: 12 nov)
- Dette Réf 7: 102 000 XOF (échéance: 30 nov)

**Timeline des rappels:**

| Date | Action | Dette Restante | SMS Envoyé |
|------|--------|----------------|------------|
| 4 déc | Détection dette | 127 000 XOF | ✅ 1er rappel |
| 5 déc | Vérification | 127 000 XOF | ❌ (< 3 jours) |
| 6 déc | Vérification | 127 000 XOF | ❌ (< 3 jours) |
| 7 déc | 3 jours écoulés | 127 000 XOF | ✅ 2ème rappel |
| 8 déc | Client paie 50k | 77 000 XOF | ❌ (< 3 jours) |
| 10 déc | 3 jours écoulés | 77 000 XOF | ✅ 3ème rappel |
| 12 déc | Client paie 77k | 0 XOF | ✅ **ARRÊT** |

## 🗄️ Stockage des Dates

Le système utilise la table `app_cache` pour stocker la dernière date d'envoi :

```sql
-- Exemple d'enregistrement
cache_key: "DEBT_REMINDER_LAST_SENT_52"  -- Client ID 52
cache_value: "2025-12-04T17:12:00"       -- Dernière notification
```

## 📱 Format des Messages

### Premier Rappel
```
Bonjour Fa Guité,

Nous vous informons que certaines créances ont dépassé leur date d'échéance :

Factures en retard:
 - Facture FAC-0096 • Échéance: 2025-11-12 • Restant: 25000 XOF

Créances manuelles en retard:
 - Réf 7 • Échéance: 2025-11-30 • Restant: 102000 XOF

Merci de régulariser votre situation dans les meilleurs délais.
```

### Rappels Suivants
Le message est identique mais reflète le montant restant actuel.

## 🧪 Test du Système

### Test en Mode DRY_RUN (Recommandé d'abord)
```bash
# Affiche les messages sans envoyer
docker exec powerclasss_app python3 test_debt_simple.py
```

### Test avec Envoi Réel
```bash
# 1. Activer l'envoi réel
# Modifier .env: DEBT_REMINDER_DRY_RUN=false

# 2. Redémarrer l'application
docker compose restart app

# 3. Forcer un test immédiat
docker exec powerclasss_app python3 test_debt_simple.py
```

### Simuler un Rappel Après 3 Jours
```bash
# Voir le script test_rappel_3jours.py
docker exec powerclasss_app python3 test_rappel_3jours.py
```

## 📈 Monitoring

### Voir les Logs en Temps Réel
```bash
docker logs -f powerclasss_app | grep DebtNotifier
```

### Vérifier les Derniers Envois
```sql
-- Dans la base de données
SELECT * FROM app_cache 
WHERE cache_key LIKE 'DEBT_REMINDER_LAST_SENT_%'
ORDER BY cache_key;
```

### Statistiques
```bash
# Nombre de clients avec dettes
docker exec powerclasss_app python3 -c "
from app.database import SessionLocal, Invoice, ClientDebt
from datetime import date
db = SessionLocal()
today = date.today()
inv_count = db.query(Invoice).filter(Invoice.remaining_amount > 0, Invoice.due_date < today).count()
debt_count = db.query(ClientDebt).filter(ClientDebt.remaining_amount > 0, ClientDebt.due_date < today).count()
print(f'Factures en retard: {inv_count}')
print(f'Dettes manuelles en retard: {debt_count}')
"
```

## 💰 Estimation des Coûts

### Avec 17 Clients Actuels
- **SMS par rappel:** 17 SMS
- **Coût par SMS:** ~0.0075 USD
- **Coût par rappel:** ~0.13 USD

### Sur 1 Mois (rappels tous les 3 jours)
- **Nombre de rappels:** ~10 rappels/mois
- **Coût total:** ~1.30 USD/mois
- **Si 50% paient dans le mois:** ~0.65 USD/mois

## ⚠️ Recommandations

### Pour la Production
1. **Tester d'abord en DRY_RUN** pendant 1-2 jours
2. **Activer pour 2-3 clients** seulement au début
3. **Monitorer les retours** clients
4. **Ajuster la période** si nécessaire (2-4 jours)
5. **Vérifier le solde Twilio** régulièrement

### Personnalisation du Message
Pour modifier le message, éditez le fichier :
```
/opt/powerclasss/app/services/debt_notifier.py
Ligne 132-149 : Construction du message
```

### Ajuster la Fréquence
```env
# Plus fréquent (tous les 2 jours)
DEBT_REMINDER_PERIOD_DAYS=2

# Moins fréquent (toutes les semaines)
DEBT_REMINDER_PERIOD_DAYS=7

# Très urgent (tous les jours) - Non recommandé
DEBT_REMINDER_PERIOD_DAYS=1
```

## 🔧 Dépannage

### Les rappels ne s'envoient pas après 3 jours
1. Vérifier les logs: `docker logs powerclasss_app`
2. Vérifier la table app_cache
3. Vérifier que l'app tourne: `docker ps`

### Forcer un nouveau rappel pour un client
```sql
-- Supprimer l'enregistrement de cache
DELETE FROM app_cache 
WHERE cache_key = 'DEBT_REMINDER_LAST_SENT_52';  -- Remplacer 52 par l'ID client
```

### Tester sans attendre 3 jours
```env
# Temporairement, mettre à 0 pour tester
DEBT_REMINDER_PERIOD_DAYS=0
# Puis redémarrer: docker compose restart app
# N'oubliez pas de remettre à 3 après !
```

## ✅ Checklist de Mise en Production

- [x] Configuration testée en DRY_RUN
- [x] Période de rappel définie (3 jours)
- [x] Intervalle de vérification configuré (6h)
- [ ] Mode DRY_RUN désactivé (`false`)
- [ ] Application redémarrée
- [ ] Logs monitorés pendant 24h
- [ ] Solde Twilio vérifié
- [ ] Retours clients collectés
- [ ] Ajustements effectués si nécessaire

## 📞 Support

Pour toute question ou problème :
1. Consulter les logs
2. Vérifier la configuration .env
3. Tester en mode DRY_RUN
4. Vérifier la base de données (app_cache)

---

**Système configuré pour rappels tous les 3 jours** ✅
**Date:** 4 décembre 2025
