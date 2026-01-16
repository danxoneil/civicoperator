# Implementation Guide
## Jenkins Creative Counseling Center - monday.com MVP

**Estimated Time:** 4-6 hours (technical setup)
**Prerequisite:** monday.com Enterprise account with HIPAA BAA
**Role Required:** Board creator/administrator access

---

## Table of Contents
1. [Pre-Implementation Checklist](#pre-implementation-checklist)
2. [Phase 1: Workspace Setup](#phase-1-workspace-setup)
3. [Phase 2: Board Creation](#phase-2-board-creation)
4. [Phase 3: Data Import](#phase-3-data-import)
5. [Phase 4: Automation Configuration](#phase-4-automation-configuration)
6. [Phase 5: Connected Boards Setup](#phase-5-connected-boards-setup)
7. [Phase 6: Permissions & Security](#phase-6-permissions--security)
8. [Phase 7: Testing & Validation](#phase-7-testing--validation)
9. [Phase 8: User Training & Go-Live](#phase-8-user-training--go-live)
10. [Troubleshooting](#troubleshooting)

---

## Pre-Implementation Checklist

### Account Setup
- [ ] monday.com Enterprise subscription activated
- [ ] HIPAA Business Associate Agreement (BAA) signed
- [ ] Two-factor authentication enabled for all users
- [ ] User accounts created for all staff members
- [ ] Billing information configured

### Team Preparation
- [ ] Implementation team identified (minimum 2 people)
- [ ] Board owner/administrator assigned
- [ ] User roles mapped to monday.com access levels
- [ ] Training schedule drafted
- [ ] Communication plan for go-live prepared

### Technical Preparation
- [ ] CSV files downloaded from `/csvs/` directory
- [ ] Board specifications reviewed from `/boards/` directory
- [ ] Automation specifications reviewed
- [ ] SimplePractice export format reviewed (for future data imports)

### Timeline
- [ ] Implementation start date set
- [ ] User training dates scheduled (2-4 hours per group)
- [ ] Go-live date identified
- [ ] Backup/rollback plan documented

---

## Phase 1: Workspace Setup
**Time Required:** 15 minutes

### Step 1.1: Create Workspace
1. Log into monday.com as account administrator
2. Click **"Add workspace"** in left sidebar
3. Name: `Jenkins Operations`
4. Description: `Operational system for patient intake, clinician management, claims tracking, and assignments`
5. Set workspace privacy: **Private** (recommended for PHI protection)
6. Click **Create**

### Step 1.2: Configure Workspace Settings
1. Click workspace name → **Settings**
2. **Security Settings:**
   - Enable: "Require 2FA for all members"
   - Enable: "Session timeout" (set to 30 minutes)
   - Enable: "Activity log" (audit trail)
3. **Default Settings:**
   - Time zone: [Your practice's time zone]
   - First day of week: Monday
   - Date format: MM/DD/YYYY (or preference)

### Step 1.3: Add Workspace Members
1. Click **Invite members**
2. Add users by email with appropriate roles:
   - **Admin** - Board owner, IT staff
   - **Member** - Intake coordinators, billing staff
   - **Viewer** - Clinicians, leadership (for dashboards)
3. Don't assign board access yet (will do in Phase 6)

---

## Phase 2: Board Creation
**Time Required:** 2 hours

For each board, follow this process using specifications from `/boards/` directory.

### Step 2.1: Create Board 1 - Patients & Intake

1. **Create Board:**
   - In workspace, click **Add** → **New board**
   - Name: `Patients & Intake`
   - Choose template: **Blank board**
   - Click **Create**

2. **Set Up Groups:**
   Create groups (click **New Group**):
   - New Referrals
   - Intake In Progress
   - Ready for Scheduling
   - Stalled/Exception
   - Archived

3. **Configure Columns:**
   Reference: `/boards/01-patients-intake-board.md`

   Add columns (click **+** next to last column):

   | Column Name | Column Type | Settings |
   |-------------|-------------|----------|
   | Patient Name | Text | Default column (rename "Item") |
   | Patient ID | Text | - |
   | Referral Date | Date | - |
   | Referral Source | Dropdown | Options: School, Self, Insurance, Provider, County |
   | Primary Contact | Text | - |
   | Contact Phone | Phone | - |
   | Contact Email | Email | - |
   | Insurance Carrier | Dropdown | Options: Aetna, Blue Cross Blue Shield, UnitedHealthcare, Cigna, Medicaid, Self-Pay |
   | Insurance Status | Status | Labels: Not Verified, Verified, Denied, Self-Pay |
   | Forms Status | Status | Labels: Not Sent, Sent, Partially Complete, Complete |
   | Adobe Sign Link | Link | - |
   | Intake Coordinator | Person | - |
   | Current Status | Status | Labels: New, Contacted, Forms Sent, Forms Complete, Verified, Ready, Complete |
   | Location Assigned | Connect Board | (Configure in Phase 5) |
   | Days in Stage | Numbers | Will use formula (see below) |
   | Priority | Status | Labels: Normal, High, Urgent |
   | Next Action | Text | - |
   | Notes | Long Text | - |
   | SimplePractice Entry Date | Date | - |

4. **Configure Formula Column:**
   - Column: "Days in Stage"
   - Formula: `DAYS({Last Updated}, TODAY())`
   - This calculates days since last status change

5. **Set Column Permissions:**
   - Right-click "Patient Name" → **Column permissions**
   - Set to: "Admins and specific people only"
   - Add: Intake coordinators, billing staff

6. **Save Board**

---

### Step 2.2: Create Board 2 - Clinicians

Follow same process as Board 1, using specifications from `/boards/02-clinicians-board.md`

**Groups:**
- Active Clinicians
- Onboarding
- Inactive/On Leave
- Offboarded

**Key Columns to Note:**
- **Days Until Expiration:** Formula = `DAYS(TODAY(), {License Expiration})`
- **Availability %:** Formula = `({Max Weekly Sessions} - {Current Patient Count}) / {Max Weekly Sessions} * 100`
- **Supervisor:** Connect Board to same board (self-reference) - configure in Phase 5
- **Insurance Panels:** Dropdown (multi-select) with all payer options

**Column Permissions:**
- Restrict "NPI Number" and "License Number" to admins only

---

### Step 2.3: Create Board 3 - Claims Tracking

Reference: `/boards/03-claims-tracking-board.md`

**Groups:**
- Newly Submitted (< 30 days)
- Pending/In Process (30-60 days)
- Aging (60-90 days)
- At Risk (90+ days)
- Denied
- Resolved

**Key Columns to Note:**
- **Days Outstanding:** Formula = `DAYS({Submission Date}, TODAY())`
- **Patient Name:** Connect Board (to Patients board) - configure in Phase 5
- **Clinician:** Connect Board (to Clinicians board) - configure in Phase 5
- **Denial Reason:** Dropdown - Options: Authorization, Eligibility, Coding, Timely Filing, Other
- **Aging Category:** Status - Labels: 0-30, 31-60, 61-90, 90+

**Important:** This board will receive weekly imports from SimplePractice

---

### Step 2.4: Create Board 4 - Locations

Reference: `/boards/04-locations-board.md`

**Groups:**
- Primary Offices
- Schools
- Partner Sites
- Inactive Locations

**Key Columns to Note:**
- **Days Until Renewal:** Formula = `DAYS(TODAY(), {Agreement Expiration})`
- **Utilization %:** Formula = `({Current Census} / {Max Capacity}) * 100`
- **Services Offered:** Dropdown (multi-select) - Options: Individual, Group, Family, Equine
- **Insurance Accepted:** Dropdown (multi-select) - All payer options

---

### Step 2.5: Create Board 5 - Patient-Clinician Assignments

Reference: `/boards/05-patient-clinician-assignments-board.md`

**Groups:**
- Active Assignments
- Pending Start
- On Hold
- Closed

**Key Columns to Note:**
- **Patient:** Connect Board (to Patients) - configure in Phase 5
- **Clinician:** Connect Board (to Clinicians) - configure in Phase 5
- **Location:** Connect Board (to Locations) - configure in Phase 5
- **Sessions Remaining:** Formula = `{Authorized Sessions} - {Sessions Used}`
- **Days Until Auth Expires:** Formula = `DAYS(TODAY(), {Authorization End Date})`
- **Days Since Last Session:** Formula = `DAYS({Last Session Date}, TODAY())`
- **Supervisor:** Connect Board (to Clinicians) - configure in Phase 5

---

## Phase 3: Data Import
**Time Required:** 30 minutes

### Step 3.1: Import Order
Import in this order to maintain connected board relationships:

1. **Locations** (no dependencies)
2. **Clinicians** (no dependencies except self-reference)
3. **Patients & Intake** (no dependencies yet)
4. **Patient-Clinician Assignments** (depends on all above)
5. **Claims Tracking** (depends on Patients and Clinicians)

### Step 3.2: Import Process (for each board)

**Example: Importing Locations**

1. Open `Locations` board
2. Click **⋯** (board menu) → **Import data**
3. Choose **Import from file** → **Upload file**
4. Select `/csvs/04-locations.csv`
5. **Map Columns:**
   - monday.com will auto-detect column names
   - Verify each CSV column maps to correct board column
   - **Important:** Map "Location Name" to the "Item" column (first column)
6. **Import Settings:**
   - Create new items: **Yes**
   - Update existing items: **No** (first import)
7. Click **Import**
8. Verify 8 locations imported successfully

**Repeat for:**
- `02-clinicians.csv` → Clinicians board (12 records)
- `01-patients-intake.csv` → Patients & Intake board (25 records)
- `05-patient-clinician-assignments.csv` → Assignments board (28 records)
- `03-claims-tracking.csv` → Claims Tracking board (40 records)

### Step 3.3: Verify Import Success

For each board:
- [ ] Correct number of items imported
- [ ] All columns populated correctly
- [ ] Status labels displaying properly
- [ ] Date fields formatted correctly
- [ ] Formula columns calculating (Days in Stage, etc.)

---

## Phase 4: Automation Configuration
**Time Required:** 1.5 hours

Reference: `/automations/automations-spec.md`

### Step 4.1: Enable Automations

1. Open board → Click **Automate** button (top right)
2. Click **Create automation** → **Create custom automation**

### Step 4.2: Configure Priority Automations (Phase 1)

**Automation 1: Intake SLA Alert (Patients & Intake)**

1. In Patients & Intake board, click **Automate**
2. Choose **Custom automation**
3. Build recipe:
   ```
   When column "Days in Stage" changes to something
   and only if "Days in Stage" is greater than 7
   notify person in "Intake Coordinator"
   with message "Patient has been in same stage for {Days in Stage} days - action needed"
   ```
4. Click **Create automation**
5. Test: Manually change a patient's Days in Stage to 8 → verify notification

**Automation 6: License Expiration Alert (Clinicians)**

1. In Clinicians board, click **Automate**
2. Recipe:
   ```
   When column "Days Until Expiration" changes to something
   and only if "Days Until Expiration" is lower than or equal to 60
   notify person in column [Clinician Name]
   and notify board owner
   with message "License expiring in {Days Until Expiration} days - begin renewal process"
   ```
3. Test: Create test clinician with license expiring in 50 days

**Automation 11: Denial Alert (Claims)**

1. In Claims board, click **Automate**
2. Recipe:
   ```
   When column "Claim Status" changes to "Denied"
   change status of "Priority" to "High"
   and notify person in "Follow-Up Owner"
   with message "Claim denied - review for appeal: {Denial Reason}"
   ```
3. Test: Change a test claim to Denied status

**Automation 16: Authorization Expiration Alert (Assignments)**

1. In Assignments board, click **Automate**
2. Recipe:
   ```
   When column "Days Until Auth Expires" changes to something
   and only if "Days Until Auth Expires" is lower than or equal to 14
   change status of "Risk Flag" to "Auth Expiring"
   and notify person in "Clinician"
   with message "Authorization expiring soon - submit extension for {Patient}"
   ```

### Step 4.3: Configure Additional Automations

Implement remaining 14 automations from `/automations/automations-spec.md` following same pattern:
- Automations 2, 3, 4, 5 (Patients & Intake)
- Automations 7, 8, 9 (Clinicians)
- Automations 10, 12, 13 (Claims)
- Automations 14, 15 (Locations)
- Automations 17, 18 (Assignments)

**Implementation Priority:**
- **Week 1:** Automations 1, 6, 11, 16 (critical alerts)
- **Week 2:** Automations 2, 3, 10, 14 (workflow automation)
- **Week 3:** Remaining automations (optimization)

---

## Phase 5: Connected Boards Setup
**Time Required:** 1 hour

### Step 5.1: Understanding Connected Boards

Connected boards link items between boards, enabling:
- **Relationships:** Link patients to clinicians, claims to patients, etc.
- **Mirror columns:** Display data from connected board
- **Bidirectional updates:** Changes reflect across boards

### Step 5.2: Configure Connections

**Connection 1: Assignments → Patients**

1. Open **Patient-Clinician Assignments** board
2. Find the **Patient** column (currently empty Connect Board column)
3. Click column header → **Edit column**
4. **Choose board to connect:** Select "Patients & Intake"
5. **Mirror columns** (click + Add columns to mirror):
   - Insurance Carrier (from Patients board)
   - Current Status (from Patients board)
   - Location Assigned (from Patients board)
6. Click **Save**
7. **Populate connections:**
   - For each assignment row, click the Patient column
   - Search for patient by Patient ID (e.g., PT-1001)
   - Select correct patient
   - Repeat for all 28 assignments (use CSV reference for correct mappings)

**Connection 2: Assignments → Clinicians**

1. In Assignments board, find **Clinician** column
2. Edit column → Connect to "Clinicians" board
3. **Mirror columns:**
   - License Type
   - Primary Location
   - Supervisor (if applicable)
4. **Populate connections:**
   - Map each assignment to correct clinician using Clinician ID from CSV

**Connection 3: Assignments → Locations**

1. In Assignments board, find **Location** column
2. Edit column → Connect to "Locations" board
3. **Mirror columns:**
   - Location Type
   - Agreement Status
   - Max Capacity
4. **Populate connections:**
   - Map assignments to locations using CSV reference

**Connection 4: Claims → Patients**

1. In Claims board, find **Patient Name** column
2. Edit column → Connect to "Patients & Intake" board
3. **Mirror columns:**
   - Insurance Carrier
   - Referral Source
4. **Populate connections:**
   - Use Patient ID from CSV to map claims to patients

**Connection 5: Claims → Clinicians**

1. In Claims board, find **Clinician** column
2. Edit column → Connect to "Clinicians" board
3. **Mirror columns:**
   - License Type
   - NPI Number
4. **Populate connections:**
   - Map claims to clinicians per CSV

**Connection 6: Clinicians → Clinicians (Supervision)**

1. In Clinicians board, find **Supervisor** column
2. Edit column → Connect to "Clinicians" board (same board)
3. No mirror columns needed
4. **Populate connections:**
   - Link supervised clinicians to their supervisors:
     - CL-2005 (David Martinez) → CL-2001 (Dr. Sarah Mitchell)
     - CL-2009 (Robert Garcia) → CL-2002 (Jennifer Rodriguez)
     - CL-2012 (Rachel Moore) → CL-2004 (Emily Thompson)

### Step 5.3: Verify Connections

For each connected board:
- [ ] Items link correctly
- [ ] Mirror columns display data
- [ ] Changes in source board reflect in mirror columns
- [ ] No broken connections or errors

---

## Phase 6: Permissions & Security
**Time Required:** 30 minutes

### Step 6.1: Board-Level Permissions

For each board, configure privacy:

**Patients & Intake Board:**
1. Board menu **⋯** → **Board permissions**
2. Privacy: **Private** (only specific people)
3. Add members:
   - Admins: Full access
   - Intake coordinators: Full access
   - Billing staff: View only
4. Enable: "Allow guests to view this board" → **NO**

**Clinicians Board:**
1. Privacy: **Private**
2. Add members:
   - Admins: Full access
   - Billing staff: View only
   - Intake coordinators: View only
   - Clinical supervisors: View only

**Claims Tracking Board:**
1. Privacy: **Private**
2. Add members:
   - Admins: Full access
   - Billing staff: Full access
   - Leadership: View only

**Locations Board:**
1. Privacy: **Private**
2. Add members:
   - Admins: Full access
   - All staff: View only

**Assignments Board:**
1. Privacy: **Private**
2. Add members:
   - Admins: Full access
   - Clinical supervisors: Full access
   - Billing staff: View only
3. **Create filtered view for clinicians:**
   - Create view: "My Assignments"
   - Filter: "Clinician" = [Current User]
   - Share view with all clinicians (view only)

### Step 6.2: Column-Level Permissions

Restrict sensitive columns:

**Patients & Intake:**
- **Patient Name:** Admins + Intake coordinators only
- **Contact Phone/Email:** Admins + Intake coordinators only

**Clinicians:**
- **NPI Number:** Admins only
- **License Number:** Admins only
- **Background Check Date:** Admins only

**Claims:**
- **Patient Name column:** Admins + Billing staff only

### Step 6.3: Automation Permissions

1. Go to **Automations Center** (account level)
2. Review all automations
3. Ensure notifications only go to authorized users
4. Disable email notifications for non-work emails (if any)

---

## Phase 7: Testing & Validation
**Time Required:** 1 hour

### Step 7.1: Data Validation Testing

Create test checklist:

**Patients & Intake:**
- [ ] Search for patient "Emma Martinez" (PT-1001)
- [ ] Verify all columns populated correctly
- [ ] Check connected Location shows "Lincoln Elementary"
- [ ] Confirm Days in Stage calculates correctly
- [ ] Test changing Current Status → verify automation triggers

**Clinicians:**
- [ ] Find Dr. Sarah Mitchell (CL-2001)
- [ ] Verify License Expiration calculates Days Until Expiration
- [ ] Check Availability % formula works
- [ ] Confirm NPI number is restricted to admins only

**Claims:**
- [ ] Find claim CLM-8903 (denied claim)
- [ ] Verify connected Patient name displays
- [ ] Check Days Outstanding calculation
- [ ] Confirm claim appears in correct aging group
- [ ] Test denial automation by changing claim status

**Locations:**
- [ ] Open Main Office (LOC-3001)
- [ ] Verify Utilization % calculates correctly
- [ ] Check Services Offered displays all selections

**Assignments:**
- [ ] Find assignment ASSGN-4001
- [ ] Verify patient, clinician, and location all connect
- [ ] Check Sessions Remaining calculates correctly
- [ ] Confirm Days Until Auth Expires formula works

### Step 7.2: Automation Testing

**Test Each Critical Automation:**

1. **Intake SLA Alert:**
   - Create test patient
   - Manually set Last Updated date to 10 days ago
   - Verify notification sent to Intake Coordinator

2. **License Expiration:**
   - Create test clinician with license expiring in 55 days
   - Verify notification sent

3. **Claim Denial:**
   - Change test claim status to "Denied"
   - Verify priority changes to "High"
   - Verify notification sent to Follow-Up Owner

4. **Authorization Expiring:**
   - Create test assignment with auth expiring in 10 days
   - Verify Risk Flag changes
   - Verify clinician notified

**Document any issues in testing log**

### Step 7.3: Connected Board Testing

- [ ] Change patient location → verify reflects in Assignments
- [ ] Update clinician max sessions → verify Availability % recalculates
- [ ] Add patient to assignment → verify mirrors populate
- [ ] Modify location capacity → verify Utilization % updates

### Step 7.4: Permissions Testing

Have each user role log in and verify:
- [ ] Intake coordinator can edit Patients board
- [ ] Clinician can ONLY see "My Assignments" view
- [ ] Billing staff can edit Claims board
- [ ] Leadership has view-only access
- [ ] Sensitive columns properly restricted

---

## Phase 8: User Training & Go-Live
**Time Required:** 2-4 hours (per user group)

### Step 8.1: Training Materials Preparation

Before training sessions:
- [ ] Create board quick reference guides (one-pagers)
- [ ] Record screen-sharing videos of common tasks
- [ ] Prepare sample scenarios for hands-on practice
- [ ] Set up sandbox board for training (duplicate Patients board)

### Step 8.2: Role-Based Training Schedule

**Session 1: Administrators (1 hour)**
- Board architecture overview
- Automation management
- Permission settings
- Data import/export procedures
- Troubleshooting common issues

**Session 2: Intake Coordinators (2 hours)**
- Patients & Intake board walkthrough
- Adding new referrals
- Updating intake status
- Managing stalled cases
- Using Adobe Sign integration
- Moving patients to "Ready"
- Hands-on practice

**Session 3: Billing Staff (2 hours)**
- Claims Tracking board overview
- Importing SimplePractice claims export
- Following up on aging claims
- Managing denials and appeals
- Documenting payer communications
- Using filters and views
- Hands-on practice

**Session 4: Clinical Supervisors (1 hour)**
- Clinicians board overview
- Assignments board overview
- Monitoring supervisee caseloads
- Reviewing credential expirations
- Capacity planning
- "My Assignments" view for clinicians

**Session 5: All Clinicians (30 minutes)**
- View-only access overview
- "My Assignments" filtered view
- Understanding authorization alerts
- Mobile app basics (if applicable)

### Step 8.3: Go-Live Checklist

**1 Week Before Go-Live:**
- [ ] All boards built and tested
- [ ] All automations active and tested
- [ ] All user training completed
- [ ] Backup of current Google Sheets created
- [ ] Communication sent to all staff

**Day Before Go-Live:**
- [ ] Final data validation
- [ ] Test all user logins
- [ ] Verify notifications working
- [ ] Admin team on standby for support

**Go-Live Day:**
- [ ] Morning: Import fresh patient/claims data from SimplePractice
- [ ] 9 AM: System live - announce to staff
- [ ] Admin available for support questions all day
- [ ] Monitor automation activity
- [ ] Document any issues

**First Week Post Go-Live:**
- [ ] Daily check-ins with each user group
- [ ] Address issues immediately
- [ ] Collect feedback on usability
- [ ] Make minor adjustments as needed
- [ ] Continue parallel run with Google Sheets (as backup)

**30 Days Post Go-Live:**
- [ ] Validate data quality
- [ ] Review KPI metrics (intake time, AR aging, etc.)
- [ ] Survey users on satisfaction
- [ ] Archive Google Sheets if system validated
- [ ] Plan Phase 2 enhancements

---

## Troubleshooting

### Common Issues & Solutions

**Issue: Formula columns not calculating**
- **Solution:** Click column → Edit → Refresh formula. Ensure referenced columns have data.

**Issue: Connected board not showing items**
- **Solution:** Verify both boards have data. Check board permissions - connected board must be accessible to user.

**Issue: Automation not triggering**
- **Solution:** Go to Automations Center → Activity log. Check if conditions met. Verify notification email addresses.

**Issue: CSV import failed**
- **Solution:** Check CSV formatting (UTF-8 encoding). Verify column names match exactly. Remove special characters from data.

**Issue: Mirror columns not updating**
- **Solution:** Refresh page. Verify connection still exists. Re-save connected board column if needed.

**Issue: User can't see board**
- **Solution:** Check board permissions. Add user explicitly. Verify workspace membership.

**Issue: Notifications not received**
- **Solution:** Check monday.com notification settings (bell icon). Verify email not in spam. Check automation log.

---

## Support Resources

- **monday.com Help Center:** https://support.monday.com
- **Formula Reference:** https://support.monday.com/hc/en-us/articles/360016243619
- **Automation Recipes:** https://support.monday.com/hc/en-us/articles/360001222819
- **HIPAA Compliance:** https://monday.com/lp/hipaa
- **Video Tutorials:** https://monday.com/resources/videos

---

## Next Steps

After successful implementation:

1. **Week 1-4:** Monitor adoption and gather feedback
2. **Month 2:** Begin dashboard development (Phase 2)
3. **Month 3:** Explore SimplePractice API integration options
4. **Quarterly:** Review KPIs and system effectiveness
5. **Annually:** Evaluate advanced features and enhancements

---

**Implementation Complete!** 🎉

Your operational system is now live. Continue to iterate based on user feedback and business needs.
