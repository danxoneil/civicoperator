# Board 5: Patient-Clinician Assignments

## Purpose
Operational assignment tracking linking patients to clinicians, sessions, and locations. Non-clinical metadata only.

## Board Structure

### Groups
- **Active Assignments** - Current patient-clinician pairs
- **Pending Start** - Matched but not yet begun
- **On Hold** - Temporarily paused
- **Closed** - Completed/transferred/discharged

### Columns

| Column Name | Type | Purpose |
|-------------|------|---------|
| Assignment ID | Text | Unique identifier |
| Patient | Connect Board | Link to Patients board |
| Clinician | Connect Board | Link to Clinicians board |
| Location | Connect Board | Link to Locations board |
| Assignment Date | Date | When assignment began |
| First Session Date | Date | First actual session |
| Session Frequency | Dropdown | Weekly/Biweekly/Monthly |
| Authorized Sessions | Number | Insurance auth count |
| Sessions Used | Number | Count of sessions completed |
| Sessions Remaining | Formula | Authorized - Used |
| Authorization End Date | Date | When auth expires |
| Days Until Auth Expires | Formula | Auto-calculated |
| Assignment Status | Status | Active/Pending/On Hold/Closed |
| Primary Insurance | Dropdown | Active insurance carrier |
| Copay Amount | Number | Patient copay per session |
| Last Session Date | Date | Most recent session |
| Days Since Last Session | Formula | Today - Last Session Date |
| Supervisor (if applicable) | Connect Board | Link to supervisor clinician |
| Assignment Type | Dropdown | Individual/Group/Family/Equine |
| Risk Flag | Status | None/Auth Expiring/Gaps in Service/Other |
| Notes | Long Text | Assignment notes |
| Closure Reason | Dropdown | Completed/Transferred/Discharged/Insurance Change |

## Key Metrics to Track
- Total active assignments
- Expiring authorizations (next 14/30 days)
- Gaps in service (>30 days since last session)
- Utilization by clinician
- Average session frequency

## Views
1. **All Active Assignments** - Current active cases
2. **Authorization Alerts** - Expiring within 30 days
3. **Service Gaps** - >21 days since last session
4. **By Clinician** - Grouped by assigned clinician
5. **By Location** - Grouped by service location
6. **Supervision Required** - Assignments with supervisors
