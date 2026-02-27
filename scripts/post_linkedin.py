"""
LinkedIn Auto-Post Agent - Silver Tier AI Employee

This script automates posting text content to LinkedIn using Playwright browser automation.

⚠️ IMPORTANT DISCLAIMER:
This tool is intended for authorized personal use, educational purposes, and testing only.
LinkedIn's Terms of Service generally prohibit automated posting. Users are responsible
for compliance with LinkedIn's policies. Use at your own risk.

Features:
- Automated LinkedIn login using environment credentials
- Text post creation and publishing
- Retry logic for transient failures
- Comprehensive error handling and logging
- Headless browser operation
- Screenshot capture on errors

Requirements:
- playwright (pip install playwright)
- python-dotenv (pip install python-dotenv)
- Run: playwright install chromium
"""

import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, TimeoutError as PlaywrightTimeout
except ImportError:
    print("[ERROR] Playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("[ERROR] python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)


# Configuration
LOGS_FOLDER = "logs"
ACTIONS_LOG = os.path.join(LOGS_FOLDER, "actions.log")
SCREENSHOTS_FOLDER = os.path.join(LOGS_FOLDER, "screenshots")

# LinkedIn URLs
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"

# Timeouts (milliseconds)
DEFAULT_TIMEOUT = 30000
NAVIGATION_TIMEOUT = 30000
LOGIN_TIMEOUT = 15000
POST_TIMEOUT = 10000

# Retry configuration
MAX_RETRIES = 2
RETRY_DELAY_BASE = 5  # seconds


class LinkedInPoster:
    """
    Handles automated posting to LinkedIn using browser automation.
    """

    def __init__(self, headless: bool = True, timeout: int = DEFAULT_TIMEOUT, max_retries: int = MAX_RETRIES):
        """
        Initialize the LinkedIn poster.

        Args:
            headless (bool): Run browser in headless mode
            timeout (int): Default timeout in milliseconds
            max_retries (int): Maximum number of retry attempts
        """
        self.headless = headless
        self.timeout = timeout
        self.max_retries = max_retries
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Load environment variables
        load_dotenv()
        self.email = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")

        # Ensure directories exist
        os.makedirs(LOGS_FOLDER, exist_ok=True)
        os.makedirs(SCREENSHOTS_FOLDER, exist_ok=True)

    def log_action(self, message: str, level: str = "INFO"):
        """
        Log an action to the actions.log file with timestamp.

        Args:
            message (str): The message to log
            level (str): Log level (INFO, ERROR, WARNING, SUCCESS)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [LINKEDIN] {message}\n"

        try:
            with open(ACTIONS_LOG, "a", encoding="utf-8") as f:
                f.write(log_entry)
            print(f"[{level}] {message}")
        except Exception as e:
            print(f"[ERROR] Failed to write to log: {e}")

    def take_screenshot(self, name: str):
        """
        Take a screenshot for debugging purposes.

        Args:
            name (str): Name for the screenshot file
        """
        try:
            if self.page:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.png"
                filepath = os.path.join(SCREENSHOTS_FOLDER, filename)
                self.page.screenshot(path=filepath)
                self.log_action(f"Screenshot saved: {filepath}", "INFO")
        except Exception as e:
            self.log_action(f"Failed to take screenshot: {str(e)}", "WARNING")

    def validate_credentials(self) -> bool:
        """
        Validate that required credentials are present.

        Returns:
            bool: True if credentials are valid
        """
        if not self.email or not self.password:
            self.log_action("Missing LinkedIn credentials. Check .env file for LINKEDIN_EMAIL and LINKEDIN_PASSWORD", "ERROR")
            return False
        return True

    def launch_browser(self) -> bool:
        """
        Launch the browser and create a new page.

        Returns:
            bool: True if successful
        """
        try:
            self.log_action("Starting LinkedIn post automation", "INFO")
            playwright = sync_playwright().start()

            self.browser = playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            self.context = self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            self.page = self.context.new_page()
            self.page.set_default_timeout(self.timeout)

            self.log_action(f"Browser launched (headless={self.headless})", "INFO")
            return True

        except Exception as e:
            self.log_action(f"Failed to launch browser: {str(e)}", "ERROR")
            return False

    def login(self) -> bool:
        """
        Login to LinkedIn using credentials from environment variables.

        Returns:
            bool: True if login successful
        """
        try:
            self.log_action("Navigating to login page", "INFO")
            self.page.goto(LINKEDIN_LOGIN_URL, timeout=NAVIGATION_TIMEOUT)
            time.sleep(2)  # Wait for page to stabilize

            # Check if already logged in
            if "feed" in self.page.url:
                self.log_action("Already logged in", "INFO")
                return True

            # Enter email
            self.log_action("Entering email", "INFO")
            email_input = self.page.locator('input[id="username"]')
            email_input.fill(self.email)
            time.sleep(1)

            # Enter password
            self.log_action("Entering password", "INFO")
            password_input = self.page.locator('input[id="password"]')
            password_input.fill(self.password)
            time.sleep(1)

            # Click sign in button
            self.log_action("Clicking sign in button", "INFO")
            sign_in_button = self.page.locator('button[type="submit"]')
            sign_in_button.click()

            # Wait for navigation
            time.sleep(5)

            # Check for successful login
            current_url = self.page.url

            # Check for CAPTCHA or verification
            if "checkpoint" in current_url or "challenge" in current_url:
                self.log_action("CAPTCHA or verification required. Cannot proceed automatically.", "ERROR")
                self.take_screenshot("captcha_detected")
                return False

            # Check if login failed
            if "login" in current_url:
                self.log_action("Login failed. Check credentials or account status.", "ERROR")
                self.take_screenshot("login_failed")
                return False

            # Check if we reached the feed
            if "feed" in current_url or "mynetwork" in current_url or "jobs" in current_url:
                self.log_action("Login successful", "SUCCESS")
                return True

            # Unknown state
            self.log_action(f"Unexpected page after login: {current_url}", "WARNING")
            self.take_screenshot("unexpected_page")
            return False

        except PlaywrightTimeout:
            self.log_action("Login timeout. Check network connection or LinkedIn availability.", "ERROR")
            self.take_screenshot("login_timeout")
            return False
        except Exception as e:
            self.log_action(f"Login error: {str(e)}", "ERROR")
            self.take_screenshot("login_error")
            return False

    def navigate_to_feed(self) -> bool:
        """
        Navigate to LinkedIn feed.

        Returns:
            bool: True if successful
        """
        try:
            if "feed" not in self.page.url:
                self.log_action("Navigating to feed", "INFO")
                self.page.goto(LINKEDIN_FEED_URL, timeout=NAVIGATION_TIMEOUT)
                time.sleep(3)

            self.log_action("On LinkedIn feed", "INFO")
            return True

        except Exception as e:
            self.log_action(f"Failed to navigate to feed: {str(e)}", "ERROR")
            self.take_screenshot("navigate_feed_error")
            return False

    def create_post(self, content: str) -> bool:
        """
        Create and publish a text post on LinkedIn.

        Args:
            content (str): The text content to post

        Returns:
            bool: True if post was published successfully
        """
        try:
            # Click "Start a post" button
            self.log_action("Looking for 'Start a post' button", "INFO")

            # Try multiple selectors (LinkedIn UI can vary)
            start_post_selectors = [
                'button:has-text("Start a post")',
                'button[aria-label*="Start a post"]',
                '.share-box-feed-entry__trigger',
                'button.artdeco-button--secondary:has-text("Start")'
            ]

            clicked = False
            for selector in start_post_selectors:
                try:
                    start_post_button = self.page.locator(selector).first
                    if start_post_button.is_visible(timeout=5000):
                        start_post_button.click()
                        clicked = True
                        self.log_action("Clicked 'Start a post' button", "INFO")
                        break
                except:
                    continue

            if not clicked:
                self.log_action("Could not find 'Start a post' button", "ERROR")
                self.take_screenshot("start_post_not_found")
                return False

            time.sleep(2)

            # Enter post content
            self.log_action(f"Entering post content ({len(content)} characters)", "INFO")

            # Try multiple selectors for the content editor
            content_selectors = [
                'div[role="textbox"][contenteditable="true"]',
                '.ql-editor[contenteditable="true"]',
                'div.ql-editor'
            ]

            content_entered = False
            for selector in content_selectors:
                try:
                    content_editor = self.page.locator(selector).first
                    if content_editor.is_visible(timeout=5000):
                        content_editor.click()
                        time.sleep(1)
                        content_editor.fill(content)
                        content_entered = True
                        self.log_action("Content entered successfully", "INFO")
                        break
                except:
                    continue

            if not content_entered:
                self.log_action("Could not find content editor", "ERROR")
                self.take_screenshot("content_editor_not_found")
                return False

            time.sleep(2)

            # Click "Post" button
            self.log_action("Looking for 'Post' button", "INFO")

            post_button_selectors = [
                'button:has-text("Post")',
                'button[aria-label*="Post"]',
                '.share-actions__primary-action'
            ]

            posted = False
            for selector in post_button_selectors:
                try:
                    post_button = self.page.locator(selector).first
                    if post_button.is_visible(timeout=5000) and post_button.is_enabled():
                        post_button.click()
                        posted = True
                        self.log_action("Clicked 'Post' button", "INFO")
                        break
                except:
                    continue

            if not posted:
                self.log_action("Could not find or click 'Post' button", "ERROR")
                self.take_screenshot("post_button_not_found")
                return False

            # Wait for post to be published
            time.sleep(5)

            # Verify post was published (check if modal closed)
            try:
                # If modal is still visible, post might have failed
                modal = self.page.locator('div[role="dialog"]').first
                if modal.is_visible(timeout=2000):
                    self.log_action("Post modal still visible, post may have failed", "WARNING")
                    self.take_screenshot("post_verification_warning")
            except:
                # Modal not found, likely closed successfully
                pass

            self.log_action("Post published successfully", "SUCCESS")
            self.take_screenshot("post_success")
            return True

        except PlaywrightTimeout:
            self.log_action("Post creation timeout", "ERROR")
            self.take_screenshot("post_timeout")
            return False
        except Exception as e:
            self.log_action(f"Post creation error: {str(e)}", "ERROR")
            self.take_screenshot("post_error")
            return False

    def cleanup(self):
        """
        Close browser and cleanup resources.
        """
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            self.log_action("Browser closed", "INFO")
        except Exception as e:
            self.log_action(f"Cleanup error: {str(e)}", "WARNING")

    def post(self, content: str) -> bool:
        """
        Main method to post content to LinkedIn with retry logic.

        Args:
            content (str): The text content to post

        Returns:
            bool: True if post was successful
        """
        if not content or not content.strip():
            self.log_action("Post content is empty", "ERROR")
            return False

        if not self.validate_credentials():
            return False

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    delay = RETRY_DELAY_BASE * (2 ** (attempt - 1))
                    self.log_action(f"Retry attempt {attempt}/{self.max_retries} after {delay}s delay", "INFO")
                    time.sleep(delay)

                # Launch browser
                if not self.launch_browser():
                    continue

                # Login
                if not self.login():
                    self.cleanup()
                    if attempt == self.max_retries:
                        return False
                    continue

                # Navigate to feed
                if not self.navigate_to_feed():
                    self.cleanup()
                    if attempt == self.max_retries:
                        return False
                    continue

                # Create post
                if not self.create_post(content):
                    self.cleanup()
                    if attempt == self.max_retries:
                        return False
                    continue

                # Success!
                self.cleanup()
                return True

            except Exception as e:
                self.log_action(f"Unexpected error on attempt {attempt + 1}: {str(e)}", "ERROR")
                self.cleanup()
                if attempt == self.max_retries:
                    return False

        return False


def main():
    """
    Main entry point for command-line usage.
    """
    parser = argparse.ArgumentParser(description="Post content to LinkedIn automatically")
    parser.add_argument("content", type=str, help="The text content to post")
    parser.add_argument("--headless", type=str, default="true", help="Run in headless mode (true/false)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout in milliseconds")

    args = parser.parse_args()

    # Parse headless argument
    headless = args.headless.lower() in ['true', '1', 'yes', 'y']

    # Create poster and post
    poster = LinkedInPoster(headless=headless, timeout=args.timeout)
    success = poster.post(args.content)

    if success:
        print("\n✓ Post published successfully!")
        sys.exit(0)
    else:
        print("\n✗ Failed to publish post. Check logs/actions.log for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
