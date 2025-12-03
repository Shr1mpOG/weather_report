# Arbre Logique - Weather Report

## Vue d'ensemble du programme

Ce programme récupère des données météorologiques via l'API OpenWeatherMap, les formate, et les sauvegarde dans des fichiers JSON. Il supporte deux modes d'exécution : **CLI** (ligne de commande) et **Interactif** (menu).

---

## 1. INITIALISATION (Au démarrage du script)

```
┌─────────────────────────────────┐
│ Script démarré                  │
│ (if __name__ == "__main__")     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ setup_logging()                 │
│ (Exécuté automatiquement)       │
└────────────┬────────────────────┘
             │
             ├─► Dossier "Logs" existe ?
             │   ├─► NON → Créer le dossier
             │   └─► OUI → Continuer
             │
             ▼
┌─────────────────────────────────┐
│ Configuration loguru            │
│ - Rotation quotidienne          │
│ - Rétention 30 jours            │
│ - Format: timestamp | level | msg│
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ cli() appelée                   │
│ (Point d'entrée principal)      │
└─────────────────────────────────┘
```

---

## 2. POINT D'ENTRÉE PRINCIPAL : cli()

```
┌─────────────────────────────────┐
│ cli() - Fonction principale     │
│ Arguments: city, country,        │
│           api_key, no_display    │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ city ET       │
     │ country       │
     │ fournis ?     │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌─────────────────────────────┐
         │  │ MODE INTERACTIF             │
         │  └─────────────────────────────┘
         │       │
         │       ▼
         │  ┌─────────────────────────────┐
         │  │ Vérification clé API         │
         │  │ - api_key fourni ?          │
         │  │   OUI → Utiliser            │
         │  │   NON → load_api_key()      │
         │  └───────────────┬───────────────┘
         │                │
         │                ▼
         │          ┌───────────────┐
         │          │ Clé API       │
         │          │ trouvée ?     │
         │          └───┬───────┬───┘
         │              │       │
         │             OUI     NON
         │              │       │
         │              │       ▼
         │              │   ┌──────────────────┐
         │              │   │ ERREUR            │
         │              │   │ Sortie programme │
         │              │   └──────────────────┘
         │              │
         │              ▼
         │          ┌──────────────────┐
         │          │ verify_api_key()  │
         │          └────────┬──────────┘
         │                  │
         │                  ▼
         │          ┌───────────────┐
         │          │ Clé valide ?  │
         │          └───┬───────┬───┘
         │              │       │
         │             OUI     NON
         │              │       │
         │              │       ▼
         │              │   ┌──────────────────┐
         │              │   │ ERREUR            │
         │              │   │ Sortie programme │
         │              │   └──────────────────┘
         │              │
         │              ▼
         │          ┌──────────────────┐
         │          │ main_menu()       │
         │          │ (Boucle infinie)  │
         │          └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ MODE CLI                        │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Vérification clé API             │
└────────────┬────────────────────┘
             │
             ├─► api_key fourni ?
             │   ├─► OUI → verify_api_key(api_key, quiet=True)
             │   │         ├─► Valide ? → Continuer
             │   │         └─► Invalide ? → ERREUR + Sortie
             │   │
             │   └─► NON → load_api_key()
             │             ├─► Trouvée ? → verify_api_key(loaded_key, quiet=True)
             │             │              ├─► Valide ? → Continuer
             │             │              └─► Invalide ? → ERREUR + Sortie
             │             └─► Non trouvée ? → ERREUR + Sortie
             │
             ▼
┌─────────────────────────────────┐
│ execute_weather_report()        │
│ (city, country, api_key,        │
│  display=not no_display,        │
│  quiet=True)                    │
└─────────────────────────────────┘
```

---

## 3. FONCTION : load_api_key()

```
┌─────────────────────────────────┐
│ load_api_key(config_file)       │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Construire chemin complet       │
│ BASE_DIR + config_file           │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Fichier       │
     │ existe ?      │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ logger.error()   │
         │  │ print()          │
         │  │ return None      │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Ouvrir et lire le fichier       │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Exception     │
     │ levée ?       │
     └───┬───────┬───┘
         │       │
        NON     OUI
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ logger.error()   │
         │  │ print()          │
         │  │ return None      │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Parcourir chaque ligne          │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Ligne commence│
     │ par "API_KEY="│
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ Continuer       │
         │  │ (ligne suivante)│
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Extraire la clé                 │
│ key = line.split("=", 1)[1]     │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ key non vide ?│
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ logger.info()    │
         │  │ return key       │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ return None                      │
│ (Aucune clé trouvée)            │
└─────────────────────────────────┘
```

---

## 4. FONCTION : verify_api_key()

```
┌─────────────────────────────────┐
│ verify_api_key(api_key, quiet) │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ api_key       │
     │ non vide ?    │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ logger.warning()│
         │  │ return False    │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Construire URL de test          │
│ (Toulouse, FR)                  │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ requests.get(test_url,          │
│              timeout=10)        │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Exception     │
     │ levée ?       │
     └───┬───────┬───┘
         │       │
        NON     OUI
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ logger.error()  │
         │  │ if not quiet:   │
         │  │   print()       │
         │  │ return False    │
         │  └──────────────────┘
         │
         ▼
     ┌───────────────┐
     │ status_code   │
     │ == 200 ?      │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ logger.error()   │
         │  │ if not quiet:    │
         │  │   print()        │
         │  │   - 500-599 ?    │
         │  │     → Erreur serveur│
         │  │   - 401 ?        │
         │  │     → Clé invalide│
         │  │   - Autre ?      │
         │  │     → Erreur API │
         │  │ return False     │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ logger.success()                │
│ return True                      │
└─────────────────────────────────┘
```

---

## 5. FONCTION : execute_weather_report()

```
┌─────────────────────────────────┐
│ execute_weather_report(         │
│   city, country, api_key,       │
│   display, quiet)               │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ api_key       │
     │ == None ?     │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ Continuer       │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ load_api_key()                  │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ api_key       │
     │ trouvée ?     │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ logger.error()  │
         │  │ if not quiet:    │
         │  │   print()        │
         │  │ else:            │
         │  │   click.echo()   │
         │  │ return False     │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Construire URL API              │
│ (city, country, api_key)        │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ logger.info()                   │
│ if not quiet: print()           │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ requests.get(url)               │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Exception     │
     │ levée ?       │
     └───┬───────┬───┘
         │       │
        NON     OUI
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ logger.error()   │
         │  │ if not quiet:    │
         │  │   print()        │
         │  │ else:            │
         │  │   click.echo()   │
         │  │ return False     │
         │  └──────────────────┘
         │
         ▼
     ┌───────────────┐
     │ status_code   │
     │ == 200 ?      │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ logger.error()   │
         │  │ if not quiet:    │
         │  │   print()        │
         │  │ else:            │
         │  │   click.echo()   │
         │  │ return False     │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ data = response.json()          │
│ (JSON brut de l'API)            │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ formatted = format_forecast(data)│
│ (Formatage des données)         │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ display ==    │
     │ True ?        │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ Passer           │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ print(json.dumps(formatted))    │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ saved_file = save_to_file(      │
│   formatted, city, country)     │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ saved_file     │
     │ != None ?      │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ logger.error()   │
         │  │ if not quiet:    │
         │  │   print()        │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ logger.success()               │
│ if not quiet: print()           │
│ return True                     │
└─────────────────────────────────┘
```

---

## 6. FONCTION : format_forecast()

```
┌─────────────────────────────────┐
│ format_forecast(data)           │
│ (Transforme JSON brut → formaté)│
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Extraire city_info et           │
│ forecast_list                   │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Initialiser result              │
│ - forecast_location_name        │
│ - country_code                  │
│ - total_rain_period_mm = 0.0    │
│ - total_snow_period_mm = 0.0    │
│ - max_humidity_period = 0        │
│ - forecast_details = []         │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Initialiser days = {}           │
│ (Dictionnaire pour regrouper    │
│  par jour)                      │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ BOUCLE: Pour chaque entry       │
│ dans forecast_list              │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Extraire dt_txt et convertir    │
│ en date (YYYY-MM-DD)            │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Extraire rain                   │
│ - "rain" in entry ?             │
│   - OUI → "3h" in entry["rain"]?│
│     - OUI → rain = entry["rain"]["3h"]│
│     - NON → rain = 0.0          │
│   - NON → rain = 0.0            │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Extraire snow                   │
│ (Même logique que rain)          │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Extraire temp, humidity,        │
│ weather_main                    │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Mettre à jour totaux            │
│ - total_rain_period_mm += rain  │
│ - total_snow_period_mm += snow  │
│ - max_humidity_period = max()   │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ date_str      │
     │ in days ?     │
     └───┬───────┬───┘
         │       │
        NON     OUI
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ Continuer        │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Créer entrée pour ce jour       │
│ days[date_str] = {              │
│   "rain_cumul_mm": 0.0,         │
│   "snow_cumul_mm": 0.0,         │
│   "entries": []                 │
│ }                               │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Mettre à jour cumuls journaliers│
│ - days[date_str]["rain_cumul_mm"] += rain│
│ - days[date_str]["snow_cumul_mm"] += snow│
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Ajouter entrée météo            │
│ days[date_str]["entries"].append({│
│   "temp": temp,                 │
│   "weather": weather_main        │
│ })                              │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Plus d'       │
     │ entrées ?     │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ Continuer boucle │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ BOUCLE: Pour chaque date        │
│ dans days                       │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ calcul_major_transitions(       │
│   days[date]["entries"])        │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Créer day_result                │
│ - date_local                    │
│ - rain_cumul_mm (arrondi)       │
│ - snow_cumul_mm (arrondi)       │
│ - major_transitions_count       │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ result["forecast_details"].     │
│ append(day_result)              │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Plus de       │
     │ dates ?       │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ Continuer boucle │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ return result                   │
└─────────────────────────────────┘
```

---

## 7. FONCTION : calcul_major_transitions()

```
┌─────────────────────────────────┐
│ calcul_major_transitions(       │
│   entries)                      │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ major_transitions = 0            │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ BOUCLE: i de 1 à len(entries)-1 │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ prev = entries[i-1]             │
│ curr = entries[i]               │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ weather_main_changed =           │
│   (prev["weather"] !=           │
│    curr["weather"])              │
│ temp_change =                    │
│   abs(prev["temp"] -            │
│       curr["temp"])              │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ weather_main_ │
     │ changed ET    │
     │ temp_change   │
     │ > 3°C ?      │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ Continuer        │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ major_transitions += 1          │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Plus d'       │
     │ entrées ?     │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ Continuer boucle  │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ return major_transitions        │
└─────────────────────────────────┘
```

---

## 8. FONCTION : save_to_file()

```
┌─────────────────────────────────┐
│ save_to_file(data, filename,    │
│              city, country)     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Construire output_dir           │
│ BASE_DIR + JSON_OUTPUT_DIR_NAME  │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ output_dir    │
     │ existe ?      │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ try:             │
         │  │   os.makedirs() │
         │  │   logger.info() │
         │  │ except:         │
         │  │   logger.error()│
         │  │   return None   │
         │  └──────────────────┘
         │
         ▼
     ┌───────────────┐
     │ filename      │
     │ == None ?     │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ Utiliser        │
         │  │ filename fourni │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Générer filename automatique    │
│ city_name_country_timestamp.json│
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ filename      │
     │ finit par     │
     │ ".json" ?     │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ filename +=       │
         │  │ ".json"           │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Construire complete_path        │
│ output_dir + filename            │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ try:                            │
│   Ouvrir fichier en écriture    │
│   json.dump(data, f, ...)       │
│   logger.success()              │
│   return complete_path          │
│ except:                         │
│   logger.error()                │
│   return None                   │
└─────────────────────────────────┘
```

---

## 9. MODE INTERACTIF : main_menu()

```
┌─────────────────────────────────┐
│ main_menu()                     │
│ (Boucle infinie)                │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Afficher menu                    │
│ 1. Weather Report                │
│ 2. Ascii                         │
│ 3. Exit                          │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ choice = input()                 │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ choice == ?   │
     └───┬───┬───┬───┘
         │   │   │
        "1" "2" "3" Autre
         │   │   │   │
         │   │   │   ▼
         │   │   │ ┌──────────────────┐
         │   │   │ │ print("Erreur")   │
         │   │   │ │ Continuer boucle  │
         │   │   │ └──────────────────┘
         │   │   │
         │   │   ▼
         │   │ ┌──────────────────┐
         │   │ │ logger.info()     │
         │   │ │ print()           │
         │   │ │ break (sortie)    │
         │   │ └──────────────────┘
         │   │
         │   ▼
         │ ┌──────────────────┐
         │ │ display_ascii_art()│
         │ │ Continuer boucle  │
         │ └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ weather_report()                 │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ load_api_key()                  │
└────────────┬────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ api_key       │
     │ trouvée ?     │
     └───┬───────┬───┘
         │       │
        OUI     NON
         │       │
         │       ▼
         │  ┌──────────────────┐
         │  │ print("Erreur")  │
         │  │ return           │
         │  └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Demander city et country         │
│ (input())                        │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Demander display                │
│ (o/n)                           │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ execute_weather_report(          │
│   city, country, api_key,        │
│   display)                       │
└─────────────────────────────────┘
```

---

## 10. RÉSUMÉ DES DÉCISIONS PRINCIPALES

### Points de décision critiques :

1. **Mode d'exécution** (ligne 469)
   - `city AND country fournis ?` → CLI ou Interactif

2. **Clé API** (plusieurs endroits)
   - `api_key fourni ?` → Utiliser ou charger depuis fichier
   - `api_key trouvée ?` → Continuer ou ERREUR
   - `api_key valide ?` → Continuer ou ERREUR

3. **Réponse API** (ligne 368)
   - `status_code == 200 ?` → Continuer ou ERREUR

4. **Affichage** (ligne 383)
   - `display == True ?` → Afficher ou non

5. **Sauvegarde** (ligne 389)
   - `saved_file != None ?` → Succès ou ERREUR

6. **Menu interactif** (ligne 433)
   - `choice == "1" ?` → Weather Report
   - `choice == "2" ?` → ASCII Art
   - `choice == "3" ?` → Exit
   - `Autre ?` → ERREUR

7. **Transitions majeures** (ligne 158)
   - `weather_main_changed AND temp_change > 3°C ?` → Transition majeure

---

## 11. FLUX DE DONNÉES

```
API OpenWeatherMap
    │
    ▼
JSON brut (data)
    │
    ▼
format_forecast(data)
    │
    ├─► Extraction données
    ├─► Regroupement par jour
    ├─► Calcul cumuls
    ├─► calcul_major_transitions()
    │
    ▼
JSON formaté (formatted)
    │
    ├─► Affichage (si display=True)
    │
    ▼
save_to_file(formatted)
    │
    ├─► Génération nom fichier
    ├─► Création dossier si nécessaire
    │
    ▼
Fichier JSON sauvegardé
```

---

## 12. GESTION DES ERREURS

### Points d'erreur et actions :

1. **Fichier config introuvable**
   - `load_api_key()` → logger.error() + print() + return None

2. **Clé API vide/invalide**
   - `verify_api_key()` → logger.error() + print() + return False

3. **Erreur réseau**
   - `requests.get()` → Exception → logger.error() + print() + return False

4. **Erreur API (status != 200)**
   - `execute_weather_report()` → logger.error() + print() + return False

5. **Erreur sauvegarde**
   - `save_to_file()` → logger.error() + return None

6. **Erreur création dossier**
   - `setup_logging()` / `save_to_file()` → logger.error() + return/return None

---

## 13. HIÉRARCHIE DES APPELS DE FONCTIONS

```
cli()
├─► load_api_key()
├─► verify_api_key()
│   └─► requests.get() (test)
└─► [Mode CLI]
    └─► execute_weather_report()
        ├─► load_api_key() (si nécessaire)
        ├─► requests.get() (API)
        ├─► format_forecast()
        │   ├─► calcul_major_transitions()
        │   └─► (boucles de traitement)
        └─► save_to_file()
            └─► json.dump()

└─► [Mode Interactif]
    └─► main_menu()
        ├─► weather_report()
        │   ├─► load_api_key()
        │   └─► execute_weather_report()
        │       └─► (même structure que ci-dessus)
        └─► display_ascii_art()
```

---

## 14. CONSTANTES ET CONFIGURATION

### Constantes utilisées :

- **Dossiers** : `LOGS_DIR_NAME`, `JSON_OUTPUT_DIR_NAME`
- **Fichiers** : `CONFIG_FILE_NAME`, `JSON_EXTENSION`, `LOG_FILE_PREFIX`
- **Formats de date** : `DATE_FORMAT`, `DATETIME_FORMAT`, `LOG_DATE_FORMAT`, `FILE_TIMESTAMP_FORMAT`
- **Valeurs par défaut** : `DEFAULT_CITY_NAME`

### Configuration loguru :

- **Rotation** : 1 jour
- **Rétention** : 30 jours
- **Niveau** : INFO
- **Format** : `{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}`
- **Encodage** : UTF-8

---

## 15. POINTS CLÉS POUR LA PRÉSENTATION

1. **Deux modes d'exécution** : CLI (automatisé) et Interactif (menu)
2. **Gestion robuste des erreurs** : Vérification API, gestion fichiers, logs
3. **Formatage intelligent** : Transformation JSON brut → format structuré
4. **Calcul météorologique** : Transitions majeures (changement météo + variation temp > 3°C)
5. **Organisation fichiers** : Dossiers automatiques, noms avec timestamps
6. **Logging complet** : Toutes les actions sont loggées pour traçabilité

---

**Fin du document**

