"""
MCP Executor Agent - Action Orchestrator

This script executes external actions like sending emails and posting to social media.
It implements human-in-the-loop approval workflows for sensitive actions.

Features:
- Execute email, LinkedIn, and webhook actions
- Human-in-the-loop approval workflow
- Retry logic with exponential backoff
- Comprehensive error handling
- Action status tracking
- Detailed logging

Usage:
    python scripts/mcp_executor.py              # Process all pending actions
    python scripts/mcp_executor.py --file action.md  # Process specific action
    python scripts/mcp_executor.py --dry-run    # Validate without executing
"""

import os
import sys
import json
import time
import argparse
import subprocess
import smtplib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    import requests
except ImportError:
    requests = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# Configuration
ACTIONS_FOLDER = os.path.join("AI_Employee_Vault", "Actions")
NEEDS_APPROVAL_FOLDER = os.path.join("AI_Employee_Vault", "Needs_Approval")
DONE_FOLDER = os.path.join("AI_Employee_Vault", "Done")
LOGS_FOLDER = "logs"
ACTIONS_LOG = os.path.join(LOGS_FOLDER, "actions.log")
LINKEDIN_SCRIPT = os.path.join("scripts", "post_linkedin.py")

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_BASE = 1  # seconds


class MCPExecutor:
    """
    Action orchestrator for executing external operations.
    """

    def __init__(self, dry_run: bool = False, force: bool = False):
        """
        Initialize the MCP Executor.

        Args:
            dry_run (bool): Validate without executing
            force (bool): Skip approval checks (use with caution)
        """
        self.dry_run = dry_run
        self.force = force
        self.actions_processed = 0
        self.actions_failed = 0

        # Ensure directories exist
        os.makedirs(ACTIONS_FOLDER, exist_ok=True)
        os.makedirs(NEEDS_APPROVAL_FOLDER, exist_ok=True)
        os.makedirs(DONE_FOLDER, exist_ok=True)
        os.makedirs(LOGS_FOLDER, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """
        Log a message to the actions log file.

        Args:
            message (str): Message to log
            level (str): Log level
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [MCP] {message}\n"

        try:
            with open(ACTIONS_LOG, "a", encoding="utf-8") as f:
                f.write(log_entry)
            print(f"[{level}] {message}")
        except Exception as e:
            print(f"[ERROR] Failed to write to log: {e}")

    def parse_action_file(self, filepath: str) -> Optional[Dict]:
        """
        Parse an action request file.

        Args:
            filepath (str): Path to action file

        Returns:
            Optional[Dict]: Parsed action data or None if invalid
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse frontmatter
            if not content.startswith("---"):
                self.log(f"Invalid action file (no frontmatter): {filepath}", "ERROR")
                return None

            lines = content.split("\n")
            frontmatter_end = -1
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    frontmatter_end = i
                    break

            if frontmatter_end == -1:
                self.log(f"Invalid action file (malformed frontmatter): {filepath}", "ERROR")
                return None

            # Parse frontmatter
            metadata = {}
            for line in lines[1:frontmatter_end]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()

            # Get body
            body = "\n".join(lines[frontmatter_end + 1:]).strip()

            # Parse body based on action type
            action_data = {
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "metadata": metadata,
                "body": body
            }

            return action_data

        except Exception as e:
            self.log(f"Error parsing action file {filepath}: {str(e)}", "ERROR")
            return None

    def requires_approval(self, action_data: Dict) -> bool:
        """
        Check if action requires human approval.

        Args:
            action_data (Dict): Action data

        Returns:
            bool: True if approval required
        """
        if self.force:
            return False

        metadata = action_data.get("metadata", {})
        requires_approval = metadata.get("requires_approval", "true").lower()

        return requires_approval in ["true", "yes", "1"]

    def is_approved(self, action_data: Dict) -> bool:
        """
        Check if action has been approved.

        Args:
            action_data (Dict): Action data

        Returns:
            bool: True if approved
        """
        metadata = action_data.get("metadata", {})
        status = metadata.get("status", "pending").lower()
        approved = metadata.get("approved", "false").lower()

        return status == "approved" or approved in ["true", "yes", "1"]

    def move_to_approval(self, action_data: Dict) -> bool:
        """
        Move action to Needs_Approval folder.

        Args:
            action_data (Dict): Action data

        Returns:
            bool: True if successful
        """
        try:
            source = action_data["filepath"]
            filename = action_data["filename"]
            dest = os.path.join(NEEDS_APPROVAL_FOLDER, filename)

            if self.dry_run:
                self.log(f"[DRY RUN] Would move {filename} to Needs_Approval/", "INFO")
                return True

            # Move file
            os.rename(source, dest)
            self.log(f"Moved {filename} to Needs_Approval/ for human review", "INFO")
            return True

        except Exception as e:
            self.log(f"Error moving to approval: {str(e)}", "ERROR")
            return False

    def move_to_done(self, action_data: Dict, status: str, error_message: str = None) -> bool:
        """
        Move action to Done folder with updated status.

        Args:
            action_data (Dict): Action data
            status (str): Final status (completed or failed)
            error_message (str): Error message if failed

        Returns:
            bool: True if successful
        """
        try:
            source = action_data["filepath"]
            filename = action_data["filename"]
            dest = os.path.join(DONE_FOLDER, filename)

            if self.dry_run:
                self.log(f"[DRY RUN] Would move {filename} to Done/ with status: {status}", "INFO")
                return True

            # Read and update content
            with open(source, "r", encoding="utf-8") as f:
                content = f.read()

            # Update frontmatter
            lines = content.split("\n")
            updated_lines = []
            in_frontmatter = False
            frontmatter_updated = False

            for i, line in enumerate(lines):
                if i == 0 and line.strip() == "---":
                    in_frontmatter = True
                    updated_lines.append(line)
                elif in_frontmatter and line.strip() == "---":
                    # Add status before closing frontmatter
                    if not frontmatter_updated:
                        updated_lines.append(f"status: {status}")
                        updated_lines.append(f"completed_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        if error_message:
                            updated_lines.append(f"error_message: {error_message}")
                    updated_lines.append(line)
                    in_frontmatter = False
                    frontmatter_updated = True
                elif in_frontmatter and line.startswith("status:"):
                    updated_lines.append(f"status: {status}")
                else:
                    updated_lines.append(line)

            # Write updated content to destination
            with open(dest, "w", encoding="utf-8") as f:
                f.write("\n".join(updated_lines))

            # Remove source
            os.remove(source)

            self.log(f"Moved {filename} to Done/ with status: {status}", "INFO")
            return True

        except Exception as e:
            self.log(f"Error moving to done: {str(e)}", "ERROR")
            return False

    def execute_email_action(self, action_data: Dict) -> Tuple[bool, str]:
        """
        Execute email action.

        Args:
            action_data (Dict): Action data

        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        try:
            body = action_data["body"]

            # Parse email fields from body
            to_email = None
            cc_email = None
            subject = None
            email_body = []
            current_section = None

            for line in body.split("\n"):
                if line.startswith("## To"):
                    current_section = "to"
                elif line.startswith("## CC"):
                    current_section = "cc"
                elif line.startswith("## Subject"):
                    current_section = "subject"
                elif line.startswith("## Body"):
                    current_section = "body"
                elif current_section == "to" and line.strip():
                    to_email = line.strip()
                elif current_section == "cc" and line.strip():
                    cc_email = line.strip()
                elif current_section == "subject" and line.strip():
                    subject = line.strip()
                elif current_section == "body":
                    email_body.append(line)

            if not to_email or not subject:
                return False, "Missing required fields: to or subject"

            email_body_text = "\n".join(email_body).strip()

            if self.dry_run:
                self.log(f"[DRY RUN] Would send email to: {to_email}", "INFO")
                self.log(f"[DRY RUN] Subject: {subject}", "INFO")
                return True, None

            # Send email via SMTP
            sender = os.getenv("GMAIL_SENDER")
            password = os.getenv("GMAIL_APP_PASSWORD")

            if not sender or not password:
                return False, "Missing GMAIL_SENDER or GMAIL_APP_PASSWORD in .env"

            # Create message
            msg = MIMEMultipart()
            msg["From"] = sender
            msg["To"] = to_email
            if cc_email:
                msg["Cc"] = cc_email
            msg["Subject"] = subject
            msg.attach(MIMEText(email_body_text, "plain"))

            # Send via Gmail SMTP
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)

            self.log(f"Email sent to: {to_email}", "SUCCESS")
            return True, None

        except Exception as e:
            error_msg = f"Email sending failed: {str(e)}"
            self.log(error_msg, "ERROR")
            return False, error_msg

    def execute_linkedin_action(self, action_data: Dict) -> Tuple[bool, str]:
        """
        Execute LinkedIn action using existing post_linkedin.py script.

        Args:
            action_data (Dict): Action data

        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        try:
            body = action_data["body"]

            # Extract post content (everything after title)
            lines = body.split("\n")
            content_lines = []
            skip_title = True

            for line in lines:
                if skip_title and line.startswith("#"):
                    skip_title = False
                    continue
                if not skip_title:
                    content_lines.append(line)

            post_content = "\n".join(content_lines).strip()

            if not post_content:
                return False, "Empty post content"

            if self.dry_run:
                self.log(f"[DRY RUN] Would post to LinkedIn: {post_content[:50]}...", "INFO")
                return True, None

            # Check if LinkedIn script exists
            if not os.path.exists(LINKEDIN_SCRIPT):
                return False, f"LinkedIn script not found: {LINKEDIN_SCRIPT}"

            # Execute LinkedIn script
            result = subprocess.run(
                [sys.executable, LINKEDIN_SCRIPT, post_content],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                self.log(f"LinkedIn post published successfully", "SUCCESS")
                return True, None
            else:
                error_msg = f"LinkedIn posting failed: {result.stderr[:200]}"
                self.log(error_msg, "ERROR")
                return False, error_msg

        except subprocess.TimeoutExpired:
            error_msg = "LinkedIn posting timed out"
            self.log(error_msg, "ERROR")
            return False, error_msg
        except Exception as e:
            error_msg = f"LinkedIn posting failed: {str(e)}"
            self.log(error_msg, "ERROR")
            return False, error_msg

    def execute_webhook_action(self, action_data: Dict) -> Tuple[bool, str]:
        """
        Execute webhook action.

        Args:
            action_data (Dict): Action data

        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        try:
            if requests is None:
                return False, "requests library not installed (pip install requests)"

            metadata = action_data["metadata"]
            url = metadata.get("url")
            method = metadata.get("method", "POST").upper()
            body = action_data["body"]

            if not url:
                return False, "Missing webhook URL"

            # Parse headers if present
            headers = {}
            header_prefix = "header_"
            for key, value in metadata.items():
                if key.startswith(header_prefix):
                    header_name = key[len(header_prefix):].replace("_", "-")
                    headers[header_name] = value

            # Default to JSON content type
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json"

            if self.dry_run:
                self.log(f"[DRY RUN] Would send {method} to: {url}", "INFO")
                return True, None

            # Send request
            if method == "POST":
                response = requests.post(url, data=body, headers=headers, timeout=30)
            elif method == "PUT":
                response = requests.put(url, data=body, headers=headers, timeout=30)
            elif method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            else:
                return False, f"Unsupported HTTP method: {method}"

            if response.status_code >= 200 and response.status_code < 300:
                self.log(f"Webhook {method} to {url} succeeded (status: {response.status_code})", "SUCCESS")
                return True, None
            else:
                error_msg = f"Webhook failed with status {response.status_code}: {response.text[:200]}"
                self.log(error_msg, "ERROR")
                return False, error_msg

        except Exception as e:
            error_msg = f"Webhook execution failed: {str(e)}"
            self.log(error_msg, "ERROR")
            return False, error_msg

    def execute_action(self, action_data: Dict) -> bool:
        """
        Execute an action with retry logic.

        Args:
            action_data (Dict): Action data

        Returns:
            bool: True if successful
        """
        metadata = action_data.get("metadata", {})
        action_type = metadata.get("action_type", "unknown")
        max_retries = int(metadata.get("max_retries", MAX_RETRIES))
        retry_count = int(metadata.get("retry_count", 0))

        self.log(f"Executing action: {action_data['filename']} (type: {action_type})", "INFO")

        # Execute based on action type
        for attempt in range(max_retries + 1):
            if attempt > 0:
                delay = RETRY_DELAY_BASE * (2 ** (attempt - 1))
                self.log(f"Retry attempt {attempt}/{max_retries} after {delay}s delay", "INFO")
                time.sleep(delay)

            # Execute action
            success = False
            error_message = None

            if action_type == "email":
                success, error_message = self.execute_email_action(action_data)
            elif action_type == "linkedin":
                success, error_message = self.execute_linkedin_action(action_data)
            elif action_type == "webhook":
                success, error_message = self.execute_webhook_action(action_data)
            else:
                error_message = f"Unknown action type: {action_type}"
                self.log(error_message, "ERROR")
                break

            if success:
                self.move_to_done(action_data, "completed")
                self.actions_processed += 1
                return True

            # Check if error is retryable
            if error_message and ("timeout" in error_message.lower() or "network" in error_message.lower()):
                continue  # Retry
            else:
                break  # Non-retryable error

        # All retries failed
        self.move_to_done(action_data, "failed", error_message)
        self.actions_failed += 1
        return False

    def process_action_file(self, filepath: str) -> bool:
        """
        Process a single action file.

        Args:
            filepath (str): Path to action file

        Returns:
            bool: True if processed successfully
        """
        try:
            self.log(f"Processing action: {os.path.basename(filepath)}", "INFO")

            # Parse action file
            action_data = self.parse_action_file(filepath)
            if not action_data:
                return False

            # Check if approval required
            if self.requires_approval(action_data):
                if not self.is_approved(action_data):
                    self.log(f"Action requires approval, moving to Needs_Approval/", "INFO")
                    return self.move_to_approval(action_data)

            # Execute action
            return self.execute_action(action_data)

        except Exception as e:
            self.log(f"Error processing action file: {str(e)}", "ERROR")
            return False

    def process_all_actions(self) -> Dict:
        """
        Process all pending actions in Actions/ and approved actions in Needs_Approval/.

        Returns:
            Dict: Processing results
        """
        self.log("Starting MCP Executor", "INFO")

        processed = 0
        failed = 0

        # Process actions in Actions/ folder
        if os.path.exists(ACTIONS_FOLDER):
            for filename in os.listdir(ACTIONS_FOLDER):
                if filename.endswith(".md"):
                    filepath = os.path.join(ACTIONS_FOLDER, filename)
                    if self.process_action_file(filepath):
                        processed += 1
                    else:
                        failed += 1

        # Process approved actions in Needs_Approval/ folder
        if os.path.exists(NEEDS_APPROVAL_FOLDER):
            for filename in os.listdir(NEEDS_APPROVAL_FOLDER):
                if filename.endswith(".md"):
                    filepath = os.path.join(NEEDS_APPROVAL_FOLDER, filename)
                    action_data = self.parse_action_file(filepath)
                    if action_data and self.is_approved(action_data):
                        if self.execute_action(action_data):
                            processed += 1
                        else:
                            failed += 1

        self.log(f"MCP Executor completed - Processed: {processed}, Failed: {failed}", "INFO")

        return {
            "processed": processed,
            "failed": failed
        }


def main():
    """
    Main entry point for command-line usage.
    """
    parser = argparse.ArgumentParser(description="MCP Executor - Action Orchestrator")
    parser.add_argument("--file", type=str, help="Process specific action file")
    parser.add_argument("--dry-run", action="store_true", help="Validate without executing")
    parser.add_argument("--force", action="store_true", help="Skip approval checks (use with caution)")

    args = parser.parse_args()

    # Create executor
    executor = MCPExecutor(dry_run=args.dry_run, force=args.force)

    try:
        if args.file:
            # Process specific file
            success = executor.process_action_file(args.file)
            sys.exit(0 if success else 1)
        else:
            # Process all actions
            results = executor.process_all_actions()
            sys.exit(0 if results["failed"] == 0 else 1)

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
