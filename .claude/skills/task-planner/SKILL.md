# Task Planner Agent Skill

## Description
Automatically processes new markdown files from the Inbox, analyzes their content, and generates actionable step-by-step plans. Integrates with the AI Employee Vault system for seamless task management.

## Trigger
- Command: `/task-planner` or `task-planner`
- Auto-trigger: Can be invoked by file watchers or schedulers when new .md files appear in Inbox

## Capabilities
- Reads and analyzes .md files from `AI_Employee_Vault/Inbox/`
- Generates structured, actionable plans with clear steps
- Places plans in `AI_Employee_Vault/Needs_Action/` for review
- Tracks processed files to ensure idempotency
- Logs all actions to `logs/actions.log`
- Integrates with vault-file-manager for file lifecycle management

## Workflow

1. **Scan Inbox**
   - Check `AI_Employee_Vault/Inbox/` for new .md files
   - Skip files already processed (tracked in `logs/processed.json`)

2. **Analyze Content**
   - Read file content and extract key information
   - Identify task type, priority, and requirements
   - Determine complexity and dependencies

3. **Generate Plan**
   - Create structured plan with:
     - Executive summary
     - Step-by-step breakdown
     - Success criteria
     - Potential risks/blockers
     - Estimated effort level

4. **Save Plan**
   - Write plan to `AI_Employee_Vault/Needs_Action/Plan_<original_filename>.md`
   - Include metadata (timestamp, source file, status)

5. **Mark as Processed**
   - Add file to processed tracking
   - Log action with timestamp
   - Optionally move source file to Done (if vault-file-manager available)

## Output Format

Plans are saved as markdown files with frontmatter:

```markdown
---
type: action_plan
status: pending
priority: <derived from content>
created_at: <timestamp>
source_file: AI_Employee_Vault/Inbox/<filename>
related_files: []
---

# Plan: <Task Title>

## Executive Summary
Brief overview of what needs to be accomplished.

## Step-by-Step Plan
1. **Step 1**: Description
   - Sub-task A
   - Sub-task B
2. **Step 2**: Description
   - Sub-task A

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Potential Risks/Blockers
- Risk 1: Description and mitigation
- Risk 2: Description and mitigation

## Effort Estimate
Low/Medium/High

## Notes
Additional context or considerations.
```

## Integration Points

- **File Watcher**: Can be triggered when new .md files detected
- **Task Scheduler**: Can run on schedule (e.g., every 5 minutes)
- **Vault File Manager**: Moves processed files to Done folder
- **Dashboard**: Updates task counts and status

## Configuration

The skill uses these paths (relative to project root):
- Input: `AI_Employee_Vault/Inbox/*.md`
- Output: `AI_Employee_Vault/Needs_Action/Plan_*.md`
- Tracking: `logs/processed.json`
- Logging: `logs/actions.log`

## Usage Examples

### Manual Invocation
```bash
python scripts/task_planner.py
```

### Via Claude Code
```
/task-planner
```

### With File Watcher Integration
The file watcher can be configured to trigger this skill when .md files appear.

## Error Handling

- Gracefully handles missing directories (creates them)
- Logs all errors to `logs/actions.log`
- Continues processing other files if one fails
- Validates file format before processing

## Idempotency

The skill maintains a processed files registry in `logs/processed.json`:
```json
{
  "processed_files": [
    {
      "filename": "task_request.md",
      "processed_at": "2026-02-27 10:30:00",
      "plan_created": "Plan_task_request.md"
    }
  ]
}
```

This ensures files are only processed once, even if the skill runs multiple times.

## Dependencies

- Python 3.7+
- Standard library only (no external packages required)
- Compatible with existing AI Employee Vault structure

## Notes

- Only processes .md files (ignores .txt and other formats)
- Preserves original files in Inbox until vault-file-manager moves them
- Plans are human-readable and ready for immediate action
- Designed for autonomous operation with minimal supervision
