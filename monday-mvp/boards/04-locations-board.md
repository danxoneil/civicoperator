# Board 4: Locations

## Purpose
Master directory of physical practice locations, schools, and partner sites.

## Board Structure

### Groups
- **Primary Offices** - Owned/leased practice locations
- **Schools** - School-based service sites
- **Partner Sites** - External partner locations (including equine)
- **Inactive Locations** - Former/seasonal sites

### Columns

| Column Name | Type | Purpose |
|-------------|------|---------|
| Location Name | Text | Site name |
| Location ID | Text | Unique identifier |
| Location Type | Dropdown | Office/School/Partner/County Program |
| Address | Text | Full street address |
| County | Dropdown | Service county |
| Primary Contact | Text | Site contact person |
| Contact Phone | Phone | Site phone number |
| Contact Email | Email | Site email |
| Agreement Status | Status | Active/Pending/Expired/No Agreement |
| Agreement Expiration | Date | Contract renewal date |
| Days Until Renewal | Formula | Auto-calculated |
| Max Capacity | Number | Maximum patients at site |
| Current Census | Number | Active patients at location |
| Utilization % | Formula | (Current/Max) * 100 |
| Services Offered | Dropdown (Multi) | Individual/Group/Family/Equine |
| Insurance Accepted | Dropdown (Multi) | Accepted carriers at location |
| Active Clinicians | Connect Board | Link to Clinicians (mirror) |
| Active Patients | Connect Board | Link to Patients (mirror) |
| Location Status | Status | Active/Seasonal/Inactive |
| Notes | Long Text | Internal site notes |

## Key Metrics to Track
- Total active locations
- Capacity utilization by site
- Expiring agreements (next 30/60/90 days)
- Patient distribution by location
- Clinician coverage by site

## Views
1. **All Active Locations** - Currently operating sites
2. **Capacity Overview** - Sorted by utilization
3. **Agreement Renewals** - Expiring within 90 days
4. **By County** - Grouped by service county
5. **School Sites** - Schools only
