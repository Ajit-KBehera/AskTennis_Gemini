import pandas as pd
import sqlite3
import glob
import os

# --- Configuration ---
# Path to the folder containing the ATP match CSVs
DATA_DIR = "data/tennis_atp"
# Years to include in the database
YEARS = [2023, 2024, 2025] 
# Database file name
DB_FILE = "tennis_data.db"

def load_data():
    """
    Reads ATP match data for specified years, combines it,
    and loads it into a SQLite database.
    """
    all_files = glob.glob(os.path.join(DATA_DIR, "atp_matches_*.csv"))
    
    df_list = []
    for year in YEARS:
        file_path = os.path.join(DATA_DIR, f"atp_matches_{year}.csv")
        if file_path in all_files:
            print(f"Reading {file_path}...")
            df = pd.read_csv(file_path)
            df_list.append(df)
        else:
            print(f"Warning: Could not find data for year {year}")

    if not df_list:
        print("No dataframes to concatenate. Exiting.")
        return

    # Combine all dataframes into one
    matches_df = pd.concat(df_list, ignore_index=True)
    
    # Convert tourney_date to datetime objects for proper sorting/filtering
    matches_df['tourney_date'] = pd.to_datetime(matches_df['tourney_date'], format='%Y%m%d')

    print(f"\nTotal matches loaded: {len(matches_df)}")
    
    # --- Create SQLite Database ---
    conn = sqlite3.connect(DB_FILE)
    
    # Write the dataframe to a table named 'matches'
    # 'if_exists='replace'' will drop the table if it already exists and create a new one.
    matches_df.to_sql('matches', conn, if_exists='replace', index=False)
    
    conn.close()
    
    print(f"\nSuccessfully created database '{DB_FILE}' with table 'matches'.")

if __name__ == '__main__':
    load_data()