# Project Specification: Coffee Lead CRM

## The Big Picture (What Are We Building?)

A **lead generation and sales pipeline system** for a coffee supplier targeting professional service offices.

Think of it like a **fishing net that catches potential customers, sorts them, and guides them through your sales process** — mostly on autopilot.

---

## The Problem We're Solving

You want to offer free coffee samples to professional offices, but:
- Manually finding businesses is tedious
- Tracking who you've contacted is messy
- Following up at the right time is easy to forget
- You can't see your progress at a glance

**This system automates the boring parts so you can focus on delivering samples and closing deals.**

---

## Target Customers

Professional service offices where employees would appreciate quality coffee:

| Business Type | Example Search Terms |
|---------------|---------------------|
| Real Estate Agencies | "real estate agent", "estate agent" |
| Accountant Firms | "accountant", "CPA", "bookkeeper" |
| Branding Agencies | "branding agency", "brand design" |
| Marketing Companies | "marketing agency", "digital marketing" |
| Architecture Firms | "architect", "architecture firm" |
| Interior Design Studios | "interior designer", "interior design" |
| Law Firms | "solicitor", "lawyer", "law firm" |
| Wealth Management | "wealth management", "financial advisor" |

---

## How It Works (The Flow)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE COFFEE LEAD PIPELINE                        │
└─────────────────────────────────────────────────────────────────────────┘

    [1] SCRAPE                    [2] STORE                [3] EMAIL
    ─────────────                 ─────────                ────────────
    Google Maps          →        Google Sheets    →       Auto-send
    Places API                    (Your CRM)               200/day
         │                             │                        │
         ▼                             ▼                        ▼
    Find businesses              Save contact             Offer free
    with emails                  details                  coffee sample
         │                             │                        │
         └──────────────┬──────────────┴────────────────────────┘
                        │
                        ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │                        [4] TRACK RESPONSES                          │
    ├─────────────────────────────────────────────────────────────────────┤
    │                                                                     │
    │   📧 Bounced ──────→ Mark as invalid, archive                      │
    │   ❌ No/Negative ──→ Archive (don't contact again)                 │
    │   ❓ Question ────→ Human follow-up needed                         │
    │   ✅ Yes ─────────→ Add to "Waiting for Sample" list               │
    │                                                                     │
    └─────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │                      [5] DELIVERY & FOLLOW-UP                       │
    ├─────────────────────────────────────────────────────────────────────┤
    │                                                                     │
    │   Human clicks "Delivered"                                          │
    │         │                                                           │
    │         ▼                                                           │
    │   Wait 5 days (automatic)                                           │
    │         │                                                           │
    │         ▼                                                           │
    │   Auto-send onboarding email: "How was the coffee?"                │
    │   + Invitation to join Upstock ordering platform                   │
    │                                                                     │
    └─────────────────────────────────────────────────────────────────────┘
```

---

## The Dashboard (What You See)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  COFFEE LEAD CRM                                        [Week 12, 2026] │
├──────────────┬───────────────────────────────────────────────────────────┤
│              │                                                           │
│  📂 SIDEBAR  │  📊 ACTION REQUIRED                                      │
│  ──────────  │  ─────────────────────────────────────────               │
│              │                                                           │
│  📥 New      │  🏢 Sterling Real Estate          [Delivered] [Attempted]│
│     Leads    │     📍 Manchester | Waiting for sample                   │
│              │                                                           │
│  ⏳ Waiting  │  🏢 Brooks & Partners Law         [Delivered] [Attempted]│
│     Samples  │     📍 Leeds | Waiting for sample                        │
│              │                                                           │
│  🚚 To       │  🏢 Apex Marketing Group          [Delivered] [Attempted]│
│     Deliver  │     📍 Birmingham | Waiting for sample                   │
│              │                                                           │
│  📧 Bounced  │  ─────────────────────────────────────────               │
│              │                                                           │
│  ❌ Archived │  📈 THIS WEEK'S STATS                                    │
│              │  ├─ Emails Sent: 847                                     │
│  ✅ Onboard  │  ├─ Response Rate: 12%                                   │
│              │  ├─ Samples Requested: 28                                │
│  📈 Stats    │  └─ Conversion Rate: 3.3%                                │
│              │                                                           │
└──────────────┴───────────────────────────────────────────────────────────┘
```

---

## Success Metrics

| Metric | Daily Target | Weekly Target |
|--------|-------------|---------------|
| Emails Sent | 200 | 1,000 |
| Response Rate | - | 10-15% |
| Sample Requests | 6 | 30 |
| Deliveries Made | - | 25+ |

---

## Key Features (MVP First)

### Phase 1: MVP (Must Have)
1. **Scraper** - Pull businesses from Google Maps Places API
2. **Email Automation** - Send outreach emails, track bounces
3. **Google Sheets Backend** - Store all lead data
4. **Exclusion List** - Skip already-contacted businesses

### Phase 2: Dashboard
5. **Web Dashboard** - Visual interface to manage leads
6. **Status Buttons** - Click to update lead status
7. **Analytics View** - See conversion stats

### Phase 3: Full Automation
8. **Auto Follow-up** - 5-day delay after delivery
9. **Onboarding Integration** - Invite to Upstock platform
10. **Smart Scheduling** - Respect email sending limits

---

## Technical Boundaries

| Constraint | Approach |
|------------|----------|
| Stay in Google's free tier | Limit to 200 emails/day |
| Exclude past contacts | Check against existing list before sending |
| Handle negatives gracefully | Archive, never delete |
| Human oversight | Dashboard for manual status updates |

---

## Data We Store (Per Lead)

| Field | Example |
|-------|---------|
| Business Name | "Sterling Real Estate" |
| Business Type | "Real Estate Agency" |
| Address | "123 High Street, Manchester" |
| Email | "info@sterlingestate.co.uk" |
| Phone | "0161 234 5678" |
| Status | "waiting_sample" |
| Email Sent Date | "2026-01-08" |
| Email Status | "delivered" / "bounced" / "opened" |
| Response | "yes" / "no" / "question" / "none" |
| Sample Delivered | "2026-01-10" |
| Follow-up Sent | "2026-01-15" |
| Notes | "Asked about pods - follow up" |

---

## Status Flow

```
NEW → EMAILED → [BOUNCED/NO_RESPONSE/INTERESTED/NOT_INTERESTED]
                        │
                        ▼ (if INTERESTED)
               WAITING_SAMPLE → DELIVERED → FOLLOW_UP_SENT → ONBOARDED
                        │
                        ▼ (if delivery fails)
                   ATTEMPTED → RETRY
```

---

*Document Version: 1.0*
*Last Updated: 2026-01-08*
*Project: Coffee-militant*
