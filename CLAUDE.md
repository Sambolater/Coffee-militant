# CLAUDE.md - AI Memory File

> This file helps Claude remember the project context, rules, and decisions.
> Claude reads this file at the start of each conversation.

---

## Project Identity

**Name:** Coffee Lead CRM (Coffee-militant)
**Owner:** Hark Coffee Roasters
**Purpose:** Automated lead generation and sales pipeline for B2B coffee samples
**End Goal:** Convert professional offices into customers on the Upstock ordering platform

---

## Business Details

| Field | Value |
|-------|-------|
| **Business Name** | Hark Coffee Roasters |
| **Director** | Sam McKay |
| **Email** | sam@harkcoffee.com |
| **Phone** | 0478 121 171 |
| **Instagram** | [@harkcoffee](https://www.instagram.com/harkcoffee/) |
| **Location 1** | HARK ROASTERY & CAFÉ: 57 Boothby Street, Panorama |
| **Location 2** | HARK CENTRAL: 65-67 Duthy Street, Malvern |
| **Location 3** | MOLLYMAWK: 243 Seacombe Road, South Brighton |

---

## Scraper Configuration

| Setting | Value |
|---------|-------|
| **Target Region** | Adelaide, South Australia |
| **Search Radius** | TBD (start with metro area) |
| **Existing Contacts Sheet** | [Google Sheet](https://docs.google.com/spreadsheets/d/15JmjQjjQIfhY0zKMzqBlvMMRGgJf3VFVgpOut_DG49s/) |

---

## The User

- **Coding Experience:** Complete beginner - has never coded
- **Role:** Business owner/operator who will USE the system, not build it
- **Expectation:** Claude does ALL the coding; user focuses on business operations
- **Communication Style:** Use plain language, simple metaphors, avoid jargon

---

## Critical Business Rules

### DO Target These Businesses:
- Real estate agencies
- Accountant firms
- Branding agencies
- Marketing companies
- Architecture firms
- Interior design studios
- Law firms / Solicitors
- Wealth management firms

### DO NOT Target:
- Cafes (they have their own coffee)
- Restaurants with coffee focus
- Coffee shops
- Any food/beverage businesses

### Email Rules:
- Maximum 200 emails per day (stay in free tier)
- NEVER email businesses on the exclusion list
- NEVER re-email businesses that said "no"
- Archive negative responses, don't delete them

---

## Existing Assets

The user has:
1. **Google Maps Places API** - Already set up and working
2. **Existing contact list** - Businesses already emailed (to be provided)
3. **Upstock account** - Ordering platform for onboarding customers

---

## Technical Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Language | Python | Readable, beginner-friendly |
| Dashboard | Streamlit | Python-based, simple, free hosting |
| Database | Google Sheets | User already comfortable with it |
| Email Service | TBD | Need to evaluate free tier options |
| Hosting | TBD | Need low-cost/free option |

---

## Status Definitions

| Status | Meaning |
|--------|---------|
| `new` | Just scraped, not yet emailed |
| `emailed` | Outreach email sent |
| `bounced` | Email failed to deliver |
| `no_response` | No reply after X days |
| `interested` | Replied YES to sample |
| `not_interested` | Replied NO (archive this) |
| `question` | Asked a question, needs human follow-up |
| `waiting_sample` | On the delivery list |
| `attempted` | Tried to deliver, failed |
| `delivered` | Sample successfully delivered |
| `follow_up_sent` | 5-day follow-up email sent |
| `onboarded` | Signed up on Upstock |

---

## Automation Timings

| Trigger | Action | Delay |
|---------|--------|-------|
| Lead scraped | Send outreach email | Same day (within limits) |
| Sample delivered | Send follow-up email | 5 days |
| No response to outreach | Mark as no_response | 7 days |

---

## Dashboard Requirements

### Sidebar (Collapsible)
- New Leads
- Waiting for Sample
- To Deliver
- Bounced Emails
- Archived
- Onboarded
- Analytics

### Main View
- "Action Required" list showing leads needing human attention
- Action buttons: [Delivered] [Attempted]
- Weekly stats: emails sent, response rate, samples requested

---

## Success Metrics

- **Daily:** 200 emails sent
- **Weekly:** 30 sample requests (success threshold)
- **Track:** Response rate percentage, conversion rate

---

## File Structure (Planned)

```
Coffee-militant/
├── CLAUDE.md              # This file (AI memory)
├── project_spec.md        # Project specification
├── learning_roadmap.md    # Technical terms explained
├── README.md              # Project overview
│
├── src/                   # Source code
│   ├── scraper/          # Google Maps scraping
│   ├── email/            # Email automation
│   ├── sheets/           # Google Sheets integration
│   └── dashboard/        # Streamlit dashboard
│
├── config/               # Configuration files
│   ├── .env.example     # Environment variables template
│   └── search_terms.json # Business types to search
│
├── data/                 # Local data files
│   └── exclusion_list.csv # Businesses to skip
│
└── docs/                 # Documentation
    └── setup_guide.md   # How to set up the system
```

---

## Reminders for Claude

1. **Always explain** what code does in simple terms
2. **Never assume** the user knows technical concepts
3. **Use metaphors** to explain complex ideas
4. **Test thoroughly** before saying something works
5. **Keep costs at zero** where possible (free tiers)
6. **Ask before proceeding** if something is unclear
7. **Commit frequently** with clear messages

---

## Questions to Ask User (When Needed)

- [x] What location(s) should the scraper search? → **Adelaide, South Australia**
- [x] What email address will send the outreach emails? → **sam@harkcoffee.com**
- [x] Can you share the existing contact list to exclude? → **Google Sheet provided**
- [x] What's the email template/message for outreach? → **See email_templates.md**
- [ ] What's the follow-up email template? → Draft created, needs approval

---

## Outstanding Questions

- [ ] Column structure of existing contacts Google Sheet (need access or description)
- [ ] Upstock signup link for follow-up email

---

*Last Updated: 2026-01-09*
*Version: 1.1*
