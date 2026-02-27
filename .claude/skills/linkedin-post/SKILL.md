# LinkedIn Auto-Post Agent Skill

## Description
Automates posting text content to LinkedIn using browser automation. This skill handles authentication, navigation, and post creation through Playwright, providing a production-ready solution for scheduled or triggered LinkedIn posting.

## ⚠️ Important Disclaimers

**Legal & Terms of Service:**
- LinkedIn's Terms of Service generally prohibit automated posting
- This tool is intended for:
  - Personal authorized use only
  - Educational purposes
  - Testing in development environments
  - Authorized business accounts with proper permissions
- Users are responsible for compliance with LinkedIn's policies
- Excessive automation may result in account restrictions or bans

**Technical Limitations:**
- Cannot bypass CAPTCHA or 2FA automatically
- May fail if LinkedIn updates their UI/selectors
- Rate limiting applies (recommended: max 5-10 posts/day)
- Requires valid LinkedIn credentials

## Trigger
- Command: `/linkedin-post` or `linkedin-post`
- Manual: `python scripts/post_linkedin.py "Your post content here"`
- Programmatic: Import and call from other scripts

## Capabilities
- Automated LinkedIn login using credentials from environment variables
- Navigate to LinkedIn feed
- Create and publish text posts
- Retry logic for transient failures (max 2 retries)
- Comprehensive error handling and logging
- Headless browser operation (configurable)
- Screenshot capture on errors for debugging
- Session management and cleanup

## Prerequisites

### 1. Install Dependencies
```bash
pip install playwright python-dotenv
playwright install chromium
```

### 2. Configure Environment Variables
Create a `.env` file in the project root:
```env
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_secure_password
```

**Security Notes:**
- Never commit `.env` file to version control
- Add `.env` to `.gitignore`
- Use strong, unique passwords
- Consider using a dedicated account for automation
- Rotate credentials regularly

## Usage

### Command Line
```bash
# Basic usage
python scripts/post_linkedin.py "Just shipped a new feature! 🚀"

# With visible browser (non-headless)
python scripts/post_linkedin.py "My post content" --headless=false

# From project root
cd "F:\Hackathon 0 Mahab\Silver Tier"
python scripts/post_linkedin.py "Your content here"
```

### Programmatic Usage
```python
from scripts.post_linkedin import LinkedInPoster

poster = LinkedInPoster(headless=True)
success = poster.post("Your post content here")

if success:
    print("Post published successfully!")
else:
    print("Failed to publish post")
```

### Via Claude Code
```
/linkedin-post
```

## Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. Load Environment Variables                          │
│     - LINKEDIN_EMAIL                                    │
│     - LINKEDIN_PASSWORD                                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  2. Launch Browser (Chromium)                           │
│     - Headless mode (default)                           │
│     - Set user agent and viewport                       │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  3. Navigate to LinkedIn Login                          │
│     - https://www.linkedin.com/login                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  4. Authenticate                                        │
│     - Enter email and password                          │
│     - Submit login form                                 │
│     - Wait for feed to load                             │
│     - Handle errors (invalid credentials, CAPTCHA)      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  5. Create Post                                         │
│     - Click "Start a post" button                       │
│     - Enter post content                                │
│     - Click "Post" button                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  6. Verify & Cleanup                                    │
│     - Wait for post confirmation                        │
│     - Log success/failure                               │
│     - Close browser                                     │
│     - Return result                                     │
└─────────────────────────────────────────────────────────┘
```

## Error Handling

The skill handles various error scenarios:

### Authentication Errors
- **Invalid Credentials**: Logs error and exits gracefully
- **CAPTCHA Required**: Logs warning, cannot proceed automatically
- **2FA Enabled**: Logs warning, requires manual intervention
- **Account Locked**: Logs error with recommendation to check account

### Posting Errors
- **Network Issues**: Retries up to 2 times with exponential backoff
- **UI Changes**: Logs selector errors with screenshots
- **Rate Limiting**: Detects and logs rate limit warnings
- **Session Expired**: Attempts re-authentication once

### Technical Errors
- **Browser Crash**: Logs error and attempts cleanup
- **Timeout**: Configurable timeouts with clear error messages
- **Missing Elements**: Robust selector strategies with fallbacks

## Logging

All actions are logged to `logs/actions.log`:

```
[2026-02-27 11:00:00] [LINKEDIN] Starting LinkedIn post automation
[2026-02-27 11:00:01] [LINKEDIN] Browser launched (headless=True)
[2026-02-27 11:00:02] [LINKEDIN] Navigating to login page
[2026-02-27 11:00:05] [LINKEDIN] Login successful
[2026-02-27 11:00:06] [LINKEDIN] Navigating to feed
[2026-02-27 11:00:08] [LINKEDIN] Clicked 'Start a post' button
[2026-02-27 11:00:09] [LINKEDIN] Entered post content (125 characters)
[2026-02-27 11:00:10] [LINKEDIN] Clicked 'Post' button
[2026-02-27 11:00:12] [SUCCESS] Post published successfully
[2026-02-27 11:00:12] [LINKEDIN] Browser closed
```

## Configuration

### Environment Variables
- `LINKEDIN_EMAIL`: Your LinkedIn email address (required)
- `LINKEDIN_PASSWORD`: Your LinkedIn password (required)
- `HEADLESS`: Run browser in headless mode (default: true)
- `LINKEDIN_TIMEOUT`: Page load timeout in milliseconds (default: 30000)

### Script Parameters
```python
LinkedInPoster(
    headless=True,          # Run browser in headless mode
    timeout=30000,          # Page load timeout (ms)
    max_retries=2,          # Maximum retry attempts
    screenshot_on_error=True # Capture screenshots on errors
)
```

## Retry Logic

The skill implements intelligent retry logic:

1. **First Attempt**: Normal execution
2. **Retry 1** (if failed): Wait 5 seconds, retry
3. **Retry 2** (if failed): Wait 10 seconds, retry
4. **Final Failure**: Log error and return failure

Retries are triggered by:
- Network timeouts
- Transient element not found errors
- Temporary LinkedIn service issues

Retries are NOT triggered by:
- Invalid credentials
- CAPTCHA challenges
- Account restrictions
- Permanent errors

## Security Best Practices

1. **Credential Storage**
   - Use `.env` file (never hardcode)
   - Add `.env` to `.gitignore`
   - Use environment-specific credentials

2. **Access Control**
   - Restrict file permissions on `.env` (chmod 600)
   - Use dedicated automation account
   - Enable 2FA on main account

3. **Rate Limiting**
   - Max 5-10 posts per day recommended
   - Add delays between posts (5-10 minutes)
   - Monitor for rate limit warnings

4. **Monitoring**
   - Review logs regularly
   - Watch for authentication failures
   - Check for LinkedIn policy updates

## Troubleshooting

### "Login Failed" Error
- Verify credentials in `.env` file
- Check if account has CAPTCHA or 2FA enabled
- Try logging in manually to verify account status
- Check for account restrictions

### "Element Not Found" Error
- LinkedIn may have updated their UI
- Check logs for specific selector that failed
- Update selectors in script if needed
- Run in non-headless mode to debug visually

### "Rate Limit Exceeded" Warning
- Reduce posting frequency
- Wait 24 hours before retrying
- Review LinkedIn's usage policies

### Browser Crashes
- Ensure Playwright is properly installed
- Update Playwright: `playwright install chromium`
- Check system resources (RAM, CPU)
- Try non-headless mode for debugging

## Performance

- **Execution Time**: 15-30 seconds per post
- **Memory Usage**: ~200-300 MB (Chromium browser)
- **CPU Usage**: Moderate during execution, idle otherwise
- **Network**: Minimal bandwidth usage

## Limitations

1. **Text Posts Only**: Currently supports text-only posts
2. **No Media**: Images, videos, documents not supported yet
3. **No Scheduling**: Runs immediately when invoked
4. **Single Account**: One account per execution
5. **No Analytics**: Doesn't track post performance
6. **CAPTCHA**: Cannot bypass CAPTCHA automatically
7. **2FA**: Requires manual intervention if enabled

## Future Enhancements

- Support for image/video attachments
- Post scheduling capabilities
- Multi-account support
- Post analytics and engagement tracking
- Comment automation
- Connection request automation
- Profile update automation
- LinkedIn API integration (if available)

## Integration Examples

### With Task Scheduler
```python
# Schedule daily LinkedIn post
from scripts.post_linkedin import LinkedInPoster
from datetime import datetime

content = f"Daily update for {datetime.now().strftime('%B %d, %Y')}"
poster = LinkedInPoster()
poster.post(content)
```

### With Vault System
```python
# Post content from vault file
import os
from scripts.post_linkedin import LinkedInPoster

# Read post content from file
post_file = "AI_Employee_Vault/Needs_Action/linkedin_post.txt"
with open(post_file, 'r') as f:
    content = f.read()

# Post to LinkedIn
poster = LinkedInPoster()
if poster.post(content):
    # Move file to Done
    os.rename(post_file, "AI_Employee_Vault/Done/linkedin_post.txt")
```

### With Content Generator
```python
# Generate and post AI content
from scripts.post_linkedin import LinkedInPoster

# Generate content (placeholder)
content = generate_linkedin_content()

# Post to LinkedIn
poster = LinkedInPoster()
poster.post(content)
```

## Dependencies

```
playwright>=1.40.0
python-dotenv>=1.0.0
```

Install with:
```bash
pip install playwright python-dotenv
playwright install chromium
```

## Files Structure

```
.claude/skills/linkedin-post/
└── SKILL.md                    # This documentation

scripts/
└── post_linkedin.py            # Main automation script

logs/
└── actions.log                 # Activity logs

.env                            # Credentials (DO NOT COMMIT)
.env.example                    # Template for credentials
```

## Legal & Compliance

- Review LinkedIn's Terms of Service before use
- Obtain proper authorization for business accounts
- Respect rate limits and usage policies
- Monitor for policy changes
- Use responsibly and ethically
- Consider LinkedIn's official API for production use

## Support

For issues or questions:
1. Check logs in `logs/actions.log`
2. Review troubleshooting section
3. Run in non-headless mode for visual debugging
4. Verify LinkedIn hasn't changed their UI
5. Check Playwright documentation

## Notes

- Designed for authorized personal/business use
- Requires active LinkedIn account
- Subject to LinkedIn's terms and policies
- May require updates if LinkedIn changes UI
- Use at your own risk
- Consider official LinkedIn API for production systems
