# Board 1: Patients & Intake

## Purpose
Central operational board for managing patient intake workflow from referral through readiness for scheduling in SimplePractice.

## Board Structure

### Groups
- **New Referrals** - Initial intake requests
- **Intake In Progress** - Active intake processes
- **Ready for Scheduling** - Completed intake, ready for SimplePractice
- **Stalled/Exception** - Cases requiring attention
- **Archived** - Closed/cancelled intakes

### Columns

| Column Name | Type | Purpose |
|-------------|------|---------|
| Patient Name | Text | Patient full name (PHI - controlled access) |
| Patient ID | Text | Unique identifier (will match SimplePractice) |
| Referral Date | Date | When referral was received |
| Referral Source | Dropdown | School/Self/Insurance/Provider/County |
| Primary Contact | Text | Parent/guardian name |
| Contact Phone | Phone | Primary contact number |
| Contact Email | Email | Primary contact email |
| Insurance Carrier | Dropdown | Insurance provider |
| Insurance Status | Status | Not Verified/Verified/Denied/Self-Pay |
| Forms Status | Status | Not Sent/Sent/Partially Complete/Complete |
| Adobe Sign Link | Link | URL to Adobe Sign packet |
| Intake Coordinator | Person | Assigned admin staff |
| Current Status | Status | New/Contacted/Forms Sent/Forms Complete/Verified/Ready |
| Location Assigned | Connect Board | Link to Locations board |
| Days in Stage | Number | Auto-calculated aging |
| Priority | Status | Normal/High/Urgent |
| Next Action | Text | What needs to happen next |
| Notes | Long Text | Internal notes (limited PHI) |
| SimplePractice Entry Date | Date | When entered into SP |

## Key Metrics to Track
- Average days from referral to ready
- Stalled intake count (>7 days in same status)
- Forms completion rate
- Insurance verification turnaround time

## Views
1. **Main Board** - All active intakes
2. **My Intakes** - Filtered by logged-in user
3. **Stalled Cases** - >7 days without status change
4. **By Location** - Grouped by assigned location
5. **By Insurance Status** - Grouped by insurance status
