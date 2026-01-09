# Learning Roadmap: Technical Terms Explained

> Every technical term we'll use in this project, explained with simple metaphors.
> Refer back to this whenever you see a term you don't recognize.

---

## The Basics

### API (Application Programming Interface)
**Metaphor:** A waiter at a restaurant.

You (the customer) don't go into the kitchen yourself. Instead, you tell the waiter what you want, and they bring it back. An API is the waiter between your code and another service (like Google Maps).

- **Google Maps Places API** = A waiter who can fetch business information from Google's massive directory
- **Google Sheets API** = A waiter who can read/write data to your spreadsheets

---

### Backend vs Frontend
**Metaphor:** A restaurant's kitchen vs dining room.

- **Frontend** = The dining room. What customers see and interact with (your dashboard).
- **Backend** = The kitchen. Where the work happens behind the scenes (scraping, emailing, storing data).

Your project: The dashboard is frontend. The scraper and email system are backend.

---

### Database
**Metaphor:** A filing cabinet.

A place to store information in an organized way so you can find it later. Google Sheets is your filing cabinet — each row is a folder, each column is a label on that folder.

---

### CRUD Operations
**Metaphor:** What you can do with files in a cabinet.

- **C**reate = Add a new file (new lead)
- **R**ead = Look at a file (view lead details)
- **U**pdate = Change something in a file (mark as "delivered")
- **D**elete = Remove a file (we'll archive instead)

---

## Scraping Concepts

### Web Scraper
**Metaphor:** A robot assistant with a notepad.

You send the robot to Google Maps. It looks at business listings, writes down names, addresses, and emails, then brings the notepad back to you. That's scraping.

---

### Rate Limiting
**Metaphor:** A bouncer at a club.

Google doesn't want anyone overwhelming their servers, so they have a "bouncer" that only lets you make a certain number of requests. If you ask too fast or too often, you get temporarily blocked (or charged money).

**Our approach:** Stay well under the limit (200/day) to avoid fees.

---

### API Key
**Metaphor:** A VIP pass.

To use Google's services, you need to identify yourself. The API key is your personal pass that tells Google "this request is from me, and I'm allowed to be here."

**Important:** Keep it secret! If someone steals your pass, they can use your services (and you get the bill).

---

## Email Concepts

### SMTP (Simple Mail Transfer Protocol)
**Metaphor:** The postal service for emails.

When you send a letter, you put it in a mailbox and the postal service delivers it. SMTP is the postal service for digital emails. Your code hands the email to SMTP, and it delivers it.

---

### Email Bounce
**Metaphor:** A letter returned to sender.

You sent a letter, but the address doesn't exist (or the mailbox is full). The post office sends it back. Same with email — if the address is wrong or the inbox is full, it "bounces" back.

- **Hard bounce** = Address doesn't exist (permanent)
- **Soft bounce** = Inbox full or server busy (temporary)

---

### Email Open Tracking
**Metaphor:** A tiny invisible spy.

Emails can include a tiny invisible image. When someone opens the email, their email app tries to load that image from your server. Your server says "Aha! Someone loaded my image, so they must have opened the email."

*Note: This doesn't work if the recipient blocks images.*

---

### Email Deliverability
**Metaphor:** Your reputation with the post office.

If you send a lot of mail and people keep marking it as junk, the post office starts treating ALL your mail as suspicious. Same with email — if too many people mark you as spam, email providers will block you.

**How to stay reputable:**
- Send to real addresses
- Don't send too many at once
- Make it easy to unsubscribe

---

## Dashboard Concepts

### Streamlit
**Metaphor:** A magic coloring book.

Normally, building a website requires lots of different skills (HTML, CSS, JavaScript). Streamlit is like a coloring book where you just fill in the blanks with Python, and it creates a nice-looking web page for you.

---

### Deployment / Hosting
**Metaphor:** Renting an apartment for your code.

Your code needs to live somewhere that's always "on" and accessible from the internet. Deployment is the process of moving your code from your computer to a server (the apartment). Hosting is the ongoing rental of that server.

---

### Environment Variables
**Metaphor:** A secret notebook.

Some information (like API keys and passwords) shouldn't be written directly in your code. Instead, you write them in a secret notebook (`.env` file) that only your computer can read. The code knows to look in the notebook when it needs those secrets.

---

## Automation Concepts

### Cron Job / Scheduled Task
**Metaphor:** An alarm clock for your code.

You can tell your code: "Run every day at 9 AM" or "Run every hour." The cron job is the alarm clock that wakes your code up at the right time.

---

### Webhook
**Metaphor:** A doorbell that triggers an action.

When something happens elsewhere (like someone replies to an email), a webhook is a "doorbell ring" that tells your system "Hey! Something happened! Do something about it!"

---

### Queue
**Metaphor:** A line at the coffee shop.

If 500 leads need emails, you don't send them all at once (that would overwhelm the system). Instead, they line up in a queue, and you process them one by one, at a comfortable pace.

---

## Data Concepts

### CSV (Comma-Separated Values)
**Metaphor:** A simple spreadsheet in disguise.

A CSV is just a text file where each line is a row, and commas separate the columns. It's the simplest way to store spreadsheet-like data. Excel and Google Sheets can both read/write CSV files.

```
Name,Email,Status
Sterling Real Estate,info@sterling.com,new
Brooks Law Firm,contact@brooks.com,emailed
```

---

### JSON (JavaScript Object Notation)
**Metaphor:** A labeled container.

JSON is a way to organize data with labels. Like a box where everything is clearly labeled:

```json
{
  "name": "Sterling Real Estate",
  "email": "info@sterling.com",
  "status": "new"
}
```

APIs often speak in JSON because it's easy for computers to read.

---

## Code Concepts

### Function
**Metaphor:** A recipe.

A function is a set of instructions with a name. Instead of writing the same steps over and over, you write them once as a "recipe" and just call it by name whenever you need it.

```python
def send_email(address, message):
    # steps to send email
```

Now you just say `send_email("bob@mail.com", "Hello!")` instead of writing all the steps.

---

### Variable
**Metaphor:** A labeled jar.

A variable is a jar with a label. You put something in it (a number, text, a list) and the label helps you find it later.

```python
daily_limit = 200  # A jar labeled "daily_limit" containing 200
```

---

### Loop
**Metaphor:** Assembly line worker.

A loop does the same task over and over for each item in a list. Like a worker on an assembly line who puts a lid on every jar that passes by.

```python
for lead in all_leads:
    send_email(lead)  # Do this for every lead
```

---

### If Statement
**Metaphor:** A fork in the road.

"If it's raining, take an umbrella. Otherwise, wear sunglasses."

```python
if response == "yes":
    add_to_sample_list()
else:
    archive_lead()
```

---

## Security Concepts

### Authentication
**Metaphor:** Showing your ID at the door.

Proving you are who you say you are. Like showing your ID to enter a building. Logging into the dashboard = authentication.

---

### Authorization
**Metaphor:** Your key card access levels.

Once you're in the building, what rooms can you enter? A janitor can access utility rooms; executives can access the boardroom. Authorization determines what you're allowed to do.

---

### .env File
**Metaphor:** A safe for valuables.

Never put passwords or API keys directly in your code. Instead, store them in a `.env` file (the safe) and tell your code to look there. This file should never be shared or uploaded to the internet.

---

## Git Concepts

### Git
**Metaphor:** A time machine for your code.

Git saves "snapshots" of your code at different points in time. If something breaks, you can go back to when it worked. It also lets multiple people work on code without overwriting each other.

---

### Commit
**Metaphor:** Taking a photograph.

A commit is a snapshot of your code at a moment in time. You add a note describing what changed: "Added email tracking feature."

---

### Push / Pull
**Metaphor:** Uploading/downloading photos to the cloud.

- **Push** = Send your local commits to the online repository (GitHub)
- **Pull** = Download new changes from GitHub to your computer

---

### Branch
**Metaphor:** A parallel universe.

A branch lets you make changes without affecting the "main" version. Like working on a draft while the published version stays safe. When your draft is ready, you merge it back.

---

## Glossary Quick Reference

| Term | One-Line Explanation |
|------|---------------------|
| API | Messenger between your code and another service |
| Backend | The behind-the-scenes code (scraping, data) |
| Frontend | The part users see (dashboard) |
| CRUD | Create, Read, Update, Delete - basic data operations |
| Scraper | Robot that collects data from websites |
| Rate Limit | Maximum requests allowed per time period |
| SMTP | Email delivery service |
| Bounce | Email that couldn't be delivered |
| Webhook | Alert that something happened |
| Cron | Scheduled automatic task |
| CSV | Simple spreadsheet text file |
| JSON | Labeled data format for APIs |
| Git | Code version control (time machine) |
| Commit | Save a snapshot of code changes |
| Deploy | Put your code on a live server |

---

*Last Updated: 2026-01-08*
*Refer back to this document whenever you encounter unfamiliar terms!*
