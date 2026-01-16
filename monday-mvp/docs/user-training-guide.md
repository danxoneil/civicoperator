# User Training Guide
## Jenkins Creative Counseling Center - monday.com Operations System

**Version:** 1.0
**Last Updated:** January 16, 2026

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Intake Coordinator Guide](#intake-coordinator-guide)
3. [Billing Staff Guide](#billing-staff-guide)
4. [Clinical Supervisor Guide](#clinical-supervisor-guide)
5. [Clinician Guide](#clinician-guide)
6. [Administrator Guide](#administrator-guide)
7. [Mobile App Basics](#mobile-app-basics)
8. [Tips & Best Practices](#tips--best-practices)

---

## Getting Started

### Logging In

1. Go to **monday.com** or use the direct link provided by your admin
2. Enter your work email address
3. Enter your password
4. **Complete 2FA verification** (required for HIPAA compliance)
   - Enter code from authenticator app or SMS

### Your monday.com Workspace

When you log in, you'll see:
- **Left Sidebar:** Your boards and workspace
- **Main Area:** The active board you're viewing
- **Top Bar:** Search, notifications, your profile

### Understanding Boards

Think of boards like specialized spreadsheets:
- **Rows (Items):** Individual patients, clinicians, claims, etc.
- **Columns:** Different types of information (name, date, status, etc.)
- **Groups:** Organize items by stage (New Referrals, Active, etc.)

### Key Concepts

**Status Columns:**
- Color-coded labels showing current state
- Example: "New" (gray), "In Progress" (orange), "Complete" (green)

**Connected Boards:**
- Link items between boards
- Example: Link a claim to a patient

**Automations:**
- Rules that trigger actions automatically
- Example: Alert you when something is overdue

**Notifications:**
- Click the bell icon (🔔) to see your notifications
- You'll be notified when:
  - Someone assigns you a task
  - An automation triggers an alert
  - Someone mentions you (@name)

---

## Intake Coordinator Guide

### Your Primary Board: Patients & Intake

**Purpose:** Track patients from initial referral through readiness for SimplePractice entry.

### Daily Workflow

#### Morning Routine (15-30 min)

1. **Open Patients & Intake board**
2. **Check "My Intakes" view:**
   - Click **Views** dropdown → **My Intakes**
   - Shows only patients assigned to you
3. **Review stalled cases:**
   - Look for red flags in "Days in Stage" column
   - Follow up on any patient >7 days in same status
4. **Check notifications:**
   - Click bell icon for automated alerts
   - Address urgent patient needs first

#### Adding a New Referral

**Step-by-Step:**

1. Click **+ New item** button (top of any group)
2. **Which group?**
   - Choose "New Referrals" group
3. **Fill in required fields:**
   - **Patient Name:** Full name (Last, First)
   - **Patient ID:** Use next available number (PT-XXXX)
   - **Referral Date:** Date referral received
   - **Referral Source:** Choose from dropdown
   - **Primary Contact:** Parent/guardian name
   - **Contact Phone:** Format: 555-0XXX
   - **Contact Email:** Primary email
   - **Insurance Carrier:** Select from dropdown
   - **Intake Coordinator:** Assign to yourself
   - **Priority:** Normal (unless urgent)
4. Click anywhere outside the row to save

**Pro Tip:** Use Tab key to move quickly between fields.

#### Moving Through Intake Stages

**Stage 1: New → Contacted**

1. Call or email family
2. Document outreach in **Notes** column
3. Update **Current Status** to "Contacted"
4. Update **Next Action:** "Send intake packet"

**Stage 2: Contacted → Forms Sent**

1. Send Adobe Sign intake packet
2. Copy Adobe Sign URL to **Adobe Sign Link** column
3. Update **Forms Status** to "Sent"
4. Update **Current Status** to "Forms Sent"
5. **Automation will:** Set follow-up reminder

**Stage 3: Forms Sent → Forms Complete**

1. Check Adobe Sign for completion
2. When all forms signed:
   - Update **Forms Status** to "Complete"
3. **Automation will:** Automatically move to "Ready for Scheduling" group

**Stage 4: Verify Insurance**

1. Call insurance carrier or use online portal
2. Update **Insurance Status:**
   - "Verified" if active coverage confirmed
   - "Denied" if not covered (triggers alert)
3. Document findings in **Notes**

**Stage 5: Ready → SimplePractice Entry**

1. Once forms complete AND insurance verified:
   - Patient appears in "Ready for Scheduling" group
2. Enter all information into SimplePractice
3. Update **SimplePractice Entry Date** with today's date
4. **Automation will:** Move patient to "Archived" group

#### Handling Exceptions

**If Insurance Denied:**
- Priority automatically changes to "High"
- You'll receive notification
- Discuss self-pay or alternative insurance with family
- Document decision in Notes

**If Forms Incomplete After 7 Days:**
- You'll receive automated alert
- Follow up via phone call
- Document attempt in Notes
- If no response after 3 attempts, move to "Stalled/Exception"

**If Urgent Referral:**
- Set **Priority** to "Urgent" (triggers immediate alert to supervisor)
- Expedite all steps
- Communicate urgency to family

#### Using Views Effectively

**"My Intakes" View:**
- See only your assigned patients
- Default view for daily work

**"Stalled Cases" View:**
- Shows all patients >7 days without progress
- Review weekly to prevent cases from falling through cracks

**"By Location" View:**
- Grouped by assigned location
- Useful for coordinating school-based intakes

**"By Insurance Status" View:**
- See all patients grouped by insurance verification status
- Helpful for batch processing insurance calls

### Common Tasks

**Reassigning a Patient:**
1. Click **Intake Coordinator** column
2. Remove yourself, add another coordinator
3. They'll receive notification

**Adding Notes:**
1. Click **Notes** column (or open item view)
2. Type note with date stamp
3. Use format: "1/16/26 - Called family, left voicemail"

**Searching for a Patient:**
1. Click search icon (top bar)
2. Type patient name or ID
3. Click result to open

**Filtering the Board:**
1. Click **Filter** button
2. Choose criteria (e.g., Insurance Carrier = "Medicaid")
3. Click **Apply**
4. Clear filter when done

---

## Billing Staff Guide

### Your Primary Boards: Claims Tracking

**Purpose:** Track claims from submission through payment/resolution.

### Daily Workflow

#### Morning Routine (30-45 min)

1. **Open Claims Tracking board**
2. **Check "High Dollar Claims" view:**
   - Claims >$500 needing attention
3. **Review "At Risk" group:**
   - Claims 90+ days outstanding
   - Prioritize these for follow-up
4. **Check notifications:**
   - Automated alerts for denials
   - Authorization issues

#### Weekly SimplePractice Import

**Every Monday Morning:**

1. **Export from SimplePractice:**
   - Go to SimplePractice → Claims → Export
   - Date range: Last 7 days
   - Format: CSV
   - Include: Claim #, Patient, Clinician, Service Date, Submission Date, Payer, Amount, Status

2. **Import to monday.com:**
   - Open Claims board → Menu **⋯** → **Import data**
   - Upload CSV file
   - **Map columns carefully:**
     - Claim Number → Claim Number
     - Patient Name → Patient Name (will need to connect)
     - Service Date → Service Date
     - Etc.
   - Choose: **Update existing items** (based on Claim Number match)
   - Click Import

3. **Connect New Claims:**
   - For new claims, link to Patient and Clinician:
     - Click **Patient Name** column
     - Search by Patient ID
     - Select correct patient
   - Repeat for Clinician

#### Following Up on Aging Claims

**30-60 Day Claims:**

1. Filter board: Aging Category = "31-60"
2. For each claim:
   - Check **Last Follow-Up Date**
   - If >14 days, call payer
   - Document call in **Resolution Notes**
   - Update **Next Follow-Up Date**
   - Assign to yourself in **Follow-Up Owner**

**60-90 Day Claims:**

1. Filter: Aging Category = "61-90"
2. Escalate follow-up:
   - Call payer supervisor line
   - Request expedited review
   - Set **Priority** to "High"
   - Update **Next Follow-Up Date** (7 days max)

**90+ Day Claims (HIGH PRIORITY):**

1. These appear in "At Risk" group automatically
2. **Automation has:** Set Priority to "Urgent"
3. **Your action:**
   - Call payer immediately
   - Escalate to manager if needed
   - Document all communication
   - Consider appeal or write-off if appropriate

#### Handling Denials

**When Claim Status = "Denied":**

1. **Automation will:**
   - Change Priority to "High"
   - Notify you
2. **Your action:**
   - Review **Denial Reason**
   - Determine if correctable:
     - **Authorization:** Check if auth exists, appeal if needed
     - **Eligibility:** Verify insurance was active on DOS
     - **Coding:** Coordinate with clinician for corrected code
     - **Timely Filing:** Appeal with documentation
   - Update **Resolution Notes** with action plan
   - If appealing:
     - Update **Appeal Filed Date**
     - Set **Next Follow-Up Date** for appeal status check

#### Posting Payments

**When Payment Received:**

1. Find claim in board (search by Claim Number)
2. Update **Paid Amount** with amount received
3. Update **Claim Status** to "Paid"
4. **Automation will:** Move to "Resolved" group
5. Post payment in SimplePractice (system of record)

#### Using Views

**"All Active Claims":**
- Everything not yet paid/closed
- Default view for daily work

**"Aging Report":**
- Grouped by 0-30, 31-60, 61-90, 90+ days
- Use for weekly aging review

**"My Claims":**
- Filtered to Follow-Up Owner = You
- Your personal work queue

**"By Payer":**
- Grouped by insurance carrier
- Useful for payer-specific batch calls

**"Denials & Appeals":**
- Only denied claims
- Track appeal status

### Common Tasks

**Calculating Total AR:**
1. Click on **Claim Amount** column header
2. View sum at bottom of board
3. Filter by aging category for bucket totals

**Batch Status Updates:**
1. Select multiple claims (checkboxes on left)
2. Right-click → **Batch actions**
3. Choose action (e.g., update Follow-Up Owner)

**Creating a Payer Communication Log:**
1. Click claim to open item view
2. Go to **Updates** section (bottom)
3. Post update: "Called BCBS - confirmed in review queue"
4. Use **Resolution Notes** column for summary

---

## Clinical Supervisor Guide

### Your Primary Boards: Clinicians & Assignments

**Purpose:** Monitor clinician capacity, credentials, and supervisee caseloads.

### Weekly Workflow

#### Monday Morning Review (30 min)

1. **Open Clinicians board**
2. **Check "Credential Alerts" view:**
   - Any licenses expiring <60 days?
   - Background checks expiring?
3. **Review "Capacity Overview" view:**
   - Who's near max capacity (>90%)?
   - Who has availability for new patients?
4. **Check "Supervision Structure" view:**
   - Review supervisee caseloads
   - Ensure supervision hours scheduled

#### Managing Supervisees

**Linking Yourself as Supervisor:**

1. For each supervisee on Clinicians board:
   - Click their **Supervisor** column
   - Search for your name
   - Select yourself

**Monitoring Supervisee Assignments:**

1. Open **Patient-Clinician Assignments** board
2. Filter: **Supervisor** = [Your Name]
3. Review all supervised assignments:
   - Check for risk flags (auth expiring, service gaps)
   - Verify session frequency appropriate
   - Monitor sessions remaining

**Reviewing Sessions:**

1. Check **Sessions Used** vs **Authorized Sessions**
2. If Sessions Remaining ≤ 2:
   - **Automation alerts:** Supervisee and you
   - Ensure new authorization requested

#### Capacity Planning

**Assigning New Patients:**

1. Open Clinicians board → "Capacity Overview" view
2. Sort by **Availability %** (high to low)
3. Consider:
   - Specialty match
   - Location match
   - Insurance panel compatibility
4. Once decided, inform intake coordinator

**Balancing Caseloads:**

1. If clinician >90% capacity:
   - **Automation alerts:** You automatically
   - Review for transfer opportunities
   - Consider temporary hold on new assignments

---

## Clinician Guide

### Your Primary Access: "My Assignments" View

**Purpose:** View your current patient assignments and track authorization status.

### What You Can See

You have **view-only** access to:
- **Your assignments** (filtered view)
- **Your patients** (connected from assignments)

You do NOT have access to:
- Full patient intake board
- Claims/billing information
- Other clinicians' caseloads (unless supervisor)

### Daily Check-In (5 min)

1. Open **Patient-Clinician Assignments** board
2. Select **"My Assignments"** view
   - Automatically filtered to show only your patients
3. **Check for alerts:**
   - **Risk Flag** column shows:
     - "Auth Expiring" = Authorization ending soon
     - "Gaps in Service" = Patient hasn't had session in >21 days
4. Review **Sessions Remaining** for each patient

### Understanding Your Assignment View

**Columns You'll See:**

- **Patient:** Your patient's name (connected to Patients board)
- **Location:** Where you see this patient
- **Session Frequency:** Weekly, Biweekly, or Monthly
- **Authorized Sessions:** Total approved by insurance
- **Sessions Used:** How many completed
- **Sessions Remaining:** Auto-calculated
- **Authorization End Date:** When auth expires
- **Days Until Auth Expires:** Auto-calculated countdown
- **Last Session Date:** Most recent appointment
- **Risk Flag:** Alerts you to issues

### Responding to Alerts

**"Auth Expiring" Alert:**

1. **Automation notifies:** You when ≤14 days until expiration
2. **Your action:**
   - Contact billing/admin to request authorization extension
   - Provide clinical justification for continued services
   - Do NOT continue sessions without valid auth

**"Gaps in Service" Alert:**

1. **Automation notifies:** You when >21 days since last session
2. **Your action:**
   - Reach out to patient/family
   - Reschedule if appropriate
   - Document outreach attempt
   - Inform supervisor if patient disengaging

**Sessions Running Low (≤2 remaining):**

1. **Automation notifies:** You and billing staff
2. **Your action:**
   - Coordinate with billing for auth extension
   - Do not schedule beyond authorized sessions

### Mobile App Access

**Download monday.com mobile app:**
- iOS: App Store
- Android: Google Play

**Using Mobile View:**

1. Log in with work email
2. Navigate to Assignments board
3. View "My Assignments"
4. Check for alerts on-the-go
5. Update Last Session Date after appointments (if you have edit access)

---

## Administrator Guide

### Your Responsibilities

As board admin, you:
- Manage board architecture
- Configure automations
- Set permissions
- Import/export data
- Train users
- Troubleshoot issues

### Daily Monitoring (15 min)

**Check Automation Activity:**
1. Click **Automate** button on any board
2. View **Activity log**
3. Verify automations triggering correctly
4. Address any errors

**Review Notifications:**
1. You receive escalations (urgent patients, high-dollar claims)
2. Triage and delegate as appropriate

### Weekly Maintenance

**Monday Morning:**
1. Import SimplePractice claims export (see Billing Guide)
2. Validate data import success
3. Check for any broken connected board links

**Friday Afternoon:**
1. Export backup CSVs from all boards
2. Store in secure, encrypted location
3. Review weekly activity metrics

### Monthly Tasks

**First Monday of Month:**
1. **Audit credential expirations:**
   - Run "Credential Alerts" report
   - Send summary to ownership
2. **Review capacity utilization:**
   - Check clinician Availability % trends
   - Identify hiring needs
3. **Run AR aging report:**
   - Export Claims by aging category
   - Provide to leadership
4. **User access review:**
   - Verify all users have appropriate permissions
   - Remove access for termed employees

### Managing Automations

**Editing an Automation:**
1. Open board → **Automate**
2. Find automation in list
3. Click **⋯** → **Edit**
4. Modify trigger or action
5. Test before saving

**Disabling an Automation:**
1. Automate → Find automation
2. Toggle switch to **Off**
3. Document reason (temporarily disabled vs. deprecated)

**Creating New Automation:**
1. Review `/automations/automations-spec.md` for approved automations
2. Click **Create automation**
3. Build recipe using template
4. Test thoroughly before activating
5. Document in system manual

### Managing Permissions

**Adding a New User:**
1. Workspace settings → **Invite members**
2. Enter email, assign role
3. Grant board access based on job role:
   - Intake Coordinator → Patients & Intake (full), Clinicians (view), Locations (view)
   - Billing Staff → Claims (full), Patients (view), Clinicians (view)
   - Clinician → Assignments (view - filtered)
   - Leadership → All boards (view only)

**Removing User Access:**
1. Workspace settings → **Members**
2. Find user → **⋯** → **Remove from workspace**
3. Verify removal from all boards

### Data Import/Export

**CSV Export (Backup):**
1. Open board → **⋯** → **Export**
2. Format: CSV
3. Include all columns
4. Save with date stamp: `Patients_2026-01-16.csv`

**CSV Import (Update):**
1. Prepare CSV with matching column names
2. Board → **⋯** → **Import data**
3. Map columns carefully
4. Choose update strategy:
   - Update existing items (match on Patient ID, Claim Number, etc.)
   - Create new items only
5. Review import log for errors

### Troubleshooting

**Formula Not Calculating:**
- Edit column → **Refresh formula**
- Verify referenced columns have data
- Check formula syntax

**Automation Not Triggering:**
- Check Activity log for errors
- Verify conditions are met
- Confirm notification recipients are valid users

**Connected Board Broken:**
- Re-save the connected column
- Verify both boards accessible to users
- Check if source item was deleted

**User Can't Access Board:**
- Verify workspace membership
- Check board-specific permissions
- Ensure user email confirmed

---

## Mobile App Basics

### Getting Started

1. **Download App:**
   - iOS: Search "monday.com" in App Store
   - Android: Search "monday.com" in Google Play

2. **Log In:**
   - Enter work email
   - Enter password
   - Complete 2FA verification

3. **Navigate:**
   - Tap workspace name to see boards
   - Tap board to open
   - Swipe to scroll, tap to open items

### Mobile Features

**Viewing Boards:**
- Tap board name to open
- Swipe left/right to see columns
- Tap item to see full details

**Notifications:**
- Push notifications for automations
- Tap notification to go directly to item

**Updating Items:**
- Tap item to open
- Tap column to edit
- Changes sync immediately

**Offline Access:**
- Recently viewed boards cached
- Changes sync when back online

### Mobile Best Practices

- Use for viewing and quick updates only
- Do NOT use for bulk data entry
- Enable push notifications for alerts
- Keep app updated

---

## Tips & Best Practices

### General Tips

**Use Search Effectively:**
- Search by Patient ID for fastest results
- Use quotes for exact phrases: "Emma Martinez"
- Search works across all boards you can access

**Leverage Views:**
- Create custom views for your workflow
- Save filters as views for reuse
- Share views with team members

**Stay Organized:**
- Update items immediately (don't batch at end of day)
- Use consistent naming conventions
- Document actions in Notes column
- Clear completed items from active groups

**Communicate:**
- Use @mentions to notify specific people
- Use Updates section for item-specific communication
- Don't use monday.com for PHI-heavy clinical discussions

**Mobile vs Desktop:**
- Desktop: Data entry, bulk updates, exports
- Mobile: Quick checks, notifications, status updates

### Keyboard Shortcuts

- **Enter:** Open item
- **Tab:** Move to next column
- **Escape:** Close item view
- **Cmd/Ctrl + K:** Quick search
- **Cmd/Ctrl + F:** Filter board

### Data Hygiene

**Do:**
- Enter data consistently (e.g., phone format: 555-0123)
- Use dropdowns instead of free text when available
- Update status columns in real-time
- Document actions in Notes

**Don't:**
- Leave items in wrong groups
- Ignore automation alerts
- Duplicate items (search first!)
- Store detailed clinical notes (use SimplePractice)

### Getting Help

**In-App Help:**
- Click **?** icon → **Help Center**
- Search for specific topics

**Ask Your Admin:**
- Board-specific questions
- Permission issues
- Technical problems

**monday.com Support:**
- Complex technical issues
- Automation errors
- Account/billing questions

---

## Training Exercises

### Exercise 1: Intake Coordinator

**Scenario:** New referral received

1. Add new patient: "John Doe" (PT-1030)
2. Referral Date: Today
3. Referral Source: School
4. Insurance: Blue Cross Blue Shield
5. Assign to yourself
6. Send intake forms
7. Update status to "Forms Sent"

**Check:** Did automation set follow-up reminder?

---

### Exercise 2: Billing Staff

**Scenario:** Claim denied

1. Find claim CLM-8941 (practice claim)
2. Change Status to "Denied"
3. Denial Reason: "Authorization"
4. Document in Resolution Notes: "Missing prior auth - will appeal"
5. Set Next Follow-Up Date: 7 days out

**Check:** Did Priority change to "High"? Did you get notified?

---

### Exercise 3: Clinician

**Scenario:** Check your caseload

1. Open Assignments board
2. Go to "My Assignments" view
3. Find any "Auth Expiring" alerts
4. Note Sessions Remaining for each patient
5. Identify any service gaps

**Check:** Do you know which patients need auth renewals?

---

## Quick Reference Cards

### Intake Coordinator - Quick Card

**Daily Checklist:**
- [ ] Check "My Intakes" view
- [ ] Follow up on Forms Sent (>3 days)
- [ ] Verify insurance for Ready patients
- [ ] Address any Stalled cases
- [ ] Enter Ready patients to SimplePractice

**Status Flow:**
New → Contacted → Forms Sent → Forms Complete → Ready → Archived

**Key Automations:**
- Forms Complete = Auto-move to Ready
- >7 days in stage = Alert you
- Insurance Denied = Priority High

---

### Billing Staff - Quick Card

**Daily Checklist:**
- [ ] Review 90+ day claims (At Risk group)
- [ ] Follow up on denials
- [ ] Check claim aging buckets
- [ ] Post any payments received
- [ ] Update next follow-up dates

**Weekly Task:**
- Monday AM: Import SimplePractice claims export

**Key Automations:**
- Claim Denied = Priority High + Alert
- 90+ days + >$500 = Urgent alert
- Paid status = Auto-move to Resolved

---

### Clinician - Quick Card

**Daily Checklist:**
- [ ] Check "My Assignments" view
- [ ] Review any Risk Flags
- [ ] Note Sessions Remaining for each patient
- [ ] Respond to authorization alerts

**Alerts to Watch:**
- **Auth Expiring:** ≤14 days - contact billing
- **Gaps in Service:** >21 days - outreach to patient
- **Sessions Low:** ≤2 remaining - request new auth

---

**End of User Training Guide**

*For technical implementation details, see Implementation Guide.*
*For system architecture, see Technical Specifications.*
