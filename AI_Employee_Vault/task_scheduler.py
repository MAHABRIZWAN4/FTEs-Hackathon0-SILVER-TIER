"""
Task Scheduler - Bronze Tier AI Employee

This script schedules and executes tasks based on priority and timing.
It integrates with the file watcher and task management system.

Features:
- Priority-based task execution
- Scheduled task processing
- Integration with existing task management system
"""

import os
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading
import queue
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colors
init(autoreset=True)

class TaskScheduler:
    def __init__(self):
        self.task_queue = queue.PriorityQueue()
        self.running = False
        self.scheduler_thread = None

        # Task priority mapping
        self.priority_map = {
            'high': 1,
            'medium': 2,
            'low': 3
        }

    def print_banner(self):
        """Print a colorful banner for the Task Scheduler."""
        print()
        print(Fore.MAGENTA + Style.BRIGHT + "=" * 60)
        print(Fore.MAGENTA + Style.BRIGHT + "  [TASK SCHEDULER] - AI Employee (Bronze Tier)")
        print(Fore.MAGENTA + Style.BRIGHT + "=" * 60)
        print()

    def load_tasks_from_needs_action(self) -> List[Dict]:
        """Load tasks from Needs_Action folder and parse their metadata."""
        tasks = []
        needs_action_dir = os.path.join("AI_Employee_Vault", "Needs_Action")

        if not os.path.exists(needs_action_dir):
            os.makedirs(needs_action_dir, exist_ok=True)
            return tasks

        for filename in os.listdir(needs_action_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(needs_action_dir, filename)
                task_data = self.parse_task_file(filepath)
                if task_data:
                    tasks.append(task_data)

        return tasks

    def parse_task_file(self, filepath: str) -> Optional[Dict]:
        """Parse a task file to extract metadata and content."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter if present
            lines = content.split('\n')
            if len(lines) > 0 and lines[0].strip() == '---':
                end_frontmatter_idx = -1
                for i in range(1, len(lines)):
                    if lines[i].strip() == '---':
                        end_frontmatter_idx = i
                        break

                if end_frontmatter_idx != -1:
                    frontmatter = '\n'.join(lines[1:end_frontmatter_idx])
                    task_body = '\n'.join(lines[end_frontmatter_idx + 1:])

                    # Parse frontmatter manually
                    metadata = {}
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip().strip('"\'')

                    return {
                        'filepath': filepath,
                        'filename': os.path.basename(filepath),
                        'priority': metadata.get('priority', 'medium'),
                        'status': metadata.get('status', 'pending'),
                        'type': metadata.get('type', 'general_task'),
                        'created_at': metadata.get('created_at', ''),
                        'content': task_body
                    }

            # If no frontmatter, create default task
            return {
                'filepath': filepath,
                'filename': os.path.basename(filepath),
                'priority': 'medium',
                'status': 'pending',
                'type': 'general_task',
                'created_at': '',
                'content': content
            }

        except Exception as e:
            print(f"Error parsing task file {filepath}: {e}")
            return None

    def schedule_tasks(self):
        """Load tasks and add them to the priority queue."""
        tasks = self.load_tasks_from_needs_action()

        for task in tasks:
            if task['status'] == 'pending':
                priority_num = self.priority_map.get(task['priority'], 2)

                # Create a tuple for the priority queue: (priority, timestamp, task)
                queue_item = (priority_num, time.time(), task)
                self.task_queue.put(queue_item)

                # Color based on priority
                priority_color = Fore.RED if task['priority'] == 'high' else Fore.YELLOW if task['priority'] == 'medium' else Fore.GREEN
                print(Fore.CYAN + "  [*] " + Fore.WHITE + f"Scheduled: " + Fore.WHITE + f"{task['filename']}" + Fore.WHITE + " | Priority: " + priority_color + Style.BRIGHT + task['priority'].upper())

    def execute_next_task(self):
        """Execute the next highest priority task from the queue."""
        if not self.task_queue.empty():
            priority, timestamp, task = self.task_queue.get()

            print(Fore.MAGENTA + Style.BRIGHT + "  [>] " + Fore.WHITE + f"Executing: " + Fore.YELLOW + task['filename'])

            # High priority tasks go to Needs_Approval, others go to Done
            if task['priority'] == 'high':
                self.move_to_approval(task)
            else:
                self.complete_task(task)

            return True
        return False

    def move_to_approval(self, task: Dict):
        """Move a task to Needs_Approval folder for review."""
        try:
            # Read the original content
            with open(task['filepath'], 'r', encoding='utf-8') as f:
                content = f.read()

            # Update the frontmatter to mark as awaiting approval
            lines = content.split('\n')
            updated_content = content

            if len(lines) > 0 and lines[0].strip() == '---':
                # Find the end of frontmatter
                end_frontmatter_idx = -1
                for i in range(1, len(lines)):
                    if lines[i].strip() == '---':
                        end_frontmatter_idx = i
                        break

                if end_frontmatter_idx != -1:
                    frontmatter = '\n'.join(lines[1:end_frontmatter_idx])
                    task_body = '\n'.join(lines[end_frontmatter_idx + 1:])

                    # Update status
                    updated_frontmatter = []
                    for line in frontmatter.split('\n'):
                        if line.startswith('status:'):
                            updated_frontmatter.append('status: awaiting_approval')
                        else:
                            updated_frontmatter.append(line)

                    updated_content = f"---\n{'\\n'.join(updated_frontmatter)}\n---\n{task_body}"

            # Move the file to Needs_Approval folder
            approval_folder = os.path.join("AI_Employee_Vault", "Needs_Approval")
            if not os.path.exists(approval_folder):
                os.makedirs(approval_folder, exist_ok=True)

            approval_filepath = os.path.join(approval_folder, task['filename'])
            with open(approval_filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            # Remove the original file
            os.remove(task['filepath'])

            print(Fore.YELLOW + Style.BRIGHT + "  [!] " + Fore.WHITE + f"Moved to Approval: " + Fore.YELLOW + task['filename'])

        except Exception as e:
            print(Fore.RED + Style.BRIGHT + "  [X] " + Fore.WHITE + f"Error moving to approval {task['filename']}: {e}")

    def complete_task(self, task: Dict):
        """Complete a task by moving it to the Done folder."""
        try:
            # Read the original content
            with open(task['filepath'], 'r', encoding='utf-8') as f:
                content = f.read()

            # Update the frontmatter to mark as completed
            lines = content.split('\n')
            updated_content = content

            if len(lines) > 0 and lines[0].strip() == '---':
                # Find the end of frontmatter
                end_frontmatter_idx = -1
                for i in range(1, len(lines)):
                    if lines[i].strip() == '---':
                        end_frontmatter_idx = i
                        break

                if end_frontmatter_idx != -1:
                    frontmatter = '\n'.join(lines[1:end_frontmatter_idx])
                    task_body = '\n'.join(lines[end_frontmatter_idx + 1:])

                    # Update status and add completion time
                    updated_frontmatter = []
                    for line in frontmatter.split('\n'):
                        if line.startswith('status:'):
                            updated_frontmatter.append('status: completed')
                        elif line.startswith('completed_at:'):
                            # Skip old completed_at line, we'll add a new one
                            continue
                        else:
                            updated_frontmatter.append(line)

                    # Add completed_at line
                    updated_frontmatter.append(f"completed_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                    updated_content = f"---\n{'\\n'.join(updated_frontmatter)}\n---\n{task_body}"

            # Move the file to Done folder
            done_folder = os.path.join("AI_Employee_Vault", "Done")
            if not os.path.exists(done_folder):
                os.makedirs(done_folder, exist_ok=True)

            done_filepath = os.path.join(done_folder, task['filename'])
            with open(done_filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            # Remove the original file
            os.remove(task['filepath'])

            # Update dashboard
            self.update_dashboard(task)

            print(Fore.GREEN + Style.BRIGHT + "  [+] " + Fore.WHITE + f"Completed: " + Fore.GREEN + task['filename'])

        except Exception as e:
            print(Fore.RED + Style.BRIGHT + "  [X] " + Fore.WHITE + f"Error completing task {task['filename']}: {e}")

    def update_dashboard(self, task: Dict):
        """Update the dashboard with completed task information."""
        try:
            dashboard_path = os.path.join("AI_Employee_Vault", "Dashboard.md")

            # Read current dashboard
            if os.path.exists(dashboard_path):
                with open(dashboard_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = "# Dashboard\n\n## Pending Tasks\n\n<!-- Add pending tasks here -->\n\n## Completed Tasks\n\n## Quick Notes\n\n<!-- Add quick notes and reminders here -->"

            # Add completed task to the completed tasks section
            completed_section_marker = "## Completed Tasks"
            completed_task_entry = f"\n\n- **{task['filename']}** - Completed {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n  - Type: {task.get('type', 'general_task')}\n  - Priority: {task.get('priority', 'medium')}"

            # Insert the new completed task
            parts = content.split(completed_section_marker)
            if len(parts) >= 2:
                new_content = f"{parts[0]}{completed_section_marker}{completed_task_entry}{parts[1]}"
            else:
                new_content = content  # Fallback if section marker not found

            # Write updated dashboard
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        except Exception as e:
            print(f"Error updating dashboard: {e}")

    def run_scheduler(self):
        """Main scheduler loop."""
        self.running = True
        self.print_banner()
        print(Fore.GREEN + Style.BRIGHT + "  [>] " + Fore.WHITE + "Task Scheduler started...")
        print(Fore.CYAN + "  Waiting for tasks in " + Fore.YELLOW + "AI_Employee_Vault/Needs_Action/" + Fore.CYAN + " folder")
        print(Fore.CYAN + "-" * 60)

        while self.running:
            # Schedule any new tasks
            self.schedule_tasks()

            # Execute next task if available
            if self.execute_next_task():
                print(Fore.GREEN + "  [*] " + Fore.WHITE + "Task executed successfully")

            # Sleep for a bit before next cycle
            time.sleep(10)  # Check every 10 seconds

    def start(self):
        """Start the scheduler in a separate thread."""
        self.scheduler_thread = threading.Thread(target=self.run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        print(Fore.GREEN + Style.BRIGHT + "  [>] " + Fore.WHITE + "Task Scheduler thread started")

    def stop(self):
        """Stop the scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        print(Fore.YELLOW + Style.BRIGHT + "  [STOP] " + Fore.WHITE + "Task Scheduler stopped")


def main():
    """Main function to run the task scheduler."""
    scheduler = TaskScheduler()

    try:
        scheduler.start()

        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print(Fore.YELLOW + Style.BRIGHT + "\n  [STOP] " + Fore.WHITE + "Stopping scheduler...")
        scheduler.stop()


if __name__ == "__main__":
    main()