# Phased Implementation Guide
## Jenkins Creative Counseling Center - monday.com MVP

**Version:** 1.0
**Date:** January 18, 2026

---

## Overview

This guide provides three implementation approaches, allowing you to start small and expand as budget, capacity, and confidence allow.

**All approaches include:**
- HIPAA-compliant monday.com Enterprise setup
- Board design and configuration
- Sample data for testing
- User training (onsite or remote)
- 30-day post-launch support
- Complete documentation

---

## Three Implementation Paths

| Approach | Boards | Users | Timeline | Investment | Best For |
|----------|--------|-------|----------|------------|----------|
| **Pilot** | 1 board | 2-3 users | 30 days | Lower | Proving concept, tight budget, organizational change |
| **Phased** | 2 boards | 5-8 users | 60 days | Moderate | Building confidence, growing adoption |
| **Full MVP** | 5 boards | All staff | 90 days | Full | Ready to transform operations |

---

## Phase 0: Pilot Implementation

### Purpose
Prove value with lowest risk and investment. Ideal for practices experiencing organizational change or budget constraints.

### What You Get

**1 Board: Claims & Revenue Operations**

Why start here?
- ✅ Immediate ROI (reduce AR aging, catch denials faster)
- ✅ Small user group (2-3 billing staff = easier training)
- ✅ Measurable results (claims aging %, denial response time)
- ✅ Lower change management burden (doesn't affect clinical staff)

**Board Features:**
- Claim tracking with auto-aging buckets
- Denial alerts and follow-up workflow
- High-dollar claim prioritization
- Payer communication log
- Basic aging dashboard

**Automations (5):**
1. Auto-assign aging category (30/60/90 days)
2. Denial notification to billing team
3. High-dollar at-risk alert (>$500 + >90 days)
4. Payment received → archive
5. Follow-up date reminder

**Connected Boards:** None (standalone for pilot)

---

### Pilot Timeline

**Week 1: Setup**
- Day 1-2: monday.com Enterprise account setup, HIPAA BAA
- Day 3-4: Build Claims board structure
- Day 5: Import sample data for testing

**Week 2: Configuration & Training**
- Day 1-2: Configure 5 critical automations
- Day 3: Test with real data (last 30 days of claims)
- Day 4: Billing team training (remote, 2 hours)
- Day 5: Soft launch (parallel with existing spreadsheets)

**Week 3-4: Validation**
- Run parallel with Google Sheets
- Daily check-ins with billing team
- Address issues immediately
- Collect feedback

**Week 5: Evaluation**
- Review metrics (before/after comparison)
- Decide: Continue to Phase 1 OR end pilot
- If continuing: Plan Phase 1 expansion

---

### Pilot Deliverables

**Technical:**
- Claims Tracking board (fully configured)
- 5 automations active and tested
- CSV import template for SimplePractice
- Permission structure (private board, billing team only)

**Training:**
- 2-hour remote training for billing team
- Quick reference guide (one-pager)
- Video recordings of key workflows
- Q&A support during pilot period

**Documentation:**
- Claims board specification
- SimplePractice import procedure
- Automation documentation
- Troubleshooting guide

---

### Pilot Success Metrics

Measure after 30 days:

**Quantitative:**
- AR >90 days as % of total (target: 10-15% reduction)
- Average denial response time (target: <7 days)
- Claims follow-up completion rate (target: >90%)
- Time spent on claims management (target: 20% reduction)

**Qualitative:**
- Billing team satisfaction (survey)
- Ease of use (1-10 rating)
- Confidence in data accuracy
- Desire to expand to other boards

**Go/No-Go Decision:**
- ✅ **Expand to Phase 1:** If 3+ metrics show improvement
- ⏸️ **Adjust & Continue:** If 2 metrics show improvement, refine workflows
- ❌ **Conclude Pilot:** If <2 metrics show improvement (refund arrangement TBD)

---

### Pilot Investment

**monday.com Subscription:**
- Enterprise plan: 5 users minimum
- $16/user/month × 5 users = $80/month
- Annual: ~$960/year
- Includes: HIPAA BAA, private boards, automations, audit log

**Implementation Services:**
- Board design & build: Included
- Automation configuration: Included
- Data import (sample + initial real data): Included
- Remote training (2 hours): Included
- 30-day support: Included
- Documentation: Included

**Total Pilot Investment:**
- Software: $80/month (month-to-month, cancel anytime)
- Services: TBD based on scope discussion
- **No long-term commitment required**

**Optional Add-Ons:**
- Onsite training day: Available if needed
- Extended support (60 days): Available
- Additional training sessions: Available

---

## Phase 1: Phased Implementation

### Purpose
Build on pilot success. Add intake workflow to complement claims management. Create connected view of patient journey.

### What You Get

**2 Boards: Claims + Intake**

**Board 1: Claims & Revenue Operations** (from pilot)
- All pilot features retained
- Enhanced with patient connections

**Board 2: Patients & Intake**
- Structured referral-to-scheduling workflow
- Intake SLA monitoring (stalled case alerts)
- Insurance verification tracking
- Forms completion status
- SimplePractice entry confirmation
- Connected to Claims board for full patient financial view

**Automations (10 total):**
- 5 from pilot (claims)
- 5 new (intake):
  - Intake SLA alert (>7 days in stage)
  - Forms complete → auto-advance status
  - Insurance denied → priority escalation
  - SimplePractice entry → archive
  - Urgent patient notification

**Connected Boards:**
- Claims → Patients (link claims to patient records)
- Patients → Locations (optional, if ready)

---

### Phase 1 Timeline

**Week 1-2: Build on Pilot**
- Validate pilot success metrics
- Refine Claims board based on 30-day learning
- Plan Patients & Intake board structure

**Week 3-4: Intake Board Development**
- Build Patients & Intake board
- Import current intake pipeline (Google Sheets → monday.com)
- Configure intake automations
- Connect to Claims board

**Week 5: Training & Launch**
- Intake coordinator training (2 hours, remote or onsite)
- Billing team refresher (1 hour)
- Soft launch intake workflow
- Parallel run with existing sheets (2 weeks)

**Week 6-8: Stabilization**
- Daily check-ins with intake team
- Bi-weekly check-ins with billing team
- Address issues, optimize workflows
- Build confidence

---

### Phase 1 Deliverables

**Technical:**
- 2 boards (Claims + Patients & Intake)
- 10 automations configured
- Connected board integration (Claims ↔ Patients)
- Enhanced permissions (intake team + billing team)

**Training:**
- Intake coordinator training (2-3 hours)
- Billing team refresher (1 hour)
- Leadership overview (optional, 30 min)
- Quick reference guides for both boards

**Documentation:**
- Complete board specifications (both boards)
- SimplePractice integration guide
- Import procedures for both boards
- User training guide (role-specific sections)

---

### Phase 1 Success Metrics

**Claims Metrics (ongoing from pilot):**
- Continued improvement in AR aging
- Denial response time holding <7 days
- User adoption >90%

**New Intake Metrics:**
- Average referral-to-ready time (baseline → target)
- % of intakes stalled >7 days (target: <10%)
- Forms completion rate (target: >90%)
- Intake coordinator time savings (target: 20%)

**Go/No-Go for Phase 2:**
- If both boards showing value → Expand to Full MVP
- If only one board working → Refine and hold
- If struggling → Revert to pilot scope, regroup

---

### Phase 1 Investment

**monday.com Subscription:**
- 8 users (3 billing + 2 intake + 1 admin + 2 leadership view-only)
- $16/user/month × 8 = $128/month
- Or annual: ~$1,536/year

**Implementation Services:**
- Intake board design & build: Included
- 5 additional automations: Included
- Connected board setup: Included
- Training (4 hours total): Included
- 30-day post-launch support: Included
- Enhanced documentation: Included

**Total Phase 1 Investment:**
- Software: $128/month
- Services: TBD based on scope discussion
- Builds on pilot (pilot costs credited if applicable)

---

## Phase 2: Full MVP Implementation

### Purpose
Complete operational transformation. All 5 boards integrated for end-to-end visibility.

### What You Get

**All 5 Boards:**
1. Patients & Intake
2. Clinicians
3. Claims & Revenue Operations
4. Locations & Partners
5. Patient-Clinician Assignments

**Complete Feature Set:**
- 18 total automations
- 6 connected board integrations
- Comprehensive dashboards
- Role-based access for all staff types
- Mobile access for clinicians

**Full Scope:**
- Everything in phased approach PLUS:
- Clinician credential tracking
- Capacity management
- Location utilization tracking
- Assignment metadata (non-clinical)
- Executive dashboards

---

### Full MVP Timeline

**Week 1-2: Foundation**
- Review pilot and Phase 1 learnings
- Finalize requirements for remaining 3 boards
- Build Clinicians board
- Build Locations board
- Build Assignments board

**Week 3-4: Integration**
- Connect all 5 boards
- Configure remaining 8 automations
- Import all data (clinicians, locations, assignments)
- Set up executive dashboards

**Week 5-6: Training**
- Administrator training (4 hours, onsite)
- Intake coordinator training (2 hours)
- Billing staff training (2 hours)
- Clinical supervisor training (2 hours)
- Clinician overview (1 hour)
- All-hands overview (30 min)

**Week 7-12: Rollout & Stabilization**
- Week 7: Go-live (all boards)
- Week 8-10: Intensive support (daily check-ins)
- Week 11-12: Transition to steady-state
- Week 12: Final evaluation and optimization

---

### Full MVP Deliverables

**Technical:**
- 5 production boards (fully configured)
- 18 automations (all active and tested)
- 6 connected board integrations
- Comprehensive permission structure
- Executive dashboards
- Mobile app configuration

**Training:**
- 2 days onsite training (all user groups)
- Role-specific training materials
- Video library (common tasks)
- Quick reference cards (laminated)
- Admin certification

**Documentation:**
- Complete Implementation Guide
- Technical Specifications
- User Training Guide
- SimplePractice Integration Guide
- FAQ Document
- Troubleshooting Guide
- All board specifications

---

### Full MVP Success Metrics

**Comprehensive KPIs:**

**Intake:**
- 30% reduction in referral-to-ready time
- <10% intakes stalled >7 days
- >90% forms completion rate

**Claims:**
- 40% reduction in AR >90 days
- <5% denial rate (or 20% improvement from baseline)
- <45 days average to payment

**Workforce:**
- 0 expired credentials
- 75-85% clinician utilization
- <10% variance in caseload balance

**System:**
- >90% user adoption (daily active users)
- >95% data quality score
- >98% automation success rate

---

### Full MVP Investment

**monday.com Subscription:**
- 20 users (all staff)
- $16/user/month × 20 = $320/month
- Annual: ~$3,840/year

**Implementation Services:**
- Complete system design: Included
- All 5 boards built and configured: Included
- 18 automations configured: Included
- 6 connected board integrations: Included
- Data migration (all boards): Included
- 2 days onsite training: Included
- 30-day intensive support: Included
- Complete documentation package: Included

**Total Full MVP Investment:**
- Software: $320/month (or $3,840/year)
- Services: Per original proposal
- Optionally builds on pilot/Phase 1 (costs credited)

---

## Comparison Matrix

| Feature | Pilot | Phase 1 | Full MVP |
|---------|-------|---------|----------|
| **Boards** | 1 (Claims) | 2 (Claims + Intake) | 5 (All) |
| **Users** | 2-3 | 5-8 | 15-20 |
| **Automations** | 5 | 10 | 18 |
| **Connected Boards** | 0 | 1 connection | 6 connections |
| **Training** | 2 hr remote | 4 hr remote/onsite | 2 days onsite |
| **Timeline** | 30 days | 60 days | 90 days |
| **Support** | 30 days | 30 days | 30 days intensive |
| **Documentation** | Basic | Enhanced | Complete |
| **Dashboards** | 1 simple | 2 boards | Executive suite |
| **Monthly Cost** | ~$80 | ~$128 | ~$320 |
| **Risk Level** | Lowest | Low | Moderate |
| **ROI Timeline** | 60-90 days | 90-120 days | 120-180 days |
| **Cancellation** | Month-to-month | Month-to-month | Annual commit |

---

## Choosing Your Path

### Choose **Pilot** if:
- ✅ Experiencing organizational change/turnover
- ✅ Budget constraints or uncertainty
- ✅ Need to prove value before larger commitment
- ✅ Want to start immediately with minimal disruption
- ✅ Billing/AR is your highest pain point
- ✅ Small team can test and validate

### Choose **Phase 1 (Phased)** if:
- ✅ Pilot proved value
- ✅ Ready to tackle intake workflow
- ✅ Have buy-in from intake + billing teams
- ✅ Budget available for modest expansion
- ✅ Want connected view of patient journey
- ✅ Comfortable with technology adoption

### Choose **Full MVP** if:
- ✅ Ready for complete operational transformation
- ✅ Have organizational buy-in (ownership + clinical leadership)
- ✅ Budget allocated for full implementation
- ✅ Staff stable and ready for change
- ✅ Committed to 90-day implementation timeline
- ✅ Want comprehensive dashboards and reporting

---

## Migration Path

You can **start small and expand** without losing work:

### Pilot → Phase 1:
- Claims board stays intact (no rebuild)
- Add Intake board
- Connect the two
- Billing team already trained (minimal refresher needed)
- **Additional investment:** Phase 1 increment only

### Phase 1 → Full MVP:
- Claims and Intake boards stay intact
- Add remaining 3 boards
- Connect all boards
- Existing users already comfortable
- **Additional investment:** Full MVP increment only

### Direct to Full MVP:
- Skip pilots, implement all at once
- Higher risk, but fastest to full value
- Requires strong change management
- **Investment:** Full MVP cost

---

## Recommended Approach for JCCC

Based on conversation context (organizational change, financial transition, interest but cautious):

### **Start with Pilot**

**Rationale:**
1. **Lowest risk:** Small user group (billing team), proven ROI area (AR aging)
2. **Fast results:** 30 days to measurable improvement
3. **Manageable during change:** Doesn't require clinical staff adoption during turnover period
4. **Budget-friendly:** Month-to-month commitment, can pause/cancel
5. **Builds confidence:** Proves technology and approach before full commitment

**Timeline:**
- **Month 1:** Pilot implementation
- **Month 2:** Validate success, make go/no-go decision
- **Month 3:** If successful, begin Phase 1 (add Intake)
- **Month 4-6:** Stabilize Phase 1
- **Month 7+:** Evaluate Full MVP when organizational change settles

**Investment Schedule:**
- Month 1-2: Pilot cost only
- Month 3+: Incremental increase if expanding
- **Flexibility to adjust** based on business conditions

---

## Next Steps

### If Choosing Pilot:

1. **Schedule kickoff call** (30 min)
   - Finalize Claims board scope
   - Confirm SimplePractice export capabilities
   - Identify 2-3 billing team members for pilot

2. **Contract & Setup** (Week 1)
   - Sign monday.com Enterprise agreement + BAA
   - Create workspace and user accounts
   - Grant admin access to implementation team

3. **Build & Test** (Week 2)
   - Build Claims board
   - Import sample data
   - Configure automations
   - Test workflows

4. **Train & Launch** (Week 3)
   - 2-hour remote training for billing team
   - Import real claims data
   - Go live (soft launch, parallel run)

5. **Validate** (Week 4-5)
   - Daily support/check-ins
   - Measure metrics
   - Make go/no-go decision for Phase 1

### If Choosing Phase 1:

(Assumes pilot already completed or skipping pilot)

1. Schedule planning session (1 hour)
2. Finalize scope for both boards
3. Follow Week 1-8 timeline (see Phase 1 section)

### If Choosing Full MVP:

1. Schedule discovery workshop (2 hours)
2. Finalize complete requirements
3. Follow 90-day timeline (see Full MVP section)

---

## Frequently Asked Questions

### Can I pause between phases?

**Yes.** Each phase is a stable endpoint. You can:
- Run Pilot indefinitely (just Claims board)
- Run Phase 1 indefinitely (Claims + Intake)
- Take breaks between phases to stabilize

### What if pilot doesn't work?

**Month-to-month commitment** means you can cancel. We recommend:
- 30-day minimum to truly evaluate
- Work with us to troubleshoot before canceling
- Refund/credit policy TBD based on contract terms

### Can I skip pilot and go straight to Full MVP?

**Yes**, but higher risk. We recommend pilot if:
- First time using monday.com
- Organizational change happening
- Budget uncertainty
- Need to build internal buy-in

Full MVP makes sense if you're confident and committed.

### What happens to my data if I cancel?

- You own all data
- Export all boards to CSV before canceling
- monday.com retains data 30 days after cancellation
- We provide final export as part of offboarding

### Do pilot costs credit toward full implementation?

**Yes**, we can structure as:
- Pilot = Phase 0
- If you continue to Phase 1 or Full MVP, pilot implementation costs credit toward total
- Details in contract/proposal

### Can I change my mind mid-implementation?

**Yes**, though easier at phase boundaries:
- Easy: Finish current phase, pause before next
- Moderate: Adjust scope during current phase (may affect timeline)
- Complex: Cancel mid-phase (may lose work in progress)

We'll work with you to find the right path forward.

---

## Summary: Three Paths Forward

| | Pilot | Phase 1 | Full MVP |
|---|---|---|---|
| **Commitment** | Low | Medium | High |
| **Timeline** | 1 month | 2 months | 3 months |
| **Budget** | Lowest | Moderate | Full |
| **Risk** | Minimal | Low | Moderate |
| **Value** | Quick win | Substantial | Transformative |
| **Best For** | Proving concept | Building momentum | Complete transformation |

**All paths lead to success.** Start where you're comfortable, expand when ready.

---

**Ready to discuss?** Let's talk about which path makes sense for your current situation.
