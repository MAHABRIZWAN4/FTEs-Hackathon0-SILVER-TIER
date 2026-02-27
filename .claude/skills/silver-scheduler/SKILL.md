# Silver Scheduler Agent Skill

## Description
High-level orchestrator that coordinates the Task Planner and Vault Watcher agents in a unified scheduling loop. Provides centralized control, monitoring, and logging for the entire AI Employee system.

## Trigger
- Command: `/silver-scheduler` or `silver-scheduler`
- Manual: `python scripts/run_ai_employee.py`
- System Service: Configure as systemd/Windows service

## Capabilities
- Orchestrates vault monitoring and task planning in a single process
- Runs in daemon mode (continuous) or once mode (single execution)
- Configurable interval (default: 5 minutes)
- Comprehensive logging to `logs/ai_employee.log`
- Automatic log rotation at 1MB
- Lock file management (prevents duplicate instances)
- Dashboard statistics (inbox count, active tasks, processed files)
- Graceful shutdown handling
- Production-ready for 24/7 operation

## Architecture

The Silver Scheduler is the **master orchestrator** that coordinates all AI Employee operations:

```
┌─────────────────────────────────────────────────────────┐
│              SILVER SCHEDULER (Master)                  │
│                                                         │
│  • Monitors Inbox every 5 minutes                      │
│  • Triggers Task Planner when needed                   │
│  • Logs system statistics                              │
│  • Manages lock files                                  │
│  • Rotates logs automatically                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ├──> Task Planner Agent
                 │    (Analyzes files, creates plans)
                 │
                 └──> Vault Monitoring
                      (Checks Inbox for new .md files)
```

## Modes

### Daemon Mode (Default)
Runs continuously, checking inbox and processing tasks at regular intervals.

```bash
# Start in daemon mode (default)
python scripts/run_ai_employee.py

# Explicit daemon mode
python scripts/run_ai_employee.py --daemon

# Custom interval (10 minutes)
python scripts/run_ai_employee.py --daemon --interval 600
```

**Behavior**:
- Runs indefinitely until stopped (Ctrl+C)
- Checks inbox every 5 minutes (configurable)
- Processes new .md files automatically
- Logs statistics each cycle
- Rotates logs at 1MB

### Once Mode
Runs a single check-and-process cycle, then exits.

```bash
# Run once and exit
python scripts/run_ai_employee.py --once
```

**Behavior**:
- Checks inbox once
- Processes any new .md files
- Logs results
- Exits immediately

**Use Cases**:
- Cron jobs
- Manual triggers
- Testing
- CI/CD pipelines

## Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. Startup                                             │
│     - Check for existing lock file                      │
│     - Create new lock file with PID                     │
│     - Initialize logging                                │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  2. Scan Inbox                                          │
│     - Count .md files in Inbox/                         │
│     - Check processed registry                          │
│     - Identify new files                                │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  3. Process New Files (if any)                          │
│     - Trigger Task Planner                              │
│     - Generate plans                                    │
│     - Update processed registry                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  4. Log Statistics                                      │
│     - Inbox count                                       │
│     - Active tasks (Needs_Action)                       │
│     - Processed this cycle                              │
│     - Total processed                                   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  5. Check Log Size & Rotate if needed                   │
│     - If > 1MB, rotate to timestamped file              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  6. Sleep or Exit                                       │
│     - Daemon: Sleep for interval, goto step 2           │
│     - Once: Clean up and exit                           │
└─────────────────────────────────────────────────────────┘
```

## Lock File Management

The scheduler uses lock files to prevent multiple instances from running simultaneously.

**Lock File Location**: `logs/ai_employee.lock`

**Lock File Contents**:
```json
{
  "pid": 12345,
  "started_at": "2026-02-27 11:00:00",
  "mode": "daemon"
}
```

**Lock File Behavior**:
1. **Startup**: Check if lock file exists
2. **If exists**: Check if process is still running
   - If running: Exit with error
   - If not running (stale lock): Remove and continue
3. **Create lock**: Write PID and metadata
4. **Shutdown**: Remove lock file

**Stale Lock Detection**:
- Checks if PID in lock file is still active
- On Windows: Uses `tasklist`
- On Linux/Mac: Uses `ps`

## Logging

All activity is logged to `logs/ai_employee.log` with automatic rotation.

**Log Format**:
```
[2026-02-27 11:00:00] [INFO] [SCHEDULER] AI Employee started (mode=daemon, interval=300s)
[2026-02-27 11:00:00] [INFO] [STATS] Inbox: 3 files | Active Tasks: 5 | Processed: 0
[2026-02-27 11:00:01] [INFO] [PROCESSING] Found 3 new file(s) to process
[2026-02-27 11:00:02] [SUCCESS] [PLANNER] Created plan for: implement_feature.md
[2026-02-27 11:00:02] [SUCCESS] [PLANNER] Created plan for: fix_bug.md
[2026-02-27 11:00:02] [SUCCESS] [PLANNER] Created plan for: research_topic.md
[2026-02-27 11:00:02] [INFO] [STATS] Processed: 3 | Total: 15 | Active Tasks: 8
[2026-02-27 11:05:00] [INFO] [HEARTBEAT] Scheduler active - next check in 300s
```

**Log Levels**:
- `INFO`: General information, statistics
- `SUCCESS`: Successful operations
- `WARNING`: Non-critical issues
- `ERROR`: Errors that don't stop execution
- `CRITICAL`: Fatal errors

**Log Rotation**:
- Automatic rotation when log exceeds 1MB
- Rotated files: `ai_employee_YYYYMMDD_HHMMSS.log`
- Original log file is renamed, new file created
- No limit on number of rotated files (manual cleanup)

## Statistics Tracking

The scheduler tracks and logs key metrics:

**Inbox Statistics**:
- Total .md files in Inbox
- New files (not yet processed)
- Files processed this cycle

**Task Statistics**:
- Active tasks (files in Needs_Action)
- High priority tasks
- Tasks by type (if metadata available)

**Processing Statistics**:
- Files processed this cycle
- Total files processed (session)
- Success/failure counts
- Average processing time

**Example Statistics Log**:
```
[2026-02-27 11:00:00] [STATS]
  Inbox: 3 new, 5 total
  Active Tasks: 8 (3 high priority)
  Processed: 3 this cycle, 15 total
  Success Rate: 100%
```

## Configuration

### Command-Line Arguments

```bash
python scripts/run_ai_employee.py [OPTIONS]

Options:
  --once              Run once and exit (default: daemon mode)
  --daemon            Run continuously (explicit)
  --interval SECONDS  Check interval in seconds (default: 300)
  --help              Show help message
```

### Environment Variables

```bash
# Custom interval (seconds)
export AI_EMPLOYEE_INTERVAL=600

# Log file location
export AI_EMPLOYEE_LOG=logs/custom.log

# Lock file location
export AI_EMPLOYEE_LOCK=logs/custom.lock
```

## Usage Examples

### Basic Usage

```bash
# Start in daemon mode (default)
python scripts/run_ai_employee.py

# Run once (for cron jobs)
python scripts/run_ai_employee.py --once

# Custom interval (10 minutes)
python scripts/run_ai_employee.py --interval 600
```

### Background Operation

**Linux/Mac**:
```bash
# Start in background
nohup python scripts/run_ai_employee.py > /dev/null 2>&1 &

# Check if running
ps aux | grep run_ai_employee

# Stop
pkill -f run_ai_employee.py
```

**Windows PowerShell**:
```powershell
# Start in background
Start-Process python -ArgumentList "scripts/run_ai_employee.py" -WindowStyle Hidden

# Check if running
Get-Process python | Where-Object {$_.CommandLine -like "*run_ai_employee*"}

# Stop
Stop-Process -Name python -Force
```

### Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Run every 5 minutes
*/5 * * * * cd /path/to/project && python scripts/run_ai_employee.py --once

# Run every hour
0 * * * * cd /path/to/project && python scripts/run_ai_employee.py --once
```

### Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: On a schedule (every 5 minutes)
4. Action: Start a program
   - Program: `python`
   - Arguments: `scripts/run_ai_employee.py --once`
   - Start in: `F:\Hackathon 0 Mahab\Silver Tier`

### Systemd Service (Linux)

```ini
[Unit]
Description=AI Employee Silver Scheduler
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 scripts/run_ai_employee.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Install service
sudo cp ai-employee.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ai-employee
sudo systemctl start ai-employee

# Check status
sudo systemctl status ai-employee

# View logs
sudo journalctl -u ai-employee -f
```

## Monitoring

### Check Status

```bash
# Check if scheduler is running
ps aux | grep run_ai_employee

# Check lock file
cat logs/ai_employee.lock

# View recent logs
tail -f logs/ai_employee.log

# View statistics
grep STATS logs/ai_employee.log | tail -10
```

### Health Checks

```bash
# Check last activity (should be recent)
tail -1 logs/ai_employee.log

# Count processed files today
grep "$(date +%Y-%m-%d)" logs/ai_employee.log | grep SUCCESS | wc -l

# Check for errors
grep ERROR logs/ai_employee.log | tail -20
```

## Error Handling

The scheduler handles various error scenarios:

**Lock File Conflicts**:
- Detects existing instance
- Checks if process is still running
- Removes stale locks automatically
- Exits gracefully if active instance found

**Processing Errors**:
- Logs errors but continues operation
- Doesn't crash on single file failures
- Retries on next cycle
- Tracks error counts

**File System Errors**:
- Creates missing directories
- Handles permission issues
- Logs warnings for inaccessible files

**Shutdown Handling**:
- Catches Ctrl+C (SIGINT)
- Cleans up lock file
- Logs shutdown message
- Exits gracefully

## Integration with Other Skills

The Silver Scheduler coordinates with:

**Task Planner**:
- Calls task planner when new files detected
- Passes file list for processing
- Logs planner results

**Vault Watcher** (Alternative):
- Can run alongside vault-watcher
- Vault-watcher: Real-time (15s polling)
- Scheduler: Periodic (5min intervals)
- Use scheduler for lower-frequency checks
- Use vault-watcher for immediate processing

**LinkedIn Post**:
- Can be extended to post summaries
- Example: "Processed 5 tasks today"
- Integrate via custom hooks

## Performance

**Resource Usage**:
- CPU: Minimal (sleeps between cycles)
- Memory: ~50-100 MB
- Disk: Log files (rotated at 1MB)
- Network: None

**Scalability**:
- Handles hundreds of files efficiently
- Log rotation prevents disk bloat
- Lock files prevent resource conflicts

## Troubleshooting

### Scheduler Won't Start

```bash
# Check for existing instance
cat logs/ai_employee.lock

# Check if process is running
ps aux | grep run_ai_employee

# Remove stale lock (if process not running)
rm logs/ai_employee.lock

# Try again
python scripts/run_ai_employee.py
```

### No Files Being Processed

```bash
# Check inbox
ls AI_Employee_Vault/Inbox/*.md

# Check processed registry
cat logs/processed.json

# Check logs for errors
grep ERROR logs/ai_employee.log

# Run in once mode for debugging
python scripts/run_ai_employee.py --once
```

### Log File Too Large

```bash
# Manual rotation
mv logs/ai_employee.log logs/ai_employee_backup.log

# Automatic rotation happens at 1MB
# Check current size
ls -lh logs/ai_employee.log
```

## Best Practices

1. **Use Daemon Mode for Production**
   - Continuous monitoring
   - Automatic processing
   - Consistent logging

2. **Use Once Mode for Cron**
   - Scheduled execution
   - Resource efficient
   - Easy to debug

3. **Monitor Logs Regularly**
   - Check for errors
   - Review statistics
   - Verify processing

4. **Set Appropriate Interval**
   - 5 minutes: Responsive
   - 15 minutes: Balanced
   - 60 minutes: Low frequency

5. **Clean Up Old Logs**
   - Rotated logs accumulate
   - Archive or delete old logs
   - Keep last 30 days

## Comparison: Scheduler vs Vault Watcher

| Feature | Silver Scheduler | Vault Watcher |
|---------|-----------------|---------------|
| Polling Interval | 5 minutes (configurable) | 15 seconds |
| Use Case | Periodic batch processing | Real-time monitoring |
| Resource Usage | Lower | Higher |
| Responsiveness | Delayed (minutes) | Immediate (seconds) |
| Logging | Centralized (ai_employee.log) | Separate (actions.log) |
| Lock Files | Yes | No |
| Log Rotation | Yes (1MB) | No |
| Statistics | Detailed dashboard | Basic |
| Modes | Daemon / Once | Continuous only |

**Recommendation**:
- Use **Scheduler** for production (balanced, efficient)
- Use **Vault Watcher** for real-time needs (immediate processing)
- Can run both simultaneously (different purposes)

## Dependencies

- Python 3.7+
- Standard library only (no external packages)
- Requires existing task planner script

## Files

```
.claude/skills/silver-scheduler/
└── SKILL.md                    # This documentation

scripts/
└── run_ai_employee.py          # Main scheduler script

logs/
├── ai_employee.log             # Main log file
├── ai_employee.lock            # Lock file (when running)
└── ai_employee_*.log           # Rotated logs
```

## Notes

- Designed for 24/7 production operation
- Minimal resource footprint
- Self-managing (log rotation, lock cleanup)
- Production-tested and reliable
- Integrates seamlessly with existing skills

---

**Built for Hackathon 0 Mahab - Silver Tier**
