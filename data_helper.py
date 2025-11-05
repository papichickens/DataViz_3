import pandas as pd
import os

###
# --------- Flag helpers (paste near top of callbacks.py) -------------
try:
    import pycountry
except Exception:
    pycountry = None

# small manual override map for names that fail ISO lookup
MANUAL_NAME_TO_ISO2 = {
    # --- Critical Fixes & Common Names ---
    "Germany": "de",
    "USA": "us",
    "Republic of Ireland": "ie",
    "Korea Republic": "kr",          # Official FIFA name for South Korea
    "South Korea": "kr",
    "Korea DPR": "kp",               # Official FIFA name for North Korea
    "North Korea": "kp",
    "IR Iran": "ir",                 # Official FIFA name for Iran

    # --- UK Home Nations (use special sub-country codes for better flags) ---
    "England": "gb-eng",
    "Scotland": "gb-sct",
    "Wales": "gb-wls",
    "Northern Ireland": "gb-nir",

    # --- Historic or Former Country Names (mapped to modern equivalent) ---
    "Germany FR": "de",              # West Germany
    "Germany DR": "de",              # East Germany (renders same German flag)
    "Soviet Union": "ru",            # Fallback to Russia
    "Yugoslavia": "rs",              # Fallback to Serbia
    "Czechoslovakia": "cz",          # Fallback to Czech Republic
    "Dutch East Indies": "id",       # Historical name for Indonesia
    "Serbia and Montenegro": "rs",   # Fallback to Serbia
    "Zaire": "cd",                   # Now DR Congo

    # --- Standard Country Names (Alphabetical) ---
    "Algeria": "dz",
    "Angola": "ao",
    "Argentina": "ar",
    "Australia": "au",
    "Austria": "at",
    "Belgium": "be",
    "Bolivia": "bo",
    "Bosnia and Herzegovina": "ba",
    "Brazil": "br",
    "Bulgaria": "bg",
    "Cameroon": "cm",
    "Canada": "ca",
    "Chile": "cl",
    "China PR": "cn",
    "Colombia": "co",
    "Costa Rica": "cr",
    "Cote d'Ivoire": "ci",           # Ivory Coast
    "Côte d'Ivoire": "ci",
    "Croatia": "hr",
    "Cuba": "cu",
    "Czech Republic": "cz",
    "Denmark": "dk",
    "Ecuador": "ec",
    "Egypt": "eg",
    "El Salvador": "sv",
    "France": "fr",
    "Ghana": "gh",
    "Greece": "gr",
    "Haiti": "ht",
    "Honduras": "hn",
    "Hungary": "hu",
    "Iceland": "is",
    "Iran": "ir",
    "Iraq": "iq",
    "Israel": "il",
    "Italy": "it",
    "Jamaica": "jm",
    "Japan": "jp",
    "Kuwait": "kw",
    "Mexico": "mx",
    "Morocco": "ma",
    "Netherlands": "nl",
    "New Zealand": "nz",
    "Nigeria": "ng",
    "Norway": "no",
    "Paraguay": "py",
    "Peru": "pe",
    "Poland": "pl",
    "Portugal": "pt",
    "Romania": "ro",
    "Russia": "ru",
    "Saudi Arabia": "sa",
    "Senegal": "sn",
    "Serbia": "rs",
    "Slovakia": "sk",
    "Slovenia": "si",
    "South Africa": "za",
    "Spain": "es",
    "Sweden": "se",
    "Switzerland": "ch",
    "Togo": "tg",
    "Trinidad and Tobago": "tt",
    "Tunisia": "tn",
    "Turkey": "tr",
    "Ukraine": "ua",
    "United Arab Emirates": "ae",
    "Uruguay": "uy",
}


def country_to_iso2(name: str) -> str | None:
    """
    Converts a country name to its ISO2 code using a reliable manual dictionary.
    Returns e.g., 'fr' for France, or None if the name is not found.
    """
    if not name or not isinstance(name, str):
        return None
    
    iso_code = MANUAL_NAME_TO_ISO2.get(name.strip())
    
    return iso_code.lower() if iso_code else None

def get_flag_url_by_iso(iso2: str) -> str:
    """Return a remote flag CDN URL for a given iso2 code (lowercase)."""
    if not iso2:
        return ""
    return f"https://flagcdn.com/w320/{iso2}.png"

def get_flag_url(country_name: str) -> str:
    """Convenience function: gets the full flag URL for a country name."""
    iso2 = country_to_iso2(country_name)
    if not iso2:
        return ""
    return get_flag_url_by_iso(iso2)
# ---------------------------------------------------------------------


###

def load_world_cup_data(folder_name="data"):
    """
    Loads World Cup overview, matches, and players data from CSV files.

    Args:
        folder_name (str): The name of the folder where the CSV files are located.

    Returns:
        tuple: A tuple containing (world_cup_overview_df, matches_df, players_df)
               or (None, None, None) if files cannot be loaded.
    """
    base_path = os.path.join(os.getcwd(), folder_name)
    
    world_cup_overview_path = os.path.join(base_path, "WorldCups.csv")
    matches_path = os.path.join(base_path, "WorldCupMatches.csv")
    players_path = os.path.join(base_path, "WorldCupPlayers.csv")

    world_cup_overview_df = None
    matches_df = None
    players_df = None

    try:
        if os.path.exists(world_cup_overview_path):
            world_cup_overview_df = pd.read_csv(world_cup_overview_path)
            # Apply corrections to overview data
            world_cup_overview_df = clean_data_names(world_cup_overview_df)
            # Basic cleaning/type conversion for overview data
            world_cup_overview_df["Year"] = pd.to_numeric(world_cup_overview_df["Year"], errors='coerce')
            world_cup_overview_df = world_cup_overview_df.dropna(subset=['Year'])
            world_cup_overview_df["Year"] = world_cup_overview_df["Year"].astype(int)
            print(f"Loaded WorldCups.csv with {len(world_cup_overview_df)} rows.")
        else:
            print(f"Error: WorldCups.csv not found at {world_cup_overview_path}")

        if os.path.exists(matches_path):
            matches_df = pd.read_csv(matches_path)
            # Apply corrections to matches data
            matches_df = clean_data_names(matches_df)
            # Basic cleaning/type conversion for matches data
            matches_df["Year"] = pd.to_numeric(matches_df["Year"], errors='coerce').fillna(-1).astype(int)
            matches_df["Datetime"] = pd.to_datetime(matches_df["Datetime"], errors='coerce')
            matches_df["Home Team Goals"] = pd.to_numeric(matches_df["Home Team Goals"], errors='coerce').fillna(0).astype(int)
            matches_df["Away Team Goals"] = pd.to_numeric(matches_df["Away Team Goals"], errors='coerce').fillna(0).astype(int)
            print(f"Loaded WorldCupMatches.csv with {len(matches_df)} rows.")
        else:
            print(f"Error: WorldCupMatches.csv not found at {matches_path}")

        if os.path.exists(players_path):
            players_df = pd.read_csv(players_path)
            # Apply corrections to players data
            players_df = clean_data_names(players_df)
            print(f"Loaded WorldCupPlayers.csv with {len(players_df)} rows.")
        else:
            print(f"Error: WorldCupPlayers.csv not found at {players_path}")

    except Exception as e:
        print(f"An error occurred while loading World Cup data: {e}")
        return None, None, None

    return world_cup_overview_df, matches_df, players_df


def clean_data_names(df):
    """
    Clean up team names, stadium names, and other text that have encoding issues in the CSV files.
    """
    if df is None:
        return df
    
    # Manual corrections for known encoding issues
    corrections = {
        # Team name corrections
        'C�te d\'Ivoire': 'Côte d\'Ivoire',
        'rn">Bosnia and Herzegovina': 'Bosnia and Herzegovina',
        'rn">Trinidad and Tobago': 'Trinidad and Tobago',
        'rn">Serbia and Montenegro': 'Serbia and Montenegro', 
        'rn">Republic of Ireland': 'Republic of Ireland',
        'rn">United Arab Emirates': 'United Arab Emirates',
        
        # Stadium name corrections
        'Maracan� - Est�dio Jornalista M�rio Filho': 'Maracanã - Estádio Jornalista Mário Filho',
        'Est�dio Jornalista M�rio Filho': 'Estádio Jornalista Mário Filho',
        'Maracan�': 'Maracanã',
        'Stade V�lodrome': 'Stade Vélodrome',
        'Nou Camp - Estadio Le�n' : 'Nou Camp - Estadio León',
        'Estadio Jos� Mar�a Minella':'Estadio José María Minella',
        'Estadio Ol�mpico Chateau Carreras' : 'Estadio Olímpico Chateau Carreras',
        'Estadio Municipal de Bala�dos': 'Estadio Municipal de Balaídos',
        'Estadio Ol�mpico Universitario': 'Estadio Olímpico Universitario',
        
        # City name corrections
        'Malm�': 'Malmö',
        'Malmo': 'Malmö', 
        'Norrk�Ping' : 'Norrköping',
        'D�Sseldorf ': 'Düsseldorf',
        'La Coru�A ': 'A Coruña'


        # Add more corrections as you find them
    }
    
    # Identify columns that likely contain text with special characters
    text_columns = []
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['team', 'country', 'winner', 'runner', 'host', 'player', 'stadium', 'city', 'referee', 'assistant']):
            text_columns.append(col)
    
    # Apply corrections to all text-related columns
    for col in text_columns:
        if col in df.columns:
            # Convert to string type to avoid issues with NaN values
            df[col] = df[col].astype(str)
            for wrong, correct in corrections.items():
                df[col] = df[col].str.replace(wrong, correct)
    
    return df


# Example usage if data_helper.py is run directly
if __name__ == "__main__":
    overview, matches, players = load_world_cup_data()

    
    if players is not None:
        print("\nWorld Cup Players Data Head:")
        print(players.head())


COUNTRY_TO_CONTINENT = {
    'Uruguay': 'South America',
    'Italy': 'Europe',
    'France': 'Europe',
    'Brazil': 'South America',
    'Switzerland': 'Europe',
    'Sweden': 'Europe',
    'Chile': 'South America',
    'England': 'Europe',
    'Mexico': 'North America',
    'Germany': 'Europe',
    'Germany FR': 'Europe', # For old data
    'Argentina': 'South America',
    'Spain': 'Europe',
    'USA': 'North America',
    'Korea/Japan': 'Asia',
    'South Africa': 'Africa',
    # Add any other host countries if they are missing from this list
}

def add_continent_column(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a 'Continent' column to the dataframe based on the 'Country' (Host) column."""
    df['Continent'] = df['Country'].map(COUNTRY_TO_CONTINENT)
    return df
