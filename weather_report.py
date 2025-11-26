# weather_report.py
import requests
import json
import click
from loguru import logger
import os
from datetime import datetime

# Variables globales pour le répertoire de base et les chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Constantes pour les noms de dossiers
LOGS_DIR_NAME = "Logs"
JSON_OUTPUT_DIR_NAME = "JSON Output"

# Constantes pour les fichiers
CONFIG_FILE_NAME = "local.conf"
JSON_EXTENSION = ".json"
LOG_FILE_PREFIX = "weather_report_"

# Constantes pour les formats de date
DATE_FORMAT = "%Y-%m-%d"  # Format pour les dates locales
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"  # Format pour les timestamps API
LOG_DATE_FORMAT = "%Y%m%d"  # Format pour les noms de fichiers de log
FILE_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"  # Format pour les timestamps de fichiers

# Constante par défaut pour la création de JSON output formattée
DEFAULT_CITY_NAME = "weather"

# Configuration des logs avec loguru
def setup_logging():
   # Configure le dossier Logs et initialise loguru pour les logs.
    logs_dir = os.path.join(BASE_DIR, LOGS_DIR_NAME)
    
    # Création du dossier Logs s'il n'existe pas
    logs_created = False
    if not os.path.exists(logs_dir):
        try:
            os.makedirs(logs_dir)
            logs_created = True
        except Exception as e:
            logger.error(f"Erreur lors de la création du dossier 'Logs' : {e}")
            return
    
    # Configuration de loguru pour écrire dans un fichier uniquement (pas de sortie console)
    logger.remove()
    
    # Avoir uniquement le handler fichier
    log_file = os.path.join(logs_dir, f"{LOG_FILE_PREFIX}{datetime.now().strftime(LOG_DATE_FORMAT)}.log")
    logger.add(
        log_file,
        rotation="1 day",
        retention="30 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        encoding="utf-8"
    )
    logger.info("Système de logs initialisé")
    if logs_created:
        logger.info(f"Dossier 'Logs' créé : {logs_dir}")

# Initialisation des logs au démarrage
setup_logging()

# Vérification de la clé API + fichier de configuration
def load_api_key(config_file=CONFIG_FILE_NAME):

    complete_path = os.path.join(BASE_DIR, config_file)
    
    if not os.path.exists(complete_path):
        logger.error(f"Fichier de configuration introuvable : {complete_path}")
        print(f"Erreur : le fichier '{complete_path}' est introuvable. \nVeuillez vérifier que le fichier soit bien présent et nommé tel que '{CONFIG_FILE_NAME}'")
        return None

    try:
        logger.info(f"Lecture du fichier de configuration : {complete_path}")
        with open(complete_path, "r") as f:
            for line in f:
                if line.startswith("API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    if key:
                        logger.info("Clé API chargée depuis le fichier de configuration")
                    return key if key else None
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier de configuration : {e}")
        print(f"Erreur lors de la lecture du fichier : {e}")
        return None

    return None  
    # Si aucune ligne API_KEY n'est trouvée

# Vérification du fonctionnement de la clé API
def verify_api_key(api_key, quiet=False): 
    if not api_key:
        logger.warning("Tentative de vérification avec une clé API vide")
        return False
    
    # Requête test avec une ville témoin (Toulouse)
    test_url = f"http://api.openweathermap.org/data/2.5/forecast?q=Toulouse,FR&appid={api_key}&units=metric"
    logger.info("Début de la vérification de la clé API")
    
    try:
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            logger.success("Clé API vérifiée avec succès (code 200)")
            return True
        else:
            logger.error(f"Échec de la vérification de la clé API (code {response.status_code})")
            if not quiet:
                print(f"Erreur : La clé API ne fonctionne pas (code {response.status_code})")
                if 500 <= response.status_code <= 599:
                    logger.error("Erreur interne du serveur (500-599)")
                    print("Erreur interne du serveur (500-599).")
                elif response.status_code == 401:
                    logger.error("Clé API invalide ou expirée")
                    print("Clé API invalide ou expirée.")
                else:
                    logger.error(f"Erreur lors de la requête à l'API (code {response.status_code})")
                    print("Erreur lors de la requête à l'API.")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Exception lors de la vérification de la clé API : {e}")
        if not quiet:
            print(f"Erreur lors de la vérification de la clé API : {e}")
        return False

# Calcul des transitions majeures basé sur list.weather.main
def calcul_major_transitions(entries):
    """
    Calcule le nombre de transitions majeures dans une journée via entries.

    La structure est la suivante:
    [
        {
            "temp": 20.0,
            "weather": "Rain"
        },
        {
            "temp": 21.0,
            "weather": "Snow"
        }

        etc....
    ]
    """
    major_transitions = 0

    # On compare chaque entrée avec la précédente
    for i in range(1, len(entries)):
        prev = entries[i - 1]
        curr = entries[i]

        # Comparaison de list.weather.main entre deux échantillons consécutifs
        weather_main_changed = (prev["weather"] != curr["weather"])
        temp_change = abs(prev["temp"] - curr["temp"])

        # Transition majeure si list.weather.main change ET variation temp > 3°C
        if weather_main_changed and temp_change > 3:
            major_transitions += 1

    return major_transitions

# Transformation et mise en forme du résultat JSON
def format_forecast(data):

    # Récupération basique des infos de la ville
    city_info = data["city"]
    forecast_list = data["list"]

    # Structure demandée
    result = {}
    result["forecast_location_name"] = city_info["name"]
    result["country_code"] = city_info["country"]
    result["total_rain_period_mm"] = 0.0
    result["total_snow_period_mm"] = 0.0
    result["max_humidity_period"] = 0
    result["forecast_details"] = []

    # On va regrouper dans ce dictionaire les jours
    days = {}

    # Puis parcourir toutes les entrées 3h 
    for entry in forecast_list:

        dt_txt = entry["dt_txt"]
        timestamp = datetime.strptime(dt_txt, DATETIME_FORMAT)
        date_str = timestamp.strftime(DATE_FORMAT)

        if "rain" in entry:
            if "3h" in entry["rain"]:
                rain = entry["rain"]["3h"]
            else:
                rain = 0.0
        else:
            rain = 0.0

        if "snow" in entry:
            if "3h" in entry["snow"]:
                snow = entry["snow"]["3h"]
            else:
                snow = 0.0
        else:
            snow = 0.0

        temp = entry["main"]["temp"]
        humidity = entry["main"]["humidity"]
        # Extraction de list.weather.main en se basant sur la Doc API OpenWeatherMap (catégorie météo principale: Rain, Snow, Clouds, etc.)
        weather_main = entry["weather"][0]["main"]

        # Mise à jour des totaux
        result["total_rain_period_mm"] += rain
        result["total_snow_period_mm"] += snow

        if humidity > result["max_humidity_period"]:
            result["max_humidity_period"] = humidity

        # Vérifier si ce jour existe déjà
        if date_str not in days:
            days[date_str] = {}
            days[date_str]["rain_cumul_mm"] = 0.0
            days[date_str]["snow_cumul_mm"] = 0.0
            days[date_str]["entries"] = []

        # Ajouter les données de la journée
        days[date_str]["rain_cumul_mm"] += rain
        days[date_str]["snow_cumul_mm"] += snow

        # Stocker l'état météo complet (temp + weather) pour une comparaison et calcul de transitions majeures plus simple
        days[date_str]["entries"].append({
            "temp": temp,
            "weather": weather_main  
        })

    # Calcul des transitions majeures 
    for date in days:

        entries = days[date]["entries"]
        major_transitions = calcul_major_transitions(entries)

        # Ajouter l'entrée journalière au résultat final
        day_result = {
            "date_local": date,
            "rain_cumul_mm": round(days[date]["rain_cumul_mm"], 2),
            "snow_cumul_mm": round(days[date]["snow_cumul_mm"], 2),
            "major_transitions_count": major_transitions
        }

        result["forecast_details"].append(day_result)

    return result

# Sauvegarde du résultat JSON dans un fichier
def save_to_file(data, filename=None, city=None, country=None):
    
    # Création du dossier JSON Output s'il n'existe pas
    output_dir = os.path.join(BASE_DIR, JSON_OUTPUT_DIR_NAME)
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logger.info(f"Dossier '{JSON_OUTPUT_DIR_NAME}' créé : {output_dir}")
        except Exception as e:
            logger.error(f"Erreur lors de la création du dossier '{JSON_OUTPUT_DIR_NAME}' : {e}")
            return None
    
    # Sauvegarde les données JSON formatées dans un fichier. Si le nom de fichier n'est pas fourni, on génère un nom automatique.
    if filename is None:
        city_name = data.get("forecast_location_name", DEFAULT_CITY_NAME)
        country_code = data.get("country_code", "")
        timestamp = datetime.now().strftime(FILE_TIMESTAMP_FORMAT)
        filename = f"{city_name}_{country_code}_{timestamp}{JSON_EXTENSION}"
    
    # S'assurer que le fichier a l'extension .json
    if not filename.endswith(JSON_EXTENSION):
        filename += JSON_EXTENSION
    
    # Chemin complet du fichier dans le dossier JSON Output
    complete_path = os.path.join(output_dir, filename)
    
    try:
        logger.info(f"Écriture du fichier JSON : {complete_path}")
        with open(complete_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.success(f"Fichier JSON écrit avec succès : {complete_path}")
        return complete_path
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture du fichier JSON : {e}")
        return None

# Fonction pour afficher l'ASCII art de Weather Report venant du Manga JOJO's Bizarre Adventure : Stone Ocean
def display_ascii_art():
    ascii_art = """Weather Report manipulates the weather.
    
    ⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣿⣿⣿⣿⣿⣿⡿⠛⢛⣋⣭⣤⣬⣉⣉⠛⠉⠙⠋⠙⠛⠛⠟⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⡟⠃⠘⠿⠿⠟⣋⣁⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣶⣦⣤⣤⣤⡆⠀⠀⠰⠤⠬⢉⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⠀⣶⡄⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⣶⣶⣶⣿⣷⡄⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⠀⠂⠹⢀⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠏⠀⠀⠀⢐⣿⣿⣿⣿⣿⣿⡄⢻⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⡇⢹⣿⣿⣿⣿⣿⡟⢹⣿⣿⡇⣿⣿⣿⣿⠇⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⢀⣤⣴⣶⣿⣿⣿⣿⣿⣿⣿⣯⠀⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⢸⣿⣿⡇⣿⣿⣿⣿⠃⠀⣴⣿⣿⣿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⢹⡇⢸⣿⣿⣿⣿⣿⣿⢸⣿⣿⡇⣿⣿⣿⣏⠂⣸⣿⣿⣿⣿⣷⣌⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⢸⡇⢸⣿⣿⣿⣿⣿⣿⣼⣿⣿⡇⣿⣿⣿⣿⠸⠿⣿⣿⣿⣿⣿⣿⣦⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠁⠁⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⢸⡇⢸⣿⣿⣿⣿⣿⣿⢻⣿⣿⡇⣿⣿⣿⣿⠆⣸⣿⣿⣿⣿⣿⣿⣿⣿⡟⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⢸⡇⢸⣿⣿⣿⣿⣿⣿⢹⣿⣿⡇⣿⣿⣿⡇⠀⢿⠿⣿⣿⣿⣿⣿⣿⣿⠠⠀⠈⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣾⢀⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⢸⡇⢸⣿⣿⣿⣿⣿⣿⣼⣿⣿⡇⣿⣿⣿⣇⠀⠀⠾⣿⣿⣿⣿⢿⠟⠁⠀⣤⣾⣆⠀⠙⠿⣿⡟⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⣿⣿⡏⣼⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⢸⡇⢸⣿⣿⣿⣿⣿⣿⣻⣿⣿⡇⣿⣿⣿⣿⡆⢻⠀⣿⣿⣿⠟⠁⠀⠀⠁⠙⣿⣿⣿⣿⣶⣄⡙⠦⠹⣿⣿⣿⣿⣿⣿⣿⣿⡏⠂⢸⣿⡇⣶⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⢸⡇⢸⣿⣿⣿⣿⣿⣿⢼⣿⣿⡇⣿⣿⣿⣿⡇⠀⣾⣿⠏⠀⠀⠀⠙⠗⠁⢀⣿⡏⠹⠿⠛⠛⠁⠄⣄⠈⠻⣿⣿⣿⣿⣿⣿⠻⣅⣼⣿⡇⢿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⢸⡇⢸⣿⣿⣿⣿⣿⣿⢸⣿⣿⡇⣿⣿⣿⣿⡇⢰⣿⣿⡄⢀⡄⠀⠀⠈⠀⢿⣿⣷⡀⠀⠀⠀⠀⠄⣰⣦⡀⠈⠙⢿⣿⣿⣿⣦⣿⣿⣿⡗⢸⣿⣿⣿⣿⣿⣿⡿⣿
    ⣿⣿⣿⣿⢸⡇⢸⣿⣿⣿⣿⣿⣿⢸⣿⣿⡇⣿⣿⣿⣿⠃⠸⣿⢿⠇⠘⠡⡤⠀⠀⠀⠸⠿⣿⣷⣌⣰⣦⣴⣶⣿⣿⡏⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⠃⢸⣿⣿⣿⣿⣿⣿⡏⢹
    ⣿⡿⣣⡧⠘⠃⢸⣿⣿⣿⣿⣿⣿⢸⣿⣿⡇⣿⣿⣿⣿⡄⢸⣿⡎⠀⠀⠀⣿⣿⣤⡶⢠⣤⡄⢿⡿⢸⣿⣿⣿⣿⡟⢀⣾⠀⠀⢻⣿⣿⣿⣿⣿⠇⠀⣾⣿⣿⣿⣿⣿⣿⣿⣸
    ⠥⠚⠉⠚⠀⣀⣸⣿⣿⣿⣿⣿⣿⢸⣿⣿⡇⣿⣿⣿⣿⣇⠘⣿⣷⡀⠀⠀⢹⣿⣿⡿⢿⣿⡿⠿⢣⣿⣿⣿⣿⡿⠀⣸⣿⠃⠀⢼⣿⣿⣿⣿⣧⡀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⠄⠀⢀⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⣿⡇⣿⣿⣿⣿⣿⡀⣿⡽⣷⣄⠀⠀⣿⣿⣷⡆⠉⣴⣿⣿⣿⣿⣿⣿⡀⣠⣧⠊⠀⠀⢸⣿⣿⣿⣿⣿⢃⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣠⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⣿⡇⣿⣿⣿⣿⣿⣧⠈⠁⠻⠇⠀⠀⠈⣿⡧⠠⣀⣤⣤⡌⢉⣻⣿⣿⣿⡿⠃⠀⠀⠀⠀⢿⣿⣿⣿⠇⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⢸⣿⣿⡇⣿⣿⣿⣿⣿⣿⡇⠀⢀⣀⠀⠀⠀⠈⢻⣶⣦⣤⣴⣶⣾⣿⡟⠛⣉⣤⣾⠆⠀⠀⠀⠀⠉⠉⠉⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢋⣡⣦⢸⣿⣿⡇⣿⣿⣿⡿⠛⣡⣴⣿⠟⣁⣴⣧⠀⢠⡀⠙⠿⣿⣿⡿⠛⠋⣠⣾⣿⣿⡏⠀⠄⠀⠀⢀⣀⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⡿⠟⣉⣤⣾⣿⡇⣾⣿⣿⠇⠛⠉⢀⣴⣿⣿⣋⣡⣾⣿⣿⣿⣿⣷⡄⠻⣶⡄⠀⠀⠀⣀⣼⣿⣿⣿⣿⠃⠀⢀⣠⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⠟⢋⣴⣾⣿⣿⣿⣿⡇⢺⡿⠃⠀⠀⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠀⠡⡄⠀⢀⣿⣿⣿⣿⣿⠇⡀⠀⠙⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣿⣿⣿
    ⣿⣿⣟⣁⣼⣿⣿⣿⣿⣿⡿⠟⠁⠀⠀⠀⠀⠐⠿⠿⠿⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠃⠀⣿⣿⣆⣉⠛⠿⠿⠏⢰⠇⣀⡀⠀⠀⠙⠿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢻⣿
    ⡿⢿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⣠⣶⣦⠀⠀⠀⠀⠀⠀⠉⠉⠉⠉⠛⠛⠏⠠⠆⠀⠹⣿⣿⣿⣿⣦⣀⣰⣿⠰⣿⣿⣶⣄⠀⠀⠀⠀⢻⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣯
    ⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠈⠉⠀⠈⠀⠀⣠⣾⣿⠀⠀⠀⠀⠀⣀⠀⠀⠀⠀⠈⠀⠘⠛⠿⢿⣿⣿⣿⣿⣄⣹⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠉⠛⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⠏⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠊⠉⠀⠈⠀⠀⠀⠀⣸⣿⡇⠀⠀⠀⢠⡀⠀⠀⠀⠀⠀⠉⠉⠉⠛⠻⠿⠿⣿⣿⡿⢁⣤⡀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡿⠛⡇⠀⠀⢠⣿⣿⠀⠀⠀⠀⠀⣶⣦⡄⠀⠀⠀⠀⠀⠀⠀⠙⠛⠃⠀⠀⠴⠆⠀⠈⠻⣿⣿⣿⣿
    ⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠚⠉⠀⠀⠇⠀⠀⣼⣿⣿⣇⠀⠀⠀⠀⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿
    ⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠟⠙⠿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿
    ⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢦⢿⣿
    ⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⣠⣤⣴⣶⣶⣾⡿⠿⠛⠓⠀⠀⠀⠀⠀⠀⠀⠘⡎⣿
    ⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⣹⣿⣿⣿⣿⡿⠟⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⣾
    ⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠖⠀⣼⣿⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹
    ⡿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢐⠈⠀⠘⠉⢁⡄⠄⠀⠀⠀⠀⠀⢀⣀⣴⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸
    ⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢜⠼⢰⣠⠈⠘⢑⠀⠀⠀⢀⣤⣾⡿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠠⠤⠀⠀⢀⣠⣾⣿⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⢈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⢿⡿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
    ⠀⠀⠀⠀⠀⠶⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠁⠀⠀⠂⠀⠀⠀⠀⠀⠀⢰⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⠀⠀⠀⠀⢶⣶⡆
    ⠀⠀⠀⠀⠀⠀⠀⠂⠀⠀⠀⠀⠀⣿⣷⡀⠀⠀⣐⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠙⠇
    ⠀⢀⢲⡀⠂⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⢇⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠐⢀⠐⢎⠀⠒⠌⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠈⠀⠐⠂⠀⠀⠀⠀⠀⢀⡄⣿⣿⣿⢸⣆⠘⣿⣆⠀⠀⠀⠀⠀⠀⠀⠑⢒⠐⠑⠂⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⠀⣿⣿⣿⢸⣿⣆⠈⢻⣦⡀⠀⠀⠀⠀⠀⠐⠀⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣿⡏⠀⠀⠀⠀⣴⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⣦⣄⣀⠀⠀⠀⠀⠀⠀⠘⣻⣿⡄⣿⣿⡟⢸⣿⣿⣦⡀⠻⣿⣄⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⡟⠁⠀⠀⠀⣸⡟⠀⠀⠀⠀⠀⠀⠀⠘⣿⣶
    ⣿⣿⣿⣿⣷⣦⡀⠀⠀⣾⣿⣿⡇⣿⣿⣇⢸⣿⣿⣿⣿⣦⣄⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⠟⠛⣿⣿⡇⠀⠀⠀⣸⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻
    ⠈⠙⢝⣿⠿⠿⠕⠂⠀⠈⠙⢿⡇⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣶⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⣿⡿⠃⠀⠀⣼⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠉⠉⠈⠀⠈⠀⠀⠀⠀⠈⠁⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠀⠀⢀⣼⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""
    print(ascii_art)

# Fonction pour exécuter le rapport météo (logique séparée pour click et mode interactif)
def execute_weather_report(city, country, api_key=None, display=True, quiet=False):
    
    #Exécute le rapport météo pour une ville donnée. Charge la clé API si non fournie
    if api_key is None:
        api_key = load_api_key()
        if not api_key:
            logger.error("Clé API introuvable ou vide dans 'local.conf'")
            if not quiet:
                print("Erreur : clé API introuvable ou vide dans 'local.conf'.")
            else:
                click.echo("Erreur : clé API introuvable ou vide dans 'local.conf'.", err=True)
            return False

    url = (f"http://api.openweathermap.org/data/2.5/forecast?q={city},{country}&appid={api_key}&units=metric&lang=fr")

    logger.info(f"Envoi de la requête API pour {city}, {country}")
    if not quiet:
        print("\nRequête envoyée\n")

    try:
        response = requests.get(url)

        if response.status_code != 200:
            logger.error(f"Erreur API ({response.status_code}) : {response.text}")
            if not quiet:
                print(f"Erreur API, veuillez vérifier vos arguments ou clé API ({response.status_code}) : {response.text}")
            else:
                click.echo(f"Erreur API, veuillez vérifier vos arguments ou clé API ({response.status_code})", err=True)
            return False

        data = response.json() # Récupération du JSON raw
        logger.info(f"Données JSON brutes récupérées pour {city}, {country}")
        
        formatted = format_forecast(data) # Formatage du JSON raw
        logger.info(f"JSON formaté généré avec succès pour {city}, {country}")
        
        # Afficher le résultat si demandé
        if display:
            print(json.dumps(formatted, indent=4, ensure_ascii=False))
        
        # Sauvegarde dans un fichier
        logger.info(f"Début de la sauvegarde du fichier pour {city}, {country}")
        saved_file = save_to_file(formatted, city=city, country=country)
        if saved_file:
            logger.success(f"Fichier sauvegardé avec succès : {saved_file}")
            if not quiet:
                print(f"\nRésultat sauvegardé dans le fichier : {saved_file}")
        else:
            logger.error("Échec de la sauvegarde du fichier")
            if not quiet:
                print("\nErreur lors de la sauvegarde du fichier.")
        
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur réseau lors de la requête API : {e}")
        if not quiet:
            print(f"Erreur réseau : {e}")
        else:
            click.echo(f"Erreur réseau : {e}", err=True)
        return False

# Fonction pour appel API + JSON raw (mode interactif)
def weather_report():
    api_key = load_api_key()

    if not api_key:
        print("Erreur : clé API introuvable ou vide dans 'local.conf'.")
        return

    city = input("Entrez le nom de la ville : ")
    country = input("Entrez le code pays (FR, US, etc.) : ")
    
    # Demander si l'utilisateur souhaite afficher le résultat
    display_choice = input("\nSouhaitez-vous afficher le résultat formaté ? (o/n) : ").strip().lower()
    display = display_choice in ['o', 'oui', 'y', 'yes']
    
    execute_weather_report(city, country, api_key, display)

# Fonction pour menu intéractif
def main_menu():
    while True:
        print("==============================")
        print("1. Weather Report")
        print("2. Ascii ")
        print("3. Exit")
        print("==============================")
        choice = input("Veuillez choisir une option (1, 2, ou 3) : ")

        if choice == '1':
            # Appel de la fonction weather report
            print("\nFonction Weather Report sélectionnée.")
            weather_report() 
        elif choice == '2':
            # Appel de la fonction ascii weather report
            print("\nFonction Ascii art sélectionnée.\n")
            display_ascii_art()
        elif choice == '3':
            print("\nFermeture du programme")
            logger.info("Sortie du programme demandée par l'utilisateur (option 3)")
            # Break pour exit le programme
            break 
        else:
            print(f"\n Erreur: L'option '{choice}' n'est pas valide. Veuillez réessayer.")




# Commande CLI avec click
@click.command()
@click.option('--city', '-c', help='Nom de la ville')
@click.option('--country', '-co', help='Code pays (FR, US, etc.)')
@click.option('--api-key', '-k', help='Clé API OpenWeatherMap')
@click.option('--no-display', is_flag=True, help='Ne pas afficher le résultat formaté')
def cli(city, country, api_key, no_display):
    """
    Programme de rapport météorologique avec support CLI.
    
    Utilisation:
        python weather_report.py --city Paris --country FR
        python weather_report.py -c London -co GB --api-key YOUR_API_KEY
    """
    # Si des arguments CLI sont fournis, exécuter en mode CLI
    if city and country:
        # Vérifier la clé API
        if api_key:
            if not verify_api_key(api_key, quiet=True):
                click.echo("Erreur : La clé API fournie n'est pas valide.", err=True)
                logger.info("Sortie du programme (clé API invalide en mode CLI)")
                return
        else:
            # Charger depuis le fichier et vérifier
            loaded_key = load_api_key()
            if not loaded_key:
                click.echo("Erreur : Clé API introuvable dans 'local.conf'.", err=True)
                click.echo("Utilisez --api-key pour fournir une clé API.", err=True)
                logger.info("Sortie du programme (clé API introuvable en mode CLI)")
                return
            if not verify_api_key(loaded_key, quiet=True):
                click.echo("Erreur : La clé API n'est pas valide.", err=True)
                logger.info("Sortie du programme (clé API invalide en mode CLI)")
                return
            api_key = loaded_key
        
        # Exécuter le rapport météo
        execute_weather_report(city, country, api_key, display=not no_display, quiet=True)
        logger.info("Sortie du programme (mode CLI terminé)")
    else:
        # Mode interactif : vérifier la clé API puis lancer le menu
        print("Vérification de la clé API...")
        loaded_key = api_key if api_key else load_api_key()
        
        if not loaded_key:
            click.echo("Erreur : Clé API introuvable dans 'local.conf'.", err=True)
            click.echo("Utilisez --api-key pour fournir une clé API ou configurez local.conf", err=True)
            logger.info("Sortie du programme (clé API introuvable en mode interactif)")
            return
        
        if verify_api_key(loaded_key):
            print("Clé API valide et fonctionnelle.\n")
            main_menu()
            logger.info("Sortie du programme (menu interactif terminé)")
        else:
            click.echo("Erreur : La clé API n'est pas valide ou ne fonctionne pas. Veuillez vérifier 'local.conf'", err=True)
            logger.info("Sortie du programme (clé API invalide)")

if __name__ == "__main__":
    cli()

