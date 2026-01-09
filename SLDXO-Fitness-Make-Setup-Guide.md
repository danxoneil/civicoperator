# SLDXO Fitness Tracking - Make.com + monday.com Setup Guide

**Created:** January 8, 2026
**For:** DXO & SL
**Purpose:** Complete blueprint for fitness & nutrition tracking system

---

## 📋 Table of Contents

1. [monday.com Board Structure](#mondaycom-board-structure)
2. [Make.com Account Setup](#makecom-account-setup)
3. [Scenario 1: Daily Fitbit Sync](#scenario-1-daily-fitbit-sync)
4. [Scenario 2: Food Photo Analysis](#scenario-2-food-photo-analysis)
5. [Scenario 3: Weekly Insights Report](#scenario-3-weekly-insights-report)
6. [Quick Start Checklist](#quick-start-checklist)

---

## 🎯 monday.com Board Structure

### **Board 1: 📊 Activity Log**

**Purpose:** Track all workouts and daily activity

**Groups:**
- This Week
- Last Week
- Archive (automated after 2 weeks)

**Columns:**
| Column Name | Type | Purpose | Settings |
|------------|------|---------|----------|
| Activity | Item Name | Name of activity/workout | - |
| Date | Date | When activity occurred | Show time |
| Person | People | DXO or SL | - |
| Activity Type | Dropdown | Type of exercise | Walk, Run, Bike, Weights, Yoga, Sports, Other |
| Duration (min) | Numbers | How long | Unit: minutes |
| Calories Burned | Numbers | Energy expenditure | - |
| Steps | Numbers | Step count | - |
| Distance (km) | Numbers | Distance covered | Unit: km, 2 decimals |
| Avg Heart Rate | Numbers | Average HR | Unit: bpm |
| Max Heart Rate | Numbers | Peak HR | Unit: bpm |
| Active Zone Min | Numbers | Fitbit active minutes | - |
| Source | Status | Where data came from | Fitbit (green), Manual (blue), Imported (gray) |
| Notes | Long Text | Additional details | - |
| Fitbit ID | Text | Unique Fitbit log ID | Hidden from view |

**Views:**
1. **Main View** - All items, grouped by week
2. **DXO Activities** - Filter: Person = DXO
3. **SL Activities** - Filter: Person = SL
4. **This Month** - Filter: Date is within this month
5. **By Activity Type** - Grouped by Activity Type
6. **Calendar View** - Show all activities on calendar

**Automations (built-in monday.com):**
- When Date is 2 weeks ago, move item to Archive
- When status changes to Manual, send notification to person

---

### **Board 2: 🍽️ Nutrition Log**

**Purpose:** Track all meals and food intake

**Groups:**
- Today
- Yesterday
- This Week
- Archive (automated)

**Columns:**
| Column Name | Type | Purpose | Settings |
|------------|------|---------|----------|
| Food Item | Item Name | Name of food/meal | - |
| Date & Time | Date | When consumed | Show time |
| Person | People | DXO or SL | - |
| Meal Type | Dropdown | Type of meal | Breakfast, Lunch, Dinner, Snack |
| Calories | Numbers | Total calories | - |
| Protein (g) | Numbers | Protein content | Unit: g, 1 decimal |
| Carbs (g) | Numbers | Carbohydrate content | Unit: g, 1 decimal |
| Fat (g) | Numbers | Fat content | Unit: g, 1 decimal |
| Fiber (g) | Numbers | Fiber content | Unit: g, 1 decimal |
| Photo | File | Food photo | - |
| AI Confidence | Status | Confidence level | High (green), Medium (yellow), Low (red), Manual (blue) |
| Source | Status | Where data came from | Photo AI (green), Fitbit (blue), Manual (gray) |
| Notes | Long Text | Description, adjustments | - |

**Views:**
1. **Today's Meals** - Filter: Date is today
2. **DXO Nutrition** - Filter: Person = DXO
3. **SL Nutrition** - Filter: Person = SL
4. **This Week** - Filter: Date is within this week
5. **By Meal Type** - Grouped by Meal Type
6. **Low Confidence** - Filter: AI Confidence = Low or Medium

**Automations:**
- When Date is 1 week ago, move item to Archive
- When AI Confidence is Low, notify person to review

---

### **Board 3: 📈 Daily Summary**

**Purpose:** Aggregate daily metrics for both people

**Groups:**
- This Week
- Last Week
- This Month
- Archive

**Columns:**
| Column Name | Type | Purpose | Settings |
|------------|------|---------|----------|
| Date | Item Name | The date | Format: "Jan 8, 2026" |
| Person | People | DXO or SL | - |
| Total Steps | Numbers | Daily step count | Connected: sum from Activity Log |
| Total Calories Out | Numbers | Calories burned | Connected: sum from Activity Log |
| Total Calories In | Numbers | Calories consumed | Connected: sum from Nutrition Log |
| Net Calories | Formula | In - Out | Formula: {Total Calories In} - {Total Calories Out} |
| Total Protein (g) | Numbers | Daily protein | Connected: sum from Nutrition Log |
| Total Carbs (g) | Numbers | Daily carbs | Connected: sum from Nutrition Log |
| Total Fat (g) | Numbers | Daily fat | Connected: sum from Nutrition Log |
| Macro Ratio | Formula | P:C:F ratio | Display only |
| Activities Count | Numbers | # of workouts | Connected: count from Activity Log |
| Meals Count | Numbers | # of meals logged | Connected: count from Nutrition Log |
| Weight (kg) | Numbers | Daily weight | Manual entry |
| Sleep Hours | Numbers | Hours of sleep | From Fitbit |
| Notes | Long Text | Daily notes | - |

**Views:**
1. **This Week** - Default view
2. **DXO Summary** - Filter: Person = DXO
3. **SL Summary** - Filter: Person = SL
4. **Chart View** - Show trends over time

**Connected Boards:**
- Connect to Activity Log (mirror columns)
- Connect to Nutrition Log (mirror columns)

---

### **Board 4: 🎯 Goals & Insights**

**Purpose:** Track goals and store AI-generated insights

**Groups:**
- Active Goals
- Completed Goals
- Weekly Insights
- Monthly Reports

**Columns:**
| Column Name | Type | Purpose | Settings |
|------------|------|---------|----------|
| Goal/Insight | Item Name | Title | - |
| Type | Dropdown | Category | Goal, Weekly Insight, Monthly Report, Recommendation |
| Person | People | DXO or SL | - |
| Start Date | Date | When goal started | - |
| Target Date | Date | Goal deadline | - |
| Status | Status | Progress | Not Started, In Progress, Completed, Paused |
| Progress | Progress Tracking | Visual progress | - |
| Target Value | Numbers | Goal target | e.g., 10000 steps |
| Current Value | Numbers | Current achievement | Updated via automation |
| Content | Long Text | Insight details | AI-generated or manual |
| Data Source | Long Text | Which data informed this | JSON snapshot |

**Views:**
1. **Active Goals** - Filter: Type = Goal, Status ≠ Completed
2. **Recent Insights** - Filter: Type contains "Insight", sort by date
3. **DXO Goals** - Filter: Person = DXO
4. **SL Goals** - Filter: Person = SL

---

## 🔧 Make.com Account Setup

### Step 1: Create Make.com Account

1. Go to **make.com**
2. Click "Get Started Free"
3. Sign up with your email
4. Confirm email address

### Step 2: Connect monday.com

1. In Make.com, click "Connections" (left sidebar)
2. Click "+ Add"
3. Search for "monday.com"
4. Click "Create a connection"
5. Log in with your monday.com enterprise account
6. Authorize Make.com access
7. Name the connection: "SLDXO monday Enterprise"

### Step 3: Get API Keys

**Fitbit API:**
1. Go to dev.fitbit.com
2. Register an application
3. Application Type: "Personal"
4. OAuth 2.0 Application Type: "Personal"
5. Redirect URL: `https://hook.integromat.com/oauth/cb/oauth2` (Make.com OAuth handler)
6. Save **Client ID** and **Client Secret**

**OpenAI API:**
1. Go to platform.openai.com
2. Create API key
3. Save key securely
4. Add $10 credit to start

---

## 🤖 Scenario 1: Daily Fitbit Sync

### Overview
**Trigger:** Every day at 2:00 AM
**Actions:** Fetch yesterday's Fitbit data → Create items in monday.com
**Frequency:** Daily automatic
**Operations per run:** ~15-20

### Visual Flow

```
[Schedule: 2 AM Daily]
        ↓
[HTTP: Get Fitbit Activities]
        ↓
[Iterator: Loop through activities]
        ↓
[monday.com: Create Activity Log Item]
        ↓
[HTTP: Get Fitbit Nutrition]
        ↓
[Iterator: Loop through foods]
        ↓
[monday.com: Create Nutrition Log Item]
        ↓
[monday.com: Create Daily Summary Item]
```

### Step-by-Step Setup

#### Module 1: Schedule Trigger
1. Click "Create a new scenario"
2. Click the "+" to add first module
3. Search "Schedule" → Select "Scheduling"
4. Choose "Every day"
5. Settings:
   - Time: 02:00
   - Time zone: Your timezone
   - Advanced: Check "Run scenario even if previous run is incomplete"

#### Module 2: Set Variables (Helper)
1. Add module: "Tools" → "Set multiple variables"
2. Add variables:
   - `yesterday_date`: `{{formatDate(addDays(now; -1); "YYYY-MM-DD")}}`
   - `fitbit_user_id`: `YOUR_FITBIT_USER_ID` (get from Fitbit profile)
3. This calculates yesterday's date automatically

#### Module 3: HTTP Get Fitbit Activities
1. Add module: "HTTP" → "Make a request"
2. URL: `https://api.fitbit.com/1/user/{{yesterday_date}}/activities/list.json`
3. Method: GET
4. Headers:
   - Authorization: `Bearer YOUR_FITBIT_ACCESS_TOKEN`
5. Parse response: Yes

**Note:** You'll need to set up OAuth for production. For testing, get a token from dev.fitbit.com

#### Module 4: Iterator (Loop through activities)
1. Add module: "Flow Control" → "Iterator"
2. Array: `{{3.data.activities}}`
3. This loops through each activity returned

#### Module 5: Create monday.com Activity Item
1. Add module: "monday.com" → "Create an Item"
2. Connection: Select your monday connection
3. Board: Select "Activity Log" board
4. Group: "This Week"
5. Item Name: `{{4.name}}` (activity name from Fitbit)
6. Column Values (click "Add item" for each):

   **Date:**
   - Column: Date
   - Value: `{{4.startTime}}`

   **Person:** (You'll need to determine which user)
   - Column: Person
   - Value: DXO or SL (based on Fitbit account)

   **Activity Type:**
   - Column: Activity Type
   - Value: `{{4.activityName}}`

   **Duration (min):**
   - Column: Duration (min)
   - Value: `{{4.duration / 60000}}` (convert ms to minutes)

   **Calories Burned:**
   - Column: Calories Burned
   - Value: `{{4.calories}}`

   **Steps:**
   - Column: Steps
   - Value: `{{4.steps}}`

   **Distance (km):**
   - Column: Distance (km)
   - Value: `{{4.distance}}`

   **Avg Heart Rate:**
   - Column: Avg Heart Rate
   - Value: `{{4.averageHeartRate}}`

   **Source:**
   - Column: Source
   - Value: "Fitbit"

   **Fitbit ID:**
   - Column: Fitbit ID
   - Value: `{{4.logId}}`

7. Click "OK"

#### Module 6: HTTP Get Fitbit Nutrition
1. Add module: "HTTP" → "Make a request"
2. URL: `https://api.fitbit.com/1/user/-/foods/log/date/{{yesterday_date}}.json`
3. Method: GET
4. Headers:
   - Authorization: `Bearer YOUR_FITBIT_ACCESS_TOKEN`
5. Parse response: Yes

#### Module 7: Iterator (Loop through foods)
1. Add module: "Flow Control" → "Iterator"
2. Array: `{{6.data.foods}}`

#### Module 8: Create monday.com Nutrition Item
1. Add module: "monday.com" → "Create an Item"
2. Connection: Your monday connection
3. Board: "Nutrition Log"
4. Group: "Today"
5. Item Name: `{{7.loggedFood.name}}`
6. Column Values:

   **Date & Time:**
   - Column: Date & Time
   - Value: `{{7.loggedFood.logDate}}`

   **Person:**
   - Column: Person
   - Value: DXO or SL

   **Meal Type:**
   - Column: Meal Type
   - Value: "Breakfast" (Fitbit doesn't provide this - could add logic later)

   **Calories:**
   - Column: Calories
   - Value: `{{7.loggedFood.nutritionalValues.calories}}`

   **Protein (g):**
   - Column: Protein (g)
   - Value: `{{7.loggedFood.nutritionalValues.protein}}`

   **Carbs (g):**
   - Column: Carbs (g)
   - Value: `{{7.loggedFood.nutritionalValues.carbs}}`

   **Fat (g):**
   - Column: Fat (g)
   - Value: `{{7.loggedFood.nutritionalValues.fat}}`

   **Source:**
   - Column: Source
   - Value: "Fitbit"

7. Click "OK"

#### Module 9: Create Daily Summary
1. Add module: "monday.com" → "Create an Item"
2. Board: "Daily Summary"
3. Group: "This Week"
4. Item Name: `{{formatDate(yesterday_date; "MMM DD, YYYY")}}`
5. Column Values:
   - Person: DXO or SL
   - Date: `{{yesterday_date}}`
   - (Other columns will auto-populate from connected boards)

### Save & Test

1. Click "Save" (bottom left)
2. Name scenario: "Daily Fitbit Sync"
3. Click "Run once" to test
4. Check monday.com boards for new items
5. Debug any errors in Make.com execution log

---

## 📸 Scenario 2: Food Photo Analysis

### Overview
**Trigger:** New file uploaded to Nutrition Log board
**Actions:** Download photo → Analyze with AI → Update item with macros
**Frequency:** Instant (webhook)
**Operations per run:** ~5-7

### Visual Flow

```
[Webhook: monday.com File Upload]
        ↓
[monday.com: Get Item Details]
        ↓
[HTTP: Download Photo from URL]
        ↓
[OpenAI: Analyze Image]
        ↓
[Tools: Parse JSON Response]
        ↓
[monday.com: Update Item Columns]
        ↓
[monday.com: Send Notification]
```

### Step-by-Step Setup

#### Module 1: monday.com Webhook Trigger
1. Create new scenario
2. Add module: "monday.com" → "Watch Board's Items"
3. Connection: Your monday connection
4. Board: "Nutrition Log"
5. Columns: Select "Photo" column
6. Trigger: "When column values change"
7. This creates a webhook that fires when photo is added

#### Module 2: Router (Check if Photo Exists)
1. Add module: "Flow Control" → "Router"
2. This splits the flow into two paths

**Path 1: Photo exists**
- Add filter: `{{1.Photo}}` exists (not empty)

**Path 2: No photo**
- Add filter: `{{1.Photo}}` is empty
- Add module: "Tools" → "Set variable"
- Variable: `skip` Value: `true`
- Stop execution

Continue on Path 1:

#### Module 3: HTTP Download Photo
1. Add module: "HTTP" → "Get a file"
2. URL: `{{1.Photo.url}}` (monday.com provides file URL)
3. This downloads the photo for analysis

#### Module 4: OpenAI Vision Analysis
1. Add module: "OpenAI" → "Create a Chat Completion"
2. Connection: Create OpenAI connection with your API key
3. Model: `gpt-4-vision-preview`
4. Messages:
   - Role: System
   - Content:
     ```
     You are a nutrition expert. Analyze food photos and estimate calories and macros.
     Return ONLY valid JSON in this exact format with no other text:
     {
       "foods": [
         {
           "name": "food name",
           "portion": "estimated portion size",
           "calories": number,
           "protein_g": number,
           "carbs_g": number,
           "fat_g": number,
           "fiber_g": number,
           "confidence": "high|medium|low"
         }
       ],
       "notes": "any relevant observations"
     }
     ```

   - Role: User
   - Content:
     ```
     Analyze this meal photo. Identify all foods and estimate nutritional values.

     Image: {{3.data}}

     Additional context from user: {{1.Notes}}
     ```

5. Max Tokens: 1000
6. Temperature: 0.3 (lower = more consistent)

#### Module 5: Parse JSON Response
1. Add module: "Tools" → "Parse JSON"
2. JSON string: `{{4.choices[1].message.content}}`
3. This converts AI response to usable data

#### Module 6: Iterator (Loop through foods)
1. Add module: "Flow Control" → "Iterator"
2. Array: `{{5.foods}}`
3. This handles multi-food photos

#### Module 7: Update monday.com Item
1. Add module: "monday.com" → "Update an Item"
2. Board: "Nutrition Log"
3. Item ID: `{{1.id}}`
4. Column Values:

   **Calories:**
   - Column: Calories
   - Value: `{{6.calories}}`

   **Protein (g):**
   - Column: Protein (g)
   - Value: `{{6.protein_g}}`

   **Carbs (g):**
   - Column: Carbs (g)
   - Value: `{{6.carbs_g}}`

   **Fat (g):**
   - Column: Fat (g)
   - Value: `{{6.fat_g}}`

   **Fiber (g):**
   - Column: Fiber (g)
   - Value: `{{6.fiber_g}}`

   **AI Confidence:**
   - Column: AI Confidence
   - Value: `{{6.confidence}}`

   **Source:**
   - Column: Source
   - Value: "Photo AI"

#### Module 8: Send Notification
1. Add module: "monday.com" → "Create an Update"
2. Board: "Nutrition Log"
3. Item ID: `{{1.id}}`
4. Body:
   ```
   📊 AI Analysis Complete!

   Detected: {{6.name}} ({{6.portion}})
   Calories: {{6.calories}}
   Protein: {{6.protein_g}}g | Carbs: {{6.carbs_g}}g | Fat: {{6.fat_g}}g

   Confidence: {{6.confidence}}

   Please review and adjust if needed. {{5.notes}}
   ```

### Save & Test

1. Save scenario: "Food Photo Analysis"
2. Turn on webhook
3. Test: Upload a photo to Nutrition Log board
4. Watch Make.com execution
5. Check monday.com item for updated values

---

## 📊 Scenario 3: Weekly Insights Report

### Overview
**Trigger:** Every Sunday at 8:00 PM
**Actions:** Aggregate week's data → Send to ChatGPT → Create insight item
**Frequency:** Weekly
**Operations per run:** ~25-30

### Visual Flow

```
[Schedule: Sunday 8 PM]
        ↓
[monday.com: Search Activity Items (This Week)]
        ↓
[Aggregator: Sum calories, steps, etc.]
        ↓
[monday.com: Search Nutrition Items (This Week)]
        ↓
[Aggregator: Sum macros]
        ↓
[Tools: Build Summary Object]
        ↓
[OpenAI: Generate Insights]
        ↓
[monday.com: Create Insights Item]
        ↓
[Email/Notification: Send to DXO & SL]
```

### Step-by-Step Setup

#### Module 1: Schedule Trigger
1. Create new scenario
2. Add module: "Scheduling" → "Every day"
3. Settings:
   - Day: Sunday
   - Time: 20:00
   - Time zone: Your timezone

#### Module 2: Set Date Range
1. Add module: "Tools" → "Set multiple variables"
2. Variables:
   - `week_start`: `{{formatDate(addDays(now; -7); "YYYY-MM-DD")}}`
   - `week_end`: `{{formatDate(now; "YYYY-MM-DD")}}`
   - `week_label`: `{{formatDate(addDays(now; -7); "MMM DD")}} - {{formatDate(now; "MMM DD")}}`

#### Module 3: Get Activity Data (DXO)
1. Add module: "monday.com" → "Search Items in Board"
2. Board: "Activity Log"
3. Filters:
   - Date is after `{{week_start}}`
   - Date is before `{{week_end}}`
   - Person contains "DXO"
4. Limit: 100

#### Module 4: Aggregate Activity Data (DXO)
1. Add module: "Tools" → "Numeric aggregator"
2. Source Module: Module 3
3. Aggregation function: Sum
4. Create multiple aggregators:
   - Sum of Calories Burned
   - Sum of Steps
   - Sum of Duration
   - Count of Activities

#### Module 5: Get Activity Data (SL)
1. Repeat Module 3 with Person = "SL"

#### Module 6: Aggregate Activity Data (SL)
1. Repeat Module 4 for SL's data

#### Module 7: Get Nutrition Data (DXO)
1. Add module: "monday.com" → "Search Items in Board"
2. Board: "Nutrition Log"
3. Same date filters, Person = DXO

#### Module 8: Aggregate Nutrition Data (DXO)
1. Add module: "Tools" → "Numeric aggregator"
2. Sum of: Calories, Protein, Carbs, Fat

#### Module 9: Get Nutrition Data (SL)
1. Repeat Module 7 for SL

#### Module 10: Aggregate Nutrition Data (SL)
1. Repeat Module 8 for SL

#### Module 11: Build Summary JSON
1. Add module: "Tools" → "Set variable"
2. Variable name: `weekly_summary`
3. Value (JSON format):
```json
{
  "week": "{{week_label}}",
  "dxo": {
    "activities": {
      "total_workouts": {{4.count}},
      "total_calories_burned": {{4.calories_sum}},
      "total_steps": {{4.steps_sum}},
      "total_minutes": {{4.duration_sum}}
    },
    "nutrition": {
      "total_calories_consumed": {{8.calories_sum}},
      "avg_daily_calories": {{8.calories_sum / 7}},
      "total_protein": {{8.protein_sum}},
      "avg_daily_protein": {{8.protein_sum / 7}},
      "total_carbs": {{8.carbs_sum}},
      "total_fat": {{8.fat_sum}}
    }
  },
  "sl": {
    "activities": {
      "total_workouts": {{6.count}},
      "total_calories_burned": {{6.calories_sum}},
      "total_steps": {{6.steps_sum}},
      "total_minutes": {{6.duration_sum}}
    },
    "nutrition": {
      "total_calories_consumed": {{10.calories_sum}},
      "avg_daily_calories": {{10.calories_sum / 7}},
      "total_protein": {{10.protein_sum}},
      "avg_daily_protein": {{10.protein_sum / 7}},
      "total_carbs": {{10.carbs_sum}},
      "total_fat": {{10.fat_sum}}
    }
  }
}
```

#### Module 12: OpenAI Generate Insights
1. Add module: "OpenAI" → "Create a Chat Completion"
2. Model: `gpt-4`
3. Messages:
   - Role: System
   - Content:
     ```
     You are a fitness and nutrition coach for a couple (DXO and SL).
     Analyze their weekly data and provide:
     1. Key achievements for each person
     2. Trends (improving, stable, declining)
     3. Specific recommendations for next week
     4. Encouraging observations

     Be specific, actionable, and supportive. Use their actual numbers.
     Format response in clear sections with headers.
     ```

   - Role: User
   - Content:
     ```
     Here's this week's data ({{week_label}}):

     {{11.weekly_summary}}

     Generate a comprehensive weekly insights report.
     ```

4. Max Tokens: 1500
5. Temperature: 0.7

#### Module 13: Create Insights Item (DXO)
1. Add module: "monday.com" → "Create an Item"
2. Board: "Goals & Insights"
3. Group: "Weekly Insights"
4. Item Name: `Weekly Report: {{week_label}} - DXO`
5. Column Values:
   - Type: "Weekly Insight"
   - Person: "DXO"
   - Start Date: `{{week_start}}`
   - Content: `{{12.choices[1].message.content}}`
   - Data Source: `{{11.weekly_summary}}`

#### Module 14: Create Insights Item (SL)
1. Repeat Module 13 with Person = "SL"

#### Module 15: Send Email Notification (Optional)
1. Add module: "Email" → "Send an Email"
2. To: your-email@example.com, sl-email@example.com
3. Subject: `🎯 SLDXO Weekly Fitness Report: {{week_label}}`
4. Content: `{{12.choices[1].message.content}}`

### Save & Activate

1. Save scenario: "Weekly Insights Report"
2. Turn on scenario
3. Test by clicking "Run once"
4. Wait for Sunday or change schedule for testing

---

## ✅ Quick Start Checklist

### Phase 1: Setup (Day 1)
- [ ] Create Make.com account
- [ ] Connect monday.com to Make.com
- [ ] Create all 4 monday.com boards
- [ ] Add DXO and SL as board members
- [ ] Configure board columns as specified

### Phase 2: Fitbit (Day 2-3)
- [ ] Register Fitbit Developer App
- [ ] Get Fitbit API credentials
- [ ] Build Scenario 1: Daily Fitbit Sync
- [ ] Test with one day of data
- [ ] Activate daily schedule

### Phase 3: Photo Analysis (Day 4-5)
- [ ] Get OpenAI API key
- [ ] Add credits to OpenAI account
- [ ] Build Scenario 2: Food Photo Analysis
- [ ] Test with sample food photo
- [ ] Activate webhook

### Phase 4: Insights (Day 6-7)
- [ ] Build Scenario 3: Weekly Insights
- [ ] Test with existing data
- [ ] Schedule for Sundays

### Phase 5: Usage (Ongoing)
- [ ] Daily: Upload food photos or manual entries
- [ ] Daily: Review Fitbit sync results
- [ ] Weekly: Review insights report
- [ ] Monthly: Adjust goals and targets

---

## 🎓 Make.com Learning Resources

**Recommended Learning Path:**
1. **Make Academy** (free) - make.com/en/academy
   - Complete "Make Fundamentals" course (2 hours)
   - Watch "HTTP Requests" tutorial (30 min)
   - Watch "Error Handling" tutorial (20 min)

2. **monday.com Integration Docs**
   - make.com/en/help/apps/project-management/monday

3. **Practice Scenarios:**
   - Simple: monday.com item → Send email
   - Medium: Form submission → Create monday item
   - Advanced: Your fitness scenarios!

**Support:**
- Make.com community forum
- Make.com live chat support
- monday.com community (for board questions)

---

## 💰 Cost Estimate

**Make.com:**
- Free tier: 1,000 operations/month
- Estimated usage:
  - Scenario 1 (Daily Fitbit): 20 ops × 30 days = 600 ops/month
  - Scenario 2 (Photo Analysis): 7 ops × 60 photos = 420 ops/month
  - Scenario 3 (Weekly Insights): 30 ops × 4 weeks = 120 ops/month
  - **Total: ~1,140 ops/month** → Need Core plan ($9/month)

**OpenAI:**
- GPT-4 Vision: $0.01-0.03 per image × 60 photos = $0.60-1.80
- GPT-4 Text: $0.03 per 1K tokens × 4 reports = $0.12
- **Total: ~$1-2/month**

**Grand Total: ~$10-11/month**

---

## 🚀 Next Steps

1. **Review this guide** and familiarize yourself with the structure
2. **Create your monday.com boards** (takes 30-60 minutes)
3. **Sign up for Make.com** and complete the first tutorial
4. **Start with Scenario 1** (Fitbit sync) as your learning project
5. **Reach out when you hit a blocker** - I can help troubleshoot!

---

## 📞 Support

If you get stuck:
1. Check Make.com execution log (shows exactly where it failed)
2. Review monday.com board structure (column names must match exactly)
3. Test API calls independently (use Postman or Make.com HTTP module)
4. Ask me for help with screenshots of the error!

---

**Good luck building your SLDXO Fitness Tracking System! 🎯💪**

*This guide will evolve as you build. Save it and update with your own notes and learnings.*
