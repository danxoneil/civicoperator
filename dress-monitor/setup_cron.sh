#!/bin/bash
# Setup daily cron job for dress monitoring

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MONITOR_SCRIPT="$SCRIPT_DIR/monitor.py"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"

echo "🕐 Setting up daily cron job for dress monitoring..."

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Create cron job (runs daily at 9:00 AM)
CRON_JOB="0 9 * * * cd $SCRIPT_DIR && $VENV_PYTHON $MONITOR_SCRIPT >> $SCRIPT_DIR/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$MONITOR_SCRIPT"; then
    echo "⚠️  Cron job already exists. Updating..."
    # Remove old cron job
    crontab -l 2>/dev/null | grep -v "$MONITOR_SCRIPT" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job added successfully!"
echo ""
echo "The monitor will run daily at 9:00 AM"
echo "To view current cron jobs: crontab -l"
echo "To edit cron jobs: crontab -e"
echo "To remove this cron job: crontab -e (then delete the line)"
echo ""
echo "Logs will be saved to: $SCRIPT_DIR/cron.log"
