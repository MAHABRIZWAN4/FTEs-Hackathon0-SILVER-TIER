# Human Approval Agent Skill

## Description
Provides a reusable human-in-the-loop approval workflow for any agent or script in the system. Creates approval requests, waits for human decision, and returns the result with timeout handling.

## Trigger
- Programmatic: Import and call from other scripts
- Manual: `python scripts/request_approval.py`
- Library: Use as approval gateway in automated workflows

## Capabilities
- Create approval request files in Needs_Approval folder
- Block execution until human responds (APPROVED/REJECTED)
- Configurable timeout (default: 1 hour)
- Polling mechanism to detect approval status
- Comprehensive logging to `logs/actions.log`
- Return approval decision to calling code
- Handle timeout scenarios gracefully
- Support for approval metadata and context

## Architecture

The Human Approval Agent acts as a **synchronous approval gateway**:

```
┌─────────────────────────────────────────────────────────┐
│  CALLING AGENT/SCRIPT                                   │
│  (Task Planner, Scheduler, MCP Executor, etc.)          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  HUMAN APPROVAL AGENT                                   │
│  • Creates approval request file                        │
│  • Blocks execution (polling)                           │
│  • Waits for human decision                             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  NEEDS_APPROVAL FOLDER                                  │
│  File: approval_request_TIMESTAMP.md                    │
│  Status: PENDING → APPROVED/REJECTED                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  HUMAN REVIEWER                                         │
│  • Opens file                                           │
│  • Reviews details                                      │
│  • Writes APPROVED or REJECTED                          │
│  • Saves file                                           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  HUMAN APPROVAL AGENT                                   │
│  • Detects decision                                     │
│  • Returns result to caller                             │
│  • Logs decision                                        │
│  • Moves file to Done/                                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  CALLING AGENT/SCRIPT                                   │
│  • Receives approval decision                           │
│  • Proceeds or aborts based on result                   │
└─────────────────────────────────────────────────────────┘
```

## Approval Request Format

All approval requests use YAML frontmatter + markdown body:

```yaml
---
request_id: approval_20260227_110000
status: PENDING
created_at: 2026-02-27 11:00:00
timeout_at: 2026-02-27 12:00:00
requester: task_planner
priority: high
---

# Approval Request: Send Email to External Client

## Action Details
**Type**: Email
**Recipient**: client@external.com
**Subject**: Project Status Update

## Context
The task planner has generated a project status email that needs to be sent to an external client. This requires approval due to external communication policy.

## Email Preview
```
Dear Client,

Your project is 80% complete. We're on track for delivery next week.

Best regards,
AI Employee
```

## Decision Required
Please review the email content and decide:

- Write **APPROVED** below to send the email
- Write **REJECTED** below to cancel

---

**YOUR DECISION**:

```

## Workflow

### Standard Approval Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. Request Approval                                    │
│     - Calling script invokes request_approval()         │
│     - Provides action details and context               │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  2. Create Approval File                                │
│     - Generate unique request ID                        │
│     - Create file in Needs_Approval/                    │
│     - Set timeout (default: 1 hour)                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  3. Wait for Decision (Polling)                         │
│     - Check file every 10 seconds                       │
│     - Look for APPROVED or REJECTED                     │
│     - Check if timeout exceeded                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  4. Decision Detected or Timeout                        │
│     - APPROVED → Return True                            │
│     - REJECTED → Return False                           │
│     - TIMEOUT → Raise TimeoutError                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  5. Cleanup                                             │
│     - Update file with final status                     │
│     - Move to Done/ folder                              │
│     - Log decision                                      │
└─────────────────────────────────────────────────────────┘
```

## Usage

### Programmatic Usage (Recommended)

```python
from scripts.request_approval import request_approval, ApprovalTimeout

# Simple approval request
try:
    approved = request_approval(
        title="Send Email to Client",
        description="Email contains project status update",
        details={
            "recipient": "client@example.com",
            "subject": "Project Update"
        }
    )

    if approved:
        print("Approved! Proceeding with action...")
        send_email()
    else:
        print("Rejected. Action cancelled.")

except ApprovalTimeout:
    print("Approval request timed out. Action cancelled.")
```

### Advanced Usage with Custom Timeout

```python
from scripts.request_approval import request_approval
import time

# Request with 30-minute timeout
approved = request_approval(
    title="Deploy to Production",
    description="Deploy version 2.0 to production servers",
    details={
        "version": "2.0.0",
        "servers": ["prod-1", "prod-2", "prod-3"],
        "estimated_downtime": "5 minutes"
    },
    timeout_seconds=1800,  # 30 minutes
    priority="high",
    requester="deployment_script"
)

if approved:
    deploy_to_production()
```

### Command Line Usage

```bash
# Request approval with title and description
python scripts/request_approval.py \
    --title "Delete Old Logs" \
    --description "Delete logs older than 90 days" \
    --timeout 3600

# Request with JSON details
python scripts/request_approval.py \
    --title "Send Bulk Email" \
    --description "Send newsletter to 1000 subscribers" \
    --details '{"count": 1000, "type": "newsletter"}' \
    --priority high
```

## Integration Examples

### Example 1: Task Planner Integration

```python
# In task_planner.py
from scripts.request_approval import request_approval

def process_high_priority_task(task_data):
    # Request approval for high-priority tasks
    approved = request_approval(
        title=f"Process High Priority Task: {task_data['name']}",
        description=f"Task requires immediate attention: {task_data['description']}",
        details={
            "priority": "high",
            "estimated_time": "2 hours",
            "resources_needed": ["database", "api_access"]
        },
        timeout_seconds=1800,  # 30 minutes
        priority="high"
    )

    if approved:
        execute_task(task_data)
    else:
        log_rejection(task_data)
```

### Example 2: MCP Executor Integration

```python
# In mcp_executor.py
from scripts.request_approval import request_approval

def execute_email_action(email_data):
    # Request approval before sending external emails
    if is_external_recipient(email_data['to']):
        approved = request_approval(
            title="Send Email to External Recipient",
            description=f"Email to: {email_data['to']}",
            details={
                "to": email_data['to'],
                "subject": email_data['subject'],
                "body_preview": email_data['body'][:200]
            },
            priority="medium"
        )

        if not approved:
            return False, "Email rejected by human reviewer"

    # Proceed with sending
    return send_email(email_data)
```

### Example 3: Scheduler Integration

```python
# In run_ai_employee.py
from scripts.request_approval import request_approval

def process_cycle():
    # Request approval before processing large batch
    if inbox_count > 50:
        approved = request_approval(
            title="Process Large Batch",
            description=f"Process {inbox_count} files in inbox",
            details={
                "file_count": inbox_count,
                "estimated_time": f"{inbox_count * 2} seconds"
            },
            timeout_seconds=600  # 10 minutes
        )

        if not approved:
            log("Batch processing cancelled by human")
            return

    # Proceed with processing
    process_inbox_files()
```

## Configuration

### Parameters

```python
request_approval(
    title: str,                    # Required: Short title
    description: str,              # Required: Detailed description
    details: dict = None,          # Optional: Additional context
    timeout_seconds: int = 3600,   # Default: 1 hour
    priority: str = "medium",      # low, medium, high
    requester: str = None,         # Calling script name
    poll_interval: int = 10        # Check every N seconds
)
```

### Return Values

- `True`: Approved
- `False`: Rejected
- `ApprovalTimeout` exception: Timeout exceeded

### Environment Variables

```bash
# Default timeout (seconds)
export APPROVAL_TIMEOUT=3600

# Polling interval (seconds)
export APPROVAL_POLL_INTERVAL=10

# Auto-approve for testing (use with caution!)
export APPROVAL_AUTO_APPROVE=false
```

## Approval File Format

### Pending Request

```yaml
---
request_id: approval_20260227_110000
status: PENDING
created_at: 2026-02-27 11:00:00
timeout_at: 2026-02-27 12:00:00
requester: task_planner
priority: high
---

# Approval Request: [Title]

## Action Details
[Details here]

## Decision Required
Write **APPROVED** or **REJECTED** below:

---

**YOUR DECISION**:
```

### After Human Review

```yaml
---
request_id: approval_20260227_110000
status: APPROVED
created_at: 2026-02-27 11:00:00
reviewed_at: 2026-02-27 11:15:00
timeout_at: 2026-02-27 12:00:00
requester: task_planner
priority: high
reviewer_notes: Looks good, approved
---

# Approval Request: [Title]

## Action Details
[Details here]

## Decision Required
Write **APPROVED** or **REJECTED** below:

---

**YOUR DECISION**: APPROVED

Reviewer notes: This action is safe to proceed.
```

## Logging

All approval requests are logged to `logs/actions.log`:

```
[2026-02-27 11:00:00] [INFO] [APPROVAL] Request created: approval_20260227_110000
[2026-02-27 11:00:00] [INFO] [APPROVAL] Title: Send Email to Client
[2026-02-27 11:00:00] [INFO] [APPROVAL] Waiting for human decision (timeout: 3600s)
[2026-02-27 11:00:10] [INFO] [APPROVAL] Polling for decision... (attempt 1)
[2026-02-27 11:00:20] [INFO] [APPROVAL] Polling for decision... (attempt 2)
[2026-02-27 11:15:00] [SUCCESS] [APPROVAL] Request approved: approval_20260227_110000
[2026-02-27 11:15:00] [INFO] [APPROVAL] Reviewer notes: Looks good
[2026-02-27 11:15:00] [INFO] [APPROVAL] Moved to Done/
```

## Error Handling

### Timeout Handling

```python
from scripts.request_approval import request_approval, ApprovalTimeout

try:
    approved = request_approval(
        title="Critical Action",
        description="Requires immediate approval",
        timeout_seconds=300  # 5 minutes
    )
except ApprovalTimeout as e:
    print(f"Approval timed out after {e.timeout_seconds} seconds")
    # Handle timeout (e.g., send notification, log, retry)
    send_timeout_notification()
```

### Invalid Decision Handling

If human writes something other than APPROVED/REJECTED:
- Continue polling (treat as still pending)
- Log warning about invalid format
- Provide clear instructions in file

### File System Errors

- If Needs_Approval folder doesn't exist: Create it
- If file can't be created: Raise exception
- If file is deleted during polling: Treat as rejection

## Best Practices

1. **Use Descriptive Titles**
   ```python
   # Good
   request_approval(title="Send Email to 100 External Clients")

   # Bad
   request_approval(title="Send Email")
   ```

2. **Provide Context in Details**
   ```python
   request_approval(
       title="Delete User Data",
       description="Permanent deletion of user account",
       details={
           "user_id": "12345",
           "email": "user@example.com",
           "data_size": "2.5 GB",
           "reason": "User requested account deletion"
       }
   )
   ```

3. **Set Appropriate Timeouts**
   - Urgent actions: 5-15 minutes
   - Normal actions: 1 hour (default)
   - Low priority: 24 hours
   - Never use infinite timeout

4. **Handle Rejections Gracefully**
   ```python
   if not approved:
       log_rejection(action)
       notify_requester("Action was rejected")
       # Don't retry automatically
   ```

5. **Use Priority Levels**
   - `high`: Urgent, needs immediate attention
   - `medium`: Normal workflow (default)
   - `low`: Can wait, review when convenient

## Monitoring

### Check Pending Approvals

```bash
# List all pending approvals
ls AI_Employee_Vault/Needs_Approval/approval_*.md

# Count pending approvals
ls AI_Employee_Vault/Needs_Approval/approval_*.md | wc -l

# View oldest pending approval
ls -t AI_Employee_Vault/Needs_Approval/approval_*.md | tail -1 | xargs cat
```

### View Approval History

```bash
# Recent approvals
grep "APPROVAL.*approved" logs/actions.log | tail -10

# Recent rejections
grep "APPROVAL.*rejected" logs/actions.log | tail -10

# Timeouts
grep "APPROVAL.*timeout" logs/actions.log | tail -10
```

### Statistics

```bash
# Approval rate
approved=$(grep "APPROVAL.*approved" logs/actions.log | wc -l)
rejected=$(grep "APPROVAL.*rejected" logs/actions.log | wc -l)
echo "Approval rate: $((approved * 100 / (approved + rejected)))%"
```

## Troubleshooting

### Approval Not Detected

**Problem**: Human wrote APPROVED but script still waiting

**Solutions**:
1. Check spelling (must be exact: APPROVED or REJECTED)
2. Ensure file is saved
3. Check file permissions
4. Verify file is in correct folder

### Timeout Too Short

**Problem**: Timeout before human can review

**Solutions**:
1. Increase timeout: `timeout_seconds=7200` (2 hours)
2. Send notification when approval needed
3. Use async approval (don't block)

### Too Many Pending Approvals

**Problem**: Backlog of pending approvals

**Solutions**:
1. Review and clear old approvals
2. Increase timeout for low-priority items
3. Implement approval delegation
4. Use auto-approval for trusted actions

## Advanced Features

### Async Approval (Non-Blocking)

```python
from scripts.request_approval import create_approval_request

# Create request but don't wait
request_id = create_approval_request(
    title="Background Task",
    description="Can be reviewed later"
)

# Continue with other work
do_other_work()

# Check later
from scripts.request_approval import check_approval_status

status = check_approval_status(request_id)
if status == "APPROVED":
    execute_action()
```

### Approval with Callback

```python
from scripts.request_approval import request_approval_async

def on_approved():
    print("Action approved!")
    execute_action()

def on_rejected():
    print("Action rejected")
    log_rejection()

def on_timeout():
    print("Approval timed out")
    send_notification()

# Non-blocking with callbacks
request_approval_async(
    title="Async Action",
    description="Will callback when decided",
    on_approved=on_approved,
    on_rejected=on_rejected,
    on_timeout=on_timeout
)
```

## Security Considerations

1. **Validate Decisions**: Only accept exact "APPROVED" or "REJECTED"
2. **Audit Trail**: All approvals logged with timestamp and reviewer
3. **Timeout Enforcement**: Never wait indefinitely
4. **File Permissions**: Ensure only authorized users can approve
5. **No Auto-Approval**: Require explicit human decision

## Dependencies

- Python 3.7+
- Standard library only (no external packages)
- Compatible with existing AI Employee Vault structure

## Files

```
.claude/skills/human-approval/
└── SKILL.md                    # This documentation

scripts/
└── request_approval.py         # Main approval script

AI_Employee_Vault/
├── Needs_Approval/             # Pending approval requests
└── Done/                       # Completed approvals

logs/
└── actions.log                 # Approval activity logs
```

## Notes

- Designed for synchronous approval workflows
- Blocks execution until decision received
- Suitable for critical actions requiring human oversight
- Integrates seamlessly with all other agent skills
- Production-ready with comprehensive error handling

---

**Built for Hackathon 0 Mahab - Silver Tier**
