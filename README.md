# Weather Report

Programme Python pour récupérer et formater les prévisions météorologiques via l'API OpenWeatherMap.

## 📋 Description

Ce programme permet de :
- Récupérer les prévisions météorologiques sur 5 jours (par tranches de 3 heures)
- Formater les données selon une structure JSON spécifique
- Calculer les transitions majeures (changements de conditions météo avec variation de température > 3°C)
- Sauvegarder les résultats dans des fichiers JSON
- Utiliser le programme en ligne de commande (CLI) ou en mode interactif

## 🔧 Prérequis

- Python 3.6 ou supérieur
- Une clé API OpenWeatherMap (gratuite sur [openweathermap.org](https://openweathermap.org/api))

## 📦 Installation

1. Clonez ou téléchargez ce projet
2. Installez les dépendances requises :

```bash
pip install -r requirements.txt
```

Ou manuellement :

```bash
pip install requests click loguru
```

## ⚙️ Configuration

### Fichier `local.conf`

Créez un fichier `local.conf` à la racine du projet avec votre clé API :

```
API_KEY=votre_cle_api_ici
```

**Note :** Le programme vérifie automatiquement la validité de la clé API au démarrage.

## 🚀 Utilisation

### Mode Ligne de Commande (CLI)

Le programme peut être utilisé directement depuis le terminal avec des arguments.

#### Syntaxe de base

```bash
python weather_report.py --city <ville> --country <code_pays>
```

#### Options disponibles

- `--city` ou `-c` : Nom de la ville (requis en mode CLI)
- `--country` ou `-co` : Code pays ISO (ex: FR, US, GB) (requis en mode CLI)
- `--api-key` ou `-k` : Clé API OpenWeatherMap (optionnel, utilise `local.conf` par défaut)
- `--no-display` : Ne pas afficher le résultat JSON formaté dans la console

#### Exemples d'utilisation CLI

```bash
# Utilisation basique avec la clé API du fichier local.conf
python weather_report.py --city Paris --country FR

# Utilisation avec une clé API fournie en argument
python weather_report.py -c London -co GB --api-key YOUR_API_KEY

# Sauvegarder sans afficher le résultat
python weather_report.py --city New York --country US --no-display

# Utilisation avec les options courtes
python weather_report.py -c Tokyo -co JP
```

#### Aide en ligne

```bash
python weather_report.py --help
```

### Mode Interactif

Si vous lancez le programme sans arguments, un menu interactif s'affiche :

```bash
python weather_report.py
```

Le menu propose 3 options :
1. **Weather Report** : Récupérer les prévisions météorologiques
2. **Ascii** : Afficher l'ASCII art de Weather Report (référence à JoJo's Bizarre Adventure)
3. **Exit** : Quitter le programme

Lors de l'option 1, le programme vous demandera :
- Le nom de la ville
- Le code pays
- Si vous souhaitez afficher le résultat formaté dans la console

## 📁 Structure des fichiers générés

### Dossier "JSON Output"

Les fichiers JSON formatés sont automatiquement sauvegardés dans le dossier `JSON Output` avec le format suivant :

```
<ville>_<code_pays>_<timestamp>.json
```

Exemple : `Paris_FR_20251126_221305.json`

### Structure du JSON généré

```json
{
    "forecast_location_name": "Paris",
    "country_code": "FR",
    "total_rain_period_mm": 12.5,
    "total_snow_period_mm": 0.0,
    "max_humidity_period": 95,
    "forecast_details": [
        {
            "date_local": "2025-11-27",
            "rain_cumul_mm": 5.2,
            "snow_cumul_mm": 0.0,
            "major_transitions_count": 2
        },
        ...
    ]
}
```

### Dossier "Logs"

Les logs sont automatiquement enregistrés dans le dossier `Logs` avec rotation quotidienne et rétention de 30 jours.

Format des fichiers de log : `weather_report_YYYYMMDD.log`

## 📊 Fonctionnalités

### Calcul des transitions majeures

Une transition majeure est détectée lorsque :
- Le type de météo change (`weather.main` : Rain, Snow, Clouds, etc.)
- **ET** la variation de température est supérieure à 3°C

### Agrégation des données

- **Pluie** : Cumul total sur la période (en mm)
- **Neige** : Cumul total sur la période (en mm)
- **Humidité** : Valeur maximale sur la période (en %)
- **Transitions majeures** : Nombre par jour

## 🔍 Logs

Le programme utilise `loguru` pour enregistrer tous les événements dans des fichiers de log :
- Vérification de la clé API
- Requêtes API
- Génération des fichiers JSON
- Erreurs et exceptions
- Sorties du programme

**Note :** Les logs ne s'affichent pas dans la console, uniquement dans les fichiers du dossier `Logs`.

## ⚠️ Gestion des erreurs

Le programme gère plusieurs types d'erreurs :

- **Clé API invalide** : Code HTTP 401
- **Erreurs serveur** : Codes HTTP 500-599
- **Erreurs réseau** : Timeouts, connexion impossible
- **Fichier de configuration manquant** : `local.conf` introuvable
- **Ville introuvable** : Code HTTP 404

Toutes les erreurs sont loggées dans les fichiers de log.

## 📝 Exemples complets

### Exemple 1 : Prévisions pour Paris

```bash
python weather_report.py --city Paris --country FR
```

### Exemple 2 : Prévisions sans affichage console

```bash
python weather_report.py -c "New York" -co US --no-display
```

### Exemple 3 : Mode interactif

```bash
python weather_report.py
# Puis sélectionner l'option 1 dans le menu
```

## 🛠️ Dépendances

- `requests` : Pour les requêtes HTTP vers l'API OpenWeatherMap
- `click` : Pour l'interface en ligne de commande
- `loguru` : Pour la gestion des logs

Ce projet est un travail pratique (TP) Python.

## 🔗 Liens utiles

- [Documentation OpenWeatherMap API](https://openweathermap.org/api)
- [Documentation Click](https://click.palletsprojects.com/)
- [Documentation Loguru](https://loguru.readthedocs.io/)

