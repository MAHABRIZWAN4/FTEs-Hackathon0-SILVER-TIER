"""
Human Approval Agent - Synchronous Approval Workflow

This script provides a reusable human-in-the-loop approval workflow.
It creates approval requests, waits for human decision, and returns the result.

Features:
- Create approval request files
- Block execution until human responds
- Configurable timeout (default: 1 hour)
- Polling mechanism to detect approval status
- Comprehensive logging
- Return approval decision to calling code

Usage:
    from scripts.request_approval import request_approval, ApprovalTimeout

    try:
        approved = request_approval(
            title="Send Email to Client",
            description="Email contains project status",
            details={"recipient": "client@example.com"}
        )

        if approved:
            send_email()
        else:
            print("Action rejected")

    except ApprovalTimeout:
        print("Approval timed out")
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any


# Configuration
NEEDS_APPROVAL_FOLDER = os.path.join("AI_Employee_Vault", "Needs_Approval")
DONE_FOLDER = os.path.join("AI_Employee_Vault", "Done")
LOGS_FOLDER = "logs"
ACTIONS_LOG = os.path.join(LOGS_FOLDER, "actions.log")

# Defaults
DEFAULT_TIMEOUT = 3600  # 1 hour
DEFAULT_POLL_INTERVAL = 10  # 10 seconds


class ApprovalTimeout(Exception):
    """Exception raised when approval request times out."""

    def __init__(self, request_id: str, timeout_seconds: int):
        self.request_id = request_id
        self.timeout_seconds = timeout_seconds
        super().__init__(f"Approval request {request_id} timed out after {timeout_seconds} seconds")


def log_action(message: str, level: str = "INFO"):
    """
    Log a message to the actions log file.

    Args:
        message (str): Message to log
        level (str): Log level
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] [APPROVAL] {message}\n"

    try:
        os.makedirs(LOGS_FOLDER, exist_ok=True)
        with open(ACTIONS_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[{level}] {message}")
    except Exception as e:
        print(f"[ERROR] Failed to write to log: {e}")


def generate_request_id() -> str:
    """
    Generate a unique request ID.

    Returns:
        str: Unique request ID
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"approval_{timestamp}"


def create_approval_request(
    title: str,
    description: str,
    details: Optional[Dict[str, Any]] = None,
    timeout_seconds: int = DEFAULT_TIMEOUT,
    priority: str = "medium",
    requester: Optional[str] = None
) -> str:
    """
    Create an approval request file.

    Args:
        title (str): Short title for the approval request
        description (str): Detailed description
        details (dict): Additional context/details
        timeout_seconds (int): Timeout in seconds
        priority (str): Priority level (low, medium, high)
        requester (str): Name of requesting script

    Returns:
        str: Request ID
    """
    # Ensure directories exist
    os.makedirs(NEEDS_APPROVAL_FOLDER, exist_ok=True)
    os.makedirs(DONE_FOLDER, exist_ok=True)

    # Generate request ID
    request_id = generate_request_id()

    # Calculate timeout
    created_at = datetime.now()
    timeout_at = created_at + timedelta(seconds=timeout_seconds)

    # Build frontmatter
    frontmatter = f"""---
request_id: {request_id}
status: PENDING
created_at: {created_at.strftime("%Y-%m-%d %H:%M:%S")}
timeout_at: {timeout_at.strftime("%Y-%m-%d %H:%M:%S")}
requester: {requester or "unknown"}
priority: {priority}
---
"""

    # Build body
    body = f"""
# Approval Request: {title}

## Description
{description}
"""

    # Add details if provided
    if details:
        body += "\n## Details\n"
        for key, value in details.items():
            body += f"- **{key}**: {value}\n"

    # Add decision section
    body += """
## Decision Required

Please review the information above and make a decision.

Write **APPROVED** or **REJECTED** below:

---

**YOUR DECISION**:

"""

    # Combine content
    content = frontmatter + body

    # Write file
    filename = f"{request_id}.md"
    filepath = os.path.join(NEEDS_APPROVAL_FOLDER, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    log_action(f"Request created: {request_id}", "INFO")
    log_action(f"Title: {title}", "INFO")
    log_action(f"Priority: {priority}, Timeout: {timeout_seconds}s", "INFO")

    return request_id


def check_approval_status(request_id: str) -> Optional[str]:
    """
    Check the current status of an approval request.

    Args:
        request_id (str): Request ID to check

    Returns:
        Optional[str]: "APPROVED", "REJECTED", "PENDING", or None if not found
    """
    filename = f"{request_id}.md"
    filepath = os.path.join(NEEDS_APPROVAL_FOLDER, filename)

    if not os.path.exists(filepath):
        # Check if moved to Done
        done_filepath = os.path.join(DONE_FOLDER, filename)
        if os.path.exists(done_filepath):
            filepath = done_filepath
        else:
            return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for APPROVED or REJECTED in content
        content_upper = content.upper()

        if "**YOUR DECISION**: APPROVED" in content_upper or \
           "YOUR DECISION**: APPROVED" in content_upper or \
           "DECISION**: APPROVED" in content_upper:
            return "APPROVED"
        elif "**YOUR DECISION**: REJECTED" in content_upper or \
             "YOUR DECISION**: REJECTED" in content_upper or \
             "DECISION**: REJECTED" in content_upper:
            return "REJECTED"
        else:
            return "PENDING"

    except Exception as e:
        log_action(f"Error checking status for {request_id}: {str(e)}", "ERROR")
        return None


def move_to_done(request_id: str, final_status: str, reviewer_notes: Optional[str] = None):
    """
    Move approval request to Done folder with final status.

    Args:
        request_id (str): Request ID
        final_status (str): Final status (APPROVED or REJECTED)
        reviewer_notes (str): Optional notes from reviewer
    """
    filename = f"{request_id}.md"
    source = os.path.join(NEEDS_APPROVAL_FOLDER, filename)
    dest = os.path.join(DONE_FOLDER, filename)

    if not os.path.exists(source):
        log_action(f"Cannot move {request_id}: file not found", "WARNING")
        return

    try:
        # Read content
        with open(source, "r", encoding="utf-8") as f:
            content = f.read()

        # Update frontmatter
        lines = content.split("\n")
        updated_lines = []
        in_frontmatter = False
        frontmatter_closed = False

        for i, line in enumerate(lines):
            if i == 0 and line.strip() == "---":
                in_frontmatter = True
                updated_lines.append(line)
            elif in_frontmatter and line.strip() == "---":
                # Add reviewed_at before closing
                updated_lines.append(f"reviewed_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                if reviewer_notes:
                    updated_lines.append(f"reviewer_notes: {reviewer_notes}")
                updated_lines.append(line)
                in_frontmatter = False
                frontmatter_closed = True
            elif in_frontmatter and line.startswith("status:"):
                updated_lines.append(f"status: {final_status}")
            else:
                updated_lines.append(line)

        # Write to destination
        with open(dest, "w", encoding="utf-8") as f:
            f.write("\n".join(updated_lines))

        # Remove source
        os.remove(source)

        log_action(f"Moved {request_id} to Done/ with status: {final_status}", "INFO")

    except Exception as e:
        log_action(f"Error moving {request_id} to Done: {str(e)}", "ERROR")


def wait_for_approval(
    request_id: str,
    timeout_seconds: int = DEFAULT_TIMEOUT,
    poll_interval: int = DEFAULT_POLL_INTERVAL
) -> bool:
    """
    Wait for human approval decision.

    Args:
        request_id (str): Request ID to wait for
        timeout_seconds (int): Timeout in seconds
        poll_interval (int): Polling interval in seconds

    Returns:
        bool: True if approved, False if rejected

    Raises:
        ApprovalTimeout: If timeout exceeded
    """
    log_action(f"Waiting for human decision (timeout: {timeout_seconds}s)", "INFO")

    start_time = time.time()
    attempt = 0

    while True:
        attempt += 1
        elapsed = time.time() - start_time

        # Check timeout
        if elapsed >= timeout_seconds:
            log_action(f"Request timed out after {timeout_seconds}s", "ERROR")
            move_to_done(request_id, "TIMEOUT", "Request timed out")
            raise ApprovalTimeout(request_id, timeout_seconds)

        # Check status
        status = check_approval_status(request_id)

        if status == "APPROVED":
            log_action(f"Request approved: {request_id}", "SUCCESS")
            move_to_done(request_id, "APPROVED")
            return True
        elif status == "REJECTED":
            log_action(f"Request rejected: {request_id}", "INFO")
            move_to_done(request_id, "REJECTED")
            return False
        elif status is None:
            log_action(f"Request file not found: {request_id}", "ERROR")
            return False

        # Log polling attempt (every 5 attempts to reduce log spam)
        if attempt % 5 == 0:
            remaining = timeout_seconds - elapsed
            log_action(f"Still waiting... ({int(remaining)}s remaining, attempt {attempt})", "INFO")

        # Sleep before next check
        time.sleep(poll_interval)


def request_approval(
    title: str,
    description: str,
    details: Optional[Dict[str, Any]] = None,
    timeout_seconds: int = DEFAULT_TIMEOUT,
    priority: str = "medium",
    requester: Optional[str] = None,
    poll_interval: int = DEFAULT_POLL_INTERVAL
) -> bool:
    """
    Request human approval and wait for decision.

    This is the main entry point for requesting approval. It creates
    an approval request file and blocks until a decision is made or
    timeout occurs.

    Args:
        title (str): Short title for the approval request
        description (str): Detailed description
        details (dict): Additional context/details
        timeout_seconds (int): Timeout in seconds (default: 1 hour)
        priority (str): Priority level (low, medium, high)
        requester (str): Name of requesting script
        poll_interval (int): Polling interval in seconds

    Returns:
        bool: True if approved, False if rejected

    Raises:
        ApprovalTimeout: If timeout exceeded

    Example:
        >>> approved = request_approval(
        ...     title="Send Email",
        ...     description="Send status update to client",
        ...     details={"recipient": "client@example.com"}
        ... )
        >>> if approved:
        ...     send_email()
    """
    # Create approval request
    request_id = create_approval_request(
        title=title,
        description=description,
        details=details,
        timeout_seconds=timeout_seconds,
        priority=priority,
        requester=requester
    )

    # Wait for decision
    try:
        return wait_for_approval(request_id, timeout_seconds, poll_interval)
    except ApprovalTimeout:
        # Re-raise to caller
        raise


def main():
    """
    Main entry point for command-line usage.
    """
    parser = argparse.ArgumentParser(description="Human Approval Agent - Request Approval")
    parser.add_argument("--title", type=str, required=True, help="Approval request title")
    parser.add_argument("--description", type=str, required=True, help="Detailed description")
    parser.add_argument("--details", type=str, help="JSON string with additional details")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout in seconds")
    parser.add_argument("--priority", type=str, default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--requester", type=str, help="Name of requesting script")

    args = parser.parse_args()

    # Parse details if provided
    details = None
    if args.details:
        try:
            details = json.loads(args.details)
        except json.JSONDecodeError:
            print("[ERROR] Invalid JSON in --details")
            sys.exit(1)

    # Request approval
    try:
        approved = request_approval(
            title=args.title,
            description=args.description,
            details=details,
            timeout_seconds=args.timeout,
            priority=args.priority,
            requester=args.requester
        )

        if approved:
            print("\n[SUCCESS] Request APPROVED")
            sys.exit(0)
        else:
            print("\n[INFO] Request REJECTED")
            sys.exit(1)

    except ApprovalTimeout as e:
        print(f"\n[ERROR] Request TIMED OUT after {e.timeout_seconds} seconds")
        sys.exit(2)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
