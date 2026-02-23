# State Spending Monitor: Launch Blog Feature Summary

## What it is
State Spending Monitor is an automated intelligence pipeline for tracking Rural Health Transformation Program (RHTP) activity across all 50 U.S. states. It combines official government sources, media monitoring, board-driven URL surveillance, and automated reporting to help teams detect, validate, and communicate changes quickly.

## Core monitoring capabilities

### 1) 50-state RHTP news monitoring (`monitor.py`)
- Monitors **all 50 states** with built-in state mappings.
- Supports three source modes:
  - `official` (CMS, HHS, and state health departments)
  - `news` (Google News RSS)
  - `all` (default, combines both)
- Pulls from multiple federal and state endpoints, including:
  - CMS newsroom feeds (with fallback feed URL patterns)
  - CMS and HHS pages via direct scraping
  - State health department news pages for every state
  - State-specific Google News RSS queries
- Includes resilient HTTP behavior:
  - retry/backoff for transient failures
  - browser-like headers for higher compatibility
  - proxy-environment isolation for CI stability

### 2) Relevance and signal quality filtering
- Uses RHTP-focused keyword matching plus broader rural-health/funding context matching.
- Requires state mention matching (abbreviation/full name) for geographic relevance.
- Applies lookback windows for freshness filtering.
- Tracks source success/error stats to monitor feed health over time.

### 3) Deduplication and historical persistence
- Prevents duplicate findings across runs.
- Writes cumulative results to `findings.json`.
- Produces execution logs in `monitor.log`.
- Generates run summaries and status payloads suitable for automation/reporting.

### 4) Notification workflows
- Sends SMTP email alerts for findings and/or run status.
- Supports configurable notification behavior through environment variables.
- Formats human-readable result digests for rapid triage.

## URL lifecycle operations (board-driven)

### 5) monday.com-powered URL change monitoring (`url_monitor.py`)
- Pulls monitored URLs directly from a monday.com board.
- Supports URL column selection by ID/title with auto-detection fallback.
- Can use item name as URL when configured.
- Fetches pages, strips boilerplate HTML, and compares normalized text snapshots.
- Detects meaningful change via hash + line-level diffs.
- Filters trivial/noise-only changes (e.g., captcha churn/timestamp-only deltas).
- Handles access-restricted pages (e.g., HTTP 403) as valid-but-undiffable states.
- Persists snapshots to `snapshots.json` for day-over-day change tracking.
- Updates monday.com status column (e.g., mark items Done when validated).

### 6) URL validation and repair tooling (`validate_urls.py`)
- Audits URL health from monday.com board entries.
- Verifies reachability and checks for RHT-related content.
- Can run in dry-run, report-only, or auto-fix mode.
- Searches for replacement URLs when links break, with .gov preference heuristics.
- Can write corrected links back to monday.com.

### 7) One-time board patch utility (`fix_board_urls.py`)
- Adds missing known state URLs and replaces known bad mappings.
- Supports dry-run mode for safe preview.
- Produces GitHub Actions summary output for operational transparency.

## Visual and asset workflows

### 8) Automated screenshots of changed pages (`screenshots.py`)
- Uses Playwright (headless Chromium) to capture full-page screenshots of changed URLs.
- Saves state-named PNG artifacts in a configurable output directory.
- Returns a map of state → screenshot path for downstream automation.

### 9) Google Drive screenshot publishing (`drive_upload.py`)
- Uploads screenshot artifacts to Google Drive via service account credentials.
- Optionally creates date/run subfolders.
- Sets files/folders to link-viewable and returns shareable URLs.
- Enables direct embedding of visual evidence in issues and reports.

## Reporting and editorial acceleration

### 10) Weekly newsletter briefing generator (`newsletter.py`)
- Pulls weekly “page changed” issues from GitHub (`url-monitor` + `page-changed` labels).
- Parses issue diffs, removes binary-garbage artifacts, and deduplicates by URL.
- Re-fetches changed pages and follows key outbound links for richer context.
- Optionally extracts PDF text when PDF tooling is available.
- Pulls topic context from monday.com topics board.
- Produces a structured briefing report intended for rapid newsletter drafting.
- Saves output and posts to GitHub for asynchronous editorial workflows.

## Operational readiness features

### 11) CI/CD and automation-friendly design
- Script-level CLI entry points for local and CI execution.
- Environment-variable based configuration for secrets and runtime behavior.
- Structured logs for troubleshooting (`monitor.log`, `url-monitor.log`, `validate-urls.log`).
- Defensive dependency handling with clear install guidance on missing packages.

### 12) Extensibility by design
- Easy keyword/source updates in monitor configuration.
- Modular components (monitoring, validation, screenshots, uploads, newsletter) can run independently or as a pipeline.
- Designed to integrate with GitHub Actions artifacts/issues and external work-management systems (monday.com, Drive).

## Launch positioning (blog-friendly framing)
- **Comprehensive coverage:** all 50 states + federal sources + media aggregation.
- **Actionable alerts:** not just collection, but change detection, validation, and notifications.
- **Operational loop closure:** from data collection → diffing → screenshots → issue/report outputs.
- **Editorial leverage:** transforms raw monitoring events into weekly narrative-ready briefings.
- **Production pragmatism:** retries, fallback source handling, dedupe, and persistent state for dependable daily operation.
