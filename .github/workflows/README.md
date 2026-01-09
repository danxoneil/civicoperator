# GitHub Actions Workflows

## Automated Dress Monitoring

This directory contains GitHub Actions workflows that automate the Emilio Pucci dress availability monitoring.

### Available Workflows

#### `dress-monitor.yml` - Daily Automated Monitoring

**Runs:** Daily at 9:00 AM UTC (automatically)

**What it does:**
1. Checks all retail sources for dress availability
2. Sends email notifications if configured
3. Creates a GitHub Issue if dress is found
4. Saves logs and findings as artifacts

**Manual Trigger:** You can also run it anytime from the "Actions" tab in GitHub

### Setup Instructions

#### 1. Enable GitHub Actions

The workflow is already configured! It will run automatically once this code is pushed to GitHub.

#### 2. Configure Email Notifications (Optional)

If you want email alerts when the dress is found:

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `SEND_EMAIL_NOTIFICATIONS` | `true` | `true` |
| `NOTIFICATION_EMAIL` | Your email address | `you@example.com` |
| `SMTP_SERVER` | SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | Your email | `you@gmail.com` |
| `SMTP_PASSWORD` | App password | `xxxx xxxx xxxx xxxx` |

**For Gmail users:** Use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

#### 3. View Results

**Check workflow runs:**
- Go to the **Actions** tab in your GitHub repository
- Click on "Emilio Pucci Dress Monitor"
- View the latest run

**Check for findings:**
- If the dress is found, a GitHub Issue will be created automatically
- Check the **Issues** tab for alerts
- Download artifacts to see full logs

**View logs:**
- Click on any workflow run
- Scroll down to **Artifacts**
- Download `monitor-logs-XXX.zip`
- Extract and view `monitor.log` and `findings.json`

### Adjusting the Schedule

By default, the monitor runs **daily at 9:00 AM UTC**.

To change the schedule, edit `.github/workflows/dress-monitor.yml`:

```yaml
on:
  schedule:
    # Examples (use cron syntax):
    - cron: '0 */6 * * *'    # Every 6 hours
    - cron: '0 9,21 * * *'   # Twice daily (9 AM and 9 PM)
    - cron: '0 9 * * 1-5'    # Weekdays only at 9 AM
```

Use [crontab.guru](https://crontab.guru/) to help create schedules.

### Manual Runs

You can trigger a check anytime:

1. Go to **Actions** tab
2. Click "Emilio Pucci Dress Monitor"
3. Click **Run workflow** button
4. Select branch and click **Run workflow**

### Troubleshooting

**Workflow not running:**
- Ensure you've pushed the `.github/workflows/dress-monitor.yml` file
- Check that Actions are enabled in Settings → Actions → General

**Email not sending:**
- Verify all SMTP secrets are configured correctly
- Check workflow run logs for error messages
- For Gmail, ensure you're using an App Password

**Want to disable monitoring:**
- Go to Actions → Emilio Pucci Dress Monitor → ... (menu) → Disable workflow

### Cost

GitHub Actions is **free** for public repositories and includes 2,000 minutes/month for private repos. This workflow uses about 2-3 minutes per run, so daily monitoring is well within free limits.

---

**Questions?** Check the main [dress-monitor README](../../dress-monitor/README.md)
