# pop - Prompt-Oriented Programming

A flexible wrapper script for generating code using any Ollama model and automatically extracting it to executable files.

## What is pop?

**pop** (Prompt-Oriented Programming) is a command-line tool that bridges the gap between natural language prompts and executable code. It leverages Ollama's local LLMs to generate scripts in any language and automatically extracts clean code from the AI's response.

### Key Features

- **Background Execution**: Runs in the background, returning your shell immediately
- **Session Tracking**: Saves all sessions with full logs and metadata
- **Default Model**: Uses `qwen3:latest` by default (configurable with `-m` flag)
- **Session Management**: View active and past sessions with `pop list`
- **Model Discovery**: List available models with `pop model`
- **Minimal Mode**: Generate cleaner code with `--minimal` (stronger prompts + comment stripping)
- **Hide Thinking**: Model thinking is hidden by default (use `--thinking` to show)
- **Incremental Naming**: Automatically avoids overwriting files (script.py → script-1.py → script-2.py)
- **Auto Shebang**: Automatically inserts appropriate shebang lines for executable scripts
- **Output Verification**: Automatic syntax checking and model-based completeness verification
- **Auto-Retry**: Automatically retries up to 3 times when verification fails, with feedback
- **Fix Mode**: Fix existing scripts with `-fix:<script>` parameter
- **Dependency Detection**: Automatically detects missing modules and generates requirements.txt
- **Multiple Input Methods**: Command-line, file input, or stdin/pipe support
- **Pure Python**: Written entirely in Python for portability

## Installation

The script is located at `/Users/jay/cc_projects/pop/pop`.

Add to your PATH:

```bash
# Add to ~/.zshrc or ~/.bashrc
export PATH="$HOME/cc_projects/pop:$PATH"

# Or create a symlink in ~/bin
ln -s /Users/jay/cc_projects/pop/pop ~/bin/pop
```

## Dependencies

- **Ollama** with at least one model installed
- **Python 3** (for code extraction)
- **extract-code.py** helper script (located at `/Users/jay/extract-code.py`)

### Installing Ollama Models

```bash
# Install models from Ollama library
ollama pull llama3.2
ollama pull codellama
ollama pull mistral
ollama pull qwen2.5-coder

# List installed models
ollama list
```

## Usage

```bash
pop [options] [prompt]
```

### Options

| Option | Description |
|--------|-------------|
| `-m MODEL` | Select Ollama model (default: qwen3:latest) |
| `-f FILE` | Read prompt from file |
| `-o OUTPUT` | Output file path (default: script.py, auto-increments if exists) |
| `-l LANG` | Language filter for code extraction (python, bash, etc.) |
| `--minimal` | Enable minimal mode (strongest prompts + strip comments) |
| `--thinking` | Show model thinking process (hidden by default) |
| `--hidethinking` | Explicitly hide model thinking process (default behavior) |
| `--no-verify` | Skip output verification (verification enabled by default) |
| `-fix:<script>` | Fix an existing script (output saved as `<script>_popfix`) |
| `-h` | Show help message |

### Commands

| Command | Description |
|---------|-------------|
| `pop list` | Show all active and past pop sessions on this host |
| `pop model` | List all available Ollama models |

### Output Verification

By default, **pop** verifies all generated code through a two-step process:

1. **Syntax Verification**: Checks that the code is syntactically valid using language-specific tools:
   - Python: `python3 -m py_compile`
   - Bash/Shell: `bash -n`
   - JavaScript: `node --check`
   - Ruby: `ruby -c`
   - Perl: `perl -c`

2. **Completeness Verification**: Uses the same model to review the generated code against the original requirements, checking for:
   - Truncated or cut-off code
   - Missing required functionality
   - Incomplete structures

If verification fails, **pop** automatically retries with feedback about what went wrong, up to 3 times.

```bash
# Default behavior - verification enabled
pop "write a web scraper"

# Skip verification for faster output
pop --no-verify "write a hello world script"
```

### Fix Mode

Fix existing scripts using the `-fix:<script>` parameter. This sends your script to the model along with your fix instructions, and outputs a corrected version.

```bash
# Fix syntax errors and add a shebang
pop -fix:./myscript.py "add a shebang and fix any syntax errors"
# Output: ./myscript.py_popfix

# Add error handling to an existing script
pop -fix:./server.py "add try/except error handling around all file operations"
# Output: ./server.py_popfix

# Refactor with a specific model
pop -m codellama -fix:./parser.sh "convert to use getopts for argument parsing"
# Output: ./parser.sh_popfix

# Fix with minimal mode (strip comments from output)
pop --minimal -fix:./verbose.py "simplify this script"
# Output: ./verbose.py_popfix
```

**How it works:**
1. Reads the source file
2. **Analyzes for issues**: Runs the script to detect runtime errors and missing modules
3. **AI Analysis**: Asks the model to identify issues, missing dependencies, and fixes needed
4. Sends the code + analysis + your instructions to the model
5. Extracts the fixed code from the response
6. Verifies syntax and completeness (same as generation mode)
7. Retries up to 3 times if verification fails
8. **Generates requirements.txt** if missing dependencies are detected
9. **Adds installation instructions** as comments in the fixed script
10. **Logs all issues found and fixed** in the session log
11. Saves output as `<original>_popfix`

The original file is **never modified** - the fixed version is always saved with the `_popfix` suffix.

### Dependency Detection

When fixing Python scripts, pop automatically:

1. **Detects missing modules** by attempting to run the script
2. **Analyzes imports** with AI to identify required packages
3. **Creates a requirements file** (e.g., `myscript_requirements.txt`)
4. **Adds installation instructions** to the fixed script header

```bash
# Fix a script that uses requests and pandas (not installed)
pop -fix:./data_fetcher.py "fix syntax errors"

# Creates:
# - data_fetcher.py_popfix (with installation instructions header)
# - data_fetcher_requirements.txt
```

**Example fixed script header:**
```python
#!/usr/bin/env python3
# ============================================================
# DEPENDENCIES REQUIRED
# ============================================================
# This script requires the following modules: requests, pandas
#
# Install dependencies with ONE of these methods:
#
#   Option 1 - Using requirements file:
#     pip install -r data_fetcher_requirements.txt
#
#   Option 2 - Install directly:
#     pip install requests pandas
#
# ============================================================

import requests
import pandas as pd
# ... rest of script
```

### Issue Logging

Fix mode logs all discovered issues and applied fixes to the session log:

```
=== Issues Found ===
  1. Unterminated string literal in line 6
  2. Missing closing parenthesis in line 8
  3. Function name typo: fetch_dat vs fetch_data

=== Missing Dependencies ===
  - pandas
  - requests

=== Fixes to Apply ===
  1. Add closing quote to the URL string
  2. Correct function name to fetch_data
  3. Fix method call from .haed() to .head()

=== Issues Addressed ===
Issues found:
  ✓ Unterminated string literal in line 6
  ✓ Missing closing parenthesis in line 8
Fixes applied:
  ✓ Add closing quote to the URL string
  ✓ Correct function name to fetch_data
```

### Input Methods

**pop** supports three flexible input methods:

1. **Command-line argument** (quick one-liners)
   ```bash
   pop "write a python script that lists files"
   ```

2. **File input** (complex prompts)
   ```bash
   pop -f my-prompt.txt -o output.sh
   ```

3. **Stdin/pipe** (chain with other tools)
   ```bash
   echo "write a port scanner" | pop -o portscan.py
   cat requirements.txt | pop "create a script from these"
   ```

## Quick Start Examples

### Basic Usage (Uses qwen3:latest by default)

```bash
# Uses default model (qwen3:latest)
pop "write a python script that lists all files in current directory"
# Runs in background, creates: script.py
# Returns shell immediately
```

### With Model Selection

```bash
# Use a specific model
pop -m llama3.2 "write a csv parser" -o csvcut.py -l python
```

### From File Input

```bash
# Create a detailed prompt file
cat > prompt.txt << 'EOF'
Write a Python script that:
1. Reads a CSV file
2. Filters rows where age > 18
3. Sorts by name
4. Writes to a new file
EOF

pop -f prompt.txt -o filter.py
```

### From Stdin

```bash
# Pipe from other commands
echo "write a bash script to backup /home to /backup" | pop -o backup.sh -l bash

# Combine with clipboard (macOS)
pbpaste | pop -o script.py

# From heredoc
cat << 'EOF' | pop -o server.py
Write a simple HTTP server that:
- Serves files from current directory
- Logs all requests
- Handles errors gracefully
EOF
```

## Session Management

### Background Execution

**pop** now runs all code generation in the background, returning your shell immediately:

```bash
$ pop "write a complex web scraper"
✓ pop session started: pop-20251208-143055-12345
✓ Model: qwen3:latest
✓ Output will be saved to: script.py
✓ Session log: /Users/jay/.pop/sessions/pop-20251208-143055-12345.log

Generation running in background (PID: 12345)
Use 'pop list' to check session status
Use 'tail -f /Users/jay/.pop/sessions/pop-20251208-143055-12345.log' to follow progress
$
# Shell is immediately available!
```

### Viewing Sessions

Use `pop list` to see all active and past sessions:

```bash
$ pop list

=== Active Sessions ===
● pop-20251208-143055-12345 (PID: 12345)
  Started: 2025-12-08 14:30:55
  Model: qwen3:latest
  Output: script.py
  Prompt: write a complex web scraper...

=== Past Sessions (Last 20) ===
✓ pop-20251208-142012-12234
  Time: 2025-12-08 14:20:12 → 2025-12-08 14:21:45
  Model: qwen3:latest
  Output: csvparser.py
  Prompt: write a csv parser with filtering...
  Log: /Users/jay/.pop/sessions/pop-20251208-142012-12234.log

✗ pop-20251208-141500-12100
  Time: 2025-12-08 14:15:00 → 2025-12-08 14:15:30
  Model: codellama:latest
  Output: test.py
  Prompt: write a unit test framework...
  Log: /Users/jay/.pop/sessions/pop-20251208-141500-12100.log
```

### Monitoring Progress

```bash
# Follow a session in real-time
tail -f ~/.pop/sessions/pop-20251208-143055-12345.log

# Check if output file is ready
ls -lh script.py
```

## Model Selection

### Default Model

By default, **pop** uses `qwen3:latest`. No selection needed:

```bash
pop "write a script"  # Uses qwen3:latest automatically
```

### Custom Model Selection

```bash
# Specify a different model
pop -m codellama "write a recursive file finder" -o find.py

# Use specific model versions
pop -m llama3.2:70b "write a complex algorithm" -o algo.py
```

## Real-World Use Cases

### Data Processing

```bash
# CSV manipulation tool
pop -m codellama "write a python script that merges multiple CSV files by column" -o merge-csv.py

# JSON formatter with jq-like capabilities
pop "create a JSON pretty-printer with sorting and filtering" -o jformat.py

# Log analyzer with statistics
pop -f log-requirements.txt -o analyze-logs.py
```

### System Administration

```bash
# Disk usage reporter with charts
pop -m mistral "write a bash script showing disk usage by directory with color output" -o disk-report.sh -l bash

# Process monitor with alerts
pop "create a script to monitor CPU and memory, send alert if >80%" -o monitor.py

# Service health checker
echo "Check if nginx, postgresql, redis are running" | pop -o healthcheck.sh -l bash
```

### Web Development

```bash
# API client with authentication
pop "write a GitHub API client with token auth and rate limiting" -o github-client.py

# Static site generator
cat requirements.txt | pop "implement a markdown to HTML converter based on these requirements" -o md2html.py

# WebSocket server
pop -m codellama "write a WebSocket echo server with connection pooling" -o ws-server.py
```

### DevOps & Automation

```bash
# Deployment script with rollback
pop -f deploy-spec.txt -o deploy.sh -l bash

# Docker cleanup utility
pop "create a script to clean up old Docker containers and images" -o docker-clean.sh -l bash

# Environment setup with validation
pop "write a script to setup development environment with dependency checks" -o setup-dev.sh -l bash
```

### Development Tools

```bash
# Code formatter wrapper
pop "write a script to format all Python files in a directory using black" -o format-all.py

# Git commit message generator
pop "create a script that generates conventional commit messages from git diff" -o genmsg.sh -l bash

# Test coverage reporter
pop "write a script to run pytest with coverage and generate HTML report" -o coverage.py
```

## Advanced Workflows

### Chain with Other Commands

```bash
# Generate and immediately run
pop "write a hello world script" -o hello.py && python hello.py

# Generate, review, then run
pop "write a file backup script" -o backup.sh -l bash && cat backup.sh && ./backup.sh

# Generate and test
pop "write a palindrome checker with tests" -o palindrome.py && python palindrome.py
```

### Multi-File Projects

```bash
# Generate related files
pop -m codellama "write a Flask REST API" -o api.py
pop -m llama3.2 "write a fetch client for Flask API" -o client.js -l javascript
pop "write pytest tests for Flask API" -o test_api.py
```

### Iterative Refinement

```bash
# Initial version
pop "write a basic calculator" -o calc.py

# Review the response
cat /tmp/pop-response.txt

# Refine based on output
pop "write a calculator with history, variables, and parentheses support" -o calc-advanced.py
```

### Template-Based Generation

```bash
# Create reusable prompt templates
cat > templates/api-client.txt << 'EOF'
Write a REST API client with:
- Request/response logging
- Retry logic with exponential backoff
- Token-based authentication
- Error handling with custom exceptions
- Async/await support
EOF

# Use template
pop -f templates/api-client.txt -o api-client.py -m codellama
```

### Combining Input Sources

```bash
# Prompt from stdin, context from argument
cat error.log | pop "analyze these errors and write a fix script"

# Multiple prompts
echo "Base requirement: web scraper" | pop "Add: rate limiting, robots.txt respect, error recovery" -o scraper.py
```

## Output Files and Logs

When you run **pop**, it creates:

1. **Your script file** - Extracted code, executable (`chmod +x`)
2. **Session log** - `~/.pop/sessions/<session-id>.log` - Full LLM response
3. **Session metadata** - `~/.pop/sessions/<session-id>.meta` - Session info

### Session Files

All sessions are saved in `~/.pop/sessions/`:

```bash
$ ls ~/.pop/sessions/
pop-20251208-143055-12345.log   # Full generation output
pop-20251208-143055-12345.meta  # Session metadata

$ cat ~/.pop/sessions/pop-20251208-143055-12345.meta
START_TIME="2025-12-08 14:30:55"
MODEL_NAME="qwen3:latest"
OUTPUT_FILE="script.py"
PROMPT_TEXT="write a complex web scraper"
STATUS="success"
END_TIME="2025-12-08 14:32:10"
```

### Active Session Tracking

Active sessions are tracked in `~/.pop/active/`:

```bash
$ ls ~/.pop/active/
pop-20251208-143055-12345.session  # Contains PID of running process
```

## Tips & Best Practices

### 1. Be Specific in Prompts

**Good:**
```bash
pop "write a python script that reads CSV, filters rows where age > 18, sorts by name, and writes to filtered.csv"
```

**Less effective:**
```bash
pop "csv filter"
```

### 2. Specify Requirements and Constraints

```bash
pop "write a REST API client with error handling, retries, logging, and timeout of 30s using requests library" -o api.py
```

### 3. Include Examples in Your Prompt

```bash
pop "write a case converter: 'hello_world' -> 'HelloWorld', 'camelCase' -> 'camel_case'" -o converter.py
```

### 4. Choose the Right Model

- **qwen3:latest** - Default, fast and capable (recommended)
- **codellama** - Best for code generation
- **qwen2.5-coder** - Excellent for complex algorithms
- **llama3.2** - Good general-purpose model
- **mistral** - Fast and efficient for simpler tasks

### 5. Monitor Active Sessions

```bash
# Check status of all sessions
pop list

# Follow a specific session
tail -f ~/.pop/sessions/<session-id>.log

# List all session logs
ls -lh ~/.pop/sessions/*.log
```

### 6. Review Before Running

Always check session logs for:
- Security considerations
- Dependencies to install (`pip install`, `npm install`, etc.)
- Usage examples and documentation from the LLM
- Edge cases and limitations

```bash
# View latest session log
cat ~/.pop/sessions/$(ls -t ~/.pop/sessions/*.log | head -1)
```

### 7. Handle Dependencies

```bash
# Generate script
pop "write a web scraper using BeautifulSoup" -o scraper.py

# Wait for completion, then check log for dependencies
pop list  # Check if session is complete
grep -i "pip install\|import" ~/.pop/sessions/pop-*.log | tail -20

# Install dependencies
pip install beautifulsoup4 requests lxml
```

### 8. Use Language Filters Wisely

```bash
# Extract specific language when LLM provides multiple
pop "write both Python and Bash versions of a log parser" -o parser.py -l python
pop "write both Python and Bash versions of a log parser" -o parser.sh -l bash
```

## Troubleshooting

### No Code Extracted

If a session shows "failed" status in `pop list`:

**Check the session log:**
```bash
# Find the failed session
pop list

# View the log
cat ~/.pop/sessions/<session-id>.log
```

**Possible causes:**
- LLM didn't include code blocks in markdown format
- Language filter doesn't match (e.g., specified `bash` but LLM used `sh`)
- Response was purely explanatory

**Solutions:**
```bash
# Try without language filter (uses first code block)
pop "your prompt" -o output.py

# Check full response
cat ~/.pop/sessions/<session-id>.log

# Extract manually with different language
/Users/jay/extract-code.py ~/.pop/sessions/<session-id>.log --lang sh > output.sh

# Extract all code blocks
/Users/jay/extract-code.py ~/.pop/sessions/<session-id>.log --all > output.py
```

### Model Not Found

```bash
# List available models
ollama list

# Pull a model if needed
ollama pull llama3.2
ollama pull codellama
```

### Wrong Language Extracted

```bash
# If LLM included multiple languages, specify the one you want
pop "write Python and Bash versions" -o script.py -l python
# or
pop "write Python and Bash versions" -o script.sh -l bash
```

### Empty Prompt from Stdin

If piping doesn't work, ensure there's content:
```bash
# This will fail (empty)
echo "" | pop

# This works
echo "write a hello world script" | pop -o hello.py

# Check if stdin has content
cat myfile.txt | tee /dev/stderr | pop -o output.py
```

### Checking Session Status

```bash
# View all sessions
pop list

# Monitor specific session progress
tail -f ~/.pop/sessions/<session-id>.log

# Check if a session is still running
ps aux | grep ollama
```

### Permission Issues

```bash
# Script should be executable, but if not:
chmod +x your-script.py

# Or run with interpreter
python your-script.py
bash your-script.sh
```

## Integration Examples

### With Git Workflow

```bash
# Generate script in a feature branch
git checkout -b feature/automation-script
pop -m codellama "write a commit linter script" -o lint-commit.sh -l bash
git add lint-commit.sh
git commit -m "feat: add commit message linter"
```

### With Testing

```bash
# Generate implementation
pop "write a prime number checker" -o primes.py

# Generate tests
pop "write pytest tests for prime number checker with edge cases" -o test_primes.py

# Run tests
pytest test_primes.py -v
```

### With Documentation

```bash
# Generate script
pop -f spec.txt -o logparse.py

# Generate README from the LLM response
pop "write markdown documentation for a log parser CLI tool" -o README.md

# Both outputs available
cat logparse.py
cat /tmp/pop-response.txt  # Contains usage examples
```

### With CI/CD

```bash
# In .github/workflows/codegen.yml
- name: Generate deployment script
  run: |
    pop -m codellama -f deploy-spec.txt -o deploy.sh -l bash
    chmod +x deploy.sh
    ./deploy.sh --dry-run
```

### With Make

```makefile
# Makefile
generate-api-client:
	pop -m codellama -f api-spec.txt -o src/api-client.py -l python
	black src/api-client.py
	pylint src/api-client.py

generate-tests:
	pop "write pytest tests for API client" -o tests/test_api.py
	pytest tests/test_api.py
```

## Related Tools

### extract-code.py

Standalone code extractor for manual use:

```bash
# Direct usage
cat llm-response.txt | /Users/jay/extract-code.py --lang python > script.py

# Extract all code blocks
/Users/jay/extract-code.py /tmp/pop-response.txt --all > combined.py

# Extract specific language from file
/Users/jay/extract-code.py response.md --lang javascript > script.js
```

### Direct Ollama Usage

For interactive conversation mode:

```bash
# Start chat session
ollama run llama3.2

# With system prompt
ollama run codellama "You are a Python expert. Help me optimize this code: [paste code]"
```

### Combining with Other Tools

```bash
# With curl for API prompts
curl -s https://api.example.com/spec | pop "create a client for this API" -o client.py

# With git diff
git diff | pop "write a commit message for these changes" -o commit-msg.txt

# With find
find . -name "*.py" -exec wc -l {} \; | pop "analyze these file sizes and suggest refactoring" -o analysis.md
```

## Configuration Tips

### Model Aliases

Create shell aliases for your favorite models:

```bash
# Add to ~/.zshrc or ~/.bashrc
alias pop-code='pop -m codellama'
alias pop-fast='pop -m mistral'
alias pop-smart='pop -m qwen2.5-coder'

# Usage
pop-code "write a binary search tree" -o bst.py
pop-fast "write a simple logger" -o logger.py
```

### Custom Templates Directory

```bash
# Create templates directory
mkdir -p ~/.pop-templates

# Add common templates
cat > ~/.pop-templates/api-client.txt << 'EOF'
Write a production-ready REST API client with:
- Comprehensive error handling
- Request/response logging
- Retry logic with exponential backoff
- Connection pooling
- Timeout configuration
- Authentication support
EOF

# Use templates
pop -f ~/.pop-templates/api-client.txt -o client.py
```

### Default Output Directory

```bash
# Create function in ~/.zshrc
popgen() {
    local script_name="$1"
    shift
    pop "$@" -o ~/generated-scripts/"$script_name"
}

# Usage
popgen parser.py "write a log parser"
```

## Comparison with Other Tools

| Feature | pop | GitHub Copilot CLI | ChatGPT Code Interpreter |
|---------|-----|-------------------|-------------------------|
| Local execution | ✓ | ✗ | ✗ |
| Offline capable | ✓ | ✗ | ✗ |
| Model selection | ✓ | ✗ | Limited |
| Stdin support | ✓ | ✗ | ✗ |
| File input | ✓ | ✗ | ✓ |
| Auto code extraction | ✓ | ✓ | Manual |
| Free/Open source | ✓ | ✗ | ✗ |

## License

This is a personal utility script. Use and modify as needed.

## Contributing

Found a bug or have a feature request? Open an issue or submit a pull request.

## See Also

- [Ollama Documentation](https://ollama.ai)
- [Ollama Model Library](https://ollama.ai/library)
- [extract-code.py source](file:///Users/jay/extract-code.py)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## Changelog

### v4.1 - Enhanced Fix Mode with Dependency Detection
- **Dependency detection**: Automatically detects missing Python modules by running the script
- **AI-powered issue analysis**: Uses the model to analyze scripts and identify all issues
- **Requirements file generation**: Creates `<script>_requirements.txt` for missing dependencies
- **Installation instructions**: Adds clear installation instructions as comments in fixed scripts
- **Issue logging**: Logs all issues found, missing dependencies, and fixes applied
- **Common package mapping**: Maps module names to pip packages (e.g., `cv2` → `opencv-python`, `PIL` → `Pillow`)
- **Enhanced fix prompts**: Includes detected issues in the fix prompt for better AI context

### v4.0 - Python Rewrite & Fix Mode
- **Complete Python rewrite**: pop is now written entirely in Python (was bash)
- **Fix mode (`-fix:<script>`)**: Fix existing scripts with AI assistance
  - Send existing code + instructions to model
  - Output saved as `<script>_popfix` (original unchanged)
  - Same verification/retry logic as generation mode
- **Session ID prefixes**: `pop-` for generation, `pop-fix-` for fix mode
- **Improved portability**: No bash dependencies, runs anywhere Python runs

### v3.2 - Output Verification & Auto-Retry
- **Output verification**: Automatic syntax checking for Python, Bash, JavaScript, Ruby, Perl
- **Completeness verification**: Model-based review to detect truncated or incomplete code
- **Auto-retry with feedback**: Automatically retries up to 3 times when verification fails
- **`--no-verify` flag**: Skip verification for faster (but less reliable) output
- **Session metadata**: Tracks attempt count and verification status in session metadata
- **Verification enabled by default**: All outputs verified unless `--no-verify` is specified

### v3.1 - Model Discovery, Minimal Mode & Quality Improvements
- **`pop model` command**: List all available Ollama models
- **Minimal mode (`--minimal`)**: Stronger prompts + automatic comment stripping for cleaner code
- **Automatic shebang insertion**: Scripts automatically get appropriate shebang lines (#!/usr/bin/env python3, #!/bin/bash, etc.)
- **Incremental file naming**: Output files auto-increment (script.py → script-1.py → script-2.py) to prevent overwrites
- **Hide thinking by default**: Model thinking process hidden by default, use `--thinking` to show
- **Improved list ordering**: Past sessions now displayed oldest-first (most recent at bottom)
- **Comment stripping**: extract-code.py can now strip comments with `--strip-comments` flag

### v3.0 - Background Execution & Session Management
- **Background execution**: All code generation runs in background, returns shell immediately
- **Session tracking**: All sessions saved to `~/.pop/sessions/` with logs and metadata
- **Default model**: Now defaults to `qwen3:latest` (no interactive selection needed)
- **`pop list` command**: View all active and past sessions on host
- **Active session tracking**: Track running sessions in `~/.pop/active/`
- Session logs include timestamps, model info, prompts, and full LLM output
- Status tracking (success/failed) for all sessions
- Improved user experience with immediate shell return

### v2.0 - "pop" rename
- Renamed from `ai-script` to `pop` (Prompt-Oriented Programming)
- Added interactive model selection
- Added stdin input support
- Added `-f` file input option
- Added `-m` model selection flag
- Improved argument parsing with proper flags
- Better error messages with colors
- Updated all documentation

### v1.0 - Initial release
- Basic script generation with gpt-oss
- Code extraction with language filtering
- Executable output files
