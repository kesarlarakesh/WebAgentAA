from dotenv import load_dotenv
import asyncio
from llm_config import get_llm
from sheets_reader import get_all_tasks
from task_runner_utils import run_task, print_summary
from report_generator import generate_html_report
import os
import config

load_dotenv()

async def main():
    llm = get_llm()
    
    # Read configuration from config.py (which reads from .env with defaults)
    spreadsheet_id = config.SPREADSHEET_ID
    
    if spreadsheet_id:
        # Get first active task from Google Sheets (reads sheet_name and start_row from .env)
        tasks = get_all_tasks(spreadsheet_id, active_only=True)
        
        if not tasks:
            print("❌ No active tasks found in Google Sheet")
            print("Make sure you have at least one task with 'Active' column set to 'yes'")
            return
        
        # Run the first active task
        task_info = tasks[0]
        
        print(f"\n{'='*60}")
        print(f"📋 Scenario: {task_info['scenario_name']}")
        print(f"📂 Category: {task_info['category']}")
        print(f"⭐ Priority: {task_info['priority']}")
        print(f"{'='*60}\n")
        
        print(f"🎯 Task: {task_info['prompt_text']}\n")
        
        # Use the common task runner with proper cleanup
        result = await run_task(llm, task_info, 1)
        
        # Print summary
        print_summary([result], title="Single Task Execution Complete")
        
        # Generate HTML report
        print("\n📊 Generating HTML report...")
        report_path = generate_html_report([result])
        print(f"✅ Report generated: {os.path.abspath(report_path)}")
        print(f"📂 Open in browser: file:///{os.path.abspath(report_path).replace(chr(92), '/')}")
    else:
        print("❌ SPREADSHEET_ID not found in .env file")
        print("Please configure Google Sheets integration first.")

if __name__ == "__main__":
    asyncio.run(main())
