# Agent Skill: Make a Plan for Tasks

## Trigger Phrase
When the user says: **"Make a plan for tasks"**

## Workflow

1. **Read all files in Needs_Action**
   - List all task files (*.md) in the `Needs_Action/` directory
   - Read each task file's content and frontmatter

2. **Categorize what types of tasks are pending**
   - Group tasks by type (file_review, general_task, etc.)
   - Note priority levels if specified
   - Identify related files or dependencies

3. **Create a new Plan file**
   - Location: `Plans/`
   - Filename format: `Plan_YYYY-MM-DD_HH-MM-SS.md`
   - Include timestamp in the filename for uniqueness

4. **Plan file structure:**
   ```markdown
   # Plan <timestamp>

   ## Summary of Pending Tasks
   (List all pending tasks with brief descriptions)

   ## Suggested Order of Execution
   (Recommended priority/order for completing tasks)

   ## Risks or Unclear Items
   (Flag any ambiguous or potentially problematic tasks)

   ## Strategy
   (Short paragraph explaining the overall approach)
   ```

## Rules

- This is **only a planning document** - do not complete tasks
- Do not move or modify task files in Needs_Action
- Keep the plan concise and actionable
- Update the Dashboard if needed to reflect planning status
