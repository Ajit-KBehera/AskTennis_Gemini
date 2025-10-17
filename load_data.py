import pandas as pd
import sqlite3
import glob
import os

# --- Configuration ---
# NEW: A list of directories to process
DATA_DIRS = ["data/tennis_atp", "data/tennis_wta"]
# Years to include in the database
YEARS = list(range(2005, 2026)) 
# Database file name
DB_FILE = "tennis_data.db"

def load_data():
    """
    Reads both ATP and WTA match data for specified years, combines it,
    and loads it into a single SQLite database.
    """
    master_df_list = []
    
    # Loop through each data directory (ATP and WTA)
    for data_dir in DATA_DIRS:
        print(f"\n--- Processing directory: {data_dir} ---")
        all_files = glob.glob(os.path.join(data_dir, "*_matches_*.csv"))
        
        df_list = []
        for year in YEARS:
            # Construct the expected file path pattern for each year
            file_pattern = os.path.join(data_dir, f"*_matches_{year}.csv")
            matching_files = glob.glob(file_pattern)
            
            if matching_files:
                file_path = matching_files[0] # Use the first match found
                print(f"Reading {file_path}...")
                df = pd.read_csv(file_path, low_memory=False)
                df_list.append(df)
            else:
                # This is not an error, just means data for that year/tour doesn't exist
                pass

        if df_list:
            # Combine all dataframes for the current tour (ATP or WTA)
            tour_df = pd.concat(df_list, ignore_index=True)
            master_df_list.append(tour_df)

    if not master_df_list:
        print("No data found in any directory. Exiting.")
        return

    # Combine the ATP and WTA dataframes into one master dataframe
    matches_df = pd.concat(master_df_list, ignore_index=True)
    
    # Convert tourney_date to datetime objects for proper sorting/filtering
    matches_df['tourney_date'] = pd.to_datetime(matches_df['tourney_date'], format='%Y%m%d')

    print(f"\nTotal matches loaded (ATP & WTA): {len(matches_df)}")
    
    # --- Create SQLite Database ---
    conn = sqlite3.connect(DB_FILE)
    
    # Write the combined dataframe to a single table named 'matches'
    matches_df.to_sql('matches', conn, if_exists='replace', index=False)
    
    conn.close()
    
    print(f"\nSuccessfully created database '{DB_FILE}' with combined ATP and WTA data.")

if __name__ == '__main__':
    load_data()