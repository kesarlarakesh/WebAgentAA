"""
Configuration management for WebAgentAA
Loads settings from environment variables with sensible defaults
"""
import os
from typing import Literal

# Google API Configuration (still read from environment for security)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS', './google-sheets-credentials.json')

# Google Sheets Configuration (hardcoded - modify here)
SPREADSHEET_ID = '1D6vrChZ87E06a-wBcVqe9PJk48UpboDQxQb22OlxouY' 
SHEET_NAME = 'Tasks'
START_ROW = 2

# Execution Configuration (hardcoded)
EXECUTION_MODE = 'sequential'  # 'sequential' or 'parallel'
TASK_DELAY = 5  # Delay between tasks in seconds
MAX_PARALLEL_AGENTS = 3

# Task Filtering Configuration (hardcoded)
RUN_PRIORITY = 'High'  # 'High', 'Medium', 'Low', or 'All'
RUN_CATEGORY = 'Hotels'  # Empty string means all categories

# Browser Configuration (hardcoded)
HEADLESS_BROWSER = True
BROWSER_TIMEOUT = int(os.getenv('BROWSER_TIMEOUT', '300000'))  # 5 minutes default

# Report Configuration
REPORTS_DIR = os.getenv('REPORTS_DIR', './reports')

# Validation
def validate_config():
    """Validate required configuration settings"""
    errors = []
    
    if not GOOGLE_API_KEY:
        errors.append("GOOGLE_API_KEY is required in .env file")
    
    if not SPREADSHEET_ID:
        errors.append("SPREADSHEET_ID is required in config.py")
    
    if not os.path.exists(GOOGLE_SHEETS_CREDENTIALS):
        errors.append(f"Google Sheets credentials file not found: {GOOGLE_SHEETS_CREDENTIALS}")
    
    if EXECUTION_MODE not in ['sequential', 'parallel']:
        errors.append(f"Invalid EXECUTION_MODE: {EXECUTION_MODE}. Must be 'sequential' or 'parallel'")
    
    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True

def print_config(hide_secrets=True):
    """Print current configuration (useful for debugging)"""
    print("\n" + "="*60)
    print("📋 Current Configuration")
    print("="*60)
    
    # Google Sheets
    print("\n🔷 Google Sheets:")
    print(f"  SPREADSHEET_ID: {SPREADSHEET_ID}")
    print(f"  SHEET_NAME: {SHEET_NAME}")
    print(f"  START_ROW: {START_ROW}")
    
    # Execution
    print("\n🔷 Execution:")
    print(f"  EXECUTION_MODE: {EXECUTION_MODE}")
    print(f"  TASK_DELAY: {TASK_DELAY}s")
    print(f"  MAX_PARALLEL_AGENTS: {MAX_PARALLEL_AGENTS}")
    
    # Filtering
    print("\n🔷 Task Filtering:")
    print(f"  RUN_PRIORITY: {RUN_PRIORITY}")
    print(f"  RUN_CATEGORY: {RUN_CATEGORY or 'All'}")
    
    # Browser
    print("\n🔷 Browser:")
    print(f"  HEADLESS_BROWSER: {HEADLESS_BROWSER}")
    print(f"  BROWSER_TIMEOUT: {BROWSER_TIMEOUT}ms")
    
    # Reports
    print("\n🔷 Reports:")
    print(f"  REPORTS_DIR: {REPORTS_DIR}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    # Allow running this file to check configuration
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        validate_config()
        print("✅ Configuration is valid!")
        print_config(hide_secrets=True)
    except ValueError as e:
        print(f"❌ {e}")
