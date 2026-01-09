# Email Templates

## Outreach Email #1 (First Contact)

**Subject:** Free Coffee for {{company_name}}

---

Hi {{company_name}} Team,

I hope you're having a great week.

We're offering you a FREE SAMPLE of our coffee for your office.

Simply reply "Yes Please" if you'd like to try some amazing coffee delivered straight to you. No obligation.

Sam McKay | Director | Hark Coffee Roasters | 0478 121 171
[@harkcoffee](https://www.instagram.com/harkcoffee/)
HARK ROASTERY & CAFÉ: 57 Boothby Street, Panorama
HARK CENTRAL: 65-67 Duthy Street, Malvern
MOLLYMAWK: 243 Seacombe Road, South Brighton

---

## Outreach Email #2 (No Response - Friendly Reminder)

**Subject:** Did you see this? Free coffee for {{company_name}}

---

Hi {{company_name}} Team,

Just wanted to make sure this didn't slip through the cracks!

We'd love to drop off a FREE SAMPLE of our specialty coffee for your office — no strings attached.

If you're interested, simply reply "Yes Please" and we'll sort out the rest.

Sam McKay | Director | Hark Coffee Roasters | 0478 121 171
[@harkcoffee](https://www.instagram.com/harkcoffee/)

---

## Outreach Email #3 (Final Attempt)

**Subject:** Last chance for free coffee, {{company_name}}

---

Hi {{company_name}} Team,

This is my last email — I promise I won't keep filling your inbox!

We're still happy to send you a free sample of our coffee if you'd like to give it a try. Just reply "Yes" if you're keen.

No worries if it's not for you — I'll leave you in peace.

Sam McKay | Director | Hark Coffee Roasters | 0478 121 171
[@harkcoffee](https://www.instagram.com/harkcoffee/)

---

## Follow-Up Email (After Sample Delivered)

**Subject:** How was the coffee, {{company_name}}?

---

Hi {{company_name}} Team,

We hope you enjoyed your coffee sample!

If you'd like to keep the good coffee flowing, all we need is your accounts email address and we'll send them a link with your product list in Upstock — super easy to order whenever you need more.

Just reply with your accounts contact and we'll take care of the rest.

Sam McKay | Director | Hark Coffee Roasters | 0478 121 171
[@harkcoffee](https://www.instagram.com/harkcoffee/)

---

## Response to "Pod Machine" Enquiry

**Subject:** Re: {{original_subject}}

---

Great news — we've got you covered!

We supply Nespresso-compatible pods, so your machine will work perfectly with our coffee.

Would you like us to drop off a sample pack of pods for your team to try?

Sam McKay | Director | Hark Coffee Roasters | 0478 121 171
[@harkcoffee](https://www.instagram.com/harkcoffee/)

---

# Response Categorization Guide

## How to Identify Response Types

The system should intelligently categorize responses based on keywords and phrases:

### BOUNCED (Email Failed)
Look for phrases containing:
- "Address not found"
- "Error"
- "Could not deliver"
- "Failure to deliver"
- "Failed to deliver"
- "Undeliverable"
- "Mail delivery failed"
- "550" (email error code)
- "Invalid recipient"

**Action:** Mark as `bounced`, move to Bounced list

---

### YES (Interested in Sample)
Look for phrases containing:
- "Yes"
- "Yes please"
- "Sure"
- "Happy to give it a go"
- "That's a great idea"
- "Thank you" (in context of accepting)
- "Sounds good"
- "We'd love to"
- "Count us in"
- "Interested"
- "Sign us up"

**Action:** Mark as `interested` → `waiting_sample`

---

### NO (Not Interested)
Look for phrases containing:
- "No thank you"
- "Not interested"
- "We're fine"
- "Already have a supplier"
- "Not at this time"
- "Unsubscribe"
- "Remove me"
- "Stop emailing"

**Action:** Mark as `not_interested`, move to Archived (NEVER contact again)

---

### QUESTION / MORE INFO (Potential Yes)
Look for phrases containing:
- "Do you have pods?"
- "We only have a pod machine"
- "What about..."
- "Can you..."
- "Do you supply..."
- "What's the cost?"
- "How much?"
- "More information"
- "Tell me more"

**Action:** Mark as `question`, show in "Action Required" for human follow-up

---

### NO RESPONSE
No reply received after X days.

**Action:**
1. After 7 days of no response to Email #1 → Send Email #2
2. After 7 days of no response to Email #2 → Send Email #3
3. After 7 days of no response to Email #3 → Move to `cold` list

---

# Follow-Up Logic Flowchart

```
                    OUTREACH EMAIL #1 SENT
                            │
                            ▼
            ┌───────────────┴───────────────┐
            │         RESPONSE?             │
            └───────────────┬───────────────┘
                            │
        ┌───────┬───────┬───┴───┬───────┬───────┐
        ▼       ▼       ▼       ▼       ▼       ▼
     BOUNCED   YES    QUESTION  NO    NO RESP  OTHER
        │       │       │       │       │       │
        ▼       ▼       ▼       ▼       ▼       ▼
     Archive  Waiting  Action   Archive Wait    Review
              Sample   Required         7 days
                │       │               │
                ▼       ▼               ▼
             DELIVER  HUMAN         EMAIL #2
                │     REPLY             │
                ▼       │               ▼
           Wait 5d     │          ┌─────┴─────┐
                │       │          │  RESPONSE? │
                ▼       ▼          └─────┬─────┘
          FOLLOW-UP  [Back to           │
          (How was   main flow]    ┌────┴────┐
           coffee?)                │         │
                │              RESPONSE  NO RESP
                ▼                  │      7 days
           [Manual               ▼         │
           Upstock           [Process]     ▼
           setup]                      EMAIL #3
                                          │
                                          ▼
                                    ┌─────┴─────┐
                                    │  RESPONSE? │
                                    └─────┬─────┘
                                          │
                                    ┌─────┴─────┐
                                RESPONSE    NO RESP
                                    │       7 days
                                    ▼          │
                                [Process]      ▼
                                           COLD LIST
```

---

# Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{company_name}}` | Business name | "Donlan Lawyers" |
| `{{first_name}}` | Contact first name (if available) | "Sarah" |
| `{{original_subject}}` | Original email subject (for replies) | "Free Coffee for Donlan Lawyers" |

---

# Product Information (For Enquiries)

## What Hark Coffee Offers:
- **Coffee Beans** — Specialty roasted coffee
- **Nespresso-Compatible Pods** — For offices with pod machines
- **Office Coffee Supply** — Regular delivery to businesses

## Locations:
- HARK ROASTERY & CAFÉ: 57 Boothby Street, Panorama
- HARK CENTRAL: 65-67 Duthy Street, Malvern
- MOLLYMAWK: 243 Seacombe Road, South Brighton

## Contact:
- Sam McKay (Director)
- 0478 121 171
- sam@harkcoffee.com
- Instagram: @harkcoffee

---

*Last Updated: 2026-01-09*
