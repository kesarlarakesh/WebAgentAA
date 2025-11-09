# WebAgentAA - Browser Automation Framework

AI-powered browser automation framework using Google Gemini and browser-use library for automated testing with Google Sheets integration. Supports both local and LambdaTest cloud execution.

## Features

- 🤖 AI-powered browser automation using Google Gemini
- 📊 Google Sheets integration for test case management
- 📝 HTML report generation with detailed execution logs
- 🔄 Sequential and parallel test execution modes
- 🎯 Filter tests by priority or category
- 🌐 Headless and headed browser modes
- ☁️ LambdaTest cloud execution support
- 📦 Agent step tracking and logging
- 📂 Separate GCS folders for local and LambdaTest reports

## Prerequisites

- Python 3.12+
- Google Gemini API key
- Google Sheets API credentials (Service Account)
- Google Sheet with test cases

## Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/kesarlarakesh/WebAgentAA.git
   cd WebAgentAA
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Configure the application**
   
   a. Create a `.env` file in the project root for sensitive credentials:
   ```env
   # Google Gemini API Key
   GOOGLE_API_KEY=your_gemini_api_key_here
   
   # Google Sheets Credentials Path
   GOOGLE_SHEETS_CREDENTIALS=./google-sheets-credentials.json
   
   # LambdaTest Configuration (Optional - for cloud execution)
   USE_LAMBDATEST=false
   LT_USERNAME=your_lambdatest_username
   LT_ACCESS_KEY=your_lambdatest_access_key
   ```
   
   b. Edit `config.py` to set your execution configuration:
   ```python
   # Google Sheets Configuration
   SPREADSHEET_ID = 'your_spreadsheet_id_here'  # Required: Add your Google Sheet ID
   SHEET_NAME = 'Sheet1'
   START_ROW = 2
   
   # Execution Configuration
   EXECUTION_MODE = 'parallel'  # 'sequential' or 'parallel'
   TASK_DELAY = 5  # Delay between tasks in seconds
   MAX_PARALLEL_AGENTS = 3
   
   # Task Filtering Configuration
   RUN_PRIORITY = 'High'  # 'High', 'Medium', 'Low', or 'All'
   RUN_CATEGORY = 'Hotels'  # Category to filter, or empty string for all
   
   # Browser Configuration
   HEADLESS_BROWSER = False  # True for headless, False to see browser
   ```

5. **Set up Google Sheets credentials**
   
   - Create a Service Account in Google Cloud Console
   - Download the JSON credentials file
   - Save it as `google-sheets-credentials.json` in the project root
   - Share your Google Sheet with the service account email

## Running Tests

### Command Line Execution

When running tests from your local terminal, the test environment (local browser or LambdaTest cloud) is controlled by the `USE_LAMBDATEST` environment variable in your `.env` file:

- **Local Browser Execution**: Set `USE_LAMBDATEST=false` (or omit it)
- **LambdaTest Cloud Execution**: Set `USE_LAMBDATEST=true` and provide credentials

### Single Task
```bash
python run_single_task.py
```

### Multiple Tasks
```bash
python run_multiple_tasks.py
```

### By Priority
```bash
python run_by_priority.py
```

### By Category
```bash
python run_by_category.py
```

## GitHub Actions Setup

To run tests in GitHub Actions, add these secrets to your repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add the following secrets:

   - `GOOGLE_API_KEY` - Your Gemini API key
   - `GOOGLE_SHEETS_CREDENTIALS_JSON` - Full JSON content of your credentials file
   - `GCP_SERVICE_ACCOUNT_KEY` - Google Cloud Platform service account key for GCS uploads
   - `SLACK_WEBHOOK_URL` - (Optional) Slack webhook URL for notifications

**For LambdaTest Integration:**
   - `LT_USERNAME` - Your LambdaTest username
   - `LT_ACCESS_KEY` - Your LambdaTest access key

**Note:** Other configuration values (SPREADSHEET_ID, execution mode, priorities, etc.) are configured in `config.py` and committed to your repository.

### Manual Workflow Trigger

1. Go to **Actions** tab
2. Select **AA Agent Automation Tests**
3. Click **Run workflow**
4. Choose:
   - **Test type**: single, multiple, priority, or category
   - **Test environment**: local or lambdatest
5. Click **Run workflow**

### Test Environments

- **Local**: Tests run on GitHub Actions runners using local Playwright browser
  - Reports uploaded to: `gs://aawebagentreports/webagentreports/local/reports/`
  
- **LambdaTest**: Tests run on LambdaTest cloud infrastructure
  - Reports uploaded to: `gs://aawebagentreports/webagentreports/lambdatest/reports/`
  - Requires `LT_USERNAME` and `LT_ACCESS_KEY` secrets

### Scheduled Runs

Tests automatically run daily at 9 AM UTC in **local** mode (configured in workflow file).

## LambdaTest Integration

WebAgentAA supports running tests on LambdaTest cloud infrastructure for cross-browser testing and scalability.

### Setup for LambdaTest

1. **Create LambdaTest Account**
   - Sign up at [LambdaTest](https://www.lambdatest.com/)
   - Get your username and access key from [LambdaTest Profile](https://accounts.lambdatest.com/profile)

2. **Configure Environment Variables**
   
   Add to your `.env` file:
   ```env
   # LambdaTest Configuration
   USE_LAMBDATEST=true
   LT_USERNAME=your_lambdatest_username
   LT_ACCESS_KEY=your_lambdatest_access_key
   ```

3. **GitHub Actions Setup**
   - Add `LT_USERNAME` and `LT_ACCESS_KEY` as repository secrets
   - Select "lambdatest" as test environment when triggering workflow

### Running Tests on LambdaTest

**Via GitHub Actions:**
- Go to Actions → AA Agent Automation Tests → Run workflow
- Select test type
- Choose "lambdatest" as test environment

**From Command Line:**
```bash
# Set environment variables
export USE_LAMBDATEST=true
export LT_USERNAME=your_username
export LT_ACCESS_KEY=your_access_key

# Run tests
python run_single_task.py
```

### Benefits of LambdaTest Integration

- ☁️ Cloud-based browser execution
- 🌍 Cross-browser and cross-platform testing capabilities
- 📊 Scalable test execution infrastructure
- 🚀 No local browser setup required on CI/CD runners

**Note:** Advanced LambdaTest features like video recording, screenshots, and platform-specific analytics require additional configuration and may not be automatically available through the current browser-use library integration.

### Important Notes

**LambdaTest Integration Status:**
The current implementation includes LambdaTest configuration and will attempt to connect using Playwright's CDP (Chrome DevTools Protocol) endpoint. The integration depends on the `browser-use` library's support for remote browser connections. If the library doesn't support the `cdp_url` parameter, tests will automatically fall back to local browser execution with a warning in the logs.

**For Full LambdaTest Support:**
If you encounter fallback warnings, you may need to:
1. Check if `browser-use` library has been updated to support remote connections
2. Update to the latest version: `pip install --upgrade browser-use`
3. Or use direct Playwright integration for LambdaTest execution

### Report Organization

Tests executed on different environments are organized separately in Google Cloud Storage:
- Local tests: `webagentreports/local/reports/`
- LambdaTest: `webagentreports/lambdatest/reports/`

## Google Sheet Structure

Your Google Sheet should have these columns (Row 1 = Headers):

| Column | Header | Description |
|--------|--------|-------------|
| A | Scenario Name | Test case name |
| B | Prompt Text | Detailed test instructions |
| C | Category | Test category (e.g., Hotels, Flights) |
| D | Priority | Priority level (High, Medium, Low) |
| E | Active | "yes" to run, "no" to skip |

## Reports

HTML reports are generated in the `reports/` directory:
- `test_report_YYYYMMDD_HHMMSS.html` - Detailed test report
- `index.html` - Redirects to latest report

Reports include:
- Test summary statistics
- Pass/fail status for each test
- Detailed agent execution steps
- Execution logs with timestamps

## Configuration Options

All configuration is managed in `config.py`. Edit this file to change settings:

### Execution Modes
- **EXECUTION_MODE = 'sequential'**: Run tests one after another (safer, easier to debug)
- **EXECUTION_MODE = 'parallel'**: Run multiple tests concurrently (faster)

### Browser Modes
- **HEADLESS_BROWSER = False**: Visible browser (for debugging)
- **HEADLESS_BROWSER = True**: No browser window (faster, for CI/CD)

### Parallel Execution
- **MAX_PARALLEL_AGENTS = 0**: Unlimited (all tests at once)
- **MAX_PARALLEL_AGENTS = 3**: Run 3 tests at a time

### Task Filtering
- **RUN_PRIORITY**: Filter tests by priority ('High', 'Medium', 'Low', or 'All')
- **RUN_CATEGORY**: Filter tests by category (e.g., 'Hotels', 'Flights', or empty string for all)

## Project Structure

```
WebAgentAA/
├── .github/
│   └── workflows/
│       └── run-tests.yml          # GitHub Actions workflow
├── reports/                        # Generated HTML reports
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── config.py                       # Configuration settings
├── llm_config.py                   # LLM configuration
├── sheets_reader.py                # Google Sheets integration
├── task_runner_utils.py            # Task execution utilities
├── report_generator.py             # HTML report generation
├── run_single_task.py              # Run single test
├── run_multiple_tasks.py           # Run all tests
├── run_by_priority.py              # Run by priority filter
└── run_by_category.py              # Run by category filter
```

## Troubleshooting

### Common Issues

1. **"GOOGLE_API_KEY not found"**
   - Ensure `.env` file exists with `GOOGLE_API_KEY` set

2. **"SPREADSHEET_ID not found in config.py"**
   - Edit `config.py` and set `SPREADSHEET_ID = 'your_spreadsheet_id_here'`

3. **"GOOGLE_SHEETS_CREDENTIALS not found"**
   - Download service account JSON and save as `google-sheets-credentials.json`
   - Update path in `.env` if different location

4. **Playwright browser not installed**
   ```bash
   playwright install chromium
   playwright install-deps  # Linux only
   ```

5. **Tests fail in headless mode**
   - Edit `config.py` and set `HEADLESS_BROWSER = False` for debugging
   - Check logs in HTML reports
