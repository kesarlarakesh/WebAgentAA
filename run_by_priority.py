from dotenv import load_dotenv
import asyncio
from llm_config import get_llm
from sheets_reader import get_tasks_by_priority
from task_runner_utils import run_tasks_sequential, run_tasks_parallel, print_summary
from report_generator import generate_html_report, save_report_index
import os

load_dotenv()


async def main():
    llm = get_llm()
    
    # Read configuration from .env
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    priority = os.getenv('RUN_PRIORITY', 'High')
    execution_mode = os.getenv('EXECUTION_MODE', 'sequential').lower()
    task_delay = int(os.getenv('TASK_DELAY', '5'))
    
    if not spreadsheet_id:
        print("❌ SPREADSHEET_ID not found in .env file")
        return
    
    if not priority:
        print("❌ RUN_PRIORITY not found in .env file")
        print("Please add RUN_PRIORITY=High (or Medium/Low) to your .env file")
        return
    
    try:
        # Get tasks filtered by priority (reads sheet_name from .env)
        tasks = get_tasks_by_priority(spreadsheet_id, priority, active_only=True)
        
        if not tasks:
            print(f"❌ No active tasks found for priority: '{priority}'")
            return
        
        print(f"\n{'='*70}")
        print(f"⭐ Running Tests with Priority: {priority}")
        print(f"{'='*70}")
        print(f"Total Tasks: {len(tasks)}")
        print(f"Execution Mode: {execution_mode.upper()}")
        print(f"{'='*70}\n")
        
        # Display task summary
        for i, task in enumerate(tasks, 1):
            print(f"{i}. [{task['category']}] {task['scenario_name']}")
        
        print(f"\n{'='*70}\n")
        
        # Run tasks based on execution mode
        if execution_mode == 'parallel':
            results = await run_tasks_parallel(llm, tasks)
        else:
            results = await run_tasks_sequential(llm, tasks, task_delay)
        
        # Print summary
        print_summary(results, title=f"Priority '{priority}' Tests Complete")
        
        # Generate HTML report
        print("\n📊 Generating HTML report...")
        report_path = generate_html_report(results)
        save_report_index(report_path)
        print(f"✅ Report generated: {os.path.abspath(report_path)}")
        print(f"📂 Open in browser: file:///{os.path.abspath(report_path).replace(chr(92), '/')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
