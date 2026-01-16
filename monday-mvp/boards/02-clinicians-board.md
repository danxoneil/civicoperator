# Board 2: Clinicians

## Purpose
Master directory of clinical workforce with credentials, capacity tracking, and compliance monitoring.

## Board Structure

### Groups
- **Active Clinicians** - Currently practicing
- **Onboarding** - New hires in training
- **Inactive/On Leave** - Temporarily unavailable
- **Offboarded** - Former clinicians (historical record)

### Columns

| Column Name | Type | Purpose |
|-------------|------|---------|
| Clinician Name | Text | Full name |
| Clinician ID | Text | Unique identifier |
| Employment Type | Dropdown | Employee/Contractor/Intern |
| Primary Location | Connect Board | Link to Locations board |
| Specialty | Dropdown | Child/Adolescent/Family/Equine/EMDR |
| License Type | Dropdown | LCSW/LMFT/LPC/Provisional/Intern |
| License Number | Text | State license number |
| License Expiration | Date | Renewal date |
| Days Until Expiration | Formula | Auto-calculated |
| NPI Number | Text | National Provider Identifier |
| Insurance Panels | Dropdown (Multi) | Credentialed insurance carriers |
| Supervisor | Connect Board | Link to supervisor (self-reference) |
| Start Date | Date | Employment start |
| Current Status | Status | Active/Onboarding/Leave/Inactive |
| Max Weekly Sessions | Number | Capacity limit |
| Current Patient Count | Number | Active caseload |
| Availability % | Number | (Max - Current)/Max * 100 |
| Background Check Date | Date | Last background check |
| Background Check Status | Status | Current/Expiring Soon/Expired |
| SimplePractice Profile | Link | Link to SP provider profile |
| Notes | Long Text | Internal notes |

## Key Metrics to Track
- Total active clinicians
- Total capacity vs utilization
- Expiring credentials (next 30/60/90 days)
- Clinicians by location
- Supervisor ratios

## Views
1. **Active Roster** - All active clinicians
2. **Capacity Overview** - Sorted by availability
3. **Credential Alerts** - Expiring within 60 days
4. **By Location** - Grouped by primary location
5. **Supervision Structure** - Grouped by supervisor
