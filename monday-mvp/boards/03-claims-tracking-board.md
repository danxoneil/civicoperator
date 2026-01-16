# Board 3: Claims Tracking

## Purpose
Post-billing claims follow-up, denial management, and revenue cycle visibility. Replaces Google Sheets tracking for account aging and collections.

## Board Structure

### Groups
- **Newly Submitted** - Claims submitted <30 days
- **Pending/In Process** - 30-60 days
- **Aging** - 60-90 days
- **At Risk** - 90+ days
- **Denied** - Requires appeal or write-off
- **Resolved** - Paid or closed

### Columns

| Column Name | Type | Purpose |
|-------------|------|---------|
| Claim Number | Text | SimplePractice claim ID |
| Patient Name | Connect Board | Link to Patients board |
| Clinician | Connect Board | Link to Clinicians board |
| Service Date | Date | Date of service |
| Submission Date | Date | Date submitted to payer |
| Days Outstanding | Formula | Today - Submission Date |
| Payer | Dropdown | Insurance carrier |
| Claim Amount | Number | Billed amount |
| Allowed Amount | Number | Insurance allowed amount |
| Paid Amount | Number | Amount received |
| Patient Responsibility | Number | Copay/coinsurance |
| Claim Status | Status | Submitted/Accepted/Processing/Paid/Denied/Appeal |
| Denial Reason | Dropdown | Auth/Eligibility/Coding/Timely Filing/Other |
| Last Follow-Up Date | Date | Last contact with payer |
| Next Follow-Up Date | Date | Scheduled next action |
| Follow-Up Owner | Person | Assigned billing staff |
| Priority | Status | Normal/High/Urgent |
| Aging Category | Status | 0-30/31-60/61-90/90+ |
| Resolution Notes | Long Text | Payer communications log |
| Appeal Filed Date | Date | If denied and appealed |
| Expected Payment Date | Date | Projected resolution |

## Key Metrics to Track
- Total AR by aging bucket
- Denial rate by payer
- Average days to payment
- Claims at risk (>90 days)
- Resolution rate

## Views
1. **All Active Claims** - Not yet paid/closed
2. **Aging Report** - Grouped by aging category
3. **My Claims** - Filtered by follow-up owner
4. **By Payer** - Grouped by insurance carrier
5. **Denials & Appeals** - Filtered by denied status
6. **High Dollar Claims** - Amount > $500
