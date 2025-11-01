"""
Common utilities for running browser automation tasks
"""
import asyncio
import os
from browser_use import Agent, Browser
import config


async def run_task(llm, task_info, task_number):
    """
    Run a single task with the browser agent.
    
    Args:
        llm: The language model instance
        task_info: Dictionary containing task details (scenario_name, prompt_text, etc.)
        task_number: The task number for display purposes
    
    Returns:
        dict: Result dictionary with task_number, scenario, success status, and error if any
    """
    print(f"\n{'='*70}")
    print(f"🚀 Running Test #{task_number}")
    print(f"📋 Scenario: {task_info['scenario_name']}")
    print(f"📂 Category: {task_info['category']}")
    print(f"⭐ Priority: {task_info['priority']}")
    print(f"🎯 Task: {task_info['prompt_text']}")
    print(f"{'='*70}\n")
    
    browser = None
    logs = []
    agent_steps = []
    
    try:
        # Get browser configuration from config.py
        headless = config.HEADLESS_BROWSER
        
        # Create browser instance with configuration
        browser = Browser(headless=headless)
        
        # Create and run agent with configured browser
        agent = Agent(task=task_info['prompt_text'], llm=llm, browser=browser)
        
        # Capture execution start time
        from datetime import datetime
        start_time = datetime.now()
        logs.append(f"[{start_time.strftime('%H:%M:%S')}] Test execution started")
        logs.append(f"[{start_time.strftime('%H:%M:%S')}] Scenario: {task_info['scenario_name']}")
        logs.append(f"[{start_time.strftime('%H:%M:%S')}] Category: {task_info['category']}")
        logs.append(f"[{start_time.strftime('%H:%M:%S')}] Priority: {task_info['priority']}")
        
        result = await agent.run()
        
        # Capture agent history/steps after execution
        if result and hasattr(result, 'history'):
            history = result.history if not callable(result.history) else result.history()
            for i, step in enumerate(history, 1):
                step_info = {
                    'step_number': i,
                    'action': str(step.action) if hasattr(step, 'action') else 'N/A',
                    'result': str(step.result) if hasattr(step, 'result') else 'N/A',
                    'model_output': str(step.model_output) if hasattr(step, 'model_output') else ''
                }
                agent_steps.append(step_info)
                logs.append(f"[{start_time.strftime('%H:%M:%S')}] Step {i}: {step_info['action']}")
        
        # Capture execution end time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logs.append(f"[{end_time.strftime('%H:%M:%S')}] Test execution completed")
        logs.append(f"[{end_time.strftime('%H:%M:%S')}] Duration: {duration:.2f} seconds")
        
        # Check if the agent actually completed the task successfully
        task_success = result.is_done() if result else False
        
        if task_success:
            print(f"\n✅ Test #{task_number} ({task_info['scenario_name']}) completed successfully!\n")
            logs.append(f"[{end_time.strftime('%H:%M:%S')}] Status: PASSED")
        else:
            print(f"\n⚠️  Test #{task_number} ({task_info['scenario_name']}) finished but task was not completed.\n")
            if result and hasattr(result, 'final_result'):
                final_msg = result.final_result()
                print(f"Final result: {final_msg}\n")
                logs.append(f"[{end_time.strftime('%H:%M:%S')}] Final result: {final_msg}")
            logs.append(f"[{end_time.strftime('%H:%M:%S')}] Status: FAILED - Task not completed")
        
        return {
            'task_number': task_number,
            'scenario': task_info['scenario_name'],
            'category': task_info['category'],
            'priority': task_info['priority'],
            'prompt': task_info['prompt_text'],
            'success': task_success,
            'error': None if task_success else 'Task not completed',
            'logs': logs,
            'agent_steps': agent_steps
        }
    except Exception as e:
        from datetime import datetime
        error_time = datetime.now()
        logs.append(f"[{error_time.strftime('%H:%M:%S')}] ERROR: {str(e)}")
        logs.append(f"[{error_time.strftime('%H:%M:%S')}] Status: FAILED - Exception occurred")
        
        print(f"\n❌ Test #{task_number} ({task_info['scenario_name']}) failed: {str(e)}\n")
        return {
            'task_number': task_number,
            'scenario': task_info['scenario_name'],
            'category': task_info['category'],
            'priority': task_info['priority'],
            'prompt': task_info['prompt_text'],
            'success': False,
            'error': str(e),
            'logs': logs,
            'agent_steps': []
        }
    finally:
        # Properly close browser and cleanup resources
        if browser is not None:
            try:
                await browser.stop()
            except Exception as cleanup_error:
                print(f"⚠️  Warning: Browser cleanup error: {cleanup_error}")


async def run_tasks_sequential(llm, tasks, task_delay):
    """
    Run tasks sequentially (one after another).
    
    Args:
        llm: The language model instance
        tasks: List of task dictionaries
        task_delay: Delay in seconds between tasks
    
    Returns:
        list: List of result dictionaries
    """
    results = []
    
    for i, task in enumerate(tasks, 1):
        result = await run_task(llm, task, i)
        results.append(result)
        
        # Add delay between tasks
        if i < len(tasks):
            print(f"⏳ Waiting {task_delay} seconds before next task...")
            await asyncio.sleep(task_delay)
    
    return results


async def run_tasks_parallel(llm, tasks):
    """
    Run tasks in parallel with configurable concurrency limit.
    
    Args:
        llm: The language model instance
        tasks: List of task dictionaries
    
    Returns:
        list: List of result dictionaries
    """
    # Get max parallel agents configuration from config.py
    max_parallel = config.MAX_PARALLEL_AGENTS
    
    # If 0 or not set, run all tasks at once (unlimited)
    if max_parallel == 0 or max_parallel >= len(tasks):
        print("\n🚀 Launching all tasks in parallel...\n")
        task_coroutines = [run_task(llm, task, i) for i, task in enumerate(tasks, 1)]
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        return results
    
    # Run tasks in batches with limited concurrency
    print(f"\n🚀 Launching tasks in parallel (max {max_parallel} at a time)...\n")
    results = []
    
    for i in range(0, len(tasks), max_parallel):
        batch = tasks[i:i + max_parallel]
        batch_start = i + 1
        
        print(f"📦 Running batch {i//max_parallel + 1}: Tasks {batch_start} to {batch_start + len(batch) - 1}")
        
        # Create coroutines for this batch
        batch_coroutines = [
            run_task(llm, task, batch_start + j) 
            for j, task in enumerate(batch)
        ]
        
        # Run batch concurrently
        batch_results = await asyncio.gather(*batch_coroutines, return_exceptions=True)
        results.extend(batch_results)
        
        # Add a small delay between batches if there are more batches
        if i + max_parallel < len(tasks):
            print(f"\n⏳ Batch complete. Starting next batch in 2 seconds...\n")
            await asyncio.sleep(2)
    
    return results


def print_summary(results, title="Test Execution Complete"):
    """
    Print test execution summary.
    
    Args:
        results: List of result dictionaries
        title: Title for the summary
    """
    # Count passed and failed
    passed = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
    failed = sum(1 for r in results if isinstance(r, dict) and not r.get('success'))
    
    # Final summary
    print(f"\n{'='*70}")
    print(f"🎉 {title}!")
    print(f"{'='*70}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(results)}")
    print(f"{'='*70}\n")
    
    # Show failed tests details
    if failed > 0:
        print(f"\n{'='*70}")
        print(f"❌ Failed Tests Details:")
        print(f"{'='*70}")
        for r in results:
            if isinstance(r, dict) and not r.get('success'):
                print(f"  • Test #{r['task_number']}: {r['scenario']}")
                print(f"    Error: {r['error']}\n")
