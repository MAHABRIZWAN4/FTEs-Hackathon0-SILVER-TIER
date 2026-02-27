# Vault Watcher Agent Skill

## Description
Continuously monitors the AI Employee Vault Inbox for new markdown files and automatically triggers the AI processing workflow. This skill acts as the entry point for autonomous task processing, detecting new work and initiating the planning pipeline.

## Trigger
- Command: `/vault-watcher` or `vault-watcher`
- Auto-start: Can be configured to run as a background service
- Manual: `python scripts/watch_inbox.py`

## Capabilities
- Real-time monitoring of `AI_Employee_Vault/Inbox/` directory
- Detects new .md files only (ignores other file types)
- Triggers task planner automatically for each new file
- Idempotent operation (never processes the same file twice)
- Comprehensive logging to `logs/actions.log`
- Configurable polling interval (10-30 seconds)
- Graceful error handling and recovery
- Production-ready with minimal resource usage

## Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. Monitor Inbox (every 10-30 seconds)                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  2. Detect new .md files                                │
│     - Compare current files vs tracked files            │
│     - Filter for .md extension only                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  3. Log detection                                       │
│     - Timestamp + filename → logs/actions.log           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  4. Trigger AI Processing                               │
│     - Execute: python scripts/task_planner.py           │
│     - Task planner analyzes file & creates plan         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  5. Mark as processed                                   │
│     - Add to watched files registry                     │
│     - Prevent duplicate processing                      │
└─────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables
- `WATCH_INTERVAL`: Polling interval in seconds (default: 15)
- `INBOX_PATH`: Path to inbox folder (default: AI_Employee_Vault/Inbox)

### File Locations
- **Monitored Directory**: `AI_Employee_Vault/Inbox/`
- **Log File**: `logs/actions.log`
- **Tracking Registry**: In-memory (resets on restart)
- **Task Planner Script**: `scripts/task_planner.py`

## AI Processing Workflow

When a new .md file is detected, the watcher triggers:

1. **Task Planner** (`scripts/task_planner.py`)
   - Analyzes file content
   - Extracts priority, type, requirements
   - Generates step-by-step plan
   - Saves plan to `AI_Employee_Vault/Needs_Action/`

2. **Downstream Processing** (optional)
   - Plans can be picked up by task scheduler
   - Human review in Needs_Action folder
   - Further automation as configured

## Usage Examples

### Start Watcher (Foreground)
```bash
python scripts/watch_inbox.py
```

### Start Watcher (Background - Linux/Mac)
```bash
nohup python scripts/watch_inbox.py > logs/watcher.log 2>&1 &
```

### Start Watcher (Background - Windows)
```powershell
Start-Process python -ArgumentList "scripts/watch_inbox.py" -WindowStyle Hidden
```

### Via Claude Code
```
/vault-watcher
```

### Custom Interval
```bash
WATCH_INTERVAL=20 python scripts/watch_inbox.py
```

## Logging Format

All actions are logged to `logs/actions.log`:

```
[2026-02-27 10:30:15] [WATCHER] Started monitoring AI_Employee_Vault/Inbox (interval: 15s)
[2026-02-27 10:30:45] [DETECTED] New file: implement_auth.md
[2026-02-27 10:30:45] [PROCESSING] Triggering task planner for: implement_auth.md
[2026-02-27 10:30:46] [SUCCESS] Plan created: Plan_implement_auth.md
[2026-02-27 10:30:46] [TRACKED] Added to processed registry: implement_auth.md
```

## Error Handling

The watcher handles various error scenarios:

- **Missing Directories**: Automatically creates required folders
- **Permission Errors**: Logs error and continues monitoring
- **Task Planner Failures**: Logs error but doesn't crash watcher
- **File System Issues**: Retries on next polling cycle
- **Keyboard Interrupt**: Graceful shutdown with cleanup

## Idempotency

The watcher maintains an in-memory set of processed files:
- Files are tracked once detected and processed
- On restart, existing files in Inbox are added to "already seen" list
- Only NEW files added after watcher starts are processed
- Task planner has its own persistent tracking in `logs/processed.json`

## Performance

- **CPU Usage**: Minimal (sleeps between polls)
- **Memory Usage**: Low (small file tracking set)
- **Disk I/O**: Minimal (directory listing only)
- **Polling Interval**: Configurable (default 15s)
- **Scalability**: Handles hundreds of files efficiently

## Integration Points

### Upstream
- **Manual File Drops**: Users/systems drop .md files in Inbox
- **API Integration**: External systems can write to Inbox
- **Email-to-File**: Email parser could create .md files

### Downstream
- **Task Planner**: Automatically invoked for each new file
- **Task Scheduler**: Picks up plans from Needs_Action
- **Dashboard**: Updated with processing status
- **Notifications**: Can be extended to send alerts

## Production Deployment

### Systemd Service (Linux)
```ini
[Unit]
Description=AI Employee Vault Watcher
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 scripts/watch_inbox.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Windows Service
Use NSSM (Non-Sucking Service Manager) or Task Scheduler

### Docker
```dockerfile
CMD ["python", "scripts/watch_inbox.py"]
```

## Monitoring & Health Checks

The watcher logs heartbeat messages every 10 cycles:
```
[2026-02-27 10:35:00] [HEARTBEAT] Watcher active - 0 files processed this session
```

Monitor `logs/actions.log` for:
- Regular heartbeat messages
- Error patterns
- Processing success rate

## Limitations

- **Not Real-Time**: Uses polling (10-30s delay)
- **In-Memory Tracking**: Processed files list resets on restart
- **Single Instance**: Run only one watcher per Inbox
- **No File Locking**: Assumes files are fully written before detection

## Future Enhancements

- File system events (inotify/watchdog) for real-time detection
- Persistent tracking across restarts
- Multi-folder monitoring
- Webhook notifications
- Metrics dashboard
- Health check endpoint

## Dependencies

- Python 3.7+
- Standard library only (no external packages)
- Requires `scripts/task_planner.py` to be present
- Compatible with existing AI Employee Vault structure

## Notes

- Designed for 24/7 operation
- Minimal resource footprint
- Self-healing (continues on errors)
- Integrates seamlessly with existing vault system
- Production-tested and reliable
