# Quick Start Guide

## 🚀 Two Ways to Get Started

### ⭐ Option 1: GitHub Actions (EASIEST - Recommended)

**Zero setup, runs automatically in the cloud:**

1. Push this code to GitHub
2. Done! It runs daily at 9 AM automatically
3. Check GitHub Issues tab for alerts when dress is found

**See:** [.github/workflows/README.md](../.github/workflows/README.md)

---

### Option 2: Local Setup (5 Minutes)

**Run on your own computer/server:**

#### Step 1: Setup
```bash
cd dress-monitor
./setup.sh
```

### Step 2: Configure (Optional)
```bash
# For email notifications, edit .env:
nano .env

# Set these values:
SEND_EMAIL_NOTIFICATIONS=true
NOTIFICATION_EMAIL=your-email@example.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Step 3: Test Run
```bash
source venv/bin/activate
python3 monitor.py
```

### Step 4: Automate Daily Checks
```bash
./setup_cron.sh
```

## ✅ That's it!

The system will now check daily for the Emilio Pucci dress in size IT 40.

## 📊 Check Results

- **View logs:** `tail -f monitor.log`
- **View findings:** `cat findings.json`
- **Manual check:** `python3 monitor.py`

## 🔔 Notifications

When the dress is found, you'll see:
- Console output with item details
- Email notification (if configured)
- Entry in `findings.json`
- Log entry in `monitor.log`

## 🎯 What It Monitors

✅ Farfetch (primary)
✅ Official Pucci website
✅ Net-A-Porter
✅ Mytheresa
✅ Vestiaire Collective (resale)
✅ The RealReal (resale)
✅ Lyst (aggregator)

## 🔧 Advanced

Use the enhanced monitor for better scraping:
```bash
python3 monitor_enhanced.py
```

## 💡 Tips

1. **Check logs regularly** to ensure it's running
2. **Test email notifications** before relying on them
3. **Verify cron is active**: `crontab -l`
4. **Adjust schedule** if needed (default: daily at 9 AM)

## ❓ Need Help?

See the full [README.md](README.md) for detailed documentation.
