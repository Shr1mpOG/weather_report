# Guide de Présentation - Weather Report

## 🎯 Points clés à expliquer

### 1. Architecture générale (2 minutes)

**Deux modes d'exécution :**
- **Mode CLI** : Arguments en ligne de commande (`--city`, `--country`)
- **Mode Interactif** : Menu avec 3 options (Weather Report, ASCII Art, Exit)

**Point d'entrée unique :** `cli()` (décorateur Click)

---

### 2. Initialisation (1 minute)

**Au démarrage :**
- `setup_logging()` s'exécute automatiquement
- Crée le dossier "Logs" si nécessaire
- Configure loguru (rotation quotidienne, rétention 30 jours)

---

### 3. Gestion de la clé API (2 minutes)

**Processus en 3 étapes :**

1. **Chargement** (`load_api_key()`)
   - Lit `local.conf`
   - Cherche ligne `API_KEY=...`
   - Retourne la clé ou `None`

2. **Vérification** (`verify_api_key()`)
   - Test avec ville témoin (Toulouse, FR)
   - Vérifie `status_code == 200`
   - Gestion des erreurs (401, 500-599, réseau)

3. **Utilisation**
   - Mode CLI : Vérifie avant exécution
   - Mode Interactif : Vérifie avant menu

**Points de décision :**
- Clé fournie en argument ? → Utiliser
- Sinon → Charger depuis fichier
- Clé valide ? → Continuer / ERREUR

---

### 4. Exécution du rapport météo (3 minutes)

**Fonction principale : `execute_weather_report()`**

**Flux :**
```
1. Vérifier/Charger clé API
   └─► Si échec → ERREUR + return False

2. Construire URL API
   └─► Format: city,country + api_key + units=metric + lang=fr

3. Requête HTTP
   └─► Si status != 200 → ERREUR + return False

4. Récupérer JSON brut
   └─► response.json()

5. Formater les données
   └─► format_forecast(data)

6. Afficher (si display=True)
   └─► print(json.dumps(formatted))

7. Sauvegarder
   └─► save_to_file(formatted)
       └─► Si échec → Log error
       └─► Si succès → Log success + return True
```

---

### 5. Formatage des données (4 minutes)

**Fonction : `format_forecast(data)`**

**Objectif :** Transformer JSON brut → Structure formatée

**Processus :**

1. **Initialisation**
   - Extraire `city_info` et `forecast_list`
   - Créer structure `result` avec totaux à 0
   - Créer dictionnaire `days = {}` pour regrouper par jour

2. **Boucle sur chaque entrée (3h)**
   - Extraire date (convertir `dt_txt` → `YYYY-MM-DD`)
   - Extraire rain (gérer cas absence : `0.0`)
   - Extraire snow (gérer cas absence : `0.0`)
   - Extraire temp, humidity, weather_main
   - Mettre à jour totaux période
   - Mettre à jour cumuls journaliers
   - Stocker entrée météo (temp + weather) pour calcul transitions

3. **Boucle sur chaque jour**
   - Calculer transitions majeures : `calcul_major_transitions(entries)`
   - Créer `day_result` avec :
     - `date_local`
     - `rain_cumul_mm` (arrondi 2 décimales)
     - `snow_cumul_mm` (arrondi 2 décimales)
     - `major_transitions_count`
   - Ajouter à `forecast_details`

4. **Résultat final**
   - `forecast_location_name`
   - `country_code`
   - `total_rain_period_mm`
   - `total_snow_period_mm`
   - `max_humidity_period`
   - `forecast_details[]` (liste des jours)

---

### 6. Calcul des transitions majeures (2 minutes)

**Fonction : `calcul_major_transitions(entries)`**

**Définition :** Transition majeure = Changement de météo (`weather.main`) **ET** variation température > 3°C

**Algorithme :**
```
Pour chaque paire d'entrées consécutives (i-1, i):
  Si weather[i-1] != weather[i] ET |temp[i-1] - temp[i]| > 3:
    major_transitions += 1
```

**Exemple :**
- `Rain` 20°C → `Snow` 18°C : Transition majeure (météo change + 2°C... non, pas > 3°C)
- `Rain` 20°C → `Snow` 16°C : Transition majeure (météo change + 4°C > 3°C)
- `Rain` 20°C → `Rain` 18°C : Pas de transition (météo identique)

---

### 7. Sauvegarde des fichiers (1 minute)

**Fonction : `save_to_file(data, filename, city, country)`**

**Processus :**
1. Créer dossier "JSON Output" si nécessaire
2. Générer nom fichier si non fourni :
   - Format : `{city}_{country}_{timestamp}.json`
   - Exemple : `Paris_FR_20251126_221305.json`
3. Vérifier extension `.json`
4. Écrire fichier avec `json.dump()`
5. Retourner chemin complet ou `None` (erreur)

---

### 8. Mode interactif (2 minutes)

**Menu principal : `main_menu()`**

**Boucle infinie avec 3 options :**

1. **Option 1 : Weather Report**
   - Appelle `weather_report()`
   - Demande city et country (input)
   - Demande affichage (o/n)
   - Appelle `execute_weather_report()`

2. **Option 2 : ASCII Art**
   - Appelle `display_ascii_art()`
   - Affiche art Weather Report (JoJo)

3. **Option 3 : Exit**
   - Log sortie
   - `break` (sortie boucle)

**Gestion erreurs :** Option invalide → Message + retour menu

---

### 9. Gestion des erreurs (2 minutes)

**Points d'erreur principaux :**

| Erreur | Fonction | Action |
|--------|----------|--------|
| Fichier config introuvable | `load_api_key()` | Log + print + return None |
| Clé API vide/invalide | `verify_api_key()` | Log + print + return False |
| Erreur réseau | `execute_weather_report()` | Log + print/click.echo + return False |
| Status API != 200 | `execute_weather_report()` | Log + print/click.echo + return False |
| Erreur sauvegarde | `save_to_file()` | Log + return None |
| Erreur création dossier | `setup_logging()` / `save_to_file()` | Log + return/return None |

**Stratégie :**
- Toutes les erreurs sont loggées
- Affichage adapté selon mode (print vs click.echo)
- Retour booléen/None pour propagation

---

### 10. Logging (1 minute)

**Configuration loguru :**
- **Fichier unique** : `Logs/weather_report_YYYYMMDD.log`
- **Rotation** : 1 jour (nouveau fichier quotidien)
- **Rétention** : 30 jours (suppression automatique)
- **Niveau** : INFO
- **Format** : `{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}`
- **Encodage** : UTF-8

**Types de logs :**
- `logger.info()` : Actions normales
- `logger.success()` : Succès (clé API, sauvegarde)
- `logger.warning()` : Avertissements
- `logger.error()` : Erreurs

---

## 📊 Structure des données

### Entrée (API OpenWeatherMap)
```json
{
  "city": { "name": "...", "country": "..." },
  "list": [
    {
      "dt_txt": "2025-11-26 12:00:00",
      "main": { "temp": 20.5, "humidity": 65 },
      "weather": [{ "main": "Rain" }],
      "rain": { "3h": 2.5 },
      "snow": { "3h": 0.0 }
    },
    ...
  ]
}
```

### Sortie (Formaté)
```json
{
  "forecast_location_name": "Paris",
  "country_code": "FR",
  "total_rain_period_mm": 15.5,
  "total_snow_period_mm": 0.0,
  "max_humidity_period": 85,
  "forecast_details": [
    {
      "date_local": "2025-11-26",
      "rain_cumul_mm": 5.2,
      "snow_cumul_mm": 0.0,
      "major_transitions_count": 2
    },
    ...
  ]
}
```

---

## 🎤 Script de présentation (15 minutes)

### Introduction (1 min)
- Présentation du projet : Récupération et formatage de données météo
- Deux modes : CLI et Interactif

### Architecture (2 min)
- Point d'entrée : `cli()`
- Décision mode : Arguments fournis ?
- Initialisation : Logging automatique

### Gestion API (2 min)
- Chargement clé : `load_api_key()`
- Vérification : `verify_api_key()`
- Gestion erreurs

### Exécution (3 min)
- Flux principal : `execute_weather_report()`
- Requête API
- Formatage : `format_forecast()`
- Sauvegarde : `save_to_file()`

### Calculs météo (2 min)
- Transitions majeures : Définition et algorithme
- Exemples concrets

### Mode interactif (2 min)
- Menu : 3 options
- Flux utilisateur

### Gestion erreurs (2 min)
- Points d'erreur
- Stratégie de logging

### Conclusion (1 min)
- Points forts : Robustesse, logging, deux modes
- Questions

---

## ❓ Questions possibles et réponses

**Q : Pourquoi deux modes ?**
R : Flexibilité - CLI pour automatisation/scripts, Interactif pour utilisation manuelle.

**Q : Pourquoi vérifier la clé API avec Toulouse ?**
R : Test rapide avant utilisation réelle, évite erreurs tardives.

**Q : Comment sont gérées les données manquantes (rain/snow) ?**
R : Vérification présence clés, valeur par défaut `0.0` si absentes.

**Q : Pourquoi calculer les transitions majeures ?**
R : Indicateur de variabilité météo importante (changement météo + variation temp significative).

**Q : Pourquoi rotation quotidienne des logs ?**
R : Évite fichiers trop volumineux, facilite recherche par date.

**Q : Que se passe-t-il si le dossier JSON Output existe déjà ?**
R : Rien, utilisation directe. Création uniquement si absent.

---

## 📝 Checklist avant présentation

- [ ] Lire `LOGICAL_TREE.md` pour comprendre tous les flux
- [ ] Lire `FLOWCHART_SIMPLIFIED.md` pour vue d'ensemble
- [ ] Tester le programme (mode CLI et interactif)
- [ ] Préparer exemples de données (entrée/sortie)
- [ ] Préparer démonstration live (optionnel)
- [ ] Anticiper questions techniques

---

**Bonne présentation ! 🎯**

