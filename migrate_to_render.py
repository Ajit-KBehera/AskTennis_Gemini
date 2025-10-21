#!/usr/bin/env python3
"""
Tennis Database Migration to Render PostgreSQL using pgloader
Fast, direct SQLite to PostgreSQL migration
"""

import os
import subprocess
import tempfile
from dotenv import load_dotenv

load_dotenv()

def create_pgloader_script():
    """
    Create pgloader script for SQLite to PostgreSQL migration
    """
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found!")
        return None
    
    # Parse DATABASE_URL to extract components
    if database_url.startswith('postgresql://'):
        # Remove postgresql:// prefix
        url_part = database_url[13:]
    elif database_url.startswith('postgres://'):
        # Remove postgres:// prefix  
        url_part = database_url[11:]
    else:
        print("❌ Invalid DATABASE_URL format!")
        return None
    
    # Split into components
    if '@' in url_part:
        auth_part, host_part = url_part.split('@', 1)
        if ':' in auth_part:
            username, password = auth_part.split(':', 1)
        else:
            username = auth_part
            password = ""
    else:
        print("❌ Could not parse DATABASE_URL!")
        return None
    
    if '/' in host_part:
        host_port, database = host_part.split('/', 1)
        if ':' in host_port:
            host, port = host_port.split(':', 1)
        else:
            host = host_port
            port = "5432"  # Default PostgreSQL port
    else:
        print("❌ Could not parse host/database from DATABASE_URL!")
        return None
    
    # Get absolute path to SQLite database
    sqlite_path = os.path.abspath('tennis_data_render.db')
    
    # Create pgloader script with SSL support
    pgloader_script = f"""
LOAD DATABASE
    FROM sqlite://{sqlite_path}
    INTO postgresql://{username}:{password}@{host}:{port}/{database}?sslmode=require
    
WITH include drop, create tables, create indexes, reset sequences

SET work_mem to '256MB', maintenance_work_mem to '512 MB'

CAST type datetime to timestamptz drop default drop not null using zero-dates-to-null,
     type date to date drop default drop not null using zero-dates-to-null,
     type integer to bigint,
     type text to text drop not null,
     type varchar to text drop not null

BEFORE LOAD DO
    $$ DROP TABLE IF EXISTS matches CASCADE; $$,
    $$ DROP TABLE IF EXISTS players CASCADE; $$,
    $$ DROP TABLE IF EXISTS doubles_matches CASCADE; $$;
"""
    
    return pgloader_script

def migrate_to_render():
    """
    Migrate tennis database using pgloader
    """
    print("🚀 Starting pgloader migration...")
    
    # Check if SQLite database exists
    if not os.path.exists('tennis_data_render.db'):
        print("❌ tennis_data_render.db not found!")
        return
    
    # Create pgloader script
    script_content = create_pgloader_script()
    if not script_content:
        return
    
    # Write script to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.load', delete=False) as f:
        f.write(script_content)
        script_path = f.name
    
    try:
        print("📝 Created pgloader script")
        print("🔄 Running pgloader migration...")
        print("⏱️  This should be much faster than Python migration!")
        
        # Run pgloader with verbose output
        print("🔄 Starting pgloader migration...")
        print("📊 Database size: 462MB")
        print("⏱️  Expected time: 1-3 minutes")
        
        # Run pgloader with real-time output
        process = subprocess.Popen(
            ['pgloader', '--verbose', script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Monitor progress with timeout
        try:
            stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout
            result = subprocess.CompletedProcess(['pgloader'], process.returncode, stdout, stderr)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            result = subprocess.CompletedProcess(['pgloader'], -1, stdout, stderr)
        
        if result.returncode == 0:
            print("✅ pgloader migration completed successfully!")
            print("📊 Migration output:")
            print(result.stdout)
        else:
            print("❌ pgloader migration failed!")
            print("Error output:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Migration timed out after 10 minutes")
    except FileNotFoundError:
        print("❌ pgloader not found! Please install pgloader:")
        print("   brew install pgloader  # macOS")
        print("   apt-get install pgloader  # Ubuntu")
        print("   Then run this script again")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        # Clean up temporary file
        try:
            os.unlink(script_path)
        except:
            pass

if __name__ == "__main__":
    migrate_to_render()
