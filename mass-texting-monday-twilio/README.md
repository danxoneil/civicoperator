# Mass Texting System via monday.com + Twilio

A generic, configurable system for sending mass SMS/text messages by pulling contact lists from monday.com boards and delivering messages via Twilio.

Perfect for civic engagement campaigns, community organizing, event notifications, and supporter outreach.

## 🌟 Features

- ✅ **monday.com Integration** - Fetch contacts directly from your monday.com boards
- 📱 **Twilio SMS** - Send text messages via Twilio's reliable API
- 🎯 **Message Personalization** - Use placeholders like `{name}`, `{first_name}`, or any board column
- ✔️ **Opt-In Compliance** - Respects opt-in status from your board
- 🧪 **Dry-Run Mode** - Test your campaign without sending real messages
- 📊 **Detailed Logging** - Track every message sent, failed, or skipped
- 🔄 **Status Updates** - Automatically update delivery status in monday.com
- ⏱️ **Rate Limiting** - Built-in delays to respect Twilio's rate limits
- 📈 **Campaign Reports** - JSON results file with full statistics
- 🤖 **GitHub Actions** - Optional automation via scheduled workflows

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [monday.com Board Setup](#mondaycom-board-setup)
- [Usage](#usage)
- [Message Templates](#message-templates)
- [Running Campaigns](#running-campaigns)
- [GitHub Actions Automation](#github-actions-automation)
- [Compliance & Best Practices](#compliance--best-practices)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)

## 🔧 Prerequisites

Before you begin, you'll need:

1. **monday.com Account**
   - Free or paid plan
   - API key (get from: https://your-org.monday.com/admin/integrations/api)
   - A board with contact information

2. **Twilio Account**
   - Free trial or paid account (https://www.twilio.com/try-twilio)
   - Account SID and Auth Token
   - A Twilio phone number (SMS-enabled)

3. **Python Environment**
   - Python 3.11 or higher
   - pip for package installation

4. **Legal Compliance**
   - Permission to text your contacts (TCPA compliance)
   - Opt-in records for all contacts

## 🚀 Quick Start

```bash
# 1. Clone and navigate
cd mass-texting-monday-twilio

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Test with dry-run
python mass_texter.py

# 5. Send real messages (when ready)
# Set DRY_RUN=false in .env
python mass_texter.py
```

## 📦 Installation

### Option 1: Local Installation

```bash
# Navigate to the directory
cd mass-texting-monday-twilio

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: GitHub Actions

No local installation needed - just configure GitHub Secrets and run workflows. See [GitHub Actions Automation](#github-actions-automation).

## ⚙️ Configuration

### 1. Create .env File

Copy the example configuration:

```bash
cp .env.example .env
```

### 2. Edit .env File

Open `.env` and configure these required settings:

```bash
# monday.com Configuration
MONDAY_API_KEY=eyJhbGc...your_api_key
MONDAY_BOARD_ID=1234567890

# monday.com Column IDs
MONDAY_PHONE_COLUMN_ID=phone
MONDAY_STATUS_COLUMN_ID=status
MONDAY_OPT_IN_COLUMN_ID=opt_in

# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+15555550100

# Message Configuration
MESSAGE_TEMPLATE=Hi {name}, this is a test message!

# Operation Settings
DRY_RUN=true
RATE_LIMIT_DELAY=1.0
UPDATE_MONDAY_STATUS=true
```

### Getting Your Credentials

#### monday.com API Key

1. Go to: https://your-org.monday.com/admin/integrations/api
2. Click **"Generate"** or copy your existing API key
3. Paste into `MONDAY_API_KEY`

#### monday.com Board ID

1. Open your board in monday.com
2. Look at the URL: `https://your-org.monday.com/boards/1234567890`
3. The number at the end (`1234567890`) is your Board ID
4. Paste into `MONDAY_BOARD_ID`

#### monday.com Column IDs

See the [Board Setup Guide](BOARD-SETUP-GUIDE.md) for detailed instructions on finding column IDs using the API Playground.

#### Twilio Credentials

1. Go to: https://console.twilio.com/
2. Find your **Account SID** and **Auth Token** on the dashboard
3. Get a phone number from: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
4. Paste into `.env`

## 📊 monday.com Board Setup

Your monday.com board needs specific columns for the system to work. See the detailed [Board Setup Guide](BOARD-SETUP-GUIDE.md) for step-by-step instructions.

### Quick Board Setup

**Required Columns:**

| Column Name | Column Type | Column ID | Purpose |
|-------------|-------------|-----------|---------|
| Name | Item Name | (default) | Contact's full name |
| Phone | Phone | `phone` | Phone number for SMS |
| Opt In | Checkbox | `opt_in` | Has contact opted in? |
| Status | Status Label | `status` | Message delivery status |

**Import Template:**

Use the included `monday-board-template.csv` to quickly set up your board:

1. Create a new board in monday.com
2. Import → From CSV
3. Upload `monday-board-template.csv`
4. Map columns and import

**Status Labels:**

Configure these labels in your Status column:
- **Pending** (Gray) - Not sent yet
- **Sent** (Green) - Successfully delivered
- **Failed** (Red) - Delivery failed
- **Skipped** (Yellow) - Not opted in or invalid

## 💬 Message Templates

Use placeholders to personalize messages with data from your monday.com board.

### Available Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{name}` | Contact's full name (Item Name) | John Doe |
| `{first_name}` | First name column | John |
| `{last_name}` | Last name column | Doe |
| `{organization}` | Organization column | Acme Corp |
| `{column_id}` | Any column ID from your board | Custom value |

### Example Templates

**Basic Message:**
```
Hi {name}, this is a reminder about our event tomorrow at 7 PM!
```

**Personalized Outreach:**
```
Hi {first_name}! Thanks for your support of {organization}. Can we count on you for this weekend's volunteer opportunity?
```

**Event Reminder:**
```
Hey {first_name}, just a reminder: Our community meeting is tonight at 6 PM. See you there! Reply STOP to unsubscribe.
```

### Best Practices for Messages

✅ **DO:**
- Keep messages under 160 characters (single SMS)
- Include your organization name
- Add "Reply STOP to unsubscribe" for compliance
- Test with dry-run mode first
- Personalize with recipient's name

❌ **DON'T:**
- Send promotional content without consent
- Include sensitive information
- Use ALL CAPS (looks like spam)
- Send too frequently
- Forget opt-out instructions

## 🚀 Usage

### Running a Campaign

#### Step 1: Dry Run (Test Mode)

Always start with a dry run to preview what will be sent:

```bash
# Ensure DRY_RUN=true in .env
python mass_texter.py
```

This will:
- Fetch all contacts from monday.com
- Check opt-in status
- Format phone numbers
- Preview messages
- **NOT send any actual texts**
- Generate a results file

#### Step 2: Review Results

Check the output:

```bash
# View the log
cat mass_texter.log

# View the results JSON
cat campaign_results_*.json
```

Look for:
- Total contacts fetched
- How many are opted in
- Any invalid phone numbers
- Message previews

#### Step 3: Live Campaign

When ready to send real messages:

1. Edit `.env` and set:
   ```bash
   DRY_RUN=false
   ```

2. Run the campaign:
   ```bash
   python mass_texter.py
   ```

3. Monitor the output in real-time

#### Step 4: Review Results

After sending:

```bash
# View summary statistics
tail -20 mass_texter.log

# Check detailed results
cat campaign_results_YYYYMMDD_HHMMSS.json
```

### Command Line Output

The script provides real-time feedback:

```
============================================================
Starting Mass Texting Campaign
Mode: LIVE
Board ID: 1234567890
============================================================
Fetching contacts from monday.com...
Fetched 50 items from board 1234567890

[1/50] Processing: John Doe (ID: 987654321)
  → To: +15555550101
  → Message: Hi John, this is a test message!
  ✓ Sent successfully - SID: SM1234567890abcdef

[2/50] Processing: Jane Smith (ID: 987654322)
  ⊘ Skipped - Not opted in

...

============================================================
CAMPAIGN SUMMARY
============================================================
Total Contacts:     50
Opted In:           42
Messages Sent:      40
Messages Failed:    2
Skipped:            8
Success Rate:       95.2%
============================================================
```

## 🤖 GitHub Actions Automation

Automate campaigns using GitHub Actions workflows.

### Setup

1. **Add Secrets** to your GitHub repository:

   Go to: Settings → Secrets and variables → Actions → New repository secret

   Add these secrets:
   ```
   MONDAY_API_KEY
   MONDAY_BOARD_ID
   MONDAY_PHONE_COLUMN_ID
   MONDAY_STATUS_COLUMN_ID
   MONDAY_OPT_IN_COLUMN_ID
   TWILIO_ACCOUNT_SID
   TWILIO_AUTH_TOKEN
   TWILIO_FROM_NUMBER
   MESSAGE_TEMPLATE
   ```

2. **Run Workflow Manually:**

   - Go to: Actions → Mass Texting Campaign → Run workflow
   - Choose dry-run mode: `true` or `false`
   - Optionally override message template
   - Click **Run workflow**

3. **View Results:**

   - Check the workflow run for live logs
   - Download artifacts for campaign results JSON

### Workflow Features

- **Manual trigger only** (for safety - prevents accidental spam)
- **Dry-run option** in workflow inputs
- **Message override** capability
- **Artifact upload** with 90-day retention
- **Summary display** in workflow output

### Scheduled Campaigns (Optional)

To enable scheduled campaigns, edit `.github/workflows/mass-texting.yml`:

```yaml
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
  workflow_dispatch:
    # ... rest of config
```

⚠️ **Warning:** Only use scheduled campaigns if you're 100% certain about:
- Your contact list is up to date
- All contacts have valid opt-ins
- Your message is appropriate for automated sending
- You have proper rate limiting configured

## 📜 Compliance & Best Practices

### Legal Requirements

⚠️ **IMPORTANT:** You are responsible for complying with all applicable laws, including:

- **TCPA (Telephone Consumer Protection Act)** - US law requiring consent
- **GDPR** - EU data protection regulation
- **CASL** - Canadian anti-spam legislation
- **State-specific laws** - Many US states have additional requirements

### Opt-In Best Practices

1. **Get Express Consent**
   - Written or verbal agreement to receive texts
   - Must be clear, conspicuous, and separate from other agreements
   - Document when/how consent was obtained

2. **Track Opt-In Status**
   - Use the "Opt In" checkbox in monday.com
   - Only send to contacts where Opt In = Yes
   - Keep records of consent (use Notes column)

3. **Provide Opt-Out**
   - Include "Reply STOP to unsubscribe" in every message
   - Honor opt-out requests immediately
   - Update monday.com when someone opts out

### Message Content Guidelines

✅ **DO:**
- Identify your organization clearly
- Keep messages relevant and valuable
- Send during reasonable hours (9 AM - 9 PM local time)
- Limit frequency (no more than 2-3 per week)
- Include opt-out instructions

❌ **DON'T:**
- Send unsolicited commercial texts
- Use misleading sender information
- Send outside of reasonable hours
- Continue after opt-out request
- Share or sell contact lists

### Rate Limiting

Twilio rate limits:
- **1 message per second** per phone number
- **Higher rates** with toll-free or short codes

The script includes built-in rate limiting:
```bash
RATE_LIMIT_DELAY=1.0  # 1 second between messages
```

Adjust if needed, but never go below Twilio's limits.

### Data Security

- **Never commit** `.env` files with real credentials
- **Use GitHub Secrets** for automation
- **Limit API access** to necessary personnel
- **Regularly review** who has access to your board
- **Delete old data** when no longer needed

## 🔍 Troubleshooting

### Common Issues

#### "No contacts found in board"

**Causes:**
- Wrong Board ID
- Board is empty
- API key doesn't have access to board

**Solutions:**
- Verify `MONDAY_BOARD_ID` in `.env`
- Check board has items
- Confirm API key permissions

#### "Failed to send SMS: 403 Forbidden"

**Causes:**
- Invalid Twilio credentials
- Phone number not SMS-enabled
- Account suspended or trial restrictions

**Solutions:**
- Verify `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`
- Check phone number capabilities in Twilio console
- Ensure account is active and funded

#### "Invalid phone number"

**Causes:**
- Phone missing country code
- Invalid format
- Non-SMS capable number

**Solutions:**
- Format: `+1-555-555-5555` (US)
- Include + and country code
- Verify number is mobile (not landline)

#### "Column not found: phone"

**Causes:**
- Column ID doesn't match
- Column doesn't exist in board

**Solutions:**
- Get exact column ID from API Playground
- Update `MONDAY_PHONE_COLUMN_ID` in `.env`
- Ensure column exists in board

### Debug Mode

For detailed debugging:

```bash
# View full error stack traces
python mass_texter.py 2>&1 | tee debug.log

# Check monday.com API response
# Add this to mass_texter.py temporarily:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Files

Check these files for troubleshooting:

```bash
# Application log
cat mass_texter.log

# Campaign results
cat campaign_results_*.json

# GitHub Actions logs
# View in: Actions → Workflow run → Job logs
```

## 📚 API Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MONDAY_API_KEY` | Yes | - | monday.com API key |
| `MONDAY_BOARD_ID` | Yes | - | Board ID for contacts |
| `MONDAY_PHONE_COLUMN_ID` | No | `phone` | Column ID for phone numbers |
| `MONDAY_STATUS_COLUMN_ID` | No | `status` | Column ID for status tracking |
| `MONDAY_OPT_IN_COLUMN_ID` | No | `opt_in` | Column ID for opt-in status |
| `TWILIO_ACCOUNT_SID` | Yes | - | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Yes | - | Twilio auth token |
| `TWILIO_FROM_NUMBER` | Yes | - | Twilio phone number (E.164 format) |
| `MESSAGE_TEMPLATE` | Yes | - | Message template with placeholders |
| `DRY_RUN` | No | `true` | Test mode (true/false) |
| `RATE_LIMIT_DELAY` | No | `1.0` | Seconds between messages |
| `UPDATE_MONDAY_STATUS` | No | `true` | Update status in monday.com (true/false) |

### Campaign Results JSON

The script generates a JSON file with this structure:

```json
{
  "timestamp": "2024-01-15T14:30:00",
  "board_id": "1234567890",
  "dry_run": false,
  "statistics": {
    "total_contacts": 50,
    "opted_in": 42,
    "messages_sent": 40,
    "messages_failed": 2,
    "skipped": 8
  },
  "results": [
    {
      "item_id": "987654321",
      "name": "John Doe",
      "phone": "+15555550101",
      "status": "sent",
      "sid": "SM1234567890abcdef",
      "error": null
    }
  ]
}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Fatal error (see logs) |

## 🤝 Contributing

Contributions welcome! Please:

1. Test changes thoroughly with dry-run mode
2. Update documentation
3. Follow existing code style
4. Add error handling

## 📄 License

This project is part of CivicOperator and follows the same license terms.

## 🆘 Support

- **Documentation Issues**: Open an issue in this repository
- **monday.com API**: https://support.monday.com
- **Twilio API**: https://support.twilio.com
- **TCPA Compliance**: Consult with legal counsel

## 🎯 Use Cases

This system is perfect for:

- **Civic Engagement**: Voter registration reminders, town hall notifications
- **Community Organizing**: Event announcements, volunteer coordination
- **Nonprofit Outreach**: Donor updates, campaign mobilization
- **Emergency Notifications**: Urgent alerts, weather warnings
- **Event Management**: RSVPs, schedule changes, reminders

## 🔄 Version History

- **v1.0.0** (2024) - Initial release
  - monday.com integration
  - Twilio SMS sending
  - Dry-run mode
  - GitHub Actions support
  - Opt-in compliance features

---

**Ready to start?** Follow the [Quick Start](#quick-start) guide above!

For board setup help, see the [Board Setup Guide](BOARD-SETUP-GUIDE.md).
