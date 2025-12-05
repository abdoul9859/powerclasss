# 📅 Timeline des Rappels Automatiques - Tous les 3 Jours

## 🎯 Scénario Exemple: Client avec Dette de 127 000 XOF

### Configuration Active
```
DEBT_REMINDER_PERIOD_DAYS=3    # Rappel tous les 3 jours
DEBT_REMINDER_INTERVAL_SECONDS=21600    # Vérification toutes les 6h
```

---

## 📊 Timeline Complète

```
┌─────────────────────────────────────────────────────────────────┐
│                    CYCLE DE RAPPELS                             │
└─────────────────────────────────────────────────────────────────┘

Jour 0 (4 déc)  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                📨 1er RAPPEL ENVOYÉ
                Dette: 127 000 XOF
                Message: "Certaines créances ont dépassé leur échéance..."
                ✅ Enregistré dans cache: 2025-12-04 17:12:00

Jour 1 (5 déc)  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                ⏳ Vérification (6h, 12h, 18h, 24h)
                ❌ Pas de rappel (< 3 jours)
                Dette: 127 000 XOF

Jour 2 (6 déc)  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                ⏳ Vérification (6h, 12h, 18h, 24h)
                ❌ Pas de rappel (< 3 jours)
                Dette: 127 000 XOF

Jour 3 (7 déc)  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                📨 2ème RAPPEL ENVOYÉ
                Dette: 127 000 XOF (ou moins si paiement partiel)
                ✅ Cache mis à jour: 2025-12-07 17:12:00

Jour 4 (8 déc)  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                ⏳ Vérification
                ❌ Pas de rappel (< 3 jours)
                💰 Client paie 50 000 XOF
                Dette restante: 77 000 XOF

Jour 5 (9 déc)  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                ⏳ Vérification
                ❌ Pas de rappel (< 3 jours)
                Dette: 77 000 XOF

Jour 6 (10 déc) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                📨 3ème RAPPEL ENVOYÉ
                Dette: 77 000 XOF (montant mis à jour)
                ✅ Cache mis à jour: 2025-12-10 17:12:00

Jour 7-8        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                ⏳ Vérification
                ❌ Pas de rappel (< 3 jours)

Jour 9 (13 déc) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                📨 4ème RAPPEL ENVOYÉ
                Dette: 77 000 XOF
                ✅ Cache mis à jour: 2025-12-13 17:12:00

Jour 10-11      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                ⏳ Vérification
                ❌ Pas de rappel (< 3 jours)

Jour 12 (16 déc)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                📨 5ème RAPPEL ENVOYÉ
                💰 Client paie 77 000 XOF (SOLDE COMPLET)
                Dette restante: 0 XOF
                ✅ ARRÊT AUTOMATIQUE DES RAPPELS
```

---

## 🔄 Logique du Système

### Vérification Toutes les 6 Heures
```
00:00 → Vérification
06:00 → Vérification
12:00 → Vérification
18:00 → Vérification
```

### Décision d'Envoi
```python
Pour chaque client avec dette:
    Si (Date actuelle - Dernier rappel) >= 3 jours:
        ✅ Envoyer rappel
        📝 Mettre à jour cache
    Sinon:
        ❌ Attendre
```

### Arrêt Automatique
```python
Si remaining_amount == 0:
    ✅ Ne plus envoyer de rappel
    🗑️  Le cache reste mais n'est plus utilisé
```

---

## 📱 Évolution des Messages

### Jour 0 - Premier Rappel
```
Bonjour Fa Guité,

Nous vous informons que certaines créances ont dépassé leur date d'échéance :

Factures en retard:
 - Facture FAC-0096 • Échéance: 2025-11-12 • Restant: 25000 XOF

Créances manuelles en retard:
 - Réf 7 • Échéance: 2025-11-30 • Restant: 102000 XOF

Merci de régulariser votre situation dans les meilleurs délais.
```

### Jour 3 - Deuxième Rappel (Identique)
```
Bonjour Fa Guité,

Nous vous informons que certaines créances ont dépassé leur date d'échéance :

Factures en retard:
 - Facture FAC-0096 • Échéance: 2025-11-12 • Restant: 25000 XOF

Créances manuelles en retard:
 - Réf 7 • Échéance: 2025-11-30 • Restant: 102000 XOF

Merci de régulariser votre situation dans les meilleurs délais.
```

### Jour 6 - Troisième Rappel (Après paiement partiel)
```
Bonjour Fa Guité,

Nous vous informons que certaines créances ont dépassé leur date d'échéance :

Créances manuelles en retard:
 - Réf 7 • Échéance: 2025-11-30 • Restant: 52000 XOF

Merci de régulariser votre situation dans les meilleurs délais.
```

---

## 📊 Statistiques sur 1 Mois

### Avec 17 Clients Actuels

| Scénario | Rappels/Client | Total SMS | Coût Estimé |
|----------|----------------|-----------|-------------|
| Tous paient en 1 semaine | 2-3 | 34-51 | $0.26-$0.38 |
| 50% paient en 2 semaines | 4-5 | 68-85 | $0.51-$0.64 |
| Tous paient en 1 mois | 10 | 170 | $1.28 |
| Aucun ne paie (1 mois) | 10 | 170 | $1.28 |

**Coût SMS:** ~$0.0075 par SMS

---

## 🎯 Cas d'Usage Réels

### Cas 1: Paiement Rapide
```
Jour 0: 📨 Rappel → Client contacte immédiatement
Jour 1: 💰 Paiement complet
Résultat: 1 seul SMS envoyé
```

### Cas 2: Paiement Progressif
```
Jour 0: 📨 Rappel (100 000 XOF)
Jour 3: 📨 Rappel (100 000 XOF)
Jour 4: 💰 Paiement 50 000 XOF
Jour 6: 📨 Rappel (50 000 XOF)
Jour 8: 💰 Paiement 50 000 XOF
Résultat: 3 SMS envoyés
```

### Cas 3: Mauvais Payeur
```
Jour 0: 📨 Rappel
Jour 3: 📨 Rappel
Jour 6: 📨 Rappel
Jour 9: 📨 Rappel
...continue jusqu'au paiement
```

---

## 🛠️ Commandes Utiles

### Voir l'État Actuel
```bash
docker exec powerclasss_app python3 test_rappel_3jours.py
# Choisir option 1
```

### Simuler 10 Jours
```bash
docker exec powerclasss_app python3 test_rappel_3jours.py
# Choisir option 2, entrer 10
```

### Forcer un Nouveau Rappel
```bash
docker exec powerclasss_app python3 test_rappel_3jours.py
# Choisir option 3, entrer l'ID client
```

### Voir les Logs en Direct
```bash
docker logs -f powerclasss_app | grep "DebtNotifier"
```

---

## 💡 Conseils

### Optimisation de la Période
- **2 jours:** Plus insistant, bon pour petites dettes
- **3 jours:** Équilibre idéal (recommandé)
- **5 jours:** Plus espacé, pour gros clients
- **7 jours:** Hebdomadaire, très courtois

### Personnalisation par Type de Client
Vous pouvez créer des règles différentes :
- VIP: 5 jours
- Réguliers: 3 jours
- Nouveaux: 2 jours

(Nécessite modification du code)

---

**Configuration actuelle: Rappels tous les 3 jours** ✅
**Vérification: Toutes les 6 heures** ✅
**Arrêt automatique: Dès paiement complet** ✅
