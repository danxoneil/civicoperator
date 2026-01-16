# Jenkins Creative Counseling Center
## monday.com MVP Implementation Package

**Version:** 1.0
**Date:** January 16, 2026
**Status:** Ready for Implementation

---

## 📋 Executive Summary

This package contains a complete MVP (Minimum Viable Product) implementation design for Jenkins Creative Counseling Center's operational system built on monday.com. The system replaces fragmented Google Sheets and manual tracking with a structured operational framework that supports:

- **Patient Intake & Operations** - Structured referral-to-scheduling workflow
- **Clinician Workforce Management** - Credentials, capacity, and compliance tracking
- **Claims & Revenue Operations** - Post-billing follow-up and account aging visibility
- **Location & Partner Management** - Site tracking and agreement management
- **Patient-Clinician Assignments** - Operational metadata linking patients, clinicians, and services

---

## 🎯 Business Objectives

### Problems Solved
1. ✅ **Account Aging Blindness** → Real-time claims aging dashboard with automated alerts
2. ✅ **Scattered Intake Tracking** → Centralized intake workflow with SLA monitoring
3. ✅ **Manual Credential Tracking** → Automated license expiration alerts
4. ✅ **No Capacity Visibility** → Live clinician caseload and availability tracking
5. ✅ **Reactive Revenue Management** → Proactive denial and aging-based follow-up

### Key Outcomes
- **Reduce intake time** from referral to scheduling by 30%
- **Eliminate expired credentials** through automated 60-day alerts
- **Decrease AR >90 days** by 40% through systematic follow-up
- **Improve clinician utilization** with capacity-based assignment routing
- **Provide leadership visibility** through executive dashboards

---

## 📦 Package Contents

```
monday-mvp/
├── README.md (this file)
├── boards/
│   ├── 01-patients-intake-board.md
│   ├── 02-clinicians-board.md
│   ├── 03-claims-tracking-board.md
│   ├── 04-locations-board.md
│   └── 05-patient-clinician-assignments-board.md
├── csvs/
│   ├── 01-patients-intake.csv (25 sample patients)
│   ├── 02-clinicians.csv (12 sample clinicians)
│   ├── 03-claims-tracking.csv (40 sample claims)
│   ├── 04-locations.csv (8 sample locations)
│   └── 05-patient-clinician-assignments.csv (28 sample assignments)
├── automations/
│   └── automations-spec.md (18 automations + connected boards)
└── docs/
    ├── implementation-guide.md
    ├── user-training-guide.md
    └── technical-specifications.md
```

---

## 🏗️ System Architecture

### Core Boards (5)
1. **Patients & Intake** - 25 sample records across intake lifecycle
2. **Clinicians** - 12 sample clinicians with varied roles and credentials
3. **Claims Tracking** - 40 sample claims spanning all aging categories
4. **Locations** - 8 sample locations (offices, schools, partners)
5. **Patient-Clinician Assignments** - 28 sample active assignments

### Automations (18)
- **5 automations** for Patients & Intake (SLA alerts, status progression)
- **4 automations** for Clinicians (credential alerts, capacity management)
- **4 automations** for Claims (aging alerts, denial management)
- **2 automations** for Locations (agreement renewals, capacity alerts)
- **3 automations** for Assignments (auth expirations, service gaps)

### Connected Boards (6 integrations)
- Patients ↔ Assignments (bidirectional)
- Clinicians ↔ Assignments (bidirectional)
- Locations ↔ Assignments (bidirectional)
- Claims → Patients (lookup)
- Claims → Clinicians (lookup)
- Clinicians → Clinicians (supervision hierarchy)

---

## 🚀 Quick Start

### Prerequisites
- **monday.com Account:** Enterprise plan (for HIPAA compliance)
- **Permissions:** Board creator access
- **Time Required:** 4-6 hours for full setup
- **Team Roles Identified:** Intake coordinators, billing staff, board owner

### Implementation Steps (Summary)

1. **Create Workspace** (15 min)
   - Create new workspace: "Jenkins Operations"
   - Set workspace permissions (private)

2. **Build Boards** (2 hours)
   - Create 5 boards using specifications in `/boards/` directory
   - Configure columns, groups, and formulas
   - Set up board permissions

3. **Import Sample Data** (30 min)
   - Import CSVs from `/csvs/` directory
   - Verify data mapping
   - Test connected board relationships

4. **Configure Automations** (1.5 hours)
   - Implement 18 automations from `/automations/automations-spec.md`
   - Test triggers and notifications
   - Adjust thresholds as needed

5. **Set Up Connections** (1 hour)
   - Create 6 connected board relationships
   - Configure mirror columns
   - Test bidirectional updates

6. **User Training** (2-4 hours)
   - Review `/docs/user-training-guide.md`
   - Conduct role-based training sessions
   - Provide quick reference guides

📖 **Detailed Instructions:** See `/docs/implementation-guide.md`

---

## 👥 User Roles & Permissions

### Board Owner / Administrator
- Full access to all boards
- Configure automations and integrations
- Manage user permissions
- Export data and run reports

### Intake Coordinators
- Full access to Patients & Intake board
- View access to Locations board
- View access to Clinicians board (for assignment planning)

### Billing Staff
- Full access to Claims Tracking board
- View access to Patients board (for claim reconciliation)
- View access to Clinicians board (for provider verification)

### Clinicians
- View access to Assignments board (filtered to own assignments)
- Limited view of Patients board (own patients only)
- No access to Claims board

### Leadership / Owner
- View-only access to all boards
- Access to executive dashboards
- Receive escalation notifications

---

## 📊 Sample Data Overview

### Patients & Intake (25 records)
- **5** Ready for Scheduling
- **8** Forms Sent (in progress)
- **6** Recently Contacted
- **3** New Referrals
- **2** Stalled Cases (>7 days)
- **1** Already Entered in SimplePractice

**Distribution:**
- Referral sources: School (9), Self (6), Insurance (4), Provider (3), County (3)
- Insurance: Aetna (6), BCBS (6), UHC (5), Cigna (4), Medicaid (3), Self-Pay (1)
- Locations: Main Office (7), Schools (8), Westside Clinic (5), Other (5)

### Clinicians (12 records)
- **9** Active employees
- **2** Contractors
- **1** Intern (onboarding)
- License types: LCSW (4), LMFT (4), LPC (3), Provisional (2), Intern (1)
- Total capacity: 340 weekly sessions
- Current utilization: 257 sessions (76%)
- **1** clinician with expiring background check

### Claims (40 records)
- **$6,010** in paid claims (10 records)
- **$1,770** in denied claims needing action (7 records)
- **$3,675** in claims 90+ days (8 records - HIGH PRIORITY)
- **$2,910** in claims 60-90 days (6 records)
- **$3,360** in claims 30-60 days (9 records)
- Average claim value: $152
- Total AR tracked: $11,715

**Denial Reasons:**
- Authorization issues (3)
- Eligibility problems (2)
- Timely filing (2)
- Coding errors (1)

### Locations (8 records)
- **2** Primary offices (85 total capacity)
- **3** School sites (63 total capacity)
- **2** Partner sites (25 total capacity)
- **1** County program site (12 total capacity)
- Overall utilization: 70% (130 of 185 capacity)

### Assignments (28 records)
- **25** Active assignments
- **2** On hold (seasonal/break)
- **1** Pending start
- **4** assignments with authorization expiring <30 days
- **2** assignments with service gaps (>21 days)

---

## 🔐 HIPAA Compliance Considerations

### PHI Minimization Strategy
- **Patient Names:** Limited to authorized users only
- **Clinical Notes:** NOT stored in monday.com (SimplePractice only)
- **Insurance Details:** Stored in controlled columns with restricted access
- **Claim Details:** Aggregated data only; no detailed medical information

### Security Measures
1. **Board-level permissions** - Private boards with explicit user access
2. **Column-level permissions** - Sensitive columns restricted to admin roles
3. **Audit logging** - Enterprise plan activity log enabled
4. **BAA Required** - Business Associate Agreement with monday.com
5. **Two-factor authentication** - Enforced for all users
6. **Session timeouts** - 30-minute idle timeout configured

### Data Backup
- **monday.com:** Daily automated backups (platform level)
- **Local Exports:** Weekly CSV exports stored in encrypted location
- **SimplePractice:** Remains system of record for all clinical data

---

## 🎓 Training & Support

### Training Materials Included
1. **Implementation Guide** - Technical setup instructions
2. **User Training Guide** - Role-based user instructions
3. **Quick Reference Cards** - One-page guides per board
4. **Video Walkthrough Scripts** - Suggested training video content

### Recommended Training Schedule
- **Week 1:** Administrative team (board owners, billing)
- **Week 2:** Intake coordinators and front desk
- **Week 3:** Clinical supervisors
- **Week 4:** All clinicians (view-only access)

### Support Resources
- monday.com Help Center: https://support.monday.com
- HIPAA Compliance Guide: https://monday.com/hipaa
- Community Forum: https://community.monday.com

---

## 📈 Success Metrics

### Track These KPIs (Monthly)
1. **Intake Efficiency**
   - Average days from referral to ready for scheduling (Target: <7 days)
   - % of intakes stalled >7 days (Target: <10%)
   - Forms completion rate (Target: >90%)

2. **Revenue Cycle**
   - AR >90 days as % of total AR (Target: <15%)
   - Denial rate (Target: <5%)
   - Average days to payment (Target: <45 days)

3. **Workforce Utilization**
   - Clinician capacity utilization (Target: 75-85%)
   - Expired credentials (Target: 0)
   - Supervisor ratio (Target: 1:3-5)

4. **Operational Health**
   - Expiring authorizations caught early (Target: >95%)
   - Service gaps identified (Target: 100%)
   - Location capacity utilization (Target: 70-80%)

---

## 🔄 Future Enhancements (Post-MVP)

### Phase 2 (3-6 months)
- **Dashboard Development** - Executive, intake, claims, and capacity dashboards
- **SimplePractice API Integration** - Automated data sync (if feasible)
- **Expanded Reporting** - Custom views and reports per role
- **Mobile App Optimization** - Clinician mobile access for assignments

### Phase 3 (6-12 months)
- **Advanced Automations** - Predictive alerts, smart routing
- **Billing Workflow** - Pre-billing claim review and scrubbing
- **Patient Communication Log** - Track outreach attempts and responses
- **Quality Metrics** - Outcome tracking and satisfaction surveys

---

## ❓ FAQ

**Q: Can we modify the boards after import?**
A: Yes, boards are fully customizable. Start with MVP structure and iterate based on user feedback.

**Q: What if we don't have monday.com Enterprise?**
A: Enterprise is required for HIPAA compliance (BAA). Pro plan can be used for testing but not for PHI.

**Q: How do we handle SimplePractice integration?**
A: MVP uses manual CSV import/export. API integration is a Phase 2 enhancement.

**Q: Can clinicians access patient data?**
A: Only through Assignments board with filtered views showing their patients only. No direct access to Intake board.

**Q: What happens to our Google Sheets?**
A: Keep as backup during transition (30-60 days), then archive. Do not delete until system is validated.

**Q: How long until we see ROI?**
A: Expect measurable improvements within 60-90 days:
- Reduced intake time (30 days)
- Improved AR aging (60 days)
- Better capacity utilization (90 days)

---

## 📞 Implementation Support

For questions during implementation:

1. **Review Documentation:** Check `/docs/` directory first
2. **monday.com Support:** Submit ticket for platform-specific issues
3. **Process Questions:** Document and discuss with team leads
4. **Custom Requirements:** Track as potential Phase 2 enhancements

---

## 📝 Change Log

**v1.0 - January 16, 2026**
- Initial MVP package created
- 5 boards designed with sample data
- 18 automations specified
- 6 connected board integrations defined
- Complete documentation suite included

---

## ✅ Next Steps

1. ✅ Review this README completely
2. ⬜ Review board specifications in `/boards/` directory
3. ⬜ Read implementation guide in `/docs/implementation-guide.md`
4. ⬜ Schedule kickoff meeting with implementation team
5. ⬜ Procure monday.com Enterprise subscription with BAA
6. ⬜ Assign board owner and user roles
7. ⬜ Begin implementation following guide
8. ⬜ Schedule user training sessions
9. ⬜ Plan go-live date and communication strategy

---

**Ready to transform your operations?** Start with `/docs/implementation-guide.md` for detailed setup instructions.
