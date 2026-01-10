# Adding Sources to the State Spending News Monitor

This guide shows you how to easily add new monitoring sources to track state spending news.

## Configuration File

All sources are configured in **`sources.json`**. This file contains:
- States to monitor
- RSS feeds to check
- Google News search queries
- Keywords to match
- Settings

## Quick Start Examples

### 1. Add a New State

To add Illinois (IL) to your monitoring:

```json
{
  "states": {
    "CA": { ... },
    "NY": { ... },
    "FL": { ... },
    "TX": { ... },
    "IL": {
      "name": "Illinois",
      "health_dept_url": "https://dph.illinois.gov/news.html",
      "enabled": true
    }
  }
}
```

**Tip:** Set `"enabled": false` to temporarily disable a state without deleting it.

### 2. Add a New RSS Feed

To add a new federal or industry news source:

```json
{
  "rss_sources": [
    {
      "name": "CMS Newsroom",
      "url": "https://www.cms.gov/newsroom/press-releases.rss",
      "type": "rss",
      "scope": "federal",
      "enabled": true
    },
    {
      "name": "Healthcare Finance News",
      "url": "https://www.healthcarefinancenews.com/feed",
      "type": "rss",
      "scope": "industry",
      "enabled": true
    }
  ]
}
```

**Fields:**
- `name` - Display name for the source
- `url` - RSS feed URL
- `type` - Always "rss" for RSS feeds
- `scope` - "federal", "industry", "state", or custom
- `enabled` - Set to false to disable

### 3. Add Google News Search Queries

Add more search queries to find relevant news:

```json
{
  "google_news_queries": [
    "{state_name} rural health funding CMS",
    "{state_name} rural health transformation",
    "{state_name} CMS rural hospital funding",
    "{state_name} rural healthcare grants",
    "{state_name} rural health infrastructure"
  ]
}
```

**Variables you can use:**
- `{state_name}` - Full state name (e.g., "California")
- `{state_code}` - Two-letter code (e.g., "CA")

### 4. Add New Keywords

To match more news articles, add keywords:

```json
{
  "keywords": {
    "primary": [
      "rural health transformation",
      "RHT program",
      "rural health funding",
      "rural healthcare infrastructure",
      "telehealth rural",
      "rural ambulance services"
    ],
    "context": [
      "CMS",
      "Centers for Medicare",
      "Medicaid",
      "billion",
      "million",
      "funding",
      "award",
      "rural",
      "hospital",
      "clinic",
      "healthcare"
    ]
  }
}
```

**How it works:**
- **Primary keywords** - If found, article is considered relevant
- **Context keywords** - Need 3+ matches (configurable) to be relevant

### 5. Adjust Settings

Fine-tune the monitoring behavior:

```json
{
  "settings": {
    "lookback_days": 7,
    "context_keyword_threshold": 3,
    "rate_limit_seconds": 3
  }
}
```

**Settings explained:**
- `lookback_days` - How many days back to search for news (default: 7)
- `context_keyword_threshold` - Minimum context keywords needed (default: 3)
- `rate_limit_seconds` - Delay between requests to avoid rate limiting (default: 3)

## Common Use Cases

### Monitor Additional States

Want to monitor all 50 states? Just add them to the `states` section:

```json
{
  "states": {
    "AL": {"name": "Alabama", "health_dept_url": "https://www.alabamapublichealth.gov/news/", "enabled": true},
    "AK": {"name": "Alaska", "health_dept_url": "https://health.alaska.gov/news/", "enabled": true},
    "AZ": {"name": "Arizona", "health_dept_url": "https://www.azdhs.gov/news/", "enabled": true}
    // ... add all 50 states
  }
}
```

### Add Industry News Sources

Track what healthcare trade publications are saying:

```json
{
  "rss_sources": [
    {"name": "Modern Healthcare", "url": "https://www.modernhealthcare.com/rss", "enabled": true},
    {"name": "Becker's Hospital Review", "url": "https://www.beckershospitalreview.com/rss-feeds", "enabled": true},
    {"name": "Healthcare Dive", "url": "https://www.healthcaredive.com/feeds/news/", "enabled": true},
    {"name": "STAT News", "url": "https://www.statnews.com/feed/", "enabled": true}
  ]
}
```

### Monitor State-Specific RSS Feeds

Some states have RSS feeds for their health departments:

```json
{
  "states": {
    "CA": {
      "name": "California",
      "health_dept_url": "https://www.cdph.ca.gov/Programs/OPA/Pages/New-Release-2026.aspx",
      "rss_feed": "https://www.cdph.ca.gov/Programs/OPA/Pages/rss.aspx",
      "enabled": true
    }
  }
}
```

**Note:** The current version checks `health_dept_url` via web scraping. Future versions may support state-specific RSS feeds.

### Track Multiple Federal Agencies

Add RSS feeds from related federal agencies:

```json
{
  "rss_sources": [
    {"name": "CMS Newsroom", "url": "https://www.cms.gov/newsroom/press-releases.rss", "enabled": true},
    {"name": "HHS Press Releases", "url": "https://www.hhs.gov/about/news/rss/press-releases.xml", "enabled": true},
    {"name": "HRSA Rural Health", "url": "https://www.hrsa.gov/about/news/rss.xml", "enabled": true},
    {"name": "CDC Rural Health", "url": "https://tools.cdc.gov/podcasts/rss.asp?feedid=180", "enabled": true}
  ]
}
```

## Finding RSS Feed URLs

### How to Find RSS Feeds

Most news sites have RSS feeds. Here's how to find them:

1. **Look in the footer** - Many sites link to RSS feeds at the bottom
2. **Add `/rss` or `/feed`** to the URL - Try `site.com/rss` or `site.com/feed`
3. **Check the source code** - Search for "rss" or "feed" in page source
4. **Use RSS discovery tools** - Try https://rss.app/ or similar tools
5. **Google it** - Search for "[site name] rss feed"

### Validating RSS Feeds

Test if an RSS feed works before adding it:

```bash
curl -s "https://example.com/feed.rss" | head -20
```

You should see XML with `<rss>` or `<feed>` tags.

## Testing Your Changes

After editing `sources.json`, test the monitor locally:

```bash
cd state-spending-monitor
python monitor.py
```

Check `monitor.log` for any errors loading your configuration.

## Environment Variables

Some settings can be overridden with environment variables:

- `LOOKBACK_DAYS` - Override the configured lookback period
- `SEND_EMAIL_NOTIFICATIONS` - Enable/disable email (true/false)
- `NOTIFICATION_EMAIL` - Email address for notifications

Example:
```bash
LOOKBACK_DAYS=14 python monitor.py
```

## Configuration Schema Reference

### State Object
```json
{
  "name": "string (required) - Full state name",
  "health_dept_url": "string (optional) - State health dept URL",
  "rss_feed": "string (optional) - State-specific RSS feed",
  "enabled": "boolean (optional, default: true) - Enable/disable state"
}
```

### RSS Source Object
```json
{
  "name": "string (required) - Display name",
  "url": "string (required) - RSS feed URL",
  "type": "string (optional) - Source type",
  "scope": "string (optional) - federal/state/industry",
  "enabled": "boolean (optional, default: true) - Enable/disable source"
}
```

## Troubleshooting

### "Config file not found"
- Make sure `sources.json` is in the same directory as `monitor.py`
- Check for JSON syntax errors with: `python -m json.tool sources.json`

### "Error parsing RSS feed"
- Verify the RSS URL works in your browser
- Some sites block automated access - check the URL manually
- The feed might not be valid RSS/Atom format

### "No findings"
- Check if keywords are too restrictive
- Lower `context_keyword_threshold` from 3 to 2
- Increase `lookback_days` to search further back

### Rate Limiting
- Increase `rate_limit_seconds` if you're getting blocked
- Some sites require delays of 5-10 seconds between requests

## Best Practices

1. **Start small** - Add one source at a time and test
2. **Use descriptive names** - Make source names clear and specific
3. **Document your sources** - Add comments in JSON (use a pre-processor if needed)
4. **Monitor your monitoring** - Check logs regularly for errors
5. **Respect rate limits** - Don't hammer sites with too many requests
6. **Keep it updated** - Remove sources that consistently fail

## Need Help?

- Check `monitor.log` for detailed error messages
- Validate your JSON: https://jsonlint.com/
- Test RSS feeds: https://validator.w3.org/feed/
- Review the main README.md for general setup

## Example: Complete Configuration

Here's a complete `sources.json` with multiple sources:

```json
{
  "states": {
    "CA": {
      "name": "California",
      "health_dept_url": "https://www.cdph.ca.gov/Programs/OPA/Pages/New-Release-2026.aspx",
      "enabled": true
    },
    "NY": {
      "name": "New York",
      "health_dept_url": "https://health.ny.gov/press/releases/",
      "enabled": true
    },
    "TX": {
      "name": "Texas",
      "health_dept_url": "https://www.dshs.texas.gov/news-alerts",
      "enabled": true
    }
  },
  "rss_sources": [
    {
      "name": "CMS Newsroom",
      "url": "https://www.cms.gov/newsroom/press-releases.rss",
      "type": "rss",
      "scope": "federal",
      "enabled": true
    },
    {
      "name": "HHS Press Releases",
      "url": "https://www.hhs.gov/about/news/rss/press-releases.xml",
      "type": "rss",
      "scope": "federal",
      "enabled": true
    },
    {
      "name": "Modern Healthcare",
      "url": "https://www.modernhealthcare.com/rss",
      "type": "rss",
      "scope": "industry",
      "enabled": true
    }
  ],
  "google_news_queries": [
    "{state_name} rural health funding CMS",
    "{state_name} rural health transformation",
    "{state_name} CMS rural hospital",
    "{state_name} rural healthcare grants"
  ],
  "keywords": {
    "primary": [
      "rural health transformation",
      "RHT program",
      "rural health funding",
      "CMS rural health",
      "rural health awards",
      "rural healthcare spending"
    ],
    "context": [
      "CMS",
      "Centers for Medicare",
      "Medicaid",
      "billion",
      "million",
      "funding",
      "award",
      "rural",
      "hospital",
      "healthcare"
    ]
  },
  "settings": {
    "lookback_days": 7,
    "context_keyword_threshold": 3,
    "rate_limit_seconds": 3
  }
}
```

Happy monitoring! 🎯
