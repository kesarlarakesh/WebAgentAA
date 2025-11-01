# WebAgentAA - Browser Automation Framework

AI-powered browser automation framework using Google Gemini and browser-use library for automated testing with Google Sheets integration.

## Features

- 🤖 AI-powered browser automation using Google Gemini
- 📊 Google Sheets integration for test case management
- 📝 HTML report generation with detailed execution logs
- 🔄 Sequential and parallel test execution modes
- 🎯 Filter tests by priority or category
- 🌐 Headless and headed browser modes
- 📦 Agent step tracking and logging

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

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Google Gemini API Key
   GOOGLE_API_KEY=your_gemini_api_key_here
   
   # Google Sheets Configuration
   GOOGLE_SHEETS_CREDENTIALS=./google-sheets-credentials.json
   SPREADSHEET_ID=your_spreadsheet_id
   SHEET_NAME=Tasks
   START_ROW=2
   
   # Execution Configuration
   EXECUTION_MODE=parallel
   TASK_DELAY=5
   RUN_PRIORITY=High
   RUN_CATEGORY=Hotels
   HEADLESS_BROWSER=false
   MAX_PARALLEL_AGENTS=3
   ```

5. **Set up Google Sheets credentials**
   
   - Create a Service Account in Google Cloud Console
   - Download the JSON credentials file
   - Save it as `google-sheets-credentials.json` in the project root
   - Share your Google Sheet with the service account email

## Running Tests

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
   - `SPREADSHEET_ID` - Your Google Sheet ID
   - `SHEET_NAME` - Sheet name (e.g., "Tasks")
   - `START_ROW` - Starting row number (e.g., "2")
   - `GOOGLE_SHEETS_CREDENTIALS_JSON` - Full JSON content of your credentials file

### Manual Workflow Trigger

1. Go to **Actions** tab
2. Select **Browser Automation Tests**
3. Click **Run workflow**
4. Choose test type (single, multiple, priority, category)

### Scheduled Runs

Tests automatically run daily at 9 AM UTC (configured in workflow file).

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

### Execution Modes
- **sequential**: Run tests one after another (safer, easier to debug)
- **parallel**: Run multiple tests concurrently (faster)

### Browser Modes
- **HEADLESS_BROWSER=false**: Visible browser (for debugging)
- **HEADLESS_BROWSER=true**: No browser window (faster, for CI/CD)

### Parallel Execution
- **MAX_PARALLEL_AGENTS=0**: Unlimited (all tests at once)
- **MAX_PARALLEL_AGENTS=3**: Run 3 tests at a time

## Project Structure

```
WebAgentAA/
├── .github/
│   └── workflows/
│       └── run-tests.yml          # GitHub Actions workflow
├── reports/                        # Generated HTML reports
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
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

2. **"GOOGLE_SHEETS_CREDENTIALS not found"**
   - Download service account JSON and save as `google-sheets-credentials.json`
   - Update path in `.env` if different location

3. **Playwright browser not installed**
   ```bash
   playwright install chromium
   playwright install-deps  # Linux only
   ```

4. **Tests fail in headless mode**
   - Set `HEADLESS_BROWSER=false` for debugging
   - Check logs in HTML reports

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For issues and questions, please open an issue on GitHub.
