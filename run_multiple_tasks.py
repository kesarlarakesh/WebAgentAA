from dotenv import load_dotenv
import asyncio
from llm_config import get_llm
from sheets_reader import get_all_tasks
from task_runner_utils import run_tasks_sequential, run_tasks_parallel, print_summary
from report_generator import generate_html_report
import os
import config

load_dotenv()


async def main():
    llm = get_llm()
    
    # Read configuration from config.py
    spreadsheet_id = config.SPREADSHEET_ID
    execution_mode = config.EXECUTION_MODE.lower()
    task_delay = config.TASK_DELAY
    
    if not spreadsheet_id:
        print("❌ SPREADSHEET_ID not found in config.py")
        print("Please configure Google Sheets integration in config.py first.")
        return
    
    try:
        # Get all active tasks from Google Sheets (reads sheet_name and start_row from .env)
        tasks = get_all_tasks(spreadsheet_id, active_only=True)
        
        if not tasks:
            print("❌ No active tasks found in Google Sheet")
            print("Make sure you have tasks with 'Active' column set to 'yes'")
            return
        
        print(f"\n{'='*70}")
        print(f"📊 Test Execution Summary")
        print(f"{'='*70}")
        print(f"Total Active Tasks: {len(tasks)}")
        print(f"Execution Mode: {execution_mode.upper()}")
        print(f"{'='*70}\n")
        
        # Display task summary
        for i, task in enumerate(tasks, 1):
            print(f"{i}. [{task['priority']}] {task['scenario_name']} ({task['category']})")
        
        print(f"\n{'='*70}\n")
        
        # Run tasks based on execution mode
        if execution_mode == 'parallel':
            results = await run_tasks_parallel(llm, tasks)
        else:
            results = await run_tasks_sequential(llm, tasks, task_delay)
        
        # Print summary
        print_summary(results, title="Test Execution Complete")
        
        # Generate HTML report
        print("\n📊 Generating HTML report...")
        report_path = generate_html_report(results)
        print(f"✅ Report generated: {os.path.abspath(report_path)}")
        print(f"📂 Open in browser: file:///{os.path.abspath(report_path).replace(chr(92), '/')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
