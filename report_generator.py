"""
HTML Report Generator for Browser Automation Tests
Generates detailed test execution reports with prompt-status mapping and logs
"""
from datetime import datetime
import os
import glob
import json
import config


def calculate_test_statistics(results):
    """
    Calculate test statistics from results.
    
    Args:
        results: List of result dictionaries from test execution
    
    Returns:
        dict: Dictionary containing total_tests, passed_tests, failed_tests, and pass_rate
    """
    total_tests = len(results)
    passed_tests = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    return {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'pass_rate': pass_rate
    }


def generate_html_report(results, output_dir='reports'):
    """
    Generate an HTML report from test results.
    
    Args:
        results: List of result dictionaries from test execution
        output_dir: Directory to save the report (default: 'reports')
    
    Returns:
        str: Path to the generated report file
    """
    # Create reports directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Delete old reports (keep only the latest)
    old_reports = glob.glob(os.path.join(output_dir, 'test_report_*.html'))
    for old_report in old_reports:
        try:
            os.remove(old_report)
        except Exception as e:
            print(f"Warning: Could not delete old report {old_report}: {e}")
    
    # Generate timestamp for report filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f'test_report_{timestamp}.html'
    report_path = os.path.join(output_dir, report_filename)
    
    # Calculate statistics
    stats = calculate_test_statistics(results)
    total_tests = stats['total_tests']
    passed_tests = stats['passed_tests']
    failed_tests = stats['failed_tests']
    pass_rate = stats['pass_rate']
    
    # Generate HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Execution Report - {timestamp}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .summary-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .summary-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        
        .summary-card h3 {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }}
        
        .summary-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .summary-card.total .value {{ color: #667eea; }}
        .summary-card.passed .value {{ color: #10b981; }}
        .summary-card.failed .value {{ color: #ef4444; }}
        .summary-card.pass-rate .value {{ color: #f59e0b; }}
        
        .results-section {{
            padding: 30px;
        }}
        
        .results-section h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .test-card {{
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            margin-bottom: 20px;
            overflow: hidden;
            transition: all 0.3s ease;
        }}
        
        .test-card:hover {{
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            border-color: #667eea;
        }}
        
        .test-card.passed {{
            border-left: 6px solid #10b981;
        }}
        
        .test-card.failed {{
            border-left: 6px solid #ef4444;
        }}
        
        .test-header {{
            padding: 20px;
            background: #f9fafb;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .test-header:hover {{
            background: #f3f4f6;
        }}
        
        .test-info {{
            flex: 1;
        }}
        
        .test-number {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .test-scenario {{
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }}
        
        .test-meta {{
            display: flex;
            gap: 15px;
            font-size: 0.9em;
            color: #666;
        }}
        
        .test-meta span {{
            background: #e5e7eb;
            padding: 4px 12px;
            border-radius: 20px;
        }}
        
        .status-badge {{
            padding: 10px 25px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .status-badge.passed {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .status-badge.failed {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .test-details {{
            padding: 20px;
            display: none;
            background: white;
            border-top: 1px solid #e5e7eb;
        }}
        
        .test-details.expanded {{
            display: block;
        }}
        
        .prompt-section {{
            margin-bottom: 20px;
        }}
        
        .prompt-section h4 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .prompt-text {{
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
            color: #333;
            line-height: 1.6;
        }}
        
        .error-section {{
            margin-top: 20px;
            background: #fee2e2;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ef4444;
        }}
        
        .error-section h4 {{
            color: #991b1b;
            margin-bottom: 10px;
        }}
        
        .error-text {{
            color: #7f1d1d;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
        }}
        
        .agent-steps-section {{
            margin-top: 20px;
            background: #f0fdf4;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #10b981;
        }}
        
        .agent-steps-section h4 {{
            color: #065f46;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        
        .agent-step {{
            background: white;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 3px solid #10b981;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .agent-step:last-child {{
            margin-bottom: 0;
        }}
        
        .step-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }}
        
        .step-number {{
            background: #10b981;
            color: white;
            padding: 4px 10px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.85em;
        }}
        
        .step-action {{
            color: #047857;
            font-weight: 600;
            font-family: 'Courier New', monospace;
        }}
        
        .step-details {{
            color: #666;
            font-size: 0.9em;
            font-family: 'Courier New', monospace;
            margin-top: 8px;
            padding: 8px;
            background: #f9fafb;
            border-radius: 4px;
        }}
        
        .logs-section {{
            margin-top: 20px;
            background: #1e293b;
            padding: 15px;
            border-radius: 8px;
            color: #e2e8f0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .logs-section h4 {{
            color: #60a5fa;
            margin-bottom: 10px;
        }}
        
        .log-entry {{
            padding: 5px 0;
            border-bottom: 1px solid #334155;
        }}
        
        .log-entry:last-child {{
            border-bottom: none;
        }}
        
        .expand-icon {{
            transition: transform 0.3s ease;
            font-size: 1.5em;
            color: #667eea;
        }}
        
        .expanded .expand-icon {{
            transform: rotate(180deg);
        }}
        
        .footer {{
            background: #f9fafb;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e5e7eb;
        }}
        
        @media (max-width: 768px) {{
            .summary {{
                grid-template-columns: 1fr;
            }}
            
            .test-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Browser Automation Test Report</h1>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card total">
                <h3>Total Tests</h3>
                <div class="value">{total_tests}</div>
            </div>
            <div class="summary-card passed">
                <h3>Passed</h3>
                <div class="value">{passed_tests}</div>
            </div>
            <div class="summary-card failed">
                <h3>Failed</h3>
                <div class="value">{failed_tests}</div>
            </div>
            <div class="summary-card pass-rate">
                <h3>Pass Rate</h3>
                <div class="value">{pass_rate:.1f}%</div>
            </div>
        </div>
        
        <div class="results-section">
            <h2>📋 Test Results</h2>
"""
    
    # Add individual test results
    for result in results:
        if not isinstance(result, dict):
            continue
            
        test_num = result.get('task_number', 'N/A')
        scenario = result.get('scenario', 'Unknown Test')
        success = result.get('success', False)
        error = result.get('error', '')
        prompt = result.get('prompt', 'No prompt available')
        category = result.get('category', 'N/A')
        priority = result.get('priority', 'N/A')
        logs = result.get('logs', [])
        agent_steps = result.get('agent_steps', [])
        
        status_class = 'passed' if success else 'failed'
        status_text = 'PASSED' if success else 'FAILED'
        
        html_content += f"""
            <div class="test-card {status_class}">
                <div class="test-header" onclick="toggleDetails(this)">
                    <div class="test-info">
                        <div class="test-number">Test #{test_num}</div>
                        <div class="test-scenario">{scenario}</div>
                        <div class="test-meta">
                            <span>📂 {category}</span>
                            <span>⭐ {priority}</span>
                        </div>
                    </div>
                    <div>
                        <span class="status-badge {status_class}">{status_text}</span>
                    </div>
                    <div class="expand-icon">▼</div>
                </div>
                
                <div class="test-details">
                    <div class="prompt-section">
                        <h4>📝 Test Prompt</h4>
                        <div class="prompt-text">{prompt}</div>
                    </div>
"""
        
        # Add agent steps section
        if agent_steps:
            html_content += """
                    <div class="agent-steps-section">
                        <h4>🤖 Agent Execution Steps</h4>
"""
            for step in agent_steps:
                step_num = step.get('step_number', '?')
                action = step.get('action', 'Unknown action')
                result_text = step.get('result', '')
                model_output = step.get('model_output', '')
                
                html_content += f"""
                        <div class="agent-step">
                            <div class="step-header">
                                <span class="step-number">Step {step_num}</span>
                                <span class="step-action">{action}</span>
                            </div>
"""
                if result_text and result_text != 'N/A':
                    html_content += f"""
                            <div class="step-details"><strong>Result:</strong> {result_text}</div>
"""
                if model_output and model_output != '':
                    # Truncate long model outputs for readability
                    truncated_output = model_output[:300] + '...' if len(model_output) > 300 else model_output
                    html_content += f"""
                            <div class="step-details"><strong>Model Output:</strong> {truncated_output}</div>
"""
                html_content += """
                        </div>
"""
            html_content += """
                    </div>
"""
        
        # Add error section if test failed
        if not success and error:
            html_content += f"""
                    <div class="error-section">
                        <h4>❌ Error Details</h4>
                        <div class="error-text">{error}</div>
                    </div>
"""
        
        # Add logs section
        if logs:
            html_content += """
                    <div class="logs-section">
                        <h4>📄 Execution Logs</h4>
"""
            for log in logs:
                html_content += f"""
                        <div class="log-entry">{log}</div>
"""
            html_content += """
                    </div>
"""
        
        html_content += """
                </div>
            </div>
"""
    
    # Close HTML structure
    html_content += f"""
        </div>
        
        <div class="footer">
            <p>Report generated by Browser Automation Framework</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                Execution Mode: {config.EXECUTION_MODE.upper()} | 
                Total Duration: Check individual test logs
            </p>
        </div>
    </div>
    
    <script>
        function toggleDetails(header) {{
            const card = header.parentElement;
            const details = card.querySelector('.test-details');
            const icon = card.querySelector('.expand-icon');
            
            details.classList.toggle('expanded');
            card.classList.toggle('expanded');
        }}
        
        // Auto-expand failed tests
        document.addEventListener('DOMContentLoaded', function() {{
            const failedCards = document.querySelectorAll('.test-card.failed');
            failedCards.forEach(card => {{
                const header = card.querySelector('.test-header');
                if (header) {{
                    toggleDetails(header);
                }}
            }});
        }});
    </script>
</body>
</html>
"""
    
    # Write HTML to file
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Generate JSON report as well
    try:
        generate_json_report(results, output_dir, timestamp)
    except Exception as e:
        print(f"Warning: Failed to generate JSON report: {e}")
        # Continue anyway - HTML report is the primary output
    
    return report_path


def generate_json_report(results, output_dir='reports', timestamp=None):
    """
    Generate a JSON report from test results.
    
    Args:
        results: List of result dictionaries from test execution
        output_dir: Directory to save the report (default: 'reports')
        timestamp: Optional timestamp string in format '%Y%m%d_%H%M%S' (e.g., '20250106_143022').
                  Used as report ID and in filename. Will be auto-generated if not provided.
    
    Returns:
        str: Path to the generated JSON report file (e.g., 'reports/json_report_20250106_143022.json')
    """
    # Create reports directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for report ID if not provided
    if timestamp is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Calculate statistics
    stats = calculate_test_statistics(results)
    
    # Prepare JSON structure
    json_report = {
        'metadata': {
            'report_id': timestamp,
            'generated_at': datetime.now().isoformat(),
            'total_tests': stats['total_tests'],
            'passed_tests': stats['passed_tests'],
            'failed_tests': stats['failed_tests'],
            'pass_rate': round(stats['pass_rate'], 2)
        },
        'tests': []
    }
    
    # Process each test result
    for result in results:
        if not isinstance(result, dict):
            continue
        
        # Prepare test data
        test_data = {
            'task_number': result.get('task_number'),
            'scenario': result.get('scenario', 'Unknown'),
            'category': result.get('category', 'Unknown'),
            'priority': result.get('priority', 'Unknown'),
            'status': 'passed' if result.get('success') else 'failed',
            'error': result.get('error'),
            'prompt': result.get('prompt', ''),
            'steps': []
        }
        
        # Add agent steps
        agent_steps = result.get('agent_steps', [])
        for step in agent_steps:
            step_data = {
                'step_number': step.get('step_number'),
                'action': step.get('action', ''),
                'thought': step.get('thought', ''),
                'result': str(step.get('result', ''))
            }
            test_data['steps'].append(step_data)
        
        # Add logs
        test_data['logs'] = result.get('logs', [])
        
        json_report['tests'].append(test_data)
    
    # Delete old JSON reports (keep only the latest)
    old_json_reports = glob.glob(os.path.join(output_dir, 'json_report_*.json'))
    for old_report in old_json_reports:
        try:
            os.remove(old_report)
        except Exception as e:
            print(f"Warning: Could not delete old JSON report {old_report}: {e}")
    
    # Write timestamped JSON report
    json_filename = f'json_report_{timestamp}.json'
    json_path = os.path.join(output_dir, json_filename)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, indent=2, ensure_ascii=False)
    
    # Create a symlink or copy as json-report.json for backward compatibility
    latest_json_path = os.path.join(output_dir, 'json-report.json')
    try:
        # Remove old symlink/file if exists
        if os.path.exists(latest_json_path):
            os.remove(latest_json_path)
        # Create a copy (Windows-friendly alternative to symlink)
        import shutil
        shutil.copy2(json_path, latest_json_path)
    except Exception as e:
        print(f"Warning: Could not create json-report.json copy: {e}")
    
    print(f"📄 JSON report generated: {json_path}")
    
    return json_path


def save_report_index(report_path):
    """
    Create/update an index.html that always points to the latest report
    """
    reports_dir = os.path.dirname(report_path)
    index_path = os.path.join(reports_dir, 'index.html')
    
    index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url={os.path.basename(report_path)}">
    <title>Redirecting to Latest Report...</title>
</head>
<body>
    <p>Redirecting to latest report...</p>
    <p>If not redirected, <a href="{os.path.basename(report_path)}">click here</a>.</p>
</body>
</html>
"""
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    return index_path
