# monday.com Board Import Guide

## Quick Import Instructions

### Step 1: Create New Boards

1. Log into your monday.com enterprise account
2. Click "+ Add" in the left sidebar
3. Select "New board"
4. Choose "Start from scratch"

### Step 2: Import Each CSV

For **each of the 4 boards**, follow these steps:

#### Board 1: Activity Log
1. Name the board: **"📊 Activity Log"**
2. Click the "..." menu (top right)
3. Select "Import data"
4. Upload: `activity-log.csv`
5. monday.com will auto-detect columns and create them
6. Click "Import"
7. **After import:** Adjust column types if needed:
   - Date → Date column (with time)
   - Person → People column
   - Activity Type → Dropdown column
   - Duration, Calories, Steps, etc. → Numbers columns
   - Source → Status column
   - Notes → Long Text column

#### Board 2: Nutrition Log
1. Name the board: **"🍽️ Nutrition Log"**
2. Import: `nutrition-log.csv`
3. **After import:** Adjust column types:
   - Date & Time → Date column (with time)
   - Person → People column
   - Meal Type → Dropdown column
   - Calories, Protein, Carbs, Fat, Fiber → Numbers columns
   - AI Confidence → Status column
   - Source → Status column
   - Notes → Long Text column
   - **Add manually:** Photo column (File type)

#### Board 3: Daily Summary
1. Name the board: **"📈 Daily Summary"**
2. Import: `daily-summary.csv`
3. **After import:** Adjust column types:
   - Date → Date column
   - Person → People column
   - All metrics → Numbers columns
   - Notes → Long Text column
4. **Set up connected boards:**
   - Add "Connect Boards" column → Connect to Activity Log
   - Add "Connect Boards" column → Connect to Nutrition Log
5. **Set up formulas:**
   - Net Calories = Total Calories In - Total Calories Out

#### Board 4: Goals & Insights
1. Name the board: **"🎯 Goals & Insights"**
2. Import: `goals-insights.csv`
3. **After import:** Adjust column types:
   - Type → Dropdown column
   - Person → People column
   - Start Date, Target Date → Date columns
   - Status → Status column
   - Progress → Progress Tracking column
   - Target Value, Current Value → Numbers columns
   - Content → Long Text column
   - Data Source → Long Text column

### Step 3: Configure Groups

After import, organize items into groups:

**Activity Log:**
- Create groups: "This Week", "Last Week", "Archive"
- Move items accordingly

**Nutrition Log:**
- Create groups: "Today", "Yesterday", "This Week", "Archive"
- Move items accordingly

**Daily Summary:**
- Create groups: "This Week", "Last Week", "This Month", "Archive"
- Move items accordingly

**Goals & Insights:**
- Create groups: "Active Goals", "Completed Goals", "Weekly Insights", "Monthly Reports"
- Move items accordingly

### Step 4: Set Up Board Views

For each board, create additional views:

**Activity Log:**
- DXO Activities (filter: Person = DXO)
- SL Activities (filter: Person = SL)
- This Month (filter: Date in this month)
- Calendar View

**Nutrition Log:**
- Today's Meals (filter: Date is today)
- DXO Nutrition (filter: Person = DXO)
- SL Nutrition (filter: Person = SL)
- By Meal Type (group by: Meal Type)

**Daily Summary:**
- DXO Summary (filter: Person = DXO)
- SL Summary (filter: Person = SL)
- Chart View (show trends)

**Goals & Insights:**
- Active Goals (filter: Type = Goal, Status ≠ Completed)
- Recent Insights (sort by date, descending)
- DXO Goals (filter: Person = DXO)
- SL Goals (filter: Person = SL)

### Step 5: Add Automations

**Activity Log:**
1. "When Date is 2 weeks ago, move item to Archive"
2. "When Source changes to Manual, notify Person"

**Nutrition Log:**
1. "When Date is 1 week ago, move item to Archive"
2. "When AI Confidence is Low or Medium, notify Person"

**Daily Summary:**
1. "When Date is 1 month ago, move item to Archive"

### Step 6: Share with Team

1. Click "Invite" button (top right of each board)
2. Add SL (if you're DXO) or DXO (if you're SL)
3. Set permissions: "Can edit"

## Important Notes

### Column Type Conversion
monday.com might import everything as text initially. You'll need to:
1. Click column header → "Edit column"
2. Change type to appropriate format (Date, Numbers, Status, etc.)
3. monday.com will convert the data automatically

### Dropdown Values
For dropdown columns (Activity Type, Meal Type, etc.), the values from the CSV will automatically become dropdown options.

### Status Column Colors
After creating Status columns, customize colors:
- **Activity Log - Source:**
  - Fitbit = Green
  - Manual = Blue
  - Imported = Gray

- **Nutrition Log - AI Confidence:**
  - High = Green
  - Medium = Yellow
  - Low = Red
  - Manual = Blue

- **Nutrition Log - Source:**
  - Photo AI = Green
  - Fitbit = Blue
  - Manual = Gray

### Adding the Photo Column
The CSV can't include file uploads, so add the Photo column manually:
1. In Nutrition Log board
2. Click "+" to add column
3. Select "File" type
4. Name it "Photo"

## Dummy Data

The CSV files include 4-5 sample rows each. These are:
- **Realistic examples** showing the data format
- **Both DXO and SL** represented
- **Various activity/meal types** for testing

Feel free to:
- ✅ Keep them for reference
- ✅ Delete them after import
- ✅ Edit them to match real data

## Next Steps After Import

1. ✅ Verify all columns imported correctly
2. ✅ Adjust column types as needed
3. ✅ Set up groups and move items
4. ✅ Create additional views
5. ✅ Share boards with your partner
6. ✅ Start adding real data manually
7. ✅ Begin building Make.com scenarios (see main guide)

## Troubleshooting

**Issue: Columns didn't import**
- Solution: Check CSV formatting. Open in Excel/Sheets to verify.

**Issue: Numbers showing as text**
- Solution: Edit column → Change type to "Numbers"

**Issue: Dates not recognized**
- Solution: Edit column → Change type to "Date" → Select format

**Issue: Person column not working**
- Solution: Edit column → Change to "People" → Assign yourself and SL

## Time Estimate

- Import all 4 boards: **15-20 minutes**
- Configure column types: **20-30 minutes**
- Set up groups and views: **30-45 minutes**
- **Total: ~1-1.5 hours**

Once imported, you'll have a fully functional fitness tracking system ready for Make.com automation!

---

**Files in this folder:**
- `activity-log.csv` - Import for Activity Log board
- `nutrition-log.csv` - Import for Nutrition Log board
- `daily-summary.csv` - Import for Daily Summary board
- `goals-insights.csv` - Import for Goals & Insights board
- `IMPORT-GUIDE.md` - This guide
