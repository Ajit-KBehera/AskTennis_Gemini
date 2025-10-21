#!/usr/bin/env python3
"""
Tennis Database Migration to Render PostgreSQL
Migrates essential tennis data optimized for free tier storage limits
"""

import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import time

load_dotenv()

def migrate_to_render():
    """
    Migrate essential tennis data to Render PostgreSQL
    Optimized for free tier storage limits
    """
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found!")
        return
    
    try:
        print("🔍 Testing database connections...")
        
        # Connect to SQLite source
        sqlite_conn = sqlite3.connect('tennis_data.db')
        print("✅ SQLite connection successful")
        
        # Connect to Render PostgreSQL
        postgres_engine = create_engine(database_url)
        postgres_conn = postgres_engine.connect()
        print("✅ PostgreSQL connection successful")
        
        print("🚀 Starting selective migration (essential data only)...")
        start_time = time.time()
        
        # Migrate only essential tables with data filtering
        essential_tables = {
            'matches': "SELECT * FROM matches WHERE event_year >= 2000 LIMIT 100000",  # Recent matches only
            'players': "SELECT * FROM players LIMIT 5000",  # Top players only
            'rankings': "SELECT * FROM rankings WHERE ranking_date >= '2020-01-01' LIMIT 50000"  # Recent rankings only
        }
        
        total_rows = 0
        
        for table_name, query in essential_tables.items():
            print(f"\n🔄 Migrating {table_name} (filtered)...")
            
            # Read filtered data
            df = pd.read_sql_query(query, sqlite_conn)
            row_count = len(df)
            total_rows += row_count
            
            print(f"   📊 Rows to migrate: {row_count:,}")
            
            # Write to PostgreSQL
            df.to_sql(table_name, postgres_conn, if_exists='replace', index=False, method='multi')
            print(f"   ✅ Successfully migrated {row_count:,} rows")
        
        # Close connections
        sqlite_conn.close()
        postgres_conn.close()
        
        # Calculate total time
        end_time = time.time()
        total_duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 SELECTIVE MIGRATION COMPLETED!")
        print("=" * 60)
        print(f"📊 Total rows migrated: {total_rows:,}")
        print(f"⏱️  Migration time: {total_duration:.1f} seconds")
        print("💾 Reduced data size for free tier compatibility")
        print("🔗 Your tennis database is now available on Render!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    migrate_to_render()
