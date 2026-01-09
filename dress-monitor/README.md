# Emilio Pucci Dress Availability Monitor

Automated daily monitoring system for tracking availability of a specific Emilio Pucci graphic-print maxi dress in size IT 40.

## 🎯 Target Item

- **Brand:** Emilio Pucci
- **Item:** Graphic-print maxi dress
- **Size:** IT 40 (EU 40)

## 🛍️ Monitored Sources

### Primary Source
- **Farfetch** - Premium fashion retailer

### Secondary Sources
- Official Pucci website (pucci.com)
- Net-A-Porter
- Mytheresa
- The Outnet
- Lyst (aggregator)

### Resale/Secondary Market
- Vestiaire Collective
- The RealReal
- Poshmark
- eBay (via reputable sellers)

## 📋 Features

- ✅ Daily automated checks across multiple retailers
- ✅ Exact match verification (brand, style, size)
- ✅ Email notifications when item is found
- ✅ Detailed logging of all checks
- ✅ JSON export of findings
- ✅ Respects retailer rate limits
- ✅ Easy configuration via environment variables

## 🚀 Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Linux/macOS with cron (for scheduling)

### Installation

1. **Run the setup script:**
   ```bash
   cd dress-monitor
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure notifications:**
   Edit the `.env` file with your settings:
   ```bash
   nano .env
   ```

   For email notifications, set:
   ```
   SEND_EMAIL_NOTIFICATIONS=true
   NOTIFICATION_EMAIL=your-email@example.com
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

   **Note for Gmail users:** Use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

3. **Test the monitor:**
   ```bash
   source venv/bin/activate
   python3 monitor.py
   ```

4. **Set up daily automated checks:**
   ```bash
   chmod +x setup_cron.sh
   ./setup_cron.sh
   ```

## 🔔 Notification Details

When a matching dress is found, you'll receive:

- Direct link to the listing
- Retailer/platform name
- Price (if available)
- Condition (new or resale)
- Size confirmation
- Timestamp of discovery
- Any relevant notes (limited stock, final sale, etc.)

## 📊 Monitoring Rules

The system will ONLY notify when:
- ✅ Exact match: Emilio Pucci graphic-print maxi dress
- ✅ Size IT 40 is explicitly available
- ✅ Listing is from a reputable source

The system will NOT notify for:
- ❌ Similar prints or different silhouettes
- ❌ Different sizes (even if close)
- ❌ Different dress styles
- ❌ Out of stock listings

## 📁 Files

- `monitor.py` - Main monitoring script
- `requirements.txt` - Python dependencies
- `.env` - Configuration (create from `.env.example`)
- `setup.sh` - Installation script
- `setup_cron.sh` - Cron job setup
- `monitor.log` - Activity logs
- `findings.json` - Found items (created when matches are found)
- `cron.log` - Cron execution logs

## 🔧 Manual Usage

Run a manual check at any time:

```bash
cd dress-monitor
source venv/bin/activate
python3 monitor.py
```

## 📅 Schedule Modification

The default schedule runs daily at 9:00 AM. To change this:

1. Edit your crontab:
   ```bash
   crontab -e
   ```

2. Modify the schedule (uses [cron syntax](https://crontab.guru/)):
   ```
   # Example: Run every 12 hours at 9 AM and 9 PM
   0 9,21 * * * cd /path/to/dress-monitor && /path/to/venv/bin/python3 monitor.py >> cron.log 2>&1

   # Example: Run every 6 hours
   0 */6 * * * cd /path/to/dress-monitor && /path/to/venv/bin/python3 monitor.py >> cron.log 2>&1
   ```

## 🐛 Troubleshooting

### Check if cron is running
```bash
crontab -l
```

### View recent logs
```bash
tail -f dress-monitor/monitor.log
```

### View cron execution logs
```bash
tail -f dress-monitor/cron.log
```

### Test email notifications
Set `SEND_EMAIL_NOTIFICATIONS=true` in `.env` and run a manual check.

### Common issues

1. **"No module named 'requests'"**
   - Make sure virtual environment is activated: `source venv/bin/activate`
   - Reinstall dependencies: `pip install -r requirements.txt`

2. **Email not sending**
   - Verify SMTP credentials in `.env`
   - For Gmail, use an App Password, not your regular password
   - Check that `SEND_EMAIL_NOTIFICATIONS=true`

3. **Cron not running**
   - Verify cron service is active: `systemctl status cron`
   - Check cron logs: `grep CRON /var/log/syslog`
   - Ensure paths in crontab are absolute paths

## 🔒 Security Notes

- Never commit `.env` file to version control
- Use app-specific passwords for email services
- Keep `findings.json` private (may contain pricing data)
- Monitor logs for unusual activity

## 🎨 Customization

To monitor different items, edit `monitor.py`:

```python
# Configuration section (lines 15-18)
TARGET_BRAND = "Your Brand"
TARGET_ITEM = "item description"
TARGET_SIZE = "your size"
```

## 📝 Advanced: JavaScript-Rendered Sites

Some retailers (like Farfetch) use JavaScript to render content. For these sites:

1. Install Selenium dependencies:
   ```bash
   pip install selenium webdriver-manager
   ```

2. Uncomment Selenium imports in `monitor.py`

3. Implement browser-based checking (example code provided in comments)

## 🤝 Contributing

This is a personal monitoring tool. Customize as needed for your use case.

## ⚖️ Legal Notice

This tool is for personal use only. Users are responsible for:
- Complying with website Terms of Service
- Respecting rate limits and robots.txt
- Not overloading retailer servers
- Following applicable laws and regulations

Web scraping should be done responsibly and ethically.

## 📞 Support

For issues with the monitoring system, check:
1. Log files (`monitor.log`, `cron.log`)
2. Environment configuration (`.env`)
3. Network connectivity
4. Python dependencies

---

**Last Updated:** January 2026
