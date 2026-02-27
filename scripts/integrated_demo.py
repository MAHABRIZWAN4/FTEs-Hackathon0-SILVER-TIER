"""
Integrated Workflow Demo - AI Employee Agent Skills

This script demonstrates how all three agent skills work together:
1. Task Planner - Analyzes tasks and creates plans
2. Vault Watcher - Monitors for new tasks
3. LinkedIn Post - Shares updates on social media

Usage:
    python scripts/integrated_demo.py
"""

import os
import time
from datetime import datetime
from pathlib import Path


def print_banner():
    """Print demo banner."""
    print("\n" + "=" * 60)
    print("  INTEGRATED WORKFLOW DEMO")
    print("  AI Employee Agent Skills - Silver Tier")
    print("=" * 60 + "\n")


def create_sample_tasks():
    """Create sample task files in the Inbox."""
    inbox = Path("AI_Employee_Vault/Inbox")
    inbox.mkdir(parents=True, exist_ok=True)

    tasks = [
        {
            "filename": "implement_api_endpoint.md",
            "content": """# Implement New API Endpoint

Priority: HIGH

## Description
We need to create a new REST API endpoint for user profile updates.

## Requirements
- Accept PUT requests to /api/users/:id
- Validate input data
- Update database
- Return updated user object
- Add authentication middleware

## Timeline
This should be completed by end of week for the mobile app release.
"""
        },
        {
            "filename": "research_caching_strategy.md",
            "content": """# Research Caching Strategy

## Objective
Investigate different caching solutions to improve API performance.

## Areas to Research
- Redis vs Memcached
- Cache invalidation strategies
- TTL configurations
- Cost analysis

## Deliverable
Recommendation document with pros/cons of each approach.
"""
        },
        {
            "filename": "fix_memory_leak.md",
            "content": """# Fix Memory Leak in Background Worker

Priority: URGENT - Production issue!

## Issue
Background worker process memory usage grows continuously until crash.

## Symptoms
- Memory increases by ~100MB/hour
- Process crashes after 8-10 hours
- Requires manual restart

## Investigation Needed
- Profile memory usage
- Check for unclosed connections
- Review event listeners
- Analyze object retention
"""
        }
    ]

    print("[*] Creating sample tasks in Inbox...")
    for task in tasks:
        filepath = inbox / task["filename"]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(task["content"])
        print(f"   [+] Created: {task['filename']}")

    print(f"\n[SUCCESS] Created {len(tasks)} sample tasks\n")
    return len(tasks)


def run_task_planner():
    """Run the task planner to process inbox files."""
    print("[*] Running Task Planner...")
    print("   Analyzing task files and generating plans...\n")

    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "scripts/task_planner.py"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("[SUCCESS] Task Planner completed successfully\n")
        return True
    else:
        print(f"[ERROR] Task Planner failed: {result.stderr}\n")
        return False


def show_generated_plans():
    """Display the generated plans."""
    needs_action = Path("AI_Employee_Vault/Needs_Action")

    if not needs_action.exists():
        print("[ERROR] Needs_Action folder not found\n")
        return

    plans = list(needs_action.glob("Plan_*.md"))

    if not plans:
        print("[ERROR] No plans found\n")
        return

    print("[*] Generated Plans:")
    print("-" * 60)

    for plan in sorted(plans)[-3:]:  # Show last 3 plans
        print(f"\n[PLAN] {plan.name}")

        # Read and display plan summary
        with open(plan, "r", encoding="utf-8") as f:
            content = f.read()

            # Extract metadata
            if content.startswith("---"):
                lines = content.split("\n")
                for line in lines[1:10]:
                    if line.strip() == "---":
                        break
                    if "priority:" in line or "task_type:" in line:
                        print(f"   {line.strip()}")

            # Extract title
            for line in content.split("\n"):
                if line.startswith("# Plan:"):
                    print(f"   {line}")
                    break

    print("\n" + "-" * 60 + "\n")


def demonstrate_watcher():
    """Demonstrate the vault watcher concept."""
    print("[*] Vault Watcher Demonstration")
    print("-" * 60)
    print("The Vault Watcher continuously monitors the Inbox folder.")
    print("When new .md files appear, it automatically triggers the")
    print("Task Planner to process them.\n")

    print("To start the watcher in production:")
    print("   python scripts/watch_inbox.py\n")

    print("The watcher will:")
    print("   - Monitor AI_Employee_Vault/Inbox/ every 15 seconds")
    print("   - Detect new .md files")
    print("   - Automatically run task planner")
    print("   - Log all activity to logs/actions.log")
    print("   - Never process the same file twice\n")


def demonstrate_linkedin():
    """Demonstrate LinkedIn posting concept."""
    print("[*] LinkedIn Auto-Post Demonstration")
    print("-" * 60)
    print("The LinkedIn Auto-Post agent can share updates about")
    print("completed tasks or project milestones.\n")

    print("Example usage:")
    print('   python scripts/post_linkedin.py "Just completed 3 tasks!"\n')

    print("Setup required:")
    print("   1. pip install playwright python-dotenv")
    print("   2. playwright install chromium")
    print("   3. cp .env.example .env")
    print("   4. Edit .env with LinkedIn credentials\n")

    print("[WARNING] Note: LinkedIn automation should be used responsibly")
    print("   and in compliance with their Terms of Service.\n")


def show_workflow_diagram():
    """Display the integrated workflow."""
    print("[*] Integrated Workflow")
    print("=" * 60)
    print("""
    ┌─────────────────────────────────────────────────────┐
    │  1. User drops task.md in Inbox/                   │
    └────────────────┬────────────────────────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────────────────────────┐
    │  2. Vault Watcher detects new file (15s)           │
    └────────────────┬────────────────────────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────────────────────────┐
    │  3. Task Planner analyzes & creates plan           │
    └────────────────┬────────────────────────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────────────────────────┐
    │  4. Plan appears in Needs_Action/                  │
    └────────────────┬────────────────────────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────────────────────────┐
    │  5. (Optional) Post update to LinkedIn             │
    └─────────────────────────────────────────────────────┘
    """)


def show_logs():
    """Display recent log entries."""
    log_file = Path("logs/actions.log")

    if not log_file.exists():
        print("[*] No logs found yet\n")
        return

    print("[*] Recent Activity (last 10 entries):")
    print("-" * 60)

    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[-10:]:
            print(f"   {line.strip()}")

    print("-" * 60 + "\n")


def main():
    """Run the integrated demo."""
    print_banner()

    print("This demo shows how all three agent skills work together:\n")
    print("   [1] Task Planner Agent")
    print("   [2] Vault Watcher Agent")
    print("   [3] LinkedIn Auto-Post Agent\n")

    input("Press Enter to start the demo...")
    print()

    # Step 1: Create sample tasks
    num_tasks = create_sample_tasks()

    input("Press Enter to run Task Planner...")
    print()

    # Step 2: Run task planner
    if run_task_planner():
        # Step 3: Show generated plans
        show_generated_plans()

    # Step 4: Show logs
    show_logs()

    # Step 5: Demonstrate watcher
    demonstrate_watcher()

    input("Press Enter to continue...")
    print()

    # Step 6: Demonstrate LinkedIn
    demonstrate_linkedin()

    input("Press Enter to see workflow diagram...")
    print()

    # Step 7: Show workflow
    show_workflow_diagram()

    # Final summary
    print("\n" + "=" * 60)
    print("  DEMO COMPLETE")
    print("=" * 60)
    print("\n[SUCCESS] All three agent skills demonstrated successfully!\n")

    print("Next steps:")
    print("   - Review generated plans in AI_Employee_Vault/Needs_Action/")
    print("   - Start the watcher: python scripts/watch_inbox.py")
    print("   - Setup LinkedIn: See LINKEDIN_SETUP.md")
    print("   - Check logs: tail -f logs/actions.log\n")

    print("[*] Documentation:")
    print("   - README.md - Complete project overview")
    print("   - .claude/skills/*/SKILL.md - Individual skill docs")
    print("   - LINKEDIN_SETUP.md - LinkedIn setup guide\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Demo interrupted by user\n")
    except Exception as e:
        print(f"\n\n[ERROR] Error: {e}\n")
