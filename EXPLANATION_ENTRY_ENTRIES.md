# Explication : `entry` vs `entries` dans format_forecast()

## 📌 Concepts clés

### `entry` (singulier) = Une prévision de 3 heures
- **Type** : Dictionnaire Python
- **Source** : Un élément de `forecast_list` (données brutes de l'API)
- **Fréquence** : Une prévision toutes les 3 heures (8 par jour)
- **Contenu** : Données météo pour un moment précis (ex: 2025-11-26 12:00:00)

### `entries` (pluriel) = Collection d'entrées pour UN jour
- **Type** : Liste de dictionnaires Python
- **Source** : Regroupement de plusieurs `entry` par jour
- **Fréquence** : Une liste par jour
- **Contenu** : Toutes les prévisions 3h d'une même journée

---

## 🔄 Flux de données

```
API OpenWeatherMap
    │
    ▼
forecast_list = [
    entry₁ (2025-11-26 00:00:00),  ← entry (singulier)
    entry₂ (2025-11-26 03:00:00),  ← entry (singulier)
    entry₃ (2025-11-26 06:00:00),  ← entry (singulier)
    entry₄ (2025-11-26 09:00:00),  ← entry (singulier)
    entry₅ (2025-11-26 12:00:00),  ← entry (singulier)
    entry₆ (2025-11-26 15:00:00),  ← entry (singulier)
    entry₇ (2025-11-26 18:00:00),  ← entry (singulier)
    entry₈ (2025-11-26 21:00:00),  ← entry (singulier)
    entry₉ (2025-11-27 00:00:00),  ← entry (singulier)
    ...
]
    │
    ▼
Regroupement par jour
    │
    ▼
days = {
    "2025-11-26": {
        "rain_cumul_mm": 5.2,
        "snow_cumul_mm": 0.0,
        "entries": [                    ← entries (pluriel)
            { "temp": 15, "weather": "Rain" },    ← entry₁ simplifié
            { "temp": 16, "weather": "Rain" },    ← entry₂ simplifié
            { "temp": 18, "weather": "Clouds" },  ← entry₃ simplifié
            { "temp": 20, "weather": "Clear" },    ← entry₄ simplifié
            { "temp": 22, "weather": "Clear" },    ← entry₅ simplifié
            { "temp": 21, "weather": "Clear" },    ← entry₆ simplifié
            { "temp": 19, "weather": "Clouds" },   ← entry₇ simplifié
            { "temp": 17, "weather": "Rain" }      ← entry₈ simplifié
        ]
    },
    "2025-11-27": {
        "rain_cumul_mm": 2.1,
        "snow_cumul_mm": 0.0,
        "entries": [                    ← entries (pluriel)
            { "temp": 16, "weather": "Rain" },    ← entry₉ simplifié
            ...
        ]
    }
}
```

---

## 📝 Explication détaillée du code

### **PARTIE 1 : Boucle sur chaque `entry` (lignes 183-232)**

```python
for entry in forecast_list:  # entry = une prévision de 3h
```

#### Étape 1 : Extraction de la date (lignes 185-187)
```python
dt_txt = entry["dt_txt"]  # Ex: "2025-11-26 12:00:00"
timestamp = datetime.strptime(dt_txt, DATETIME_FORMAT)
date_str = timestamp.strftime(DATE_FORMAT)  # Ex: "2025-11-26"
```
**Objectif** : Extraire la date (sans l'heure) pour regrouper par jour

#### Étape 2 : Extraction des précipitations (lignes 189-203)
```python
if "rain" in entry:
    if "3h" in entry["rain"]:
        rain = entry["rain"]["3h"]  # Ex: 2.5 mm
    else:
        rain = 0.0
else:
    rain = 0.0
```
**Objectif** : Récupérer la pluie des 3 dernières heures (peut être absente)

**Même logique pour `snow`** (lignes 197-203)

#### Étape 3 : Extraction autres données (lignes 205-208)
```python
temp = entry["main"]["temp"]              # Ex: 20.5°C
humidity = entry["main"]["humidity"]       # Ex: 65%
weather_main = entry["weather"][0]["main"] # Ex: "Rain"
```
**Objectif** : Récupérer température, humidité, et type météo principal

#### Étape 4 : Mise à jour des totaux PÉRIODE (lignes 210-215)
```python
result["total_rain_period_mm"] += rain  # Cumul sur TOUTE la période
result["total_snow_period_mm"] += snow
if humidity > result["max_humidity_period"]:
    result["max_humidity_period"] = humidity  # Maximum sur TOUTE la période
```
**Objectif** : Calculer les totaux pour les 5 jours complets

#### Étape 5 : Création/Initialisation du jour (lignes 218-222)
```python
if date_str not in days:  # Si ce jour n'existe pas encore
    days[date_str] = {}
    days[date_str]["rain_cumul_mm"] = 0.0
    days[date_str]["snow_cumul_mm"] = 0.0
    days[date_str]["entries"] = []  # ← Liste vide pour ce jour
```
**Objectif** : Créer une structure pour ce jour (si première fois qu'on le rencontre)

#### Étape 6 : Mise à jour des cumuls JOURNALIERS (lignes 225-226)
```python
days[date_str]["rain_cumul_mm"] += rain  # Cumul pour CE jour uniquement
days[date_str]["snow_cumul_mm"] += snow
```
**Objectif** : Additionner les précipitations pour ce jour spécifique

#### Étape 7 : Stockage dans `entries` (lignes 229-232)
```python
days[date_str]["entries"].append({
    "temp": temp,
    "weather": weather_main  
})
```
**Objectif** : Stocker une version simplifiée de `entry` dans la liste `entries` du jour

**Pourquoi simplifier ?**
- On ne garde que `temp` et `weather` (nécessaires pour calculer transitions)
- On ne garde pas toutes les données (rain, snow, humidity déjà cumulées)

---

### **PARTIE 2 : Boucle sur chaque jour (lignes 235-249)**

```python
for date in days:  # date = "2025-11-26", "2025-11-27", etc.
```

#### Étape 1 : Récupération des `entries` du jour (ligne 237)
```python
entries = days[date]["entries"]  # Liste de toutes les entrées 3h de ce jour
```

**Exemple concret :**
```python
# Si date = "2025-11-26"
entries = [
    { "temp": 15, "weather": "Rain" },    # 00:00
    { "temp": 16, "weather": "Rain" },    # 03:00
    { "temp": 18, "weather": "Clouds" },  # 06:00
    { "temp": 20, "weather": "Clear" },   # 09:00
    { "temp": 22, "weather": "Clear" },   # 12:00
    { "temp": 21, "weather": "Clear" },   # 15:00
    { "temp": 19, "weather": "Clouds" },  # 18:00
    { "temp": 17, "weather": "Rain" }      # 21:00
]
```

#### Étape 2 : Calcul des transitions majeures (ligne 238)
```python
major_transitions = calcul_major_transitions(entries)
```

**Ce que fait cette fonction :**
- Compare chaque paire d'entrées consécutives
- Détecte si `weather` change ET si `temp` varie de plus de 3°C
- Compte le nombre de transitions majeures

**Exemple avec les données ci-dessus :**
```
Rain 15°C → Rain 16°C : Pas de transition (même météo)
Rain 16°C → Clouds 18°C : Transition majeure (météo change + 2°C... non, pas > 3°C)
Clouds 18°C → Clear 20°C : Transition majeure (météo change + 2°C... non, pas > 3°C)
Clear 20°C → Clear 22°C : Pas de transition (même météo)
Clear 22°C → Clear 21°C : Pas de transition (même météo)
Clear 21°C → Clouds 19°C : Pas de transition (temp change seulement 2°C)
Clouds 19°C → Rain 17°C : Pas de transition (temp change seulement 2°C)

Résultat : 0 transitions majeures (aucune ne satisfait les deux conditions)
```

#### Étape 3 : Création du résultat journalier (lignes 241-246)
```python
day_result = {
    "date_local": date,                                    # "2025-11-26"
    "rain_cumul_mm": round(days[date]["rain_cumul_mm"], 2),  # 5.2
    "snow_cumul_mm": round(days[date]["snow_cumul_mm"], 2),  # 0.0
    "major_transitions_count": major_transitions            # 0
}
```

**Objectif** : Créer la structure finale pour ce jour

#### Étape 4 : Ajout au résultat final (ligne 248)
```python
result["forecast_details"].append(day_result)
```

**Objectif** : Ajouter ce jour à la liste des détails de prévision

---

## 🎯 Résumé visuel

### Structure de données

```
entry (singulier)
├─► Type : dict
├─► Source : API (une prévision 3h)
├─► Contenu complet :
│   ├─► dt_txt: "2025-11-26 12:00:00"
│   ├─► main: { temp: 20.5, humidity: 65 }
│   ├─► weather: [{ main: "Rain" }]
│   ├─► rain: { 3h: 2.5 }
│   └─► snow: { 3h: 0.0 }
│
└─► Traitement :
    ├─► Extraction données
    ├─► Cumul totaux période
    ├─► Cumul totaux jour
    └─► Stockage simplifié dans entries

entries (pluriel)
├─► Type : list
├─► Source : Regroupement d'entrées par jour
├─► Contenu simplifié :
│   [
│     { "temp": 15, "weather": "Rain" },
│     { "temp": 16, "weather": "Rain" },
│     { "temp": 18, "weather": "Clouds" },
│     ...
│   ]
│
└─► Utilisation :
    └─► Calcul transitions majeures
```

---

## 💡 Pourquoi cette approche ?

### 1. **Regroupement par jour**
- L'API donne des données toutes les 3h
- On veut des résultats par jour
- Solution : Regrouper les `entry` par date

### 2. **Simplification pour transitions**
- Pour calculer transitions, on a besoin de `temp` et `weather` seulement
- Pas besoin de toutes les données de chaque `entry`
- Solution : Stocker version simplifiée dans `entries`

### 3. **Double cumul**
- **Totaux période** : Pour les 5 jours complets
- **Cumuls journaliers** : Pour chaque jour individuel
- Solution : Deux compteurs séparés

---

## 🔍 Exemple concret complet

### Données API (3 entrées pour simplifier)

```json
{
  "list": [
    {
      "dt_txt": "2025-11-26 00:00:00",
      "main": { "temp": 15, "humidity": 70 },
      "weather": [{ "main": "Rain" }],
      "rain": { "3h": 2.0 }
    },
    {
      "dt_txt": "2025-11-26 03:00:00",
      "main": { "temp": 16, "humidity": 75 },
      "weather": [{ "main": "Rain" }],
      "rain": { "3h": 1.5 }
    },
    {
      "dt_txt": "2025-11-26 06:00:00",
      "main": { "temp": 20, "humidity": 60 },
      "weather": [{ "main": "Clear" }],
      "rain": { "3h": 0.0 }
    }
  ]
}
```

### Traitement

#### Itération 1 : `entry` = première prévision (00:00)
```python
date_str = "2025-11-26"
rain = 2.0
temp = 15
weather_main = "Rain"

# Création du jour
days["2025-11-26"] = {
    "rain_cumul_mm": 0.0,
    "snow_cumul_mm": 0.0,
    "entries": []
}

# Mise à jour
days["2025-11-26"]["rain_cumul_mm"] = 2.0
days["2025-11-26"]["entries"] = [
    { "temp": 15, "weather": "Rain" }
]
```

#### Itération 2 : `entry` = deuxième prévision (03:00)
```python
date_str = "2025-11-26"  # Même jour
rain = 1.5
temp = 16
weather_main = "Rain"

# Mise à jour (jour existe déjà)
days["2025-11-26"]["rain_cumul_mm"] = 2.0 + 1.5 = 3.5
days["2025-11-26"]["entries"] = [
    { "temp": 15, "weather": "Rain" },
    { "temp": 16, "weather": "Rain" }  # ← Nouvelle entrée
]
```

#### Itération 3 : `entry` = troisième prévision (06:00)
```python
date_str = "2025-11-26"  # Même jour
rain = 0.0
temp = 20
weather_main = "Clear"

# Mise à jour
days["2025-11-26"]["rain_cumul_mm"] = 3.5 + 0.0 = 3.5
days["2025-11-26"]["entries"] = [
    { "temp": 15, "weather": "Rain" },
    { "temp": 16, "weather": "Rain" },
    { "temp": 20, "weather": "Clear" }  # ← Nouvelle entrée
]
```

#### Boucle finale : Traitement du jour
```python
date = "2025-11-26"
entries = [
    { "temp": 15, "weather": "Rain" },
    { "temp": 16, "weather": "Rain" },
    { "temp": 20, "weather": "Clear" }
]

# Calcul transitions
# Rain 15°C → Rain 16°C : Pas de transition
# Rain 16°C → Clear 20°C : Transition majeure ? 
#   - Météo change : OUI (Rain → Clear)
#   - Temp change > 3°C : OUI (4°C)
#   → TRANSITION MAJEURE !

major_transitions = 1

# Résultat final
day_result = {
    "date_local": "2025-11-26",
    "rain_cumul_mm": 3.5,
    "snow_cumul_mm": 0.0,
    "major_transitions_count": 1
}
```

---

## ✅ Points clés à retenir

1. **`entry`** = Une prévision de 3h (données brutes API)
2. **`entries`** = Liste de prévisions simplifiées pour un jour
3. **Regroupement** : Les `entry` sont regroupés par jour dans `days`
4. **Simplification** : Seules `temp` et `weather` sont gardées dans `entries`
5. **Double cumul** : Totaux période ET cumuls journaliers
6. **Transitions** : Calculées à partir de `entries` (comparaison consécutive)

---

**Fin de l'explication**

