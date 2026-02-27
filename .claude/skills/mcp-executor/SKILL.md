# MCP Executor Agent Skill

## Description
Action orchestrator that executes external operations like sending emails and posting to social media. Implements human-in-the-loop approval workflows for sensitive actions, ensuring safe and controlled automation.

## Trigger
- Command: `/mcp-executor` or `mcp-executor`
- Manual: `python scripts/mcp_executor.py`
- Automated: Called by scheduler or watcher
- Programmatic: Import and use as library

## Capabilities
- Execute external actions (email, LinkedIn, etc.)
- Human-in-the-loop approval workflow
- Action request parsing from files
- Retry logic with exponential backoff
- Comprehensive error handling
- Action status tracking
- Detailed logging to `logs/actions.log`
- Integration with existing agent skills

## Architecture

The MCP Executor is the **action execution layer** that bridges planning and external systems:

```
┌─────────────────────────────────────────────────────────┐
│              PLANNING LAYER                             │
│  Task Planner → Creates action requests                │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              APPROVAL LAYER                             │
│  Needs_Approval/ → Human reviews sensitive actions     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              MCP EXECUTOR (Action Layer)                │
│  • Reads action requests                               │
│  • Validates approvals                                 │
│  • Executes external actions                           │
│  • Logs results                                        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ├──> Gmail API (send emails)
                 ├──> LinkedIn API (post updates)
                 └──> Other integrations (extensible)
```

## Action Types

### 1. Email Actions (Gmail)

Send emails via Gmail API or SMTP.

**Action Request Format**:
```yaml
---
action_type: email
status: pending
requires_approval: true
created_at: 2026-02-27 11:00:00
---

# Email: Project Update

## To
recipient@example.com

## Subject
Weekly Project Status Update

## Body
Hi Team,

Here's this week's progress update:
- Completed 5 tasks
- 3 tasks in progress
- No blockers

Best regards,
AI Employee
```

**Approval Required**: Yes (default for emails)

### 2. LinkedIn Actions

Post updates to LinkedIn using the existing linkedin-post skill.

**Action Request Format**:
```yaml
---
action_type: linkedin
status: pending
requires_approval: true
created_at: 2026-02-27 11:00:00
---

# LinkedIn Post: Feature Launch

Just shipped a major feature! 🚀

Key highlights:
✓ 50% performance improvement
✓ New user dashboard
✓ Mobile app updates

#tech #innovation #productlaunch
```

**Approval Required**: Yes (default for social media)

### 3. Webhook Actions

Send data to external webhooks.

**Action Request Format**:
```yaml
---
action_type: webhook
status: pending
requires_approval: false
url: https://api.example.com/webhook
method: POST
---

# Webhook: Task Completion Notification

{
  "event": "task_completed",
  "task_id": "123",
  "completed_at": "2026-02-27 11:00:00"
}
```

**Approval Required**: No (configurable)

## Workflow

### Standard Execution Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. Action Request Created                              │
│     - File placed in AI_Employee_Vault/Actions/         │
│     - Contains action type and parameters               │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  2. MCP Executor Scans Actions Folder                   │
│     - Finds pending action requests                     │
│     - Parses action metadata                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  3. Check Approval Requirement                          │
│     - If requires_approval: true → goto step 4          │
│     - If requires_approval: false → goto step 6         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  4. Move to Needs_Approval Folder                       │
│     - Wait for human approval                           │
│     - Human reviews and approves/rejects                │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  5. Check Approval Status                               │
│     - If approved: goto step 6                          │
│     - If rejected: goto step 8 (log rejection)          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  6. Execute Action                                      │
│     - Call appropriate handler (email, linkedin, etc.)  │
│     - Retry on transient failures                       │
│     - Log execution details                             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  7. Update Status & Move to Done                        │
│     - Mark as completed or failed                       │
│     - Move file to Done folder                          │
│     - Log final status                                  │
└─────────────────────────────────────────────────────────┘
```

### Approval Workflow

```
[Action Created] → [Needs_Approval/]
                         ↓
                   [Human Reviews]
                         ↓
                    ┌────┴────┐
                    ↓         ↓
              [Approved]  [Rejected]
                    ↓         ↓
              [Execute]   [Log & Archive]
```

**Approval Methods**:
1. **File-based**: Add `approved: true` to frontmatter
2. **Status change**: Change `status: pending` to `status: approved`
3. **Move to Actions**: Move from Needs_Approval back to Actions folder

## Configuration

### Action Request File Format

All action requests use YAML frontmatter + markdown body:

```yaml
---
action_type: email|linkedin|webhook
status: pending|approved|rejected|completed|failed
requires_approval: true|false
created_at: YYYY-MM-DD HH:MM:SS
retry_count: 0
max_retries: 3
priority: high|medium|low
---

# Action Title

Action-specific content here...
```

### Folder Structure

```
AI_Employee_Vault/
├── Actions/              # Pending actions (auto-execute if no approval needed)
├── Needs_Approval/       # Actions awaiting human approval
└── Done/                 # Completed actions (success or failure)
```

## Usage

### Command Line

```bash
# Process all pending actions
python scripts/mcp_executor.py

# Process specific action file
python scripts/mcp_executor.py --file AI_Employee_Vault/Actions/email_update.md

# Dry run (don't execute, just validate)
python scripts/mcp_executor.py --dry-run

# Force execution (skip approval check - use with caution)
python scripts/mcp_executor.py --force
```

### Programmatic Usage

```python
from scripts.mcp_executor import MCPExecutor

# Create executor
executor = MCPExecutor()

# Process all pending actions
results = executor.process_all_actions()

# Execute specific action
result = executor.execute_action_file("AI_Employee_Vault/Actions/post.md")

# Create and execute action programmatically
action = {
    "action_type": "linkedin",
    "content": "Just completed 5 tasks today! 🚀",
    "requires_approval": True
}
result = executor.execute_action(action)
```

### Integration with Scheduler

Add to `run_ai_employee.py`:

```python
# After task planning
from scripts.mcp_executor import MCPExecutor

executor = MCPExecutor()
executor.process_all_actions()
```

## Action Handlers

### Email Handler

Sends emails via Gmail API or SMTP.

**Requirements**:
- Gmail API credentials (OAuth2) or SMTP credentials
- `google-auth`, `google-auth-oauthlib`, `google-api-python-client`

**Configuration** (`.env`):
```env
GMAIL_SENDER=your.email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
# OR
GMAIL_CREDENTIALS_FILE=credentials.json
```

**Example Action**:
```yaml
---
action_type: email
requires_approval: true
---

# Email: Weekly Report

## To
team@example.com

## CC
manager@example.com

## Subject
Weekly AI Employee Report

## Body
This week's accomplishments:
- Processed 25 tasks
- Generated 15 plans
- Posted 3 LinkedIn updates
```

### LinkedIn Handler

Posts to LinkedIn using the existing `post_linkedin.py` script.

**Requirements**:
- LinkedIn credentials in `.env`
- Playwright installed

**Example Action**:
```yaml
---
action_type: linkedin
requires_approval: true
---

# LinkedIn: Milestone Announcement

Excited to announce we've processed 100 tasks this month! 🎉

The AI Employee system is working great:
✓ Automated task planning
✓ Smart prioritization
✓ Seamless workflow

#automation #ai #productivity
```

### Webhook Handler

Sends HTTP requests to external APIs.

**Example Action**:
```yaml
---
action_type: webhook
requires_approval: false
url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
method: POST
headers:
  Content-Type: application/json
---

# Webhook: Slack Notification

{
  "text": "AI Employee completed 5 tasks",
  "channel": "#updates"
}
```

## Error Handling

### Retry Logic

- **Max Retries**: 3 (configurable)
- **Backoff**: Exponential (1s, 2s, 4s)
- **Retryable Errors**: Network timeouts, temporary API failures
- **Non-Retryable**: Invalid credentials, malformed requests

### Error States

```yaml
status: failed
error_message: "LinkedIn login failed: Invalid credentials"
retry_count: 3
last_attempt: 2026-02-27 11:05:00
```

### Error Notifications

Failed actions are:
1. Logged to `logs/actions.log`
2. Moved to `Done/` with `status: failed`
3. Optionally trigger alert (email, Slack, etc.)

## Logging

All actions are logged to `logs/actions.log`:

```
[2026-02-27 11:00:00] [INFO] [MCP] Processing action: email_update.md
[2026-02-27 11:00:00] [INFO] [MCP] Action type: email, requires_approval: true
[2026-02-27 11:00:00] [INFO] [MCP] Moving to Needs_Approval for human review
[2026-02-27 11:05:00] [INFO] [MCP] Action approved, executing...
[2026-02-27 11:05:01] [SUCCESS] [MCP] Email sent to: team@example.com
[2026-02-27 11:05:01] [INFO] [MCP] Action completed, moved to Done/
```

## Security

### Approval Requirements

**Always Require Approval For**:
- Sending emails
- Posting to social media
- Financial transactions
- Data deletion
- External API calls with side effects

**Optional Approval For**:
- Read-only operations
- Internal logging
- Status updates
- Webhooks to trusted services

### Credential Management

- Store credentials in `.env` file
- Never commit credentials to git
- Use OAuth2 when possible
- Rotate credentials regularly
- Limit API permissions to minimum required

### Audit Trail

Every action creates an audit trail:
- Original request file (preserved)
- Approval timestamp (if applicable)
- Execution timestamp
- Result (success/failure)
- Error details (if failed)

## Integration Examples

### Example 1: Email Notification After Task Completion

```python
# In task_planner.py, after creating plan
def notify_completion(task_name):
    action_content = f"""---
action_type: email
requires_approval: false
---

# Email: Task Completed

## To
user@example.com

## Subject
Task Completed: {task_name}

## Body
Your task "{task_name}" has been processed and a plan has been created.
Check AI_Employee_Vault/Needs_Action/ for the plan.
"""

    with open("AI_Employee_Vault/Actions/notify_completion.md", "w") as f:
        f.write(action_content)
```

### Example 2: LinkedIn Post After Milestone

```python
# In scheduler, after processing cycle
if session_processed >= 10:
    action_content = f"""---
action_type: linkedin
requires_approval: true
---

# LinkedIn: Milestone Reached

Just processed {session_processed} tasks today! 🚀

The AI Employee system is crushing it:
✓ Automated planning
✓ Smart prioritization
✓ Seamless execution

#automation #productivity
"""

    with open("AI_Employee_Vault/Actions/milestone_post.md", "w") as f:
        f.write(action_content)
```

### Example 3: Webhook to Slack

```python
# Send Slack notification
action_content = """---
action_type: webhook
requires_approval: false
url: https://hooks.slack.com/services/YOUR/WEBHOOK
method: POST
---

# Webhook: Daily Summary

{
  "text": "AI Employee Daily Summary",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Tasks Processed:* 15\\n*Plans Created:* 12\\n*Status:* ✅ All systems operational"
      }
    }
  ]
}
"""
```

## Monitoring

### Check Pending Actions

```bash
# List pending actions
ls AI_Employee_Vault/Actions/

# List actions awaiting approval
ls AI_Employee_Vault/Needs_Approval/

# Check recent completions
ls -lt AI_Employee_Vault/Done/ | head -10
```

### View Logs

```bash
# Real-time monitoring
tail -f logs/actions.log

# Filter by action type
grep "email" logs/actions.log

# Check for failures
grep "FAILED" logs/actions.log
```

### Statistics

```bash
# Count actions by status
grep "status: completed" AI_Employee_Vault/Done/*.md | wc -l
grep "status: failed" AI_Employee_Vault/Done/*.md | wc -l

# Count by action type
grep "action_type: email" AI_Employee_Vault/Done/*.md | wc -l
grep "action_type: linkedin" AI_Employee_Vault/Done/*.md | wc -l
```

## Extensibility

### Adding New Action Types

1. Create handler function:
```python
def handle_slack_action(action_data):
    # Implementation
    pass
```

2. Register handler:
```python
ACTION_HANDLERS = {
    "email": handle_email_action,
    "linkedin": handle_linkedin_action,
    "webhook": handle_webhook_action,
    "slack": handle_slack_action,  # New handler
}
```

3. Document action format in SKILL.md

### Custom Approval Logic

Override approval check:
```python
def requires_approval(action_data):
    # Custom logic
    if action_data["action_type"] == "email":
        # Only require approval for external emails
        return "@external.com" in action_data["to"]
    return action_data.get("requires_approval", False)
```

## Best Practices

1. **Always Test with Dry Run**
   ```bash
   python scripts/mcp_executor.py --dry-run
   ```

2. **Use Approval for Sensitive Actions**
   - Emails to external recipients
   - Public social media posts
   - Financial transactions

3. **Monitor Logs Regularly**
   - Check for failed actions
   - Review approval queue
   - Verify execution results

4. **Set Appropriate Retry Limits**
   - 3 retries for transient failures
   - 0 retries for invalid credentials
   - Exponential backoff between retries

5. **Clean Up Completed Actions**
   - Archive old Done/ files
   - Keep last 30 days
   - Export audit logs

## Troubleshooting

### Actions Not Executing

```bash
# Check if actions exist
ls AI_Employee_Vault/Actions/

# Check action format
cat AI_Employee_Vault/Actions/action.md

# Run with verbose logging
python scripts/mcp_executor.py --verbose
```

### Email Sending Fails

```bash
# Check credentials
cat .env | grep GMAIL

# Test SMTP connection
python -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587)"

# Check app password (not regular password)
```

### LinkedIn Posting Fails

```bash
# Check LinkedIn credentials
cat .env | grep LINKEDIN

# Test LinkedIn script directly
python scripts/post_linkedin.py "Test post"

# Check for CAPTCHA/2FA
```

## Dependencies

```
# Core (no external deps for basic functionality)
python>=3.7

# Email support
google-auth>=2.0.0
google-auth-oauthlib>=0.5.0
google-api-python-client>=2.0.0

# OR for SMTP
# (standard library smtplib)

# LinkedIn support
# (uses existing post_linkedin.py)

# Webhook support
requests>=2.28.0
```

## Files

```
.claude/skills/mcp-executor/
└── SKILL.md                    # This documentation

scripts/
└── mcp_executor.py             # Main executor script

AI_Employee_Vault/
├── Actions/                    # Pending actions
├── Needs_Approval/             # Awaiting approval
└── Done/                       # Completed actions

logs/
└── actions.log                 # Execution logs
```

## Notes

- Designed for safe, controlled automation
- Human-in-the-loop prevents unintended actions
- Extensible architecture for new action types
- Comprehensive audit trail
- Production-ready error handling

---

**Built for Hackathon 0 Mahab - Silver Tier**
