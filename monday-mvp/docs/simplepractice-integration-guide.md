# SimplePractice Integration Guide
## Jenkins Creative Counseling Center - monday.com MVP

**Version:** 1.0
**Date:** January 18, 2026

---

## Table of Contents
1. [Integration Overview](#integration-overview)
2. [What Data Comes from SimplePractice](#what-data-comes-from-simplepractice)
3. [Export-Import Workflow](#export-import-workflow)
4. [Session Tracking Automation](#session-tracking-automation)
5. [Claims Data Sync](#claims-data-sync)
6. [Patient Data Sync](#patient-data-sync)
7. [Unique Identifier (UID) Strategy](#unique-identifier-uid-strategy)
8. [Import Frequency Options](#import-frequency-options)
9. [What Gets Updated Automatically vs. Manually](#what-gets-updated-automatically-vs-manually)
10. [Troubleshooting](#troubleshooting)

---

## Integration Overview

### The Simple Truth

**SimplePractice remains your system of record.** monday.com receives data FROM SimplePractice, not the other way around.

**Integration Method:** CSV Export/Import (manual process, scheduled weekly or bi-weekly)

**Why not API integration?**
- SimplePractice API is limited/restricted
- CSV method is proven, reliable, and gives you control
- No ongoing API maintenance/breaking changes
- Lower cost (no middleware/integration tools needed)
- You can validate data before import

### Data Flow Architecture

```
SimplePractice (Source of Truth)
    ↓
Export CSV (Weekly - Monday mornings)
    ↓
Review/Validate CSV
    ↓
Import to monday.com
    ↓
monday.com auto-updates connected boards
    ↓
Alerts/automations trigger based on new data
```

---

## What Data Comes from SimplePractice

### Export #1: Claims Data (Weekly)

**SimplePractice Report:** Claims Report → Export CSV

**Fields Needed:**
- Claim ID/Number
- Patient Name (Last, First)
- Patient ID
- Date of Service
- Submission Date
- Payer/Insurance Company
- Rendering Provider (Clinician)
- Billed Amount
- Allowed Amount
- Paid Amount
- Patient Responsibility
- Claim Status (Submitted/Pending/Paid/Denied)
- Denial Reason (if applicable)

**monday.com Destination:** Claims Tracking board

**Frequency:** Weekly (every Monday morning)

**Who does this:** Billing Staff

**Time required:** 5-10 minutes

---

### Export #2: Session/Appointment Data (Bi-weekly)

**SimplePractice Report:** Appointments Report → Export CSV

**Fields Needed:**
- Patient ID
- Patient Name
- Clinician Name
- Appointment Date
- Appointment Status (Completed/No-show/Cancelled)
- Service Type
- Authorization ID (if applicable)

**monday.com Destination:** Patient-Clinician Assignments board

**Purpose:** Updates "Sessions Used" and "Last Session Date" columns

**Frequency:** Bi-weekly (every other Monday)

**Who does this:** Billing Staff or Admin

**Time required:** 5-10 minutes

---

### Export #3: Patient Demographics (As Needed)

**SimplePractice Report:** Clients Report → Export CSV

**Fields Needed:**
- Patient ID
- Patient Name (Last, First)
- Primary Contact Name
- Contact Phone
- Contact Email
- Insurance Carrier
- Primary Clinician
- Location
- Status (Active/Inactive)

**monday.com Destination:** Patients & Intake board

**Purpose:** Keep intake board in sync with active patients

**Frequency:** As needed (typically monthly, or when completing batch intakes)

**Who does this:** Intake Coordinator

**Time required:** 10 minutes

---

### Export #4: Authorization Data (As Needed)

**SimplePractice Location:** Insurance → Authorizations

**Note:** SimplePractice may not have robust auth tracking - if not, this becomes a manual entry item in monday.com

**Fields Needed:**
- Patient ID
- Authorization Number
- Insurance Carrier
- Authorized Sessions
- Authorization Start Date
- Authorization End Date
- Service Type

**monday.com Destination:** Patient-Clinician Assignments board

**Purpose:** Track authorization expirations and sessions remaining

**Frequency:** When new auths received, or monthly review

**Who does this:** Billing Staff

**Time required:** Varies (10-30 min depending on volume)

---

## Export-Import Workflow

### Step-by-Step: Weekly Claims Import

**Every Monday Morning (9:00 AM):**

#### SimplePractice Side:

1. Log into SimplePractice
2. Navigate to **Billing → Claims Report**
3. Set date filter:
   - **Option A (Incremental):** Last 7 days
   - **Option B (Full refresh):** All active claims (not paid/closed)
4. Click **Export** → Choose **CSV format**
5. Save file: `Claims_Export_2026-01-20.csv`

#### monday.com Side:

1. Open **Claims Tracking** board
2. Click **⋯** (board menu) → **Import data**
3. Click **Upload file** → Select downloaded CSV
4. **Map columns:**
   - SimplePractice "Claim ID" → monday.com "Claim Number"
   - SimplePractice "Patient Name" → monday.com "Patient Name" (will connect to existing patient)
   - SimplePractice "DOS" → monday.com "Service Date"
   - etc. (mapping is saved after first import)
5. **Choose update method:**
   - ✅ **Update existing items** (based on Claim Number match)
   - ✅ **Create new items** (for new claims)
6. Click **Import**
7. Review import log for errors
8. **Verify connections:**
   - Spot-check 3-5 claims
   - Ensure Patient Name connected to correct patient
   - Ensure Clinician connected properly

**Common Issues:**
- Patient name mismatch (SimplePractice has "Smith, John" but monday.com has "John Smith")
  - **Solution:** Standardize format OR use Patient ID for matching
- New clinician not in system yet
  - **Solution:** Add to Clinicians board first, then re-import

**Total time:** 15-20 minutes first time, 8-10 minutes once familiar

---

### Step-by-Step: Bi-Weekly Session Update

**Every Other Monday (9:30 AM):**

#### SimplePractice Side:

1. Navigate to **Calendar → Appointments Report**
2. Set date filter: Last 14 days
3. Filter: Status = "Completed" (exclude no-shows/cancelled)
4. Export CSV: `Sessions_Export_2026-01-20.csv`

#### monday.com Side:

1. Open **Patient-Clinician Assignments** board
2. Import CSV (same process as claims)
3. **Key difference:** This import UPDATES existing assignments
   - Match on: Patient ID + Clinician ID
   - Updates: "Sessions Used" (increments count), "Last Session Date"

#### Alternative Method: Manual Update

If SimplePractice export is difficult:
- Billing staff manually reviews appointments in SimplePractice
- Updates "Sessions Used" column in monday.com for each active assignment
- Takes 15-20 minutes for ~150 active assignments

**Our recommendation:** Start manual, automate after 30 days once workflow is proven

---

## Session Tracking Automation

### The Question: "Is it possible to auto-populate sessions remaining?"

**Short Answer:** Yes, with weekly/bi-weekly imports OR manual updates

**How It Works:**

#### Columns in Patient-Clinician Assignments Board:

| Column | Type | Source | Auto-Update? |
|--------|------|--------|--------------|
| Authorized Sessions | Number | Manual entry (from auth letter) | No - entered once |
| Sessions Used | Number | SimplePractice import OR manual update | **Yes - weekly/bi-weekly** |
| Sessions Remaining | Formula | Calculated | **Yes - real-time** |
| Last Session Date | Date | SimplePractice import OR manual update | **Yes - weekly/bi-weekly** |
| Authorization End Date | Date | Manual entry (from auth letter) | No - entered once |
| Days Until Auth Expires | Formula | Calculated | **Yes - real-time** |

#### Formula Columns (Auto-Calculate):

**Sessions Remaining:**
```
{Authorized Sessions} - {Sessions Used}
```
Updates instantly when "Sessions Used" changes.

**Days Until Auth Expires:**
```
DAYS(TODAY(), {Authorization End Date})
```
Recalculates daily automatically.

**Days Since Last Session:**
```
DAYS({Last Session Date}, TODAY())
```
Recalculates daily automatically.

---

### Real-World Example

**Patient: Emma Martinez**
**Clinician: Dr. Sarah Mitchell**

#### Initial Setup (Manual Entry - One Time):
- Authorized Sessions: 20
- Authorization End Date: 03/15/2026
- Sessions Used: 0 (starting point)

#### Week 1 (After first import):
- SimplePractice shows 3 completed appointments
- Monday import updates "Sessions Used" to 3
- **Auto-calculated:**
  - Sessions Remaining: 17 (20 - 3)
  - Last Session Date: 01/17/2026
  - Days Until Auth Expires: 57 days
  - Days Since Last Session: 1 day

#### Week 5 (Import shows 12 sessions complete):
- Import updates "Sessions Used" to 12
- **Auto-calculated:**
  - Sessions Remaining: 8 (20 - 12)
  - Days Until Auth Expires: 29 days
  - **Automation triggers:** Because Sessions Remaining ≤ 10, notification sent to request auth extension

#### Week 8 (14 days before auth expires):
- Days Until Auth Expires: 13 days
- **Automation triggers:** Email sent to clinician and billing staff: "Authorization expiring soon"

---

### Import vs. Manual Update - Trade-offs

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Weekly Import** | Accurate, scalable, less prone to human error | Requires consistent SimplePractice export format, initial setup | Practices with >100 active assignments |
| **Bi-Weekly Import** | Good balance of accuracy and effort | 2-week lag on session counts | Medium practices (50-100 assignments) |
| **Manual Update** | No export needed, flexible | Time-consuming, prone to errors | Small practices (<50 assignments) OR pilot phase |

**Our Recommendation for JCCC:**
- **Months 1-2:** Manual updates (build comfort, validate workflow)
- **Month 3+:** Weekly imports (scale as comfort grows)

---

## Claims Data Sync

### Critical Fields for Claims Management

**Must-Have Fields:**
1. Claim Number (unique identifier)
2. Patient ID (to connect to patient record)
3. Submission Date (to calculate aging)
4. Claim Amount (to prioritize high-dollar follow-ups)
5. Claim Status (to trigger denial workflows)

**Nice-to-Have Fields:**
6. Denial Reason (for analytics)
7. Allowed Amount (to calculate write-offs)
8. Paid Amount (to calculate outstanding)
9. Last Payment Date (to track velocity)

### Claim Status Mapping

SimplePractice statuses → monday.com statuses:

| SimplePractice | monday.com Status | Auto-Group |
|----------------|-------------------|------------|
| Submitted | Submitted | Newly Submitted |
| In Process | Pending | Pending/In Process |
| (30-60 days old) | Pending | Aging |
| (60-90 days old) | Aging | Aging |
| (90+ days old) | At Risk | At Risk |
| Paid | Paid | Resolved |
| Denied | Denied | Denied |
| Rejected | Denied | Denied |

### Handling Denials

**Workflow:**
1. Weekly import shows Claim Status = "Denied"
2. **Automation triggers** (Automation #11):
   - Priority changes to "High"
   - Follow-Up Owner assigned (based on payer or round-robin)
   - Next Follow-Up Date set (7 days out)
   - Email sent to billing staff with claim details
3. Billing staff reviews denial reason
4. Staff updates "Resolution Notes" with action plan
5. When appeal filed, update "Appeal Filed Date"
6. On subsequent imports, if status changes to "Paid," auto-moves to Resolved

---

## Patient Data Sync

### When to Sync Patient Data

**Scenario 1: New Intake Complete**
- Patient completes intake in monday.com
- Intake coordinator enters patient into SimplePractice
- **ONE-TIME SYNC:** After SimplePractice entry, update monday.com with SimplePractice Patient ID
  - This "links" the records permanently
  - Future imports will match on this ID

**Scenario 2: Monthly Refresh**
- Export all active patients from SimplePractice
- Import to update insurance carrier, status, primary clinician
- Catches any changes made in SimplePractice

**Scenario 3: Insurance Changes**
- Patient switches insurance mid-treatment
- Update in SimplePractice
- Next monthly sync updates monday.com
- OR manually update in monday.com immediately

---

## Unique Identifier (UID) Strategy

### Why UIDs Matter

monday.com needs to know: "Is this the same patient/claim/clinician?"

Without UIDs, you get duplicates or failed connections.

### UID Strategy by Entity

#### Patients

**SimplePractice UID:** Client ID (numeric, e.g., 12345)

**monday.com Column:** "Patient ID" (e.g., PT-1001)

**Matching Strategy:**
- **Option A:** Use SimplePractice Client ID directly (12345)
- **Option B:** Create mapped ID (PT-12345)
- **Option C:** Use custom JCCC ID if you already have one

**Recommendation:** Use SimplePractice Client ID directly for simplest matching

**How It Works:**
- First import: Creates new patient, stores SimplePractice Client ID
- Future imports: Matches on Client ID, updates existing record (no duplicates)

---

#### Claims

**SimplePractice UID:** Claim ID (alphanumeric, e.g., CLM-2024-001)

**monday.com Column:** "Claim Number"

**Matching Strategy:** Direct match - SimplePractice Claim ID = monday.com Claim Number

**How It Works:**
- Import checks: Does Claim Number already exist?
  - **Yes:** Update existing claim row
  - **No:** Create new claim row

---

#### Clinicians

**SimplePractice UID:** Provider ID (numeric) OR NPI Number

**monday.com Column:** "Clinician ID" (e.g., CL-2001)

**Matching Strategy:** Map SimplePractice Provider ID to monday.com Clinician ID

**How It Works:**
- Clinician board has "SimplePractice Provider ID" column
- On import, match Provider ID from CSV to this column
- Connect to correct clinician record

---

#### Authorizations

**SimplePractice UID:** Authorization Number (if SimplePractice tracks it)

**monday.com Column:** "Authorization Number" (on Assignments board)

**Challenge:** SimplePractice may not have robust auth tracking

**Workaround:**
- Manual entry in monday.com based on authorization letters
- Create own UID: AUTH-PT1001-2026-01

---

## Import Frequency Options

### Option 1: Weekly Full Sync (Recommended for MVP)

**Schedule:**
- Every Monday, 9:00 AM
- Import Claims (last 7 days OR all active)
- Import Sessions (last 7 days)

**Pros:**
- Consistent, predictable schedule
- Data never more than 7 days stale
- Automations trigger reliably

**Cons:**
- Requires weekly discipline
- Small time commitment (20 min/week)

**Best for:** Practices with consistent billing workflows

---

### Option 2: Bi-Weekly Sync

**Schedule:**
- Every other Monday
- Import Claims (last 14 days)
- Import Sessions (last 14 days)

**Pros:**
- Half the time commitment (20 min every 2 weeks)
- Still reasonably current

**Cons:**
- Data can be 2 weeks old
- Delayed alerts (denial happened 10 days ago, just now seeing it)

**Best for:** Smaller practices, pilot phase

---

### Option 3: On-Demand Sync

**Schedule:**
- Import when needed (e.g., before month-end review)
- No regular schedule

**Pros:**
- Minimal effort
- Flexible

**Cons:**
- Automations don't work well (stale data)
- Easy to forget
- Loses most of the value of real-time alerts

**Best for:** Very small practices (<25 active patients) OR if only using monday.com for reporting, not workflow

---

### Option 4: Daily Sync (Future State - Requires Automation)

**Schedule:**
- Automated via Zapier or custom script
- Pulls data daily from SimplePractice API (if available) OR scheduled CSV export

**Pros:**
- Near real-time data
- Minimal manual effort after setup

**Cons:**
- Requires technical setup
- SimplePractice API may not support
- Higher cost (Zapier/middleware)

**Best for:** Large practices (>200 patients) after MVP validated

---

## What Gets Updated Automatically vs. Manually

### Fully Automatic (No Human Touch After Setup)

✅ **Formula columns:**
- Days Outstanding (claims)
- Sessions Remaining
- Days Until Auth Expires
- Days Since Last Session
- Availability % (clinicians)
- Utilization % (locations)

✅ **Automations:**
- Alert notifications
- Status changes based on triggers
- Item movement between groups
- Email sends

✅ **Connected board mirrors:**
- Patient insurance → displayed on Assignment
- Clinician license type → displayed on Claims
- Location capacity → displayed on Assignments

---

### Semi-Automatic (Updates via Import)

🔄 **From SimplePractice imports:**
- Sessions Used (bi-weekly import)
- Last Session Date (bi-weekly import)
- Claim Status (weekly import)
- Claim amounts (weekly import)
- Patient active status (monthly import)

**Human involvement:**
- Download CSV from SimplePractice
- Upload to monday.com
- Verify import success

**Time:** 10-20 min per import

---

### Manual Entry Required

📝 **One-time setup:**
- New patient intake (until entered in SimplePractice)
- New clinician onboarding
- New location setup
- Authorization details (if not in SimplePractice)
- Copay amounts (if not exported from SimplePractice)

📝 **Ongoing manual updates:**
- Resolution notes on claims
- Follow-up actions/dates
- Denial appeal status
- Location agreement renewals
- Credential expiration dates (if not exported)

---

## Troubleshooting

### Issue: Import creates duplicate patients

**Cause:** Patient ID doesn't match between SimplePractice and monday.com

**Solution:**
1. Check SimplePractice Client ID format
2. Verify monday.com "Patient ID" column has same format
3. Use "Update existing items" option, match on Patient ID
4. If duplicates already exist, manually merge:
   - Keep record with more complete data
   - Update Patient ID to SimplePractice ID
   - Delete duplicate

---

### Issue: Sessions Used not updating

**Cause:**
- Import not matching to correct assignment
- SimplePractice export missing data

**Solution:**
1. Verify assignment exists for that patient-clinician pair
2. Check SimplePractice export includes Patient ID and Clinician ID
3. Test with manual update first to verify formula works
4. Review import log for matching errors

---

### Issue: Claim not connecting to patient

**Cause:** Patient doesn't exist in Patients board yet

**Solution:**
1. Import patients first (before claims)
2. OR add patient manually to Patients board
3. Then re-import claims
4. Verify Patient ID matches between boards

---

### Issue: Import taking too long

**Cause:** Importing too many records at once (>500)

**Solution:**
1. Break into smaller batches (200-300 records)
2. Import incrementally (last 7 days instead of all time)
3. Use "Update existing" for weekly refreshes, not full re-import

---

### Issue: Automation not triggering after import

**Cause:** Automation looks for column CHANGE, but import doesn't count as change

**Solution:**
1. Review automation trigger: "When column changes to X"
2. For imports, use time-based triggers instead:
   - "Every Monday, if Status = Denied, notify..."
3. OR manually trigger automation test after import

---

## Future State: API Integration

### When SimplePractice API is Available

**Benefits:**
- Real-time sync (no CSV exports)
- Bi-directional updates (monday.com → SimplePractice)
- Automatic session count updates
- Instant claim status changes

**Requirements:**
- SimplePractice API access (may require enterprise plan)
- Middleware (Zapier, Integromat, or custom)
- Technical setup (developer involvement)
- Monthly middleware costs ($50-200/month)

**Timeline:** Phase 2 (after MVP validated, 6+ months)

**Estimated Cost:** $2,000-5,000 one-time setup + $100-200/month

**ROI:** Makes sense when manual import time exceeds 2-3 hours/week

---

## Summary: Your Questions Answered

### Q: "Is it possible to auto-populate sessions remaining when sessions occur?"

**A:** Yes, with bi-weekly imports from SimplePractice:
1. Export completed appointments from SimplePractice
2. Import to update "Sessions Used" column
3. "Sessions Remaining" auto-calculates via formula
4. Takes 10 minutes every 2 weeks

**Alternative:** Manual update (15-20 min/week) during pilot phase

---

### Q: "How does data get from SimplePractice to monday.com?"

**A:** CSV export/import process:
- Weekly for claims
- Bi-weekly for sessions
- Monthly for patient demographics
- Total time: 30-40 min/week

---

### Q: "What updates automatically vs. requiring manual work?"

**A:**
- **Automatic:** All formulas, automations, alerts, connected board data
- **Semi-automatic:** Data from SimplePractice (via scheduled imports)
- **Manual:** Initial setup, resolution notes, authorization details

---

## Next Steps

1. **Validate SimplePractice export capabilities:**
   - Can you export Claims Report as CSV?
   - Can you export Appointments Report as CSV?
   - What fields are available in each export?

2. **Test sample export:**
   - Export 10 sample claims
   - Email CSV to implementation team for review
   - Verify all needed fields are present

3. **Decide import frequency:**
   - Start bi-weekly (easier commitment)
   - Move to weekly after comfort builds

4. **Identify import owner:**
   - Who will do the weekly imports?
   - Backup person if primary unavailable?
   - Include in training plan

---

**Questions?** Contact your implementation team to walk through a live SimplePractice export together.
