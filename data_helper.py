import pandas as pd
import os

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
        
        # Stadium name corrections
        'Maracan� - Est�dio Jornalista M�rio Filho': 'Maracanã - Estádio Jornalista Mário Filho',
        'Est�dio Jornalista M�rio Filho': 'Estádio Jornalista Mário Filho',
        'Maracan�': 'Maracanã',
        'Stade V�lodrome': 'Stade Vélodrome',
        
        # City name corrections
        'Malm�': 'Malmö',
        'Malmo': 'Malmö', 
        'Norrk�Ping' : 'Norrköping',

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
    
    if overview is not None:
        print("\nWorld Cup Overview Data Head:")
        print(overview.head())
        # Check for any remaining encoding issues
        print("\nChecking for names with special characters in overview:")
        text_cols = [col for col in overview.columns if any(keyword in col.lower() for keyword in ['team', 'country', 'winner', 'stadium'])]
        for col in text_cols:
            unique_values = overview[col].unique()
            problematic_values = [val for val in unique_values if any(char in val for char in ['�', 'rn">'])]
            if problematic_values:
                print(f"Problematic values in {col}: {problematic_values}")
    
    if matches is not None:
        print("\nWorld Cup Matches Data Head:")
        print(matches.head())
        # Check for any remaining encoding issues in matches
        print("\nChecking for names with special characters in matches:")
        text_cols = [col for col in matches.columns if any(keyword in col.lower() for keyword in ['team', 'stadium', 'city', 'referee'])]
        for col in text_cols:
            unique_values = matches[col].unique()
            problematic_values = [val for val in unique_values if any(char in val for char in ['�', 'rn">'])]
            if problematic_values:
                print(f"Problematic values in {col}: {problematic_values}")
    
    if players is not None:
        print("\nWorld Cup Players Data Head:")
        print(players.head())