# Agent Skill: Process Tasks

## Trigger Phrase
When the user says: **"Process tasks"**

## Workflow

1. **Open the Needs_Action folder**
   - List all task files (*.md) in the `Needs_Action/` directory

2. **Read each task file**
   - Parse the YAML frontmatter (type, status, source, filename, created_at)
   - Read the task content and understand what actions are required

3. **Understand the task from its content**
   - Identify the task type and required actions
   - Determine what has been completed or needs to be done

4. **Mark status as completed inside the file**
   - Update `status: pending` → `status: completed`
   - Add `completed_at: <timestamp>` to frontmatter
   - Check off all checkboxes in the task file

5. **Move the file to the Done folder**
   - Move the task file from `Needs_Action/` to `Done/`

6. **Update Dashboard.md**
   - Add the task under "Completed Tasks" section
   - Remove it from "Pending Tasks" section if present

7. **Append entry to System_Log.md**
   - Add a short log entry describing what was completed
   - Include timestamp and task details

## Rules

- Always log important actions in System_Log.md
- Never take destructive actions without confirmation
- Keep task files structured
- If unsure, ask for clarification
