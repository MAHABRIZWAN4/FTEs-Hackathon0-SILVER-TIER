# LinkedIn Auto-Post Agent - Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
# Install Python packages
pip install -r requirements_linkedin.txt

# Install Chromium browser for Playwright
playwright install chromium
```

### 2. Configure Credentials
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your LinkedIn credentials
# IMPORTANT: Never commit .env to version control!
```

Example `.env` file:
```env
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_secure_password
```

### 3. Test the Script
```bash
# Test with a simple post (non-headless for debugging)
python scripts/post_linkedin.py "Test post from automation" --headless=false

# Production usage (headless)
python scripts/post_linkedin.py "Your post content here"
```

## Usage Examples

### Basic Text Post
```bash
python scripts/post_linkedin.py "Just shipped a new feature! 🚀 #coding #development"
```

### Multi-line Post
```bash
python scripts/post_linkedin.py "Excited to share our latest project!

Key features:
✓ Real-time collaboration
✓ AI-powered insights
✓ Seamless integration

Check it out! #tech #innovation"
```

### Programmatic Usage
```python
from scripts.post_linkedin import LinkedInPoster

# Create poster instance
poster = LinkedInPoster(headless=True)

# Post content
content = "Your LinkedIn post content here"
success = poster.post(content)

if success:
    print("Posted successfully!")
else:
    print("Failed to post. Check logs/actions.log")
```

### Integration with Vault System
```python
import os
from scripts.post_linkedin import LinkedInPoster

# Read post from vault
post_file = "AI_Employee_Vault/Needs_Action/linkedin_post.txt"
with open(post_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Post to LinkedIn
poster = LinkedInPoster()
if poster.post(content):
    # Move to Done folder
    done_file = post_file.replace("Needs_Action", "Done")
    os.rename(post_file, done_file)
    print(f"Posted and moved to: {done_file}")
```

## Security Checklist

- [ ] Created `.env` file with credentials
- [ ] Added `.env` to `.gitignore`
- [ ] Never committed credentials to git
- [ ] Using strong, unique password
- [ ] Reviewed LinkedIn's Terms of Service
- [ ] Limited posting frequency (5-10 posts/day max)

## Troubleshooting

### Playwright Not Installed
```bash
pip install playwright
playwright install chromium
```

### Login Failed
- Verify credentials in `.env` file
- Check if 2FA is enabled (requires manual intervention)
- Try logging in manually to check account status
- Look for CAPTCHA requirements

### Element Not Found
- LinkedIn may have updated their UI
- Run with `--headless=false` to see what's happening
- Check `logs/screenshots/` for debug images
- Review `logs/actions.log` for details

### Rate Limiting
- Reduce posting frequency
- Wait 24 hours before retrying
- Review LinkedIn's usage policies

## File Structure

```
.claude/skills/linkedin-post/
└── SKILL.md                    # Complete documentation

scripts/
└── post_linkedin.py            # Main automation script

logs/
├── actions.log                 # Activity logs
└── screenshots/                # Debug screenshots

.env                            # Credentials (DO NOT COMMIT)
.env.example                    # Template
requirements_linkedin.txt       # Python dependencies
```

## Important Notes

⚠️ **Legal Disclaimer**: This tool is for authorized personal use only. LinkedIn's Terms of Service generally prohibit automated posting. Use responsibly and at your own risk.

🔒 **Security**: Never commit `.env` file. Always use strong passwords. Consider using a dedicated account for automation.

📊 **Rate Limits**: Limit to 5-10 posts per day to avoid account restrictions.

🔄 **Maintenance**: LinkedIn may update their UI. Script may require updates if selectors change.

## Advanced Configuration

### Custom Timeout
```bash
python scripts/post_linkedin.py "Content" --timeout=60000
```

### Non-Headless Mode (for debugging)
```bash
python scripts/post_linkedin.py "Content" --headless=false
```

### Environment Variables
```env
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password
HEADLESS=true
LINKEDIN_TIMEOUT=30000
```

## Support

Check logs for detailed error information:
```bash
tail -f logs/actions.log
```

View screenshots for visual debugging:
```bash
ls -lt logs/screenshots/
```

## Next Steps

1. Install dependencies
2. Configure credentials
3. Test with a simple post
4. Integrate with your workflow
5. Monitor logs for issues

For full documentation, see `.claude/skills/linkedin-post/SKILL.md`
