# Flowchart Simplifié - Weather Report

## Vue d'ensemble simplifiée

```
                    ┌─────────────────────┐
                    │  DÉMARRAGE SCRIPT   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  setup_logging()    │
                    │  (Automatique)     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      cli()           │
                    │  Point d'entrée      │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
          ┌─────────────────┐   ┌─────────────────┐
          │   MODE CLI      │   │ MODE INTERACTIF │
          │ city & country  │   │  Menu principal │
          │   fournis ?     │   │                 │
          └────────┬────────┘   └────────┬────────┘
                   │                     │
                   │                     │
                   ▼                     ▼
          ┌─────────────────┐   ┌─────────────────┐
          │ Vérifier API    │   │ Vérifier API    │
          │   Clé           │   │   Clé           │
          └────────┬────────┘   └────────┬────────┘
                   │                     │
                   │                     │
                   ▼                     ▼
          ┌─────────────────┐   ┌─────────────────┐
          │ execute_weather │   │   main_menu()   │
          │    _report()     │   │  (Boucle menu)  │
          └────────┬────────┘   └────────┬────────┘
                   │                     │
                   │                     │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  Requête API        │
                   │  OpenWeatherMap     │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  format_forecast()  │
                   │  (Traitement données)│
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  save_to_file()     │
                   │  (Sauvegarde JSON)  │
                   └─────────────────────┘
```

---

## Détail du flux principal : execute_weather_report()

```
┌─────────────────────────────────────┐
│  execute_weather_report()           │
└──────────────┬──────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Clé API fournie ?   │
    └──────┬───────────┬───┘
           │           │
          NON         OUI
           │           │
           ▼           │
    ┌──────────────┐   │
    │ load_api_key()│   │
    └──────┬───────┘   │
           │           │
           └───────┬───┘
                   │
                   ▼
    ┌──────────────────────┐
    │  Clé API valide ?    │
    └──────┬───────────┬───┘
           │           │
          NON         OUI
           │           │
           ▼           │
    ┌──────────────┐   │
    │   ERREUR     │   │
    │   return False│   │
    └──────────────┘   │
                       │
                       ▼
    ┌──────────────────────┐
    │  Requête API         │
    │  requests.get(url)   │
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │  Status == 200 ?     │
    └──────┬───────────┬───┘
           │           │
          NON         OUI
           │           │
           ▼           │
    ┌──────────────┐   │
    │   ERREUR     │   │
    │   return False│   │
    └──────────────┘   │
                       │
                       ▼
    ┌──────────────────────┐
    │  format_forecast()    │
    │  (Traitement)         │
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │  display == True ?    │
    └──────┬───────────┬───┘
           │           │
          OUI         NON
           │           │
           ▼           │
    ┌──────────────┐   │
    │  Afficher    │   │
    │  JSON        │   │
    └──────────────┘   │
                       │
                       ▼
    ┌──────────────────────┐
    │  save_to_file()       │
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │  Fichier sauvegardé ? │
    └──────┬───────────┬───┘
           │           │
          NON         OUI
           │           │
           ▼           ▼
    ┌──────────────┐ ┌──────────────┐
    │   ERREUR     │ │   SUCCÈS     │
    │   Log error  │ │   Log success│
    └──────────────┘ └──────────────┘
```

---

## Détail du formatage : format_forecast()

```
┌─────────────────────────────────────┐
│  format_forecast(data)              │
└──────────────┬──────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Initialiser result  │
    │  et days = {}         │
    └──────────┬────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  BOUCLE: Pour chaque │
    │  entry (3h)          │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Extraire:           │
    │  - date              │
    │  - rain              │
    │  - snow              │
    │  - temp              │
    │  - humidity          │
    │  - weather_main      │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Mettre à jour:      │
    │  - totaux période    │
    │  - cumuls journaliers│
    │  - entries par jour  │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  BOUCLE: Pour chaque │
    │  jour                │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  calcul_major_        │
    │  transitions()        │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Créer day_result     │
    │  et ajouter à        │
    │  forecast_details    │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  return result        │
    └──────────────────────┘
```

---

## Calcul des transitions majeures

```
┌─────────────────────────────────────┐
│  calcul_major_transitions(entries)  │
└──────────────┬──────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  major_transitions=0 │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  BOUCLE: i de 1 à    │
    │  len(entries)-1       │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Comparer entry[i-1] │
    │  avec entry[i]       │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  weather changé ?     │
    │  ET temp_diff > 3°C ?│
    └──────┬───────────┬───┘
           │           │
          OUI         NON
           │           │
           ▼           │
    ┌──────────────┐   │
    │  major_      │   │
    │  transitions │   │
    │  += 1        │   │
    └──────────────┘   │
                       │
                       ▼
    ┌──────────────────────┐
    │  return major_       │
    │  transitions         │
    └──────────────────────┘
```

---

## Menu interactif

```
┌─────────────────────────────────────┐
│  main_menu()                         │
│  (Boucle infinie)                    │
└──────────────┬──────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Afficher menu       │
    │  1. Weather Report   │
    │  2. Ascii           │
    │  3. Exit            │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  choice = input()     │
    └──────────┬───────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌─────────┐         ┌─────────┐
│ choice  │         │ choice  │
│ == "1"  │         │ == "2"  │
└────┬────┘         └────┬────┘
     │                   │
     ▼                   ▼
┌─────────┐         ┌─────────┐
│ weather │         │ display │
│_report()│         │_ascii_  │
│         │         │art()    │
└─────────┘         └─────────┘
     │
     │
     ▼
┌─────────┐
│ choice  │
│ == "3"  │
└────┬────┘
     │
     ▼
┌─────────┐
│  break  │
│ (Exit)  │
└─────────┘
```

---

## Points de décision clés

### 1. Mode d'exécution
```
city ET country fournis ?
├─► OUI → Mode CLI
└─► NON → Mode Interactif
```

### 2. Clé API
```
api_key fourni ?
├─► OUI → Utiliser
└─► NON → Charger depuis local.conf
    └─► Trouvée ?
        ├─► OUI → Vérifier
        └─► NON → ERREUR
```

### 3. Réponse API
```
status_code == 200 ?
├─► OUI → Continuer
└─► NON → ERREUR
```

### 4. Affichage
```
display == True ?
├─► OUI → Afficher JSON
└─► NON → Passer
```

### 5. Transition majeure
```
weather changé ET temp_diff > 3°C ?
├─► OUI → Transition majeure
└─► NON → Pas de transition
```

---

## Résumé des fonctions principales

| Fonction | Rôle | Retour |
|----------|------|--------|
| `setup_logging()` | Configure les logs | None |
| `load_api_key()` | Charge la clé API | str ou None |
| `verify_api_key()` | Vérifie la clé API | bool |
| `execute_weather_report()` | Exécute le rapport | bool |
| `format_forecast()` | Formate les données | dict |
| `calcul_major_transitions()` | Calcule transitions | int |
| `save_to_file()` | Sauvegarde JSON | str ou None |
| `main_menu()` | Menu interactif | None |
| `weather_report()` | Mode interactif | None |
| `display_ascii_art()` | Affiche ASCII | None |

---

## Flux de données simplifié

```
API OpenWeatherMap
    │
    ▼
JSON brut
    │
    ▼
format_forecast()
    │
    ├─► Extraction
    ├─► Regroupement
    ├─► Calculs
    │
    ▼
JSON formaté
    │
    ├─► Affichage (optionnel)
    │
    ▼
save_to_file()
    │
    ▼
Fichier JSON
```

---

**Document simplifié pour présentation rapide**

