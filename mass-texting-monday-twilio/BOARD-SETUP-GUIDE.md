# monday.com Board Setup Guide for Mass Texting

This guide will help you set up a monday.com board for managing contacts and sending mass text messages via Twilio.

## Prerequisites

- A monday.com account (Free or paid plan)
- Access to create new boards in your workspace

## Step 1: Create a New Board

1. Log in to your monday.com workspace
2. Click the **"+"** button to create a new board
3. Choose **"Start from scratch"** or **"Blank board"**
4. Name your board (e.g., "SMS Contact List" or "Text Message Campaigns")
5. Select a workspace where you want the board to live

## Step 2: Import the Template

### Option A: Import from CSV (Recommended)

1. In your new board, click the **menu icon** (three dots) in the top right
2. Select **"Import data"** → **"From a CSV file"**
3. Upload the `monday-board-template.csv` file from this directory
4. Map the columns:
   - **Name** → Item Name
   - **Phone** → Phone column
   - **Opt In** → Checkbox or Status column
   - **Status** → Status column
   - **First Name** → Text column
   - **Last Name** → Text column
   - **Organization** → Text column
   - **Tags** → Tags column
   - **Notes** → Long Text column
5. Click **Import** to create the board with sample data

### Option B: Manual Setup

If you prefer to create columns manually:

1. Click **"+ Add Column"** for each of these columns:

| Column Name | Column Type | Required | Notes |
|-------------|-------------|----------|-------|
| **Name** | Item Name | Yes | Person or organization name (default column) |
| **Phone** | Phone | Yes | Phone number for SMS (use column ID: `phone`) |
| **Opt In** | Checkbox | Yes | Has the person opted in to receive texts? (use column ID: `opt_in`) |
| **Status** | Status Label | Yes | Message delivery status (use column ID: `status`) |
| **First Name** | Text | No | For message personalization |
| **Last Name** | Text | No | For message personalization |
| **Organization** | Text | No | Contact's organization |
| **Tags** | Tags | No | Categorize contacts (vip, donor, volunteer, etc.) |
| **Notes** | Long Text | No | Additional information |

## Step 3: Configure Status Labels

For the **Status** column, configure these labels:

1. Click on the Status column header
2. Add/edit labels:
   - **Pending** (Gray) - Default for new contacts
   - **Sent** (Green) - Message successfully sent
   - **Failed** (Red) - Message delivery failed
   - **Skipped** (Yellow) - Not opted in or invalid phone

## Step 4: Add Sample Contacts

Delete the imported sample data and add your real contacts:

1. Click **"+ New Item"** to add contacts one by one
2. **OR** import your existing contact list:
   - Export from your CRM/database as CSV
   - Use **"Import data"** to bulk upload
3. Make sure each contact has:
   - ✅ Valid phone number
   - ✅ Opt-in checkbox marked (if they consented)

## Step 5: Get Your Board ID

You'll need the Board ID to configure the mass texting script:

1. Open your board in monday.com
2. Look at the URL in your browser:
   ```
   https://your-org.monday.com/boards/1234567890
                                      ^^^^^^^^^^
                                      This is your Board ID
   ```
3. Copy the numeric Board ID (e.g., `1234567890`)
4. Save this for the `.env` configuration file

## Step 6: Get Column IDs

To get the exact column IDs for configuration:

### Using the API Playground (Recommended)

1. Go to: https://your-org.monday.com/developers/v2/try-it-yourself
2. Run this query (replace `YOUR_BOARD_ID` with your actual board ID):

```graphql
query {
  boards(ids: YOUR_BOARD_ID) {
    columns {
      id
      title
      type
    }
  }
}
```

3. Copy the `id` values for:
   - Phone column (usually `phone` or `phone4`)
   - Opt In column (usually `checkbox` or `opt_in`)
   - Status column (usually `status` or `status4`)

### Manual Method

1. In your board, click on a column header
2. Select **"Edit column"**
3. The column ID is shown in the settings panel
4. Note: Some columns auto-generate IDs like `phone4`, `text`, `status0`, etc.

## Step 7: Board Permissions

Ensure the API has access to your board:

1. Click the **person icon** in the top right of your board
2. Under **"Sharing & Permissions"**, verify your API user/integration has access
3. For API access, the board should be **visible** to your workspace

## Step 8: Customize for Your Use Case

### Message Personalization Columns

Add columns for any data you want to include in your messages:

- `{name}` - Person's full name (Item Name)
- `{first_name}` - First name column
- `{organization}` - Organization column
- `{custom_field}` - Any custom column ID

Example template:
```
Hi {first_name}! This is a message from {organization}. Thanks for your support!
```

### Filtering & Views

Create board views for different campaigns:

1. Click **"+ New View"** (top right)
2. Add filters:
   - **Tags contains "donor"** - Only donors
   - **Opt In is checked** - Only opted-in contacts
   - **Status is "Pending"** - Unsent messages
3. Save the view with a descriptive name

## Step 9: Opt-In Compliance

⚠️ **IMPORTANT: Comply with TCPA and SMS Regulations**

Before sending any messages:

1. **Get Consent**: Only text people who have explicitly opted in
2. **Mark Opt-In**: Check the "Opt In" checkbox for consenting contacts
3. **Provide Opt-Out**: Include "Reply STOP to unsubscribe" in messages
4. **Keep Records**: Use the Notes column to document consent

## Column ID Reference

Here are the typical column IDs you'll need for `.env` configuration:

```bash
MONDAY_PHONE_COLUMN_ID=phone        # Or phone4, phone7, etc.
MONDAY_STATUS_COLUMN_ID=status      # Or status0, status4, etc.
MONDAY_OPT_IN_COLUMN_ID=opt_in      # Or checkbox, checkbox0, etc.
```

Use the API Playground method above to get your exact column IDs.

## Next Steps

Once your board is set up:

1. Configure your `.env` file with the Board ID and Column IDs
2. Test with `DRY_RUN=true` first
3. Review the campaign results
4. Set `DRY_RUN=false` to send real messages

## Tips & Best Practices

✅ **DO:**
- Start with a small test group (5-10 contacts)
- Always use dry-run mode first
- Double-check phone numbers are valid
- Keep opt-in status up to date
- Review messages for typos before sending

❌ **DON'T:**
- Text people who haven't opted in
- Send too frequently (respect rate limits)
- Include sensitive information in SMS
- Forget to include opt-out instructions
- Send without testing first

## Troubleshooting

### Phone Numbers Not Recognized
- Ensure format includes country code: `+1-555-555-5555`
- The script auto-formats US numbers, but international numbers need `+`

### Can't Find Column IDs
- Use the API Playground method (Step 6)
- Column IDs are case-sensitive

### Board Not Found
- Verify Board ID in URL
- Check API key has board access
- Ensure board isn't archived

## Support

For issues with:
- **monday.com**: Visit https://support.monday.com
- **This script**: Check the main README.md or open an issue
- **Twilio**: Visit https://support.twilio.com

---

**Ready to send?** Return to the main [README.md](README.md) for script setup and usage instructions.
