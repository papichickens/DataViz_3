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
    "Côte d'Ivoire": "ci",
    "Cote d'Ivoire": "ci",
    "Ivory Coast": "ci",
    "Bosnia and Herzegovina": "ba",
    "Trinidad and Tobago": "tt",
    "Serbia and Montenegro": "rs",
    "Republic of Ireland": "ie",
    "Malmö": "se",
    "England": "gb",
    "Korea Republic": "kr",
    "South Korea": "kr",
    "Turkey": "tr",
    "Yugoslavia": "rs",       # historic ISO2 (FlagCDN may not have it, fallback to Serbia "rs")
    "Dutch East Indies": "id", # Indonesia
    "Wales": "gb-wls",         # subregion for UK/Wales
    "Korea DPR": "kp",
    "Germany FR": "de",
    "Scotland": "gb-sct",
    # Optional: add "Germany", "East Germany", "West Germany" etc.
}

def country_to_iso2(name: str) -> str | None:
    """Try to convert a country name to ISO2 (lowercase). Returns e.g. 'fr' or None."""
    if not name or not isinstance(name, str):
        return None
    # clean a bit
    n = name.strip()
    # try manual map first
    if n in MANUAL_NAME_TO_ISO2:
        return MANUAL_NAME_TO_ISO2[n].lower()
    # try pycountry if available
    if pycountry:
        try:
            # pycountry search might fail for some names, try exact then common name search
            country = pycountry.countries.get(name=n)
            if country:
                return country.alpha_2.lower()
            # try lookup by common name or partial match
            # first try by official_name
            for c in pycountry.countries:
                if hasattr(c, 'common_name') and c.common_name.lower() == n.lower():
                    return c.alpha_2.lower()
                if c.name.lower() == n.lower():
                    return c.alpha_2.lower()
            # last resort: fuzzy contains
            for c in pycountry.countries:
                if n.lower() in c.name.lower():
                    return c.alpha_2.lower()
        except Exception:
            pass
    # fallback: try simple heuristics (take first two letters)
    # (not reliable but better than nothing)
    safe = ''.join(ch for ch in n if ch.isalpha())
    if len(safe) >= 2:
        return safe[:2].lower()
    return None

def get_flag_url_by_iso(iso2: str) -> str:
    """Return a remote flag CDN URL for a given iso2 code (lowercase)."""
    if not iso2:
        return ""
    # FlagCDN format: https://flagcdn.com/w320/{iso2}.png (iso2 lowercase)
    return f"https://flagcdn.com/w320/{iso2}.png"

def get_flag_url(country_name: str) -> str:
    """Convenience: get flag url for a country name, or '' if unknown."""
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