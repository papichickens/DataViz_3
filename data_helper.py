import pandas as pd
import os

# --- NEW FLAG SYSTEM (PRESERVED) ---
# This new, more robust flag system is kept exactly as you designed it.
MANUAL_NAME_TO_ISO2 = {
    # Critical Fixes & Common Names
    "Germany": "de", "USA": "us", "Republic of Ireland": "ie", "Korea Republic": "kr",
    "South Korea": "kr", "Korea DPR": "kp", "North Korea": "kp", "IR Iran": "ir",
    # UK Home Nations
    "England": "gb-eng", "Scotland": "gb-sct", "Wales": "gb-wls", "Northern Ireland": "gb-nir",
    # Historic or Former Country Names
    "Germany FR": "de", "Germany DR": "de", "Soviet Union": "ru", "Yugoslavia": "rs",
    "Czechoslovakia": "cz", "Dutch East Indies": "id", "Serbia and Montenegro": "rs", "Zaire": "cd",
    # Standard Country Names
    "Algeria": "dz", "Angola": "ao", "Argentina": "ar", "Australia": "au", "Austria": "at",
    "Belgium": "be", "Bolivia": "bo", "Bosnia and Herzegovina": "ba", "Brazil": "br",
    "Bulgaria": "bg", "Cameroon": "cm", "Canada": "ca", "Chile": "cl", "China PR": "cn",
    "Colombia": "co", "Costa Rica": "cr", "Cote d'Ivoire": "ci", "Côte d'Ivoire": "ci",
    "Croatia": "hr", "Cuba": "cu", "Czech Republic": "cz", "Denmark": "dk", "Ecuador": "ec",
    "Egypt": "eg", "El Salvador": "sv", "France": "fr", "Ghana": "gh", "Greece": "gr",
    "Haiti": "ht", "Honduras": "hn", "Hungary": "hu", "Iceland": "is", "Iran": "ir",
    "Iraq": "iq", "Israel": "il", "Italy": "it", "Jamaica": "jm", "Japan": "jp",
    "Kuwait": "kw", "Mexico": "mx", "Morocco": "ma", "Netherlands": "nl", "New Zealand": "nz",
    "Nigeria": "ng", "Norway": "no", "Paraguay": "py", "Peru": "pe", "Poland": "pl",
    "Portugal": "pt", "Romania": "ro", "Russia": "ru", "Saudi Arabia": "sa", "Senegal": "sn",
    "Serbia": "rs", "Slovakia": "sk", "Slovenia": "si", "South Africa": "za", "Spain": "es",
    "Sweden": "se", "Switzerland": "ch", "Togo": "tg", "Trinidad and Tobago": "tt",
    "Tunisia": "tn", "Turkey": "tr", "Ukraine": "ua", "United Arab Emirates": "ae", "Uruguay": "uy",
}

def country_to_iso2(name: str) -> str | None:
    if not name or not isinstance(name, str): return None
    iso_code = MANUAL_NAME_TO_ISO2.get(name.strip())
    return iso_code.lower() if iso_code else None

def get_flag_url_by_iso(iso2: str) -> str:
    if not iso2: return ""
    return f"https://flagcdn.com/w320/{iso2}.png"

def get_flag_url(country_name: str) -> str:
    iso2 = country_to_iso2(country_name)
    return get_flag_url_by_iso(iso2) if iso2 else ""

# --- MAP HELPER (PRESERVED) ---
def get_country_iso_mapping():
    # This is correct. It's the ONLY place where different Germany names
    # should be consolidated for the map visualization.
    return {
        'USA': 'USA', 'Uruguay': 'URY', 'Argentina': 'ARG', 'Yugoslavia': 'YUG', 'Chile': 'CHL',
        'Brazil': 'BRA', 'France': 'FRA', 'Romania': 'ROU', 'Paraguay': 'PRY', 'Peru': 'PER',
        'Belgium': 'BEL', 'Bolivia': 'BOL', 'Mexico': 'MEX', 'Italy': 'ITA', 'Czechoslovakia': 'CZE',
        'Germany': 'DEU', 'West Germany': 'DEU', 'Germany FR': 'DEU', 'Austria': 'AUT', 'Spain': 'ESP',
        'Hungary': 'HUN', 'Switzerland': 'CHE', 'Sweden': 'SWE', 'Netherlands': 'NLD', 'Egypt': 'EGY',
        'Cuba': 'CUB', 'Norway': 'NOR', 'Poland': 'POL', 'Dutch East Indies': 'IDN', 'England': 'GBR',
        'Scotland': 'GBR', 'Wales': 'GBR', 'Northern Ireland': 'GBR', 'Turkey': 'TUR',
        'South Korea': 'KOR', 'Korea Republic': 'KOR', 'Soviet Union': 'RUS', 'Colombia': 'COL',
        'Bulgaria': 'BGR', 'North Korea': 'PRK', 'Portugal': 'PRT', 'Morocco': 'MAR',
        'El Salvador': 'SLV', 'Israel': 'ISR', 'East Germany': 'DEU', 'Australia': 'AUS',
        'Haiti': 'HTI', 'Zaire': 'COD', 'Tunisia': 'TUN', 'IR Iran': 'IRN', 'Iran': 'IRN',
        'Algeria': 'DZA', 'Cameroon': 'CMR', 'Honduras': 'HND', 'Kuwait': 'KWT',
        'New Zealand': 'NZL', 'Denmark': 'DNK', 'Iraq': 'IRQ', 'Canada': 'CAN',
        'Republic of Ireland': 'IRL', 'Costa Rica': 'CRI', 'United Arab Emirates': 'ARE',
        'Nigeria': 'NGA', 'Saudi Arabia': 'SAU', 'Russia': 'RUS', 'Greece': 'GRC',
        'Croatia': 'HRV', 'Jamaica': 'JAM', 'South Africa': 'ZAF', 'Japan': 'JPN',
        'FR Yugoslavia': 'YUG', 'Senegal': 'SEN', 'Slovenia': 'SVN', 'Ecuador': 'ECU',
        'China PR': 'CHN', 'Trinidad and Tobago': 'TTO', 'Ivory Coast': 'CIV', "Cote d'Ivoire": 'CIV',
        'Angola': 'AGO', 'Czech Republic': 'CZE', 'Ghana': 'GHA', 'Togo': 'TGO',
        'Ukraine': 'UKR', 'Serbia and Montenegro': 'SRB', 'Serbia': 'SRB', 'Slovakia': 'SVK',
        'Bosnia and Herzegovina': 'BIH', 'Iceland': 'ISL', 'Panama': 'PAN', 'Qatar': 'QAT'
    }

# --- REWORKED CLEANING AND LOADING FUNCTIONS ---

def clean_data_names(df):
    """
    Corrects encoding errors, artifacts, and performs transliteration for
    problematic characters like German umlauts.
    """
    if df is None:
        return df

    # 1. General artifact cleaning (e.g., remove 'rn">')
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(r'rn">', '', regex=True).str.strip()

    # 2. Transliteration for persistent encoding issues (German Umlauts)
    # This specifically targets the garbled representation of umlauts.
    umlaut_replacements = {
        'Ã¼': 'ue',  # For ü (e.g., Müller -> Mueller)
        'Ã¶': 'oe',  # For ö (e.g., Götze -> Goetze)
        'Ã¤': 'ae',  # For ä
        'Ã©': 'e',   # For é (e.g., Côte d'Ivoire)
        # Add any other specific mojibake-to-transliteration pairs here
    }
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].dtype == 'object':
            for bad_char, good_char in umlaut_replacements.items():
                df[col] = df[col].str.replace(bad_char, good_char, regex=False)

    # 3. Specific String Corrections for remaining encoding errors
    # This handles full-cell replacements.
    corrections = {
        'C�te d\'Ivoire': 'Côte d\'Ivoire',
        'Maracan� - Est�dio Jornalista M�rio Filho': 'Maracanã - Estádio Jornalista Mário Filho',
        'Est�dio Jornalista M�rio Filho': 'Estádio Jornalista Mário Filho',
        'Maracan�': 'Maracanã',
        'Stade V�lodrome': 'Stade Vélodrome',
        'Nou Camp - Estadio Le�n': 'Nou Camp - Estadio León',
        'Estadio Jos� Mar�a Minella': 'Estadio José María Minella',
        'Estadio Ol�mpico Chateau Carreras': 'Estadio Olímpico Chateau Carreras',
        'Estadio Municipal de Bala�dos': 'Estadio Municipal de Balaídos',
        'Estadio Ol�mpico Universitario': 'Estadio Olímpico Universitario',
        'Malm�': 'Malmö',
        'Malmo': 'Malmö', 
        'Norrk�Ping': 'Norrköping',
        'D�Sseldorf': 'Düsseldorf',
        'La Coru�A': 'A Coruña',
    }
    df.replace(corrections, inplace=True)
        
    return df

def load_world_cup_data(folder_name="data"):
    """
    Loads World Cup overview, matches, and players data from CSV files.

    Args:
        folder_name (str): The name of the folder where the CSV files are located.

    Returns:
        tuple: A tuple containing (world_cup_overview_df, matches_df, players_df, all_teams)
               or (None, None, None, None) if files cannot be loaded.
    """
    base_path = os.path.join(os.getcwd(), folder_name)
    
    world_cup_overview_path = os.path.join(base_path, "WorldCups.csv")
    matches_path = os.path.join(base_path, "WorldCupMatches.csv")
    players_path = os.path.join(base_path, "WorldCupPlayers.csv")

    # Initialize all return values to prevent UnboundLocalError
    world_cup_overview_df, matches_df, players_df = None, None, None
    all_teams = []

    try:
        if os.path.exists(world_cup_overview_path):
            world_cup_overview_df = pd.read_csv(world_cup_overview_path, encoding="utf-8-sig")
            world_cup_overview_df = clean_data_names(world_cup_overview_df)
            world_cup_overview_df["Year"] = pd.to_numeric(world_cup_overview_df["Year"], errors='coerce').dropna().astype(int)
            print(f"Loaded WorldCups.csv with {len(world_cup_overview_df)} rows.")
        else:
            print(f"Error: WorldCups.csv not found at {world_cup_overview_path}")

        if os.path.exists(matches_path):
            matches_df = pd.read_csv(matches_path, encoding="utf-8-sig")
            matches_df.drop_duplicates(subset='MatchID', keep='first', inplace=True)
            matches_df = clean_data_names(matches_df)
            matches_df["Year"] = pd.to_numeric(matches_df["Year"], errors='coerce').fillna(-1).astype(int)
            matches_df["Datetime"] = pd.to_datetime(matches_df["Datetime"], errors='coerce')
            matches_df["Home Team Goals"] = pd.to_numeric(matches_df["Home Team Goals"], errors='coerce').fillna(0).astype(int)
            matches_df["Away Team Goals"] = pd.to_numeric(matches_df["Away Team Goals"], errors='coerce').fillna(0).astype(int)
            all_teams = pd.concat([matches_df['Home Team Name'], matches_df['Away Team Name']]).dropna().unique()
            print(f"Loaded WorldCupMatches.csv with {len(matches_df)} rows.")
        else:
            print(f"Error: WorldCupMatches.csv not found at {matches_path}")

        if os.path.exists(players_path):
            players_df = pd.read_csv(players_path, encoding="utf-8-sig")
            players_df = clean_data_names(players_df)
            print(f"Loaded WorldCupPlayers.csv with {len(players_df)} rows.")
        else:
            print(f"Error: WorldCupPlayers.csv not found at {players_path}")
            
    except Exception as e:
        print(f"An error occurred while loading World Cup data: {e}")
        return None, None, None, None

    return world_cup_overview_df, matches_df, players_df, all_teams

# --- CONTINENT HELPER (PRESERVED) ---
COUNTRY_TO_CONTINENT = {
    'Uruguay': 'South America', 'Italy': 'Europe', 'France': 'Europe',
    'Brazil': 'South America', 'Switzerland': 'Europe', 'Sweden': 'Europe',
    'Chile': 'South America', 'England': 'Europe', 'Mexico': 'North America',
    'Germany': 'Europe', 'Germany FR': 'Europe', 'West Germany': 'Europe', # Handle historical hosts
    'Argentina': 'South America', 'Spain': 'Europe', 'USA': 'North America',
    'Korea/Japan': 'Asia', 'South Africa': 'Africa', 'Russia': 'Europe', 'Qatar': 'Asia'
}

def add_continent_column(df: pd.DataFrame) -> pd.DataFrame:
    df['Continent'] = df['Country'].map(COUNTRY_TO_CONTINENT)
    return df