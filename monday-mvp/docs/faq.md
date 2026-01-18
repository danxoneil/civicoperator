# Frequently Asked Questions (FAQ)
## Jenkins Creative Counseling Center - monday.com MVP

**Version:** 1.0
**Date:** January 18, 2026

---

## Table of Contents

1. [SimplePractice Integration](#simplepractice-integration)
2. [Session Tracking & Automation](#session-tracking--automation)
3. [Training & User Adoption](#training--user-adoption)
4. [Implementation & Timeline](#implementation--timeline)
5. [Cost & Budget](#cost--budget)
6. [Technical Questions](#technical-questions)
7. [Data & Security](#data--security)
8. [Change Management](#change-management)
9. [Support & Maintenance](#support--maintenance)
10. [ROI & Business Value](#roi--business-value)

---

## SimplePractice Integration

### Q: How does data get from SimplePractice to monday.com?

**A:** CSV export/import process:
1. You export reports from SimplePractice as CSV files
2. Upload CSV to monday.com boards
3. monday.com matches data to existing records (using Patient ID, Claim Number, etc.)
4. Takes 10-20 minutes per import

**Frequency:**
- Claims: Weekly (every Monday)
- Sessions: Bi-weekly
- Patients: Monthly or as-needed

See [SimplePractice Integration Guide](simplepractice-integration-guide.md) for complete details.

---

### Q: Can monday.com pull data automatically from SimplePractice?

**A:** Not with the MVP approach (CSV import).

**Future option:** API integration using Zapier or custom middleware
- Requires SimplePractice API access
- Additional cost ($100-200/month)
- Setup time (2-4 weeks)
- Recommended Phase 2 (after MVP validated)

**Why start with CSV?**
- Lower cost
- More control
- Proven reliability
- Easier troubleshooting
- No dependency on API changes

---

### Q: Does monday.com replace SimplePractice?

**A:** **No.** SimplePractice remains your system of record for:
- Clinical documentation
- Claims submission
- Payment processing
- HIPAA-compliant clinical data

monday.com is the **operational layer** for:
- Workflow management
- Task tracking
- Alerts and notifications
- Operational dashboards
- Non-clinical coordination

---

### Q: What if SimplePractice changes their export format?

**A:** We adjust the import mapping.
- Usually takes 15-30 minutes
- No data loss
- May require one-time re-import
- Covered under support agreement

---

## Session Tracking & Automation

### Q: Is it possible to auto-populate sessions remaining when a patient has a session?

**A:** Yes, with bi-weekly imports OR manual updates.

**How it works:**
1. **Authorized Sessions** (entered once manually from auth letter): 20
2. **Sessions Used** (updated via import or manually): 12
3. **Sessions Remaining** (auto-calculated formula): 8 (= 20 - 12)

**Update options:**
- **Bi-weekly import:** Export appointments from SimplePractice, import to monday.com (10 min every 2 weeks)
- **Manual update:** Billing staff updates "Sessions Used" column directly (15 min/week for ~150 assignments)

**Recommendation:** Start manual during pilot, move to imports after 30 days.

See: [SimplePractice Integration Guide - Session Tracking](simplepractice-integration-guide.md#session-tracking-automation)

---

### Q: Will I get alerts when sessions are running low?

**A:** Yes, automatically.

**Automation triggers when Sessions Remaining ≤ 2:**
- Notification sent to clinician
- Notification sent to billing staff
- Risk flag changes to "Auth Expiring"
- Message: "Only 2 sessions remain - request authorization extension"

**Also alerts when:**
- Authorization expiring in ≤14 days
- Gap in service (>21 days since last session)

---

### Q: Can I see all my active authorizations in one place?

**A:** Yes, on the Patient-Clinician Assignments board.

**Views available:**
- All Active Assignments (default)
- Authorization Alerts (expiring within 30 days)
- Sessions Running Low (≤5 remaining)
- By Clinician (grouped by provider)
- By Insurance Carrier (grouped by payer)

---

## Training & User Adoption

### Q: What if my staff isn't tech-savvy? Some of them are older and not comfortable with new systems.

**A:** We specialize in training users with varying technical comfort levels.

**Our approach:**
1. **Gradual rollout:** Start with 2-3 "champion" users, expand from there
2. **Role-specific training:** Only teach what each person needs to know
3. **Multiple formats:**
   - Onsite hands-on training (recommended)
   - Video recordings (watch on their own time)
   - Quick reference cards (one-page, laminated)
   - 1-on-1 coaching (for those who need extra help)
4. **Patient support:** We don't rush; we stay until everyone's comfortable
5. **Ongoing availability:** Call/email anytime during first 30 days

**What users say:**
- "If you can use Google Sheets, you can use monday.com"
- "It's easier than I thought"
- Interface is visual and intuitive

**Commitment from us:**
- No user left behind
- Extra training sessions at no charge if needed
- We work at your team's pace

---

### Q: How long does training take?

**A:** Depends on implementation scope.

**Pilot (Claims board only):**
- 2 hours for 2-3 billing staff
- Remote or onsite
- Hands-on practice with real data
- Follow-up Q&A session available

**Phase 1 (Claims + Intake):**
- 4 hours total
  - 2 hours: Billing team refresher
  - 2 hours: Intake coordinator training
- Can split across multiple days

**Full MVP (All 5 boards):**
- 2 days onsite (recommended)
- Day 1: Administrators, billing, intake coordinators
- Day 2: Clinical supervisors, clinicians, practice sessions
- All-hands overview (30 min)

**Ongoing learning:**
- monday.com has extensive video tutorials
- Our custom documentation for your specific setup
- Office hours during first month

---

### Q: What if someone forgets how to do something?

**A:** Multiple support resources:

**Immediate help:**
- Quick reference cards (at their desk)
- Video library (common tasks, 2-5 min each)
- Ask a colleague who's comfortable
- monday.com help center (searchable)

**Within 24 hours:**
- Email support (during implementation period)
- Scheduled office hours (weekly for first month)

**Custom documentation we provide:**
- Step-by-step guides with screenshots
- "Cookbook" format ("I need to... → Do this")
- Role-specific guides (only relevant info for each person)

---

### Q: Will clinicians need to use this? They're already overwhelmed.

**A:** Clinicians have **view-only** access to relevant information.

**What clinicians see:**
- "My Assignments" filtered view (only their patients)
- Sessions remaining for each patient
- Authorization expiration alerts
- Last session date

**What clinicians do NOT do:**
- Data entry (admin/billing handles)
- Managing board structure
- Complex workflows

**Time commitment:**
- 30-second daily check (optional)
- Respond to authorization alerts (rare, 1-2 min)
- 30-minute training (one-time)

**Mobile app available:**
- Quick check on phone
- Push notifications for urgent items
- Lightweight, simple interface

---

### Q: What if we have high turnover right now?

**A:** Common during organizational change. Strategies:

**During implementation:**
- Train "core team" first (stable, long-term staff)
- Document everything (new hires can learn from docs)
- Record all training sessions
- Simple onboarding checklist for new staff

**After go-live:**
- New hire training (1-2 hours, part of onboarding)
- Buddy system (new hire shadows experienced user)
- Lower risk than spreadsheets (structured system vs. tribal knowledge)

**Silver lining:**
- New staff learns monday.com from day 1 (no bad habits)
- System provides consistency during turnover
- Less "only Jane knows how to do this" risk

---

## Implementation & Timeline

### Q: How long does implementation take?

**A:** Depends on scope.

| Approach | Timeline | Breakdown |
|----------|----------|-----------|
| **Pilot** | 30 days | 1 week setup, 1 week training, 2 weeks validation |
| **Phase 1** | 60 days | 2 weeks per board, 2 weeks stabilization |
| **Full MVP** | 90 days | 4 weeks build, 2 weeks training, 6 weeks rollout |

See: [Phased Implementation Guide](phased-implementation-guide.md)

---

### Q: Can we go live faster if we're in a hurry?

**A:** Yes, but not recommended.

**Absolute minimum:**
- Pilot: 2-3 weeks (rush mode)
- Phase 1: 4-5 weeks
- Full MVP: 6-8 weeks

**Trade-offs:**
- Less testing time
- Higher risk of issues
- Compressed training (harder for less tech-savvy users)
- More stressful for team

**Our recommendation:** Don't rush. Better to do it right and build confidence.

---

### Q: Can we pause implementation if things get crazy?

**A:** Yes.

**Good pause points:**
- After pilot validation (before Phase 1)
- After Phase 1 stabilization (before Full MVP)
- End of any month (if month-to-month contract)

**During pause:**
- Existing boards continue working
- Support available if needed
- Resume when ready

**We understand:**
- Organizational changes happen
- Budget constraints shift
- Priorities change
- We're flexible

---

### Q: Do we have to shut down our current system during implementation?

**A:** **No.** Parallel run recommended.

**Typical approach:**
- Week 1-2: Build and test with sample data
- Week 3-4: Soft launch (use monday.com + keep existing spreadsheets)
- Week 5-6: Validate both systems match
- Week 7+: Sunset spreadsheets once confident

**Zero downtime.** Your operations never stop.

---

## Cost & Budget

### Q: What does this cost?

**A:** Two components: Software + Implementation

**Software (monday.com subscription):**

| Plan | Users | Monthly | Annual |
|------|-------|---------|--------|
| Pilot | 5 (minimum) | $80 | $960 |
| Phase 1 | 8 | $128 | $1,536 |
| Full MVP | 20 | $320 | $3,840 |

Includes: HIPAA BAA, private boards, unlimited automations, audit log, support

**Implementation Services:**
- Pilot: TBD (lower investment)
- Phase 1: TBD (moderate)
- Full MVP: TBD (per proposal)

Includes: Board design, automations, training, support, documentation

See: [Phased Implementation Guide - Investment sections](phased-implementation-guide.md)

---

### Q: Is there a long-term contract?

**A:** Depends on approach.

**Pilot & Phase 1:** Month-to-month
- Cancel anytime (30-day notice)
- Flexibility during organizational change
- Lower commitment

**Full MVP:** Annual contract (optional)
- ~20% savings vs. month-to-month
- Shows commitment = better support priority

**Implementation services:** Project-based (one-time)

---

### Q: What if we need to cancel?

**A:**

**Software:**
- 30-day notice to monday.com
- Export all data before cancellation
- No early termination fees (if month-to-month)

**Services:**
- Depends on contract terms
- Typically: Pay for work completed to-date
- We'll help with clean exit (data export, documentation)

**We prefer:** Open conversation if things aren't working, try to fix before canceling

---

### Q: Are there hidden costs?

**A:** No surprises. Transparent pricing.

**Included in software cost:**
- Unlimited boards
- Unlimited automations (within action quota)
- All features (dashboards, formulas, views, etc.)
- Mobile apps
- Standard support

**Included in implementation cost:**
- All boards in scope
- All automations configured
- Training (per agreement)
- Documentation
- 30-day support

**Potential add-ons (optional):**
- Additional training sessions
- Extended support (beyond 30 days)
- Custom API integrations (Phase 2)
- Zapier/middleware (if automating imports)

**We'll quote everything upfront.** No surprise bills.

---

### Q: What's the ROI? How do we justify the cost?

**A:** Measurable returns in multiple areas.

**Claims management:**
- Reduce AR >90 days by 30-40% = $$$ in recovered revenue
- Catch denials faster = higher appeal success rate
- Example: If you have $50K in 90+ day AR, 40% reduction = $20K recovered

**Intake efficiency:**
- Reduce referral-to-ready time by 30% = more patients served
- Fewer stalled intakes = less lost revenue
- Example: 10 more patients/month × $200/session × 10 sessions = $20K/month

**Staff productivity:**
- 20% time savings in admin tasks = capacity for growth OR reduced overtime
- Example: 1 FTE spends 10 hrs/week on claims follow-up → Save 2 hrs/week = $5K/year (at $50/hr)

**Risk reduction:**
- Zero expired credentials = avoid compliance issues
- No missed authorizations = avoid service interruptions
- Audit trail = malpractice/compliance defense

**Typical ROI:** 6-12 months (pilot even faster)

See: [ROI Framework](roi-framework.md) *(to be created)*

---

## Technical Questions

### Q: Is this HIPAA compliant?

**A:** Yes, with monday.com Enterprise plan.

**Requirements (all included):**
- ✅ Business Associate Agreement (BAA) signed
- ✅ Encryption at rest (AES-256)
- ✅ Encryption in transit (TLS 1.2+)
- ✅ US data centers only
- ✅ Audit logging (180 days)
- ✅ Access controls (role-based permissions)
- ✅ Two-factor authentication (required for all users)
- ✅ Session timeouts
- ✅ PHI minimization strategy

**What we do:**
- Private boards (not visible to unauthorized users)
- Column-level permissions (restrict sensitive data)
- Minimal PHI (no clinical notes, only operational metadata)
- Training on HIPAA best practices

**SimplePractice remains system of record** for clinical data.

---

### Q: What happens if monday.com goes down?

**A:** Rare, but we have contingency plans.

**monday.com uptime:**
- 99.9% SLA (Enterprise plan)
- ~43 minutes downtime/month maximum
- Typically much better in practice

**If outage occurs:**
- Continue operations in SimplePractice (unaffected)
- Revert to backup spreadsheet (you keep during first 30 days)
- Data automatically syncs when back online
- No data loss

**Critical operations:** Always have backup plan
- Intake forms: Adobe Sign still works
- Clinical sessions: SimplePractice unaffected
- Payments: SimplePractice unaffected

---

### Q: Can we access this from phones/tablets?

**A:** Yes, monday.com has mobile apps.

**Available on:**
- iOS (App Store)
- Android (Google Play)
- Web browser (mobile-responsive)

**Mobile features:**
- View boards (read-only or edit based on permissions)
- Update columns (status, dates, notes)
- Receive push notifications
- Add comments/updates
- Check dashboards

**Best for:**
- Clinicians checking assignments
- Managers reviewing dashboards
- Quick status updates on-the-go

**Not ideal for:**
- Heavy data entry (use desktop)
- Building boards (admin function, desktop only)
- Complex imports (desktop only)

---

### Q: What if we want to customize the boards later?

**A:** Fully customizable, anytime.

**Easy changes (you can do):**
- Add/remove columns
- Change status labels
- Create new views
- Adjust filters
- Update automations

**Moderate changes (we can help):**
- Add new connected boards
- Complex automations
- Formula columns
- Permission restructure

**System is designed to evolve** with your practice.

---

### Q: Can we export our data if we ever want to leave?

**A:** Yes, you own all data.

**Export options:**
- CSV (any board, anytime)
- Excel
- PDF (board views)
- API (programmatic export)

**Best practice:**
- Weekly backups (automated)
- Store in secure, encrypted location
- 7-year retention (compliance)

**If you cancel:**
- We'll help with final export
- Provide clean CSV files for all boards
- No data ransom, no restrictions

---

## Data & Security

### Q: Who can see patient names?

**A:** Controlled by permissions.

**Can see patient names:**
- Admins (full access)
- Intake coordinators (full access)
- Billing staff (view only)

**Cannot see patient names:**
- Clinicians (see only their assigned patients)
- Leadership (view aggregate dashboards, no PHI)
- Anyone not explicitly granted access

**Column-level permissions** restrict sensitive fields:
- Patient contact info (admin + intake only)
- Insurance details (admin + billing only)

---

### Q: Where is our data stored?

**A:** US data centers (monday.com Enterprise).

**Location:** AWS US-East (Virginia) or US-West (Oregon)
- HIPAA-compliant facilities
- SOC 2 Type II certified
- Redundant backups
- Disaster recovery

**Data residency guarantee:**
- Data never leaves US
- No international transfers
- Meets HIPAA requirements

---

### Q: What if someone leaves and we forget to remove their access?

**A:** Multi-layered security.

**Session timeouts:**
- 30 minutes of inactivity = auto-logout
- Forces re-authentication

**Regular access reviews:**
- Quarterly user audit (we recommend)
- monday.com shows "Last Active" date
- Easy to spot dormant accounts

**Offboarding process:**
- Remove from workspace immediately
- All access revoked instantly
- No lingering permissions

**Best practice:** Include monday.com access in standard IT offboarding checklist

---

## Change Management

### Q: Our team is going through a lot of changes right now. Is this the right time?

**A:** Depends on stability, but we can adapt.

**Good time to implement:**
- ✅ Want to create consistency during change
- ✅ Need to reduce reliance on specific people (tribal knowledge)
- ✅ Have 2-3 stable "champion" users to lead adoption
- ✅ View new system as part of new chapter

**Not ideal:**
- ❌ Mass turnover (>50% staff leaving in next 30 days)
- ❌ Financial crisis/uncertainty about survival
- ❌ Other major initiatives competing for attention (new EHR, office move, etc.)

**Our recommendation:**
- **Start with pilot** (low disruption, small user group)
- **Pause between phases** if things get chaotic
- **Use as stabilizing force** (structure during uncertainty)

**We've done this before.** Change is common in healthcare practices.

---

### Q: How do we get staff to actually use it?

**A:** Change management built into implementation.

**Strategies:**
1. **Identify champions** (1-2 enthusiastic early adopters)
2. **Demonstrate quick wins** (show immediate value)
3. **Make it easier than current system** (less work, not more)
4. **Leadership support** (owner uses and promotes it)
5. **Positive reinforcement** (celebrate successes)
6. **Address concerns** (listen to resistors, find solutions)

**What doesn't work:**
- ❌ Forcing without explanation
- ❌ "Figure it out yourself" approach
- ❌ Making it optional (creates two systems)

**Our role:**
- Training that builds confidence
- Quick wins in first week
- Responsive support when issues arise
- Help you communicate value to team

---

### Q: What if people just go back to the old spreadsheets?

**A:** Common concern. Prevention strategies:

**Make old system unavailable:**
- After validation period, archive Google Sheets (read-only)
- Don't delete (available for reference)
- But can't edit old system

**Make new system necessary:**
- Leadership reviews dashboards in monday.com (not sheets)
- Weekly meetings reference monday.com data
- Automated alerts only work in new system

**Address root cause:**
- If people revert, ask why
- Usually: confusion, missing feature, or fear
- Fix the issue (training, customization, reassurance)

**Our commitment:**
- We don't consider implementation done until team is using it
- Will work with you to address adoption challenges

---

## Support & Maintenance

### Q: What support do we get after go-live?

**A:** 30 days intensive support included, then options.

**First 30 days (included):**
- Email/phone support (response within 4 business hours)
- Weekly check-in calls
- Troubleshooting assistance
- Minor adjustments to automations/boards
- User questions answered

**After 30 days (options):**
- **monday.com standard support:** Included in subscription (platform issues)
- **Self-service:** Documentation + monday.com help center
- **As-needed consulting:** Hourly or project-based (for enhancements)
- **Monthly retainer:** Ongoing admin support (optional)

---

### Q: Who handles ongoing board administration?

**A:** You (with our training) or us (with retainer).

**DIY approach:**
- We train your admin during implementation
- You handle: adding users, creating views, minor automation tweaks
- We're available for questions (at consulting rates)

**Managed approach:**
- Monthly retainer for ongoing admin
- We handle: user management, optimization, monthly data reviews
- You focus on operations, we handle monday.com

**Most clients:** Start DIY, add retainer later if needed

---

### Q: What if we need changes 6 months from now?

**A:** We're here for the long term.

**Types of changes:**

**Minor (you can do):**
- Add columns
- Create views
- Adjust automations
- Change permissions

**Major (we can help):**
- Add new boards
- Complex integrations
- Dashboard enhancements
- Workflow redesigns

**Engagement options:**
- Hourly consulting
- Small project (fixed fee)
- Retainer (if ongoing needs)

**We want long-term relationship,** not one-and-done.

---

## ROI & Business Value

### Q: How quickly will we see results?

**A:** Quick wins + long-term gains.

**Week 1-2 (immediate):**
- ✅ Visual clarity (dashboard vs. spreadsheet)
- ✅ Reduced "where is that claim?" questions
- ✅ First automated alert catches something

**Month 1:**
- ✅ Billing staff spending less time searching for info
- ✅ Stalled intakes identified and resolved
- ✅ First denial caught and appealed faster

**Month 3:**
- ✅ Measurable reduction in AR aging
- ✅ Improved intake completion rate
- ✅ Team confidence in system

**Month 6:**
- ✅ Significant ROI realized
- ✅ System becomes "how we work"
- ✅ Ready for Phase 2 enhancements

---

### Q: What if our volumes grow? Does this scale?

**A:** Yes, designed to scale.

**monday.com limits (Enterprise):**
- Unlimited boards
- Unlimited items (thousands of patients/claims)
- Unlimited automations
- Performance tested to 100K+ items per board

**Your growth scenario:**
- Current: 12 clinicians, ~200 active patients
- Growth: 20 clinicians, ~350 active patients
- System handles easily (no rebuild needed)

**Scaling considerations:**
- More users = higher subscription cost (linear, predictable)
- May need dashboard optimization
- May want API integration (reduce manual import time)

**We help you scale** as practice grows.

---

### Q: Can this help us open new locations?

**A:** Yes, that's the point.

**Locations board tracks:**
- Each office, school, partner site
- Capacity utilization
- Agreement renewals
- Services offered per location
- Clinicians assigned to each

**As you add locations:**
- Replicate structure (takes minutes)
- Connected boards auto-update
- Dashboards show all locations
- No complex spreadsheet merging

**Growth enabler,** not barrier.

---

### Q: Will this work for other types of practices?

**A:** Yes, with customization.

**Designed for:**
- Mental health practices (like JCCC)
- Physical therapy
- Speech therapy
- ABA therapy
- Pediatric specialties
- Any outpatient practice with:
  - Patient intake workflow
  - Claims management needs
  - Clinician capacity tracking
  - Multiple locations

**Customization needed:**
- Terminology (patients vs. clients vs. students)
- Workflows (practice-specific processes)
- Payer relationships (insurance vs. school districts vs. grants)

**Core concept universal:** Structured operations = better outcomes

---

## Still Have Questions?

**Contact us:**
- Email: [your email]
- Phone: [your phone]
- Schedule call: [calendly link]

**Explore documentation:**
- [Implementation Guide](implementation-guide.md)
- [SimplePractice Integration Guide](simplepractice-integration-guide.md)
- [Phased Implementation Guide](phased-implementation-guide.md)
- [User Training Guide](user-training-guide.md)
- [Technical Specifications](technical-specifications.md)

**We're here to help.** No question is too small.
