"""
Common utilities for running browser automation tasks
"""
import asyncio
import os
import json
import re
from urllib.parse import quote
from browser_use import Agent, Browser
import config


def mask_sensitive_data(text):
    """
    Mask sensitive information in error messages and logs.
    
    Args:
        text: String that may contain sensitive data
        
    Returns:
        String with sensitive data masked
    """
    if not text:
        return text
    
    # Mask LambdaTest access key
    if config.LT_ACCESS_KEY and config.LT_ACCESS_KEY in text:
        text = text.replace(config.LT_ACCESS_KEY, '***MASKED_ACCESS_KEY***')
    
    # Mask access keys in JSON format
    text = re.sub(r'"accessKey"\s*:\s*"[^"]*"', '"accessKey": "***MASKED***"', text)
    
    # Mask API keys
    text = re.sub(r'(api[_-]?key|apikey)\s*[:=]\s*["\']?[\w-]{20,}["\']?', r'\1: ***MASKED***', text, flags=re.IGNORECASE)
    
    # Mask Google API keys
    if hasattr(config, 'GOOGLE_API_KEY') and config.GOOGLE_API_KEY and config.GOOGLE_API_KEY in text:
        text = text.replace(config.GOOGLE_API_KEY, '***MASKED_API_KEY***')
    
    return text


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
        # Capture execution start time
        from datetime import datetime
        start_time = datetime.now()
        
        # Get browser configuration from config.py
        headless = config.HEADLESS_BROWSER
        
        # Create browser instance with configuration
        if config.USE_LAMBDATEST:
            # LambdaTest remote browser configuration
            if not config.LT_USERNAME or not config.LT_ACCESS_KEY:
                raise ValueError("LT_USERNAME and LT_ACCESS_KEY must be set when USE_LAMBDATEST is true")
            
            logs.append(f"[{start_time.strftime('%H:%M:%S')}] Initializing LambdaTest remote execution")
            
            # LambdaTest capabilities for Playwright
            lt_capabilities = {
                "browserName": "Chrome",
                "browserVersion": "latest",
                "LT:Options": {
                    "platform": "Windows 10",
                    "build": f"WebAgentAA-{start_time.strftime('%Y%m%d')}",
                    "name": f"{task_info['scenario_name']} - Task #{task_number}",
                    "user": config.LT_USERNAME,
                    "accessKey": config.LT_ACCESS_KEY,
                    "network": True,
                    "video": True,
                    "console": True,
                    "visual": True,
                    "project": "WebAgentAA",
                    "w3c": True,
                    "plugin": "playwright-python",
                }
            }
            
            # Create LambdaTest connection URL with URL-encoded capabilities
            capabilities_json = json.dumps(lt_capabilities)
            encoded_capabilities = quote(capabilities_json, safe='')
            cdp_url = f"wss://cdp.lambdatest.com/playwright?capabilities={encoded_capabilities}"
            
            # Initialize browser with LambdaTest CDP endpoint
            # Note: This requires the browser-use library to support cdp_url parameter
            # If not supported, this will fall back to local execution with a warning
            try:
                browser = Browser(
                    headless=False,
                    cdp_url=cdp_url
                )
                logs.append(f"[{start_time.strftime('%H:%M:%S')}] Connected to LambdaTest")
            except TypeError:
                # If browser-use doesn't support cdp_url, log warning and use local
                logs.append(f"[{start_time.strftime('%H:%M:%S')}] WARNING: browser-use doesn't support remote execution")
                logs.append(f"[{start_time.strftime('%H:%M:%S')}] Falling back to local browser execution")
                browser = Browser(headless=headless)
        else:
            # Local browser execution
            browser = Browser(headless=headless)
            logs.append(f"[{start_time.strftime('%H:%M:%S')}] Using local browser execution")
        
        # Create and run agent with configured browser
        agent = Agent(task=task_info['prompt_text'], llm=llm, browser=browser)
        
        logs.append(f"[{start_time.strftime('%H:%M:%S')}] Test execution started")
        logs.append(f"[{start_time.strftime('%H:%M:%S')}] Scenario: {task_info['scenario_name']}")
        logs.append(f"[{start_time.strftime('%H:%M:%S')}] Category: {task_info['category']}")
        logs.append(f"[{start_time.strftime('%H:%M:%S')}] Priority: {task_info['priority']}")
        
        result = await agent.run()
        
        # Capture agent history/steps after execution
        if result and hasattr(result, 'history'):
            history = result.history if not callable(result.history) else result.history()
            
            for i, step in enumerate(history, 1):
                # Extract action name and details
                action_name = 'N/A'
                action_details = ''
                
                if hasattr(step, 'action'):
                    action_obj = step.action
                    
                    # Handle list of actions
                    if isinstance(action_obj, list) and len(action_obj) > 0:
                        action_obj = action_obj[0]
                    
                    # Try to extract action name from various sources
                    if action_obj is not None:
                        # Check for root attribute (common pattern in AgentOutput models)
                        if hasattr(action_obj, 'root'):
                            root_obj = action_obj.root
                            if hasattr(root_obj, '__class__'):
                                action_name = root_obj.__class__.__name__.replace('Model', '').replace('Action', '')
                            # Try to extract specific action details
                            if hasattr(root_obj, '__dict__'):
                                for key, value in root_obj.__dict__.items():
                                    if value is not None and key not in ['model_config', 'model_fields']:
                                        action_details = f"{key}: {value}"
                                        break
                        # Check for class name
                        elif hasattr(action_obj, '__class__'):
                            action_name = action_obj.__class__.__name__.replace('Model', '').replace('Action', '')
                            if hasattr(action_obj, '__dict__'):
                                action_details = str(action_obj.__dict__)
                        # Check for name attribute
                        elif hasattr(action_obj, 'name'):
                            action_name = str(action_obj.name)
                        else:
                            action_name = str(type(action_obj).__name__)
                
                # If still N/A, try to extract from result
                if action_name == 'N/A' and hasattr(step, 'result'):
                    import re
                    result_str = str(step.result)
                    # Use word boundary matching to avoid false positives
                    if re.search(r'\bClicked\b', result_str):
                        action_name = 'Click'
                    elif re.search(r'\bScrolled\b', result_str):
                        action_name = 'Scroll'
                    elif re.search(r'\b(Navigated|Navigate)\b', result_str):
                        action_name = 'Navigate'
                    elif re.search(r'\bWaited\b', result_str):
                        action_name = 'Wait'
                    elif re.search(r'\bSwitched\b', result_str):
                        action_name = 'SwitchTab'
                    elif re.search(r'\b(Input|Typed)\b', result_str):
                        action_name = 'Input'
                
                # Extract thought/reasoning
                thought = ''
                if hasattr(step, 'thought'):
                    thought = mask_sensitive_data(str(step.thought))
                elif hasattr(step, 'model_output'):
                    thought = mask_sensitive_data(str(step.model_output))
                
                # Mask sensitive data in result and model output
                result_text = mask_sensitive_data(str(step.result)) if hasattr(step, 'result') else 'N/A'
                model_output_text = mask_sensitive_data(str(step.model_output)) if hasattr(step, 'model_output') else ''
                
                step_info = {
                    'step_number': i,
                    'action': action_name,
                    'action_details': action_details,
                    'thought': thought,
                    'result': result_text,
                    'model_output': model_output_text,
                    'screenshot': None
                }
                agent_steps.append(step_info)
                logs.append(f"[{start_time.strftime('%H:%M:%S')}] Step {i}: {action_name}")
        
        # Capture execution end time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logs.append(f"[{end_time.strftime('%H:%M:%S')}] Test execution completed")
        logs.append(f"[{end_time.strftime('%H:%M:%S')}] Duration: {duration:.2f} seconds")
        
        # Check if the agent actually completed the task successfully
        task_success = result.is_done() if result else False
        
        # Additional validation: Check the final result message for failure indicators
        if task_success and result and hasattr(result, 'final_result'):
            final_msg = result.final_result().lower()
            
            # List of failure indicators in the final message
            failure_indicators = [
                'unable to',
                'could not',
                'failed to',
                'did not',
                'cannot',
                'was not able',
                'stuck at',
                'consistently failed',
                'despite numerous attempts',
                'however,',
                'but ',
                'except ',
                'unfortunately',
                'unsuccessfully'
            ]
            
            # Check if any failure indicator is present
            has_failure_indicator = any(indicator in final_msg for indicator in failure_indicators)
            
            if has_failure_indicator:
                task_success = False
                print(f"\n⚠️  Test #{task_number} ({task_info['scenario_name']}) marked as done but contains failure indicators.\n")
                print(f"Final result: {result.final_result()}\n")
                logs.append(f"[{end_time.strftime('%H:%M:%S')}] Final result: {result.final_result()}")
                logs.append(f"[{end_time.strftime('%H:%M:%S')}] Status: FAILED - Task reported completion but final message indicates failure")
        
        if task_success:
            print(f"\n✅ Test #{task_number} ({task_info['scenario_name']}) completed successfully!\n")
            if result and hasattr(result, 'final_result'):
                final_msg = result.final_result()
                print(f"Final result: {final_msg}\n")
                logs.append(f"[{end_time.strftime('%H:%M:%S')}] Final result: {final_msg}")
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
        
        # Mask sensitive data in error message
        error_message = mask_sensitive_data(str(e))
        
        logs.append(f"[{error_time.strftime('%H:%M:%S')}] ERROR: {error_message}")
        logs.append(f"[{error_time.strftime('%H:%M:%S')}] Status: FAILED - Exception occurred")
        
        print(f"\n❌ Test #{task_number} ({task_info['scenario_name']}) failed: {error_message}\n")
        return {
            'task_number': task_number,
            'scenario': task_info['scenario_name'],
            'category': task_info['category'],
            'priority': task_info['priority'],
            'prompt': task_info['prompt_text'],
            'success': False,
            'error': error_message,
            'logs': logs,
            'agent_steps': []
        }
    finally:
        # Properly close browser and cleanup resources
        if browser is not None:
            try:
                await browser.stop()
            except Exception as cleanup_error:
                cleanup_msg = mask_sensitive_data(str(cleanup_error))
                print(f"⚠️  Warning: Browser cleanup error: {cleanup_msg}")


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
