# State Spending News Monitor

Automated monitoring system for tracking Rural Health Transformation (RHT) Program spending news across all 50 U.S. states.

## Overview

This monitor tracks news and announcements related to the CMS Rural Health Transformation Program, a $50 billion initiative ($10B/year from 2026-2030) to strengthen rural healthcare across all 50 states.

### Monitored States

**All 50 U.S. states** including:
- Alabama, Alaska, Arizona, Arkansas, California, Colorado, Connecticut, Delaware
- Florida, Georgia, Hawaii, Idaho, Illinois, Indiana, Iowa, Kansas
- Kentucky, Louisiana, Maine, Maryland, Massachusetts, Michigan, Minnesota, Mississippi
- Missouri, Montana, Nebraska, Nevada, New Hampshire, New Jersey, New Mexico, New York
- North Carolina, North Dakota, Ohio, Oklahoma, Oregon, Pennsylvania, Rhode Island, South Carolina
- South Dakota, Tennessee, Texas, Utah, Vermont, Virginia, Washington, West Virginia, Wisconsin, Wyoming

**Coverage:** All 50 states have direct state health department monitoring configured, plus additional monitoring via CMS newsroom and Google News RSS feeds for comprehensive coverage.

### News Sources

1. **CMS Newsroom** - Official CMS press releases and announcements
2. **Google News RSS** - State-specific news aggregation
3. **State Health Departments** - Direct monitoring of state health agency announcements

## Features

- **Multi-source monitoring** - Checks CMS, Google News, and state health departments
- **Intelligent filtering** - Uses keyword matching and relevance scoring
- **Duplicate detection** - Prevents duplicate alerts
- **Email notifications** - Sends alerts when new items are found
- **GitHub integration** - Creates issues for new findings
- **Historical tracking** - Maintains JSON database of all findings
- **Scheduled execution** - Runs daily via GitHub Actions

## Installation

### Prerequisites

- Python 3.11+
- pip package manager

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd civicoperator/state-spending-monitor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the monitor**
   ```bash
   python monitor.py
   ```

## Configuration

### Environment Variables

Create a `.env` file or set these in GitHub Secrets:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SEND_EMAIL_NOTIFICATIONS` | Enable email alerts | No | `false` |
| `NOTIFICATION_EMAIL` | Recipient email address | Yes (if email enabled) | - |
| `SMTP_SERVER` | SMTP server address | Yes (if email enabled) | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | Yes (if email enabled) | `587` |
| `SMTP_USER` | SMTP username | Yes (if email enabled) | - |
| `SMTP_PASSWORD` | SMTP password or app-specific password | Yes (if email enabled) | - |
| `LOOKBACK_DAYS` | How many days to look back for news | No | `7` |

### Gmail Configuration

For Gmail, you need an **App-Specific Password**:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication
3. Go to **App Passwords**
4. Generate a new app password for "Mail"
5. Use this password in `SMTP_PASSWORD`

## GitHub Actions Setup

### Required Secrets

Configure these in your GitHub repository settings (Settings → Secrets → Actions):

- `SEND_EMAIL_NOTIFICATIONS` - Set to `true` to enable email
- `NOTIFICATION_EMAIL` - Your email address
- `SMTP_SERVER` - Usually `smtp.gmail.com`
- `SMTP_PORT` - Usually `587`
- `SMTP_USER` - Your email address
- `SMTP_PASSWORD` - App-specific password

### Workflow Schedule

The monitor runs automatically:
- **Daily at 9:00 AM UTC** (4:00 AM EST / 1:00 AM PST)
- Can be triggered manually via GitHub Actions UI

### Workflow Outputs

1. **Findings JSON** - Saved as workflow artifact
2. **Log file** - Saved as workflow artifact
3. **GitHub Issues** - Created automatically for new findings
4. **Workflow Summary** - Displayed in Actions tab

## Monitoring Criteria

### Primary Keywords

Items must contain at least one of these keywords:
- Rural health transformation / RHTP / RHT program
- Rural health funding / grant / awards
- CMS rural health
- Rural healthcare spending / transformation
- Rural hospital funding
- Transform rural health
- Rural health initiative

### Context Keywords

Or contain 2+ of these context keywords:
- CMS / Centers for Medicare / Medicaid / Medicare / HHS
- billion / million / funding / award / grant / federal
- rural / hospital / clinic / healthcare / health care

### State Matching

Items must mention the state (abbreviation or full name) for any of the 50 U.S. states. For example:
- CA or California
- TX or Texas
- PA or Pennsylvania
- WA or Washington

## Output Files

### findings.json

Cumulative database of all findings:

```json
[
  {
    "source": "CMS Newsroom",
    "state": "TX",
    "title": "CMS Announces Additional RHT Funding for Texas",
    "description": "...",
    "url": "https://...",
    "published": "2026-01-10T12:00:00",
    "found_at": "2026-01-10T14:30:00"
  }
]
```

### monitor.log

Execution log with timestamps:
- Info: Normal operations
- Warning: Non-critical issues
- Error: Failed checks (will not halt execution)

## Usage Examples

### Run Locally

```bash
# Basic run
python monitor.py

# With environment file
export $(cat .env | xargs) && python monitor.py

# Verbose output
python monitor.py 2>&1 | tee output.log
```

### Test Email Configuration

```bash
# Set environment variables
export SEND_EMAIL_NOTIFICATIONS=true
export NOTIFICATION_EMAIL=test@example.com
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your-email@gmail.com
export SMTP_PASSWORD=your-app-password

# Run monitor
python monitor.py
```

### Manual GitHub Actions Run

1. Go to **Actions** tab in GitHub
2. Select **State Spending News Monitor** workflow
3. Click **Run workflow**
4. Select branch and click **Run workflow**

## Customization

### Update State Health Department URLs

All 50 states now have direct health department monitoring configured. To update a state's URL if it changes, edit `monitor.py`:

```python
state_urls = {
    'CA': 'https://www.cdph.ca.gov/Programs/OPA/Pages/New-Release-2026.aspx',
    'NY': 'https://health.ny.gov/press/releases/',
    'FL': 'https://www.floridahealth.gov/newsroom/all-articles.html',
    'TX': 'https://www.dshs.texas.gov/news-alerts',
    # ... all 50 states configured
}
```

### Add Keywords

Edit `monitor.py`:

```python
KEYWORDS = [
    'rural health transformation',
    'your new keyword here',
]
```

### Change Monitoring Frequency

Edit `.github/workflows/state-spending-monitor.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # Daily at 9 AM UTC
  # - cron: '0 */6 * * *'  # Every 6 hours
  # - cron: '0 9 * * 1'  # Weekly on Mondays
```

### Add News Sources

Implement new check methods in `StateSpendingMonitor` class:

```python
def check_your_source(self, state_code: str) -> List[Dict[str, Any]]:
    """Check your custom news source"""
    findings = []
    # Your implementation
    return findings
```

Then call it in `run_all_checks()`:

```python
def run_all_checks(self):
    # ... existing checks ...
    your_findings = self.check_your_source(state_code)
    all_findings.extend(your_findings)
```

## Troubleshooting

### No Findings

- Check that keywords are not too restrictive
- Increase `LOOKBACK_DAYS` value
- Verify news sources are accessible
- Check `monitor.log` for errors

### Email Not Sending

- Verify SMTP credentials
- Check that 2FA and app-specific password are configured (Gmail)
- Test SMTP connection separately
- Check firewall/network restrictions

### GitHub Actions Failing

- Verify all secrets are configured
- Check workflow logs for specific errors
- Ensure repository has Actions enabled
- Verify Python version compatibility

### Rate Limiting

The monitor includes rate limiting (2-3 second delays) between requests. If you still encounter rate limiting:
- Increase delays in monitor.py
- Reduce number of sources checked
- Decrease monitoring frequency

## About the RHT Program

The **Rural Health Transformation (RHT) Program** is a $50 billion CMS initiative to strengthen rural healthcare:

- **Total Funding:** $50 billion over 5 years (2026-2030)
- **Annual Distribution:** $10 billion per year
- **Coverage:** All 50 states
- **2026 Allocations:** $147M (New Jersey) to $281M (Texas)

### Program Goals

- Expand access to care in rural communities
- Strengthen rural health workforce
- Modernize rural facilities and technology
- Support innovative care delivery models

### Allocation Method

- 50% distributed equally among all states
- 50% based on rurality metrics, state policies, and impact potential

## Resources

- [CMS Rural Health Transformation Program](https://www.cms.gov/priorities/rural-health-transformation-rht-program/overview)
- [CMS Newsroom](https://www.cms.gov/newsroom)
- [HHS Press Room](https://www.hhs.gov/press-room/)

## License

This monitoring system is part of the CivicOperator project.

## Support

For issues or questions:
- Check the troubleshooting section above
- Review `monitor.log` for detailed error messages
- Open a GitHub issue with logs and configuration details
