import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
import config

load_dotenv()

def _get_sheet_client(spreadsheet_id, sheet_name):
    """Helper function to authenticate and get sheet client"""
    creds_file = config.GOOGLE_SHEETS_CREDENTIALS
    
    if not creds_file:
        raise ValueError("GOOGLE_SHEETS_CREDENTIALS not found in .env file")
    
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = Credentials.from_service_account_file(creds_file, scopes=scope)
    client = gspread.authorize(creds)
    
    spreadsheet = client.open_by_key(spreadsheet_id)
    sheet = spreadsheet.worksheet(sheet_name)
    
    return sheet


def get_all_tasks(spreadsheet_id, sheet_name=None, start_row=None, active_only=True):
    """
    Read all tasks from Google Sheets.
    
    Args:
        spreadsheet_id: The ID of your Google Spreadsheet
        sheet_name: Name of the sheet tab (reads from .env if not provided)
        start_row: Starting row for data (reads from .env if not provided)
        active_only: Only return tasks where Active = "yes" (default: True)
    
    Returns:
        list: List of task dictionaries with scenario_name, prompt_text, category, priority, active
    
    Sheet Structure (Row 1 = Headers):
        Column A: Scenario Name
        Column B: Prompt Text
        Column C: Category
        Column D: Priority
        Column E: Active (yes/no)
    """
    
    # Read from config.py if not provided
    if sheet_name is None:
        sheet_name = config.SHEET_NAME
    if start_row is None:
        start_row = config.START_ROW
    
    sheet = _get_sheet_client(spreadsheet_id, sheet_name)
    
    # Get all rows starting from start_row
    all_rows = sheet.get_all_values()[start_row-1:]
    
    tasks = []
    for row_data in all_rows:
        # Skip empty rows
        if not row_data or len(row_data) < 5:
            continue
        
        # Skip rows with empty prompt text
        if not row_data[1].strip():
            continue
        
        task_info = {
            'scenario_name': row_data[0],
            'prompt_text': row_data[1],
            'category': row_data[2],
            'priority': row_data[3],
            'active': row_data[4].lower() == 'yes'
        }
        
        # Filter by active status if requested
        if active_only and not task_info['active']:
            continue
        
        tasks.append(task_info)
    
    return tasks


def get_tasks_by_category(spreadsheet_id, category, sheet_name=None, active_only=True):
    """
    Get all tasks filtered by category.
    
    Args:
        spreadsheet_id: The ID of your Google Spreadsheet
        category: Category to filter by (e.g., "Smoke Test", "Regression")
        sheet_name: Name of the sheet tab (reads from .env if not provided)
        active_only: Only return active tasks
    
    Returns:
        list: Filtered list of tasks
    """
    all_tasks = get_all_tasks(spreadsheet_id, sheet_name=sheet_name, active_only=active_only)
    return [task for task in all_tasks if task['category'].lower() == category.lower()]


def get_tasks_by_priority(spreadsheet_id, priority, sheet_name=None, active_only=True):
    """
    Get all tasks filtered by priority.
    
    Args:
        spreadsheet_id: The ID of your Google Spreadsheet
        priority: Priority to filter by (e.g., "High", "Medium", "Low")
        sheet_name: Name of the sheet tab (reads from .env if not provided)
        active_only: Only return active tasks
    
    Returns:
        list: Filtered list of tasks
    """
    all_tasks = get_all_tasks(spreadsheet_id, sheet_name=sheet_name, active_only=active_only)
    return [task for task in all_tasks if task['priority'].lower() == priority.lower()]
