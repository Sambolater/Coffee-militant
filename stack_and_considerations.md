# Stack Recommendation & Overlooked Intricacies

---

## Part 1: Stack Recommendation (Your Toolbelt)

These are the tools I recommend for building your Coffee Lead CRM. Each was chosen because it's **beginner-friendly**, **well-documented**, and **free or very cheap**.

---

### The Complete Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        YOUR TECH STACK                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LANGUAGE          Python 3.11+                                            │
│  ──────────────────────────────────────────────────────                    │
│  Why: Reads like English, huge community, perfect for automation           │
│                                                                             │
│  DATA STORAGE      Google Sheets (via gspread library)                     │
│  ──────────────────────────────────────────────────────                    │
│  Why: You already know it, free, easy to view/edit manually                │
│                                                                             │
│  LEAD SCRAPING     Google Maps Places API                                  │
│  ──────────────────────────────────────────────────────                    │
│  Why: You already have it, official source, reliable data                  │
│                                                                             │
│  EMAIL SENDING     Resend (or Gmail SMTP)                                  │
│  ──────────────────────────────────────────────────────                    │
│  Why: 3,000 free emails/month, simple API, tracks bounces                  │
│  Alternative: Gmail SMTP (500/day but trickier bounce tracking)            │
│                                                                             │
│  DASHBOARD         Streamlit                                               │
│  ──────────────────────────────────────────────────────                    │
│  Why: Write Python, get a website. Free hosting on Streamlit Cloud.        │
│                                                                             │
│  AUTOMATION        GitHub Actions (Cron)                                   │
│  ──────────────────────────────────────────────────────                    │
│  Why: Free scheduled tasks, runs your scraper daily automatically          │
│                                                                             │
│  VERSION CONTROL   Git + GitHub                                            │
│  ──────────────────────────────────────────────────────                    │
│  Why: Already set up, saves your code safely, enables automation           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Tool-by-Tool Breakdown

#### 1. Python (Language)
**What it is:** The programming language we'll write all our code in.

**Why it's perfect for you:**
- Reads almost like English: `if email_bounced: archive_lead()`
- Massive community = lots of help available
- Libraries for everything (Google Sheets, email, APIs)

**Cost:** Free

---

#### 2. Google Sheets + gspread (Database)
**What it is:** Your Google Sheets will act as the database. `gspread` is the Python library that lets code read/write to Sheets.

**Why it's perfect for you:**
- You already know how to use Sheets
- You can manually view and edit data anytime
- Easy to share with team members
- No database setup required

**Cost:** Free

**Limitation:** If you eventually have 50,000+ leads, you may need a "real" database. But Sheets handles thousands just fine.

---

#### 3. Google Maps Places API (Lead Source)
**What it is:** Google's official service for getting business information.

**Why it's perfect for you:**
- You already have the API key
- Official, accurate data
- Returns business names, addresses, phone numbers, websites

**Cost:** $200 free credit/month, then pay-per-use. At 200 requests/day, you'll stay in free tier.

**Note:** The API doesn't directly give emails. We'll need to visit business websites to find them (a second scraping step).

---

#### 4. Resend (Email Sending & Tracking)
**What it is:** A modern email API service. You tell it "send this email to X" and it handles delivery + tells you if it bounced.

**Why it's perfect for you:**
- 3,000 free emails per month (100/day = enough to start)
- Simple to use from Python
- Automatically tracks bounces
- Good deliverability reputation

**Alternative - Gmail SMTP:**
- 500 emails/day free
- Harder to track bounces
- Risk of account flagged as spam

**Cost:** Free tier (3,000/month), then $20/month for 50,000 emails

---

#### 5. Streamlit (Dashboard)
**What it is:** A Python library that turns scripts into web apps.

**Why it's perfect for you:**
- Write Python, get a website (no HTML/CSS/JavaScript needed)
- Built-in buttons, tables, charts
- Free hosting on Streamlit Cloud
- Looks professional out of the box

**Cost:** Free (including hosting)

---

#### 6. GitHub Actions (Automation)
**What it is:** GitHub's built-in automation service. You can tell it "run this code every day at 9 AM."

**Why it's perfect for you:**
- Free for public/private repos (2,000 minutes/month)
- No separate server needed
- Already integrated with your GitHub repo

**Cost:** Free tier covers your needs

---

### Stack Comparison (Why Not Others?)

| Alternative | Why NOT this |
|-------------|--------------|
| Node.js/JavaScript | Steeper learning curve, Python is more readable |
| MySQL/PostgreSQL | Overkill; Sheets is simpler and you can see your data |
| React Dashboard | Requires learning 3+ technologies; Streamlit is Python-only |
| AWS/Azure Hosting | Complex setup, potential costs; Streamlit Cloud is simpler |
| Mailchimp | Designed for newsletters, not transactional outreach |

---

## Part 2: Overlooked Intricacies

These are the "what-ifs" that trip up most projects. Let's address them now.

---

### Email-Related Gotchas

#### 1. "What if an email bounces?"
**The Problem:** Invalid email = wasted effort + hurts sender reputation.

**Our Solution:**
- Track bounces via Resend's webhook
- Auto-mark as `bounced` in Sheets
- Move to Bounced list in dashboard
- Never email again

---

#### 2. "What if someone marks us as spam?"
**The Problem:** Too many spam reports = email providers block ALL your emails.

**Our Solution:**
- Include unsubscribe link in every email
- If someone unsubscribes, auto-archive them
- Keep emails personal, not salesy
- Only email businesses (not random people)

---

#### 3. "What if we hit Google's email limits?"
**The Problem:** Send too many too fast = temporarily blocked.

**Our Solution:**
- Queue system: send 200/day max
- Space them out: ~8 per hour during business hours
- Track daily count, stop when limit reached

---

#### 4. "What if someone replies with a question?"
**The Problem:** Questions need human judgment ("Do you sell pods?" "What areas do you deliver to?").

**Our Solution:**
- Mark as `question` status
- Show in "Action Required" dashboard section
- You answer manually
- After answering, you click to update status

---

### Scraping-Related Gotchas

#### 5. "What if a business has no email on Google Maps?"
**The Problem:** Many businesses don't list email on Google Maps.

**Our Solution:**
- Scrape the business website from Google Maps
- Spider the website's Contact page for email addresses
- If no email found, skip that lead (mark as `no_email`)

---

#### 6. "What if we scrape a business we've already contacted?"
**The Problem:** Emailing twice looks unprofessional and wastes resources.

**Our Solution:**
- Import your existing contact list as an exclusion list
- Before adding any lead, check if email already exists
- If exists, skip it

---

#### 7. "What if the scraper finds a cafe accidentally?"
**The Problem:** Your search for "accountant" might return a cafe next door.

**Our Solution:**
- Filter by Google's business category
- Only keep businesses categorized as office/professional services
- Flag uncertain ones for human review

---

### Delivery & Follow-up Gotchas

#### 8. "What if we try to deliver but no one's there?"
**The Problem:** You drove to an office but they're closed/not available.

**Our Solution:**
- Click "Attempted" button
- System logs the attempt
- Shows up in "Retry Delivery" list
- After 3 attempts, mark as `delivery_failed`

---

#### 9. "What if they got the sample but don't respond to follow-up?"
**The Problem:** Delivered sample, sent follow-up email... silence.

**Our Solution:**
- After 7 days of no response, mark as `follow_up_no_response`
- Option to send ONE more follow-up
- If still no response, move to `cold` list (potential future re-engagement)

---

#### 10. "What if they say yes but then change their mind?"
**The Problem:** They requested a sample, then cancelled.

**Our Solution:**
- Add a "Cancelled" button
- Move to cancelled list (different from rejected)
- Could revisit in 6 months

---

### Data & Security Gotchas

#### 11. "What if someone accesses the dashboard who shouldn't?"
**The Problem:** Sensitive business data (emails, addresses) exposed.

**Our Solution:**
- Streamlit has built-in password protection
- Only you (and team) have the password
- Dashboard only accessible via the login

---

#### 12. "What if the Google Sheets gets accidentally deleted?"
**The Problem:** All your lead data gone.

**Our Solution:**
- Daily automatic backup to a second Sheet
- Can also export to CSV periodically
- Google Sheets has version history (restore old versions)

---

#### 13. "What if API keys get leaked?"
**The Problem:** Someone could run up your Google Maps bill.

**Our Solution:**
- Store all keys in `.env` file (never in code)
- Add `.env` to `.gitignore` (never uploaded to GitHub)
- Use environment secrets in GitHub Actions

---

### Legal & Compliance Gotchas

#### 14. "Is this legal? (GDPR/Privacy)"
**The Problem:** UK/EU have strict data protection laws.

**Our Solution:**
- You're emailing businesses, not individuals (B2B exemption)
- Include company name and unsubscribe option
- Don't store personal data you don't need
- Delete/archive when requested

**Recommendation:** Add to your email footer:
> "We found your business on Google Maps. If you'd prefer not to hear from us, simply reply 'unsubscribe' and we'll remove you from our list."

---

#### 15. "What if they accuse us of spam?"
**The Problem:** Even legitimate B2B outreach can get complaints.

**Our Solution:**
- Keep emails short and genuine
- Personalize with business name
- Make the offer valuable (free sample)
- Make unsubscribing dead simple
- One email, one follow-up max (not persistent harassment)

---

### Scale & Maintenance Gotchas

#### 16. "What if we grow beyond 200 emails/day?"
**The Problem:** Free tiers have limits.

**Our Solution:**
- Current plan handles 200/day = 1,000/week = 4,000/month
- When you need more: upgrade Resend ($20/month for 50,000)
- If Google Maps costs increase, can budget ~$50/month

---

#### 17. "What if the code breaks while I'm not looking?"
**The Problem:** Automated systems can fail silently.

**Our Solution:**
- Error notifications (email/Slack if scraper fails)
- Daily summary: "200 emails sent, 3 bounced, 12 responses"
- Dashboard shows system health status

---

### Summary Checklist

Before we build, we've accounted for:

- [x] Email bounces → Track and archive
- [x] Spam complaints → Unsubscribe link, B2B focus
- [x] Rate limits → Daily caps, spacing
- [x] Missing emails → Website scraping fallback
- [x] Duplicate contacts → Exclusion list check
- [x] Wrong business types → Category filtering
- [x] Failed deliveries → Attempt tracking
- [x] Silent follow-ups → Reminder system
- [x] Cancelled requests → Separate status
- [x] Unauthorized access → Password protection
- [x] Data loss → Automatic backups
- [x] API key security → Environment variables
- [x] Legal compliance → B2B, unsubscribe, transparency
- [x] Scaling costs → Clear upgrade path
- [x] Silent failures → Error notifications

---

*Document Version: 1.0*
*Last Updated: 2026-01-08*
