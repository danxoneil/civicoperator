RHT Data Consulting

# RHTP Data License

The complete record of the Rural Health Transformation Program, licensed as structured data for your own systems. Every state program, every solicitation, every award we can source, and the organizations and people attached to them, linked together and checked against the documents they came from.

[Request the sample](mailto:danx@civicoperator.com?subject=RHTP%20Data%20License%20%E2%80%94%20sample%20request)
[What's in it](#dataset)

The Rural Health Transformation Program is $50 billion over five years, awarded to all fifty states and administered fifty different ways. Most of that money will never appear on a procurement portal. It moves as grants and subawards, through lead agencies that differ from state to state and through intermediaries that run their own selection.

The general government-data platforms were built for contracts. This dataset was built for this one program, and it does nothing else.

## What's in the dataset

Twelve linked tables. Counts are live records as of October 2026 and grow as states publish.

| Table | What it holds | Records |
| --- | --- | --- |
| States | One record per state RHTP program: lead agency, program name, award, reported subawards, annual-report status. The hub every other table points back to. | All 50 |
| Initiatives | Each state's RHTP initiatives and budget lines, with five-year and Budget Period 1 amounts and roll-up logic that prevents double counting. | 530+ |
| Pre-procurement signals | Forecasts, webinars, guidance, advisory council decks and consultation summaries, logged before a solicitation exists and linked to the solicitation each one becomes. | 1,100+ |
| Solicitations | Every published RHTP RFP, RFA, NOFO, RFQ, RFI and direct allocation, with deadline, total available, maximum award, eligible applicants, buy category, issuer and source document. | 720+ |
| Awards | Named recipients and dollar amounts from state award lists, notices of award and federal first-tier subaward reports, tied to the solicitation, the initiative, the hospital and the people. | 4,500+ |
| Legislation | State bills that create, appropriate or condition RHTP money, plus the policy-commitment bills CMS scores. | 240+ |
| Federal outlays | The CMS-to-state prime award for every state: obligations against actual outlays. | All 50 |
| Delegated administrators | The re-granters, regional hubs, fiscal agents and sister agencies that hold RHTP money and run their own competitions. | 120+ |
| Annual reports | Each state's Year 1 report to CMS, parsed: initiatives launched, policy commitments met, and dollars awarded, obligated, disbursed and spent on administration. | All 50, with 180+ line-item metrics |
| Organizations | Awardees, hospitals, vendors, associations, universities and agencies, keyed by web domain. | 10,800+ |
| Contacts | Named people at those organizations, with title, email and the awards they are attached to. | 16,000+ |
| Rural hospitals | Every U.S. rural and critical access hospital, merged from CMS, UNC Sheps Center, HRSA and Flex Monitoring sources, linked to its health system and to the awards it received. | 2,400+ |

## Why you can't get this from a general platform

The big government-data platforms are very good at what they were built for: contracts, posted to procurement portals, coded by commodity. RHTP money mostly doesn't move that way.

- **Grants sit outside state procurement codes.** Colorado's State Controller says so in one line: “The State has exempted Grants from the Procurement Code.” Most RHTP dollars reach providers as subawards, so the portals that general platforms index have no obligation to carry them.
- **Solicitations land wherever the lead agency puts them.** In our tracking they have appeared on agency news pages, grant systems such as Submittable and IntelliGrants, press releases, posting boards, and in at least one case a Microsoft Form. The lead agency itself varies by state: Medicaid, the health department, or the governor's office.
- **A large share of the money is re-granted by someone other than the state.** Delegated administrators hold subawards and run their own rounds, often on their own websites. We track them as a table of their own because that is where awards go missing.
- **Federal award data is retrospective by rule.** Subaward reports are due the month after the obligation, cover first-tier recipients only, and tell you who won, never what is open.

One general state-and-local procurement platform built a category page titled for Rural Health Transformation bids. When we checked it, its default active-opportunity view returned no results. The opportunities exist. They just aren't where those tools look.

## Every record connected

The value isn't any one table. It's that an award points to the solicitation it came from, the initiative it funds, the organization and hospital that received it, the people at that organization, and the state program above all of it. Ask which critical access hospitals in a state won telehealth money, who runs IT at each, and which vendor was named in the award, and the answer is a filter, not a research project.

Every license ships with the data dictionary (every column, its type and its allowed values) and the relationship map (every connection between tables, in plain English). Your engineers can read the model before they load a row.

## Verified, record by record

The machine finds. The operator vouches.

Collection is automated and runs daily across state program pages, procurement and grant systems, delegated administrators and federal sources. Nothing is treated as fact until a person has checked it against its source. Every solicitation, award, signal and annual report carries:

- A verification status, so you can see what has been confirmed and what is still awaiting review, rather than having the difference hidden from you
- The evidence basis: primary document, state page, third-party report, or inferred from the program
- A link to the source document it was checked against

That's the distinction that matters most for anyone acting on the data. Most automated trackers in this space disclaim the accuracy of their own deadlines. Ours tells you which records were verified and where.

## Ways to license

Snapshots start at **$12,500**. Annual, partner and services engagements are quoted on scope and use.

Snapshot

### Delivered once, date-stamped

The full dataset, or a defined slice of it (your states, your topics, or the dataset without contacts), for internal use. A good fit for a business development team that needs to load a CRM, size a market or build a target list, and doesn't need the data to move after that.

Annual license with refresh

### The dataset kept current

As states publish solicitations, name awardees and file reports, the records update and reach your systems on a schedule. This is the license most data buyers end up on, because RHTP is shifting from a solicitation market to an award market and the most valuable records are the ones that don't exist yet.

Partner and redistribution

### In front of your customers

For platforms, consultancies and associations that want to put RHTP data in front of their own customers or members. Priced by reach and use, with attribution and refresh terms agreed up front. Redistribution is never included in an internal license; it is licensed separately and deliberately.

### Services on top

The data is the foundation; some clients want it put to work.

- **System build:** a client-owned monday.com workspace loaded with the dataset and connected to Claude, so your team can query records in plain language and draft deliverables from them
- **Integration:** getting the refresh into your CRM, warehouse or existing tools
- **Statewide Awardee Sweep:** every identified RHTP awardee in a named state, with named contacts at each
- **State Fit Brief:** where your platform fits across the fifty programs, ranked. [What's in a brief →](/work/rht/brief)

## How it's delivered

Pick one or two. The data is the same in each.

### Structured files

Excel or CSV, one per table, with stable record IDs, the data dictionary, the relationship map and the source documents.

### A live workspace

A monday.com workspace with connected tables, ready to use or to copy into your own account.

### A scheduled export

Delivered into the system you already run.

## How it compares

Plenty of our buyers already pay for a general platform. This isn't a replacement for it. It's the grant layer those platforms don't carry, for the largest rural health program in a generation.

| Feature | General government-procurement platforms | Healthcare provider databases | RHTP Data License |
| --- | --- | --- | --- |
| Built for | Contracts across every agency and industry | Providers, facilities and executives | One program, all fifty states |
| Grant instruments (NOFOs, RFAs, subawards) | Contracts-first | Not their focus | The core of the dataset |
| Intermediaries that re-grant money | Not modeled | Not modeled | Their own table |
| Awards tied to solicitation, hospital and contacts | Partial | Contacts without RHTP awards | Every link in one model |
| Per-record verification and source document | Varies; often unstated | Varies | On every solicitation and award |
| Bulk delivery into your own systems | Often an add-on module | Often an add-on module | Included in every license |
| Redistribution to your customers | Rarely offered | Rarely offered | Available as its own license |
| How you buy | Annual subscription, quote-based | Annual subscription, quote-based | Snapshot, annual license or partner license |

### Who licenses it

- Health technology and services vendors loading named awardees and decision-makers into their CRM
- Consultancies and system integrators who advise rural hospitals, states or vendors and want the record in their own tools
- Platforms and associations serving rural health customers who want RHTP data inside their product or member services
- Investors and analysts sizing who is receiving money and for what

### License terms, plainly

- **Non-exclusive.** Other licensees receive the same records. Nothing here is a reserved lead.
- **Internal use** unless you hold a partner license. No reselling, and no building a competing data product from the data.
- **Contacts come from published public sources.** Your outreach is yours to run, under your own CAN-SPAM and TCPA compliance.
- **No protected health information.** The dataset contains organizations, public records and professional contacts only.
- **What you tell us stays yours.** Anything you share with us about your own awards or pipeline is confidential and never enters the shared dataset.

## Questions

### How is this different from RHTP Verified Intelligence?

[Verified Intelligence](/work/rht/intelligence) is a monthly service: we read the program for you and tell you what matters. The data license hands you the record itself, so your team can do the analysis in your own tools. Some clients have both.

### How current is it?

Collection runs every day. Snapshots are stamped with their delivery date. Annual and partner licenses refresh on a schedule set in the agreement.

### Can we license just a few states?

Yes. A scoped snapshot covers the states or topics you name. All fifty are always available if your footprint grows.

### Can we see it before we buy?

Yes. We'll send a synthetic version of the dataset: the real schema, the real tables and connections, and the full data dictionary, populated with invented states, organizations and people so nothing in it can be mistaken for a real record. It's designed for your technical team to evaluate the model before anyone talks price.

## Request the sample

Tell us what you'd use the data for, which states matter, and whether it stays inside your organization or reaches your customers. We'll send the synthetic dataset and set up a walkthrough of the live workspace.

[Request the sample](mailto:danx@civicoperator.com?subject=RHTP%20Data%20License%20%E2%80%94%20sample%20request)
[Book a conversation](https://calendar.app.google/XruT8HoUjnKLCkwD8)

[danx@civicoperator.com](mailto:danx@civicoperator.com)  ·  [(773) 960-6045](tel:+17739606045)

---
Source: https://www.civicoperator.com/work/rht/data/
