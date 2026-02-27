# AI Employee Agent Skills - Silver Tier

A collection of autonomous agent skills for task management, monitoring, and social media automation.

## 🎯 Overview

This project contains three production-ready agent skills that work together to create an autonomous AI employee system:

1. **Task Planner Agent** - Analyzes markdown files and generates actionable plans
2. **Vault Watcher Agent** - Monitors inbox for new files and triggers processing
3. **LinkedIn Auto-Post Agent** - Automates LinkedIn posting with browser automation

## 📁 Project Structure

```
F:\Hackathon 0 Mahab\Silver Tier\
├── .claude/
│   └── skills/
│       ├── task-planner/
│       │   └── SKILL.md
│       ├── vault-watcher/
│       │   └── SKILL.md
│       └── linkedin-post/
│           └── SKILL.md
├── scripts/
│   ├── task_planner.py          # Analyzes files & creates plans
│   ├── watch_inbox.py           # Monitors inbox & triggers planner
│   └── post_linkedin.py         # LinkedIn automation
├── AI_Employee_Vault/
│   ├── Inbox/                   # Drop new tasks here
│   ├── Needs_Action/            # Generated plans appear here
│   ├── Needs_Approval/          # High-priority tasks
│   └── Done/                    # Completed tasks
├── logs/
│   ├── actions.log              # All activity logs
│   ├── processed.json           # Idempotency tracking
│   └── screenshots/             # Debug screenshots
├── .env.example                 # Credentials template
├── .gitignore                   # Security configuration
├── requirements_linkedin.txt    # LinkedIn dependencies
└── LINKEDIN_SETUP.md           # LinkedIn setup guide
```

## 🚀 Quick Start

### 1. Task Planner Agent

**Purpose**: Automatically analyze task files and generate step-by-step plans.

```bash
# Run manually
python scripts/task_planner.py

# What it does:
# - Scans AI_Employee_Vault/Inbox/ for .md files
# - Analyzes content (priority, type, complexity)
# - Generates structured plans
# - Saves to AI_Employee_Vault/Needs_Action/
```

**Example**:
```bash
# Create a task file
echo "# Fix login bug\nUsers can't login with special characters in password" > AI_Employee_Vault/Inbox/fix_login.md

# Run planner
python scripts/task_planner.py

# Result: Plan_fix_login.md created in Needs_Action/
```

### 2. Vault Watcher Agent

**Purpose**: Continuously monitor inbox and automatically trigger task planner.

```bash
# Start watcher (runs continuously)
python scripts/watch_inbox.py

# What it does:
# - Monitors AI_Employee_Vault/Inbox/ every 15 seconds
# - Detects new .md files
# - Automatically runs task planner
# - Logs all activity
```

**Background operation**:
```bash
# Linux/Mac
nohup python scripts/watch_inbox.py > logs/watcher.log 2>&1 &

# Windows PowerShell
Start-Process python -ArgumentList "scripts/watch_inbox.py" -WindowStyle Hidden
```

### 3. LinkedIn Auto-Post Agent

**Purpose**: Automate posting to LinkedIn using browser automation.

**Setup**:
```bash
# Install dependencies
pip install playwright python-dotenv
playwright install chromium

# Configure credentials
cp .env.example .env
# Edit .env with your LinkedIn credentials
```

**Usage**:
```bash
# Post to LinkedIn
python scripts/post_linkedin.py "Just shipped a new feature! 🚀"

# Debug mode (visible browser)
python scripts/post_linkedin.py "Test post" --headless=false
```

## 🔄 Integrated Workflow

Here's how all three skills work together:

```
┌─────────────────────────────────────────────────────────────┐
│  1. User drops task file in Inbox/                         │
│     Example: "implement_feature.md"                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Vault Watcher detects new file (within 15 seconds)     │
│     Logs: [DETECTED] New file: implement_feature.md        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Task Planner automatically triggered                    │
│     - Analyzes content                                      │
│     - Extracts priority (high/medium/low)                   │
│     - Identifies task type (feature/bug/research)           │
│     - Generates step-by-step plan                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Plan created in Needs_Action/                           │
│     File: Plan_implement_feature.md                         │
│     Contains: steps, risks, effort estimate                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  5. (Optional) Post update to LinkedIn                      │
│     "Working on exciting new feature! 🚀"                   │
└─────────────────────────────────────────────────────────────┘
```

## 💡 Usage Examples

### Example 1: Autonomous Task Processing

```bash
# Terminal 1: Start the watcher
python scripts/watch_inbox.py

# Terminal 2: Drop tasks in inbox
echo "# Research cloud providers
Compare AWS, Azure, GCP for our migration" > AI_Employee_Vault/Inbox/cloud_research.md

# Watcher automatically detects and processes
# Check Needs_Action/ for the generated plan
```

### Example 2: Batch Processing

```bash
# Create multiple tasks
echo "# Fix payment bug" > AI_Employee_Vault/Inbox/fix_payment.md
echo "# Add dark mode" > AI_Employee_Vault/Inbox/dark_mode.md
echo "# Update docs" > AI_Employee_Vault/Inbox/update_docs.md

# Process all at once
python scripts/task_planner.py

# All plans created in Needs_Action/
```

### Example 3: LinkedIn Integration

```python
# scripts/post_task_completion.py
from scripts.post_linkedin import LinkedInPoster
import os

# Read completed task
task_file = "AI_Employee_Vault/Done/task_feature.md"
with open(task_file, 'r') as f:
    content = f.read()

# Extract task title
title = content.split('\n')[0].strip('# ')

# Post to LinkedIn
poster = LinkedInPoster()
poster.post(f"✅ Just completed: {title}\n\n#productivity #automation")
```

## 📊 Features

### Task Planner
- ✅ Smart priority detection (high/medium/low)
- ✅ Task type classification (bug_fix, feature, research, etc.)
- ✅ Step-by-step plan generation
- ✅ Risk assessment and mitigation
- ✅ Effort estimation
- ✅ Idempotent operation (no duplicates)

### Vault Watcher
- ✅ Real-time monitoring (15s polling)
- ✅ Automatic workflow triggering
- ✅ Comprehensive logging
- ✅ Error recovery
- ✅ Production-ready
- ✅ Minimal resource usage

### LinkedIn Auto-Post
- ✅ Automated login
- ✅ Text post creation
- ✅ Retry logic (max 2 retries)
- ✅ Error handling (CAPTCHA, 2FA detection)
- ✅ Screenshot debugging
- ✅ Headless operation
- ✅ Multiple selector strategies

## 🔒 Security

**Critical**: Never commit sensitive credentials!

```bash
# .env file is in .gitignore
# Always use .env for credentials
# Never hardcode passwords
```

**Checklist**:
- ✅ `.env` in `.gitignore`
- ✅ Strong, unique passwords
- ✅ Regular credential rotation
- ✅ Logs excluded from git
- ✅ Screenshots excluded from git

## 📝 Logging

All activities are logged to `logs/actions.log`:

```
[2026-02-27 10:30:00] [INFO] [WATCHER] Started monitoring
[2026-02-27 10:30:15] [INFO] [DETECTED] New file: task.md
[2026-02-27 10:30:16] [SUCCESS] Plan created: Plan_task.md
[2026-02-27 10:30:17] [INFO] [LINKEDIN] Post published
```

**View logs**:
```bash
# Real-time monitoring
tail -f logs/actions.log

# Last 50 lines
tail -n 50 logs/actions.log

# Search for errors
grep ERROR logs/actions.log
```

## 🛠️ Troubleshooting

### Task Planner Issues
```bash
# No files processed
# Check: Are there .md files in Inbox?
ls AI_Employee_Vault/Inbox/*.md

# Check processed registry
cat logs/processed.json
```

### Vault Watcher Issues
```bash
# Watcher not detecting files
# Check: Is watcher running?
ps aux | grep watch_inbox

# Check logs
tail -f logs/actions.log
```

### LinkedIn Issues
```bash
# Login failed
# Check: Credentials in .env
cat .env

# Check: Screenshots for visual debugging
ls -lt logs/screenshots/

# Run in visible mode
python scripts/post_linkedin.py "Test" --headless=false
```

## 📚 Documentation

- **Task Planner**: `.claude/skills/task-planner/SKILL.md`
- **Vault Watcher**: `.claude/skills/vault-watcher/SKILL.md`
- **LinkedIn Post**: `.claude/skills/linkedin-post/SKILL.md`
- **LinkedIn Setup**: `LINKEDIN_SETUP.md`

## ⚠️ Important Notes

### LinkedIn Automation
- LinkedIn's ToS generally prohibit automation
- Use for authorized personal use only
- Limit to 5-10 posts/day
- May require updates if LinkedIn changes UI
- Use at your own risk

### Rate Limiting
- Task Planner: No limits
- Vault Watcher: 15s polling (configurable)
- LinkedIn: 5-10 posts/day recommended

### Maintenance
- Monitor logs regularly
- Update selectors if LinkedIn UI changes
- Rotate credentials periodically
- Review processed files registry

## 🚦 Status

| Skill | Status | Production Ready |
|-------|--------|------------------|
| Task Planner | ✅ Complete | Yes |
| Vault Watcher | ✅ Complete | Yes |
| LinkedIn Post | ✅ Complete | Yes (with setup) |

## 📦 Dependencies

**Core** (no external deps):
- task_planner.py
- watch_inbox.py

**LinkedIn** (requires installation):
```bash
pip install playwright python-dotenv
playwright install chromium
```

## 🎓 Learning Resources

- Playwright: https://playwright.dev/python/
- Python dotenv: https://pypi.org/project/python-dotenv/
- LinkedIn API: https://docs.microsoft.com/en-us/linkedin/

## 📄 License

This project is for educational and personal use. Review LinkedIn's Terms of Service before using automation features.

## 🤝 Contributing

This is a hackathon project. Feel free to extend and customize for your needs.

## 📞 Support

Check logs for detailed error information:
- `logs/actions.log` - All activity
- `logs/screenshots/` - Visual debugging
- Individual SKILL.md files for detailed docs

---

**Built with ❤️ for Hackathon 0 Mahab - Silver Tier**
