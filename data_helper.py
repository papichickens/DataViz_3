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
            # Basic cleaning/type conversion for overview data
            world_cup_overview_df["Year"] = pd.to_numeric(world_cup_overview_df["Year"], errors='coerce')
            world_cup_overview_df = world_cup_overview_df.dropna(subset=['Year'])
            world_cup_overview_df["Year"] = world_cup_overview_df["Year"].astype(int)
            print(f"Loaded WorldCup.csv with {len(world_cup_overview_df)} rows.")
        else:
            print(f"Error: WorldCup.csv not found at {world_cup_overview_path}")

        if os.path.exists(matches_path):
            matches_df = pd.read_csv(matches_path)
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
            print(f"Loaded WorldCupPlayers.csv with {len(players_df)} rows.")
        else:
            print(f"Error: WorldCupPlayers.csv not found at {players_path}")

    except Exception as e:
        print(f"An error occurred while loading World Cup data: {e}")
        return None, None, None

    return world_cup_overview_df, matches_df, players_df

# Example usage if data_helper.py is run directly
if __name__ == "__main__":
    overview, matches, players = load_world_cup_data()
    if overview is not None:
        print("\nWorld Cup Overview Data Head:")
        print(overview.head())
    if matches is not None:
        print("\nWorld Cup Matches Data Head:")
        print(matches.head())
    if players is not None:
        print("\nWorld Cup Players Data Head:")
        print(players.head())
