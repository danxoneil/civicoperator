# Monday.com Automations Specification
## Jenkins Creative Counseling Center - MVP Setup

---

## Board 1: Patients & Intake

### Automation 1: Intake SLA Alert
**Trigger:** When Days in Stage > 7
**Action:** Send notification to Intake Coordinator
**Message:** "⚠️ Patient {Patient Name} has been in {Current Status} for {Days in Stage} days. Please review and take action."
**Priority:** High
**Purpose:** Prevent stalled intake cases from falling through cracks

**monday.com Recipe:**
```
When column "Days in Stage" changes and is greater than 7,
notify person in "Intake Coordinator"
with message "Patient has been in same stage for {Days in Stage} days - action needed"
```

---

### Automation 2: Forms Complete → Status Update
**Trigger:** When Forms Status changes to "Complete"
**Action:** Move to "Ready for Scheduling" group AND Change Current Status to "Ready"
**Purpose:** Automatically advance intake workflow when forms are complete

**monday.com Recipe:**
```
When column "Forms Status" changes to "Complete",
move item to group "Ready for Scheduling"
and change status of "Current Status" to "Ready"
```

---

### Automation 3: SimplePractice Entry Confirmation
**Trigger:** When SimplePractice Entry Date is filled
**Action:** Move item to "Archived" group AND Change Current Status to "Complete"
**Purpose:** Archive completed intakes once entered into clinical system

**monday.com Recipe:**
```
When column "SimplePractice Entry Date" changes and is not empty,
move item to group "Archived"
and change status of "Current Status" to "Complete"
```

---

### Automation 4: High Priority Escalation
**Trigger:** When Priority changes to "Urgent"
**Action:** Notify board owner AND Create task in a separate board (if using Tasks board)
**Message:** "🚨 URGENT: Patient {Patient Name} flagged as urgent priority. Referral source: {Referral Source}. Assigned to: {Intake Coordinator}"
**Purpose:** Ensure urgent cases get immediate attention

**monday.com Recipe:**
```
When column "Priority" changes to "Urgent",
notify board subscribers
with message "URGENT patient intake requires immediate attention"
```

---

### Automation 5: Insurance Denied → Flag & Notify
**Trigger:** When Insurance Status changes to "Denied"
**Action:** Change Priority to "High" AND Notify Intake Coordinator
**Purpose:** Ensure denied insurance is addressed quickly

**monday.com Recipe:**
```
When column "Insurance Status" changes to "Denied",
change status of "Priority" to "High"
and notify person in "Intake Coordinator"
with message "Insurance verification denied - discuss options with family"
```

---

## Board 2: Clinicians

### Automation 6: License Expiration Alert (60 days)
**Trigger:** When Days Until Expiration ≤ 60
**Action:** Notify clinician AND board owner
**Message:** "📋 License {License Type} #{License Number} for {Clinician Name} expires in {Days Until Expiration} days. Please schedule renewal."
**Priority:** Critical
**Purpose:** Prevent expired credentials

**monday.com Recipe:**
```
When column "Days Until Expiration" changes to something and is lower than or equal to 60,
notify person in column "Clinician Name"
and notify board owner
with message "License expiring in 60 days - begin renewal process"
```

---

### Automation 7: Background Check Expiration Alert
**Trigger:** When Background Check Status changes to "Expiring Soon"
**Action:** Create task for HR/Admin AND Notify clinician
**Purpose:** Maintain compliance with background check requirements

**monday.com Recipe:**
```
When column "Background Check Status" changes to "Expiring Soon",
notify board owner
with message "Background check expiring for {Clinician Name} - schedule renewal"
```

---

### Automation 8: Capacity Alert (Near Full)
**Trigger:** When Availability % < 15
**Action:** Notify board owner AND Change status indicator
**Message:** "⚠️ {Clinician Name} is at {Availability %}% capacity. Consider assignment adjustments."
**Purpose:** Balance caseloads and prevent clinician burnout

**monday.com Recipe:**
```
When column "Availability %" changes and is lower than 15,
notify board owner
with message "Clinician near capacity - {Current Patient Count} of {Max Weekly Sessions}"
```

---

### Automation 9: New Clinician Onboarding Checklist
**Trigger:** When Current Status changes to "Onboarding"
**Action:** Create subitems OR Notify admin with onboarding checklist
**Purpose:** Standardize new clinician setup

**monday.com Recipe:**
```
When column "Current Status" changes to "Onboarding",
notify board owner
with message "New clinician onboarding started - complete credential verification and SimplePractice setup"
```

---

## Board 3: Claims Tracking

### Automation 10: Aging Bucket Auto-Assignment
**Trigger:** When Days Outstanding reaches threshold (30, 60, 90)
**Action:** Update Aging Category status
**Purpose:** Automatically categorize claims by age

**monday.com Recipe:**
```
When column "Days Outstanding" changes to something greater than or equal to 90,
change status of "Aging Category" to "90+"
and change status of "Priority" to "Urgent"
```

*(Create similar recipes for 60-day and 30-day thresholds)*

---

### Automation 11: Denial Alert & Task Creation
**Trigger:** When Claim Status changes to "Denied"
**Action:** Change Priority to "High" AND Assign to Follow-Up Owner AND Set Next Follow-Up Date (7 days)
**Message:** "❌ Claim {Claim Number} denied - {Denial Reason}. Review and determine appeal action."
**Purpose:** Ensure denials are addressed promptly

**monday.com Recipe:**
```
When column "Claim Status" changes to "Denied",
change status of "Priority" to "High"
and notify person in "Follow-Up Owner"
with message "Claim denied - review for appeal: {Denial Reason}"
```

---

### Automation 12: High Dollar At-Risk Alert
**Trigger:** When Claim Amount > $500 AND Days Outstanding > 90
**Action:** Notify billing manager AND Flag as urgent
**Message:** "💰 High-value claim at risk: {Claim Number} for ${Claim Amount}, outstanding {Days Outstanding} days"
**Purpose:** Prioritize high-dollar collections

**monday.com Recipe:**
```
When column "Days Outstanding" is greater than 90 and column "Claim Amount" is greater than 500,
change status of "Priority" to "Urgent"
and notify board owner
with message "High-value claim at risk - immediate follow-up required"
```

---

### Automation 13: Payment Received → Archive
**Trigger:** When Claim Status changes to "Paid"
**Action:** Move to "Resolved" group AND Calculate payment date metrics
**Purpose:** Keep active board clean and measure collection speed

**monday.com Recipe:**
```
When column "Claim Status" changes to "Paid",
move item to group "Resolved"
```

---

## Board 4: Locations

### Automation 14: Agreement Renewal Alert
**Trigger:** When Days Until Renewal ≤ 90
**Action:** Notify board owner AND Create renewal task
**Message:** "📝 Agreement for {Location Name} expires in {Days Until Renewal} days on {Agreement Expiration}"
**Purpose:** Prevent lapsed location agreements

**monday.com Recipe:**
```
When column "Days Until Renewal" changes to something lower than or equal to 90,
notify board owner
with message "Location agreement expires in 90 days - begin renewal process for {Location Name}"
```

---

### Automation 15: Over Capacity Alert
**Trigger:** When Utilization % > 90
**Action:** Notify board owner AND Flag location
**Message:** "⚠️ {Location Name} at {Utilization %}% capacity ({Current Census}/{Max Capacity})"
**Purpose:** Manage location capacity and expansion planning

**monday.com Recipe:**
```
When column "Utilization %" changes to something greater than 90,
notify board owner
with message "Location near capacity - consider expansion or referral adjustments"
```

---

## Board 5: Patient-Clinician Assignments

### Automation 16: Authorization Expiration Alert (14 days)
**Trigger:** When Days Until Auth Expires ≤ 14
**Action:** Change Risk Flag to "Auth Expiring" AND Notify clinician and billing
**Message:** "⏰ Authorization for {Patient} expires in {Days Until Auth Expires} days. Submit extension request."
**Purpose:** Prevent service disruptions from expired authorizations

**monday.com Recipe:**
```
When column "Days Until Auth Expires" changes to something lower than or equal to 14,
change status of "Risk Flag" to "Auth Expiring"
and notify person in "Clinician"
with message "Authorization expiring soon - submit extension for {Patient}"
```

---

### Automation 17: Service Gap Detection
**Trigger:** When Days Since Last Session > 21
**Action:** Change Risk Flag to "Gaps in Service" AND Notify clinician
**Message:** "📅 No session for {Patient} in {Days Since Last Session} days. Outreach recommended."
**Purpose:** Identify patients who may be disengaging

**monday.com Recipe:**
```
When column "Days Since Last Session" changes to something greater than 21,
change status of "Risk Flag" to "Gaps in Service"
and notify person in "Clinician"
with message "Patient has service gap - consider outreach"
```

---

### Automation 18: Sessions Nearly Exhausted
**Trigger:** When Sessions Remaining ≤ 2
**Action:** Change Risk Flag AND Notify clinician and billing
**Message:** "⚠️ Only {Sessions Remaining} sessions remain for {Patient}. Authorization action needed."
**Purpose:** Ensure continuous service authorization

**monday.com Recipe:**
```
When column "Sessions Remaining" changes to something lower than or equal to 2,
change status of "Risk Flag" to "Auth Expiring"
and notify person in "Clinician"
with message "Low remaining sessions - request authorization extension"
```

---

## Connected Boards & Integrations

### Connection 1: Patients ↔ Assignments
- **Board:** Patients & Intake
- **Connected to:** Patient-Clinician Assignments
- **Column Type:** Connect Boards (two-way)
- **Mirror Columns from Assignments:**
  - Current Clinician (from Clinician column)
  - Last Session Date
  - Sessions Remaining
- **Purpose:** View patient's current assignment status directly from intake board

---

### Connection 2: Clinicians ↔ Assignments
- **Board:** Clinicians
- **Connected to:** Patient-Clinician Assignments
- **Column Type:** Connect Boards (two-way)
- **Mirror Columns from Assignments:**
  - Number of Active Assignments
  - List of Current Patients
- **Purpose:** Real-time caseload visibility on clinician roster

---

### Connection 3: Locations ↔ Assignments
- **Board:** Locations
- **Connected to:** Patient-Clinician Assignments
- **Column Type:** Connect Boards (two-way)
- **Mirror Columns from Assignments:**
  - Number of Active Patients at Location
  - Assigned Clinicians
- **Purpose:** Track location utilization and staffing

---

### Connection 4: Claims ↔ Patients
- **Board:** Claims Tracking
- **Connected to:** Patients & Intake
- **Column Type:** Connect Boards
- **Mirror Columns from Patients:**
  - Insurance Carrier
  - Current Location
- **Purpose:** Link financial tracking to patient records

---

### Connection 5: Claims ↔ Clinicians
- **Board:** Claims Tracking
- **Connected to:** Clinicians
- **Column Type:** Connect Boards
- **Mirror Columns from Clinicians:**
  - License Type
  - NPI Number
- **Purpose:** Associate claims with rendering provider credentials

---

### Connection 6: Clinicians Self-Reference (Supervision)
- **Board:** Clinicians
- **Connected to:** Clinicians (same board)
- **Column Type:** Connect Boards
- **Purpose:** Track supervisor-supervisee relationships

---

## Integration Notes

### SimplePractice Data Import Process
1. **Export from SimplePractice:**
   - Claims data: Weekly export to CSV
   - Patient demographics: As needed for intake completion
   - Session data: Weekly for assignment tracking

2. **Import to monday.com:**
   - Use CSV import function
   - Map columns to existing board structure
   - Update existing items rather than creating duplicates (match on Patient ID, Claim Number, etc.)

3. **Recommended Cadence:**
   - Claims: Weekly (every Monday morning)
   - Assignments/Sessions: Bi-weekly
   - Patient updates: As needed during intake process

---

## Dashboard Automations (Future Phase)

### Recommended Dashboard Auto-Updates
- **Intake Health Dashboard:** Auto-refresh daily at 8 AM
- **Claims Aging Dashboard:** Auto-refresh daily at 9 AM
- **Clinician Capacity Dashboard:** Auto-refresh twice daily (9 AM, 3 PM)
- **Executive Overview:** Auto-refresh daily at 6 AM (before leadership review)

---

## Implementation Priority

### Phase 1 (Week 1): Critical Automations
1. Intake SLA Alert (Auto #1)
2. License Expiration Alert (Auto #6)
3. Denial Alert (Auto #11)
4. Authorization Expiration Alert (Auto #16)

### Phase 2 (Week 2): Workflow Automations
5. Forms Complete Status Update (Auto #2)
6. Aging Bucket Assignment (Auto #10)
7. Service Gap Detection (Auto #17)
8. Agreement Renewal Alert (Auto #14)

### Phase 3 (Week 3): Optimization Automations
9. Capacity Alerts (Auto #8, #15)
10. Payment Archive (Auto #13)
11. Sessions Exhausted (Auto #18)
12. High Dollar Claims (Auto #12)

---

## Testing Checklist

Before go-live, test each automation:
- [ ] Verify trigger conditions work correctly
- [ ] Confirm notifications reach correct people
- [ ] Test status changes cascade properly
- [ ] Validate formulas calculate accurately
- [ ] Ensure connected board mirrors update in real-time
- [ ] Check permissions allow users to see relevant notifications
- [ ] Test edge cases (empty fields, multiple simultaneous triggers)

---

## Notes on monday.com Automation Limits

- **Free/Basic Plan:** Limited automations per board
- **Standard Plan:** 250 actions/month included
- **Pro Plan:** 25,000 actions/month included
- **Enterprise Plan:** 250,000 actions/month included

**Recommendation:** Start with Pro plan minimum to support 18 active automations across 5 boards with moderate usage volume.

**Estimated Monthly Actions:** ~15,000-20,000 based on:
- 100 new intakes/month
- 300 active assignments
- 400 active claims
- 12 active clinicians
- Daily formula recalculations
