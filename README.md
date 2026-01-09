# Hark Coffee Lead CRM

Automated lead generation system for Hark Coffee Roasters. Finds professional service businesses in Adelaide and manages the sales pipeline for free coffee sample outreach.

## What It Does

1. **Scrapes** Google Maps for target businesses (accountants, lawyers, architects, etc.)
2. **Finds** contact emails from business websites
3. **Excludes** businesses already contacted
4. **Saves** new leads to Google Sheets CRM
5. **Runs automatically** every morning via GitHub Actions

## Quick Start

### Prerequisites

- Python 3.11+
- Google Maps Places API key
- Google Service Account (for Sheets access)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Coffee-militant.git
cd Coffee-militant

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Run Manually

```bash
# Full scrape
python main.py

# Test without saving
python main.py --dry-run

# Single category
python main.py --category "Accounting"
```

## GitHub Secrets Required

Add these secrets in your GitHub repository settings:

| Secret | Description |
|--------|-------------|
| `GOOGLE_MAPS_API_KEY` | Your Google Maps Places API key |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Full JSON content of your service account |
| `EXCLUSION_SHEET_ID` | ID of sheet with existing contacts |
| `CRM_SHEET_ID` | ID of sheet for new leads |

## Project Structure

```
Coffee-militant/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
│
├── src/
│   ├── scraper/           # Google Maps scraping
│   │   └── places_scraper.py
│   └── sheets/            # Google Sheets integration
│       └── sheets_client.py
│
├── config/
│   └── search_terms.json  # Business types to search
│
├── .github/
│   └── workflows/
│       └── daily-scrape.yml  # Automated daily runs
│
└── data/                  # Documentation
    └── existing_contacts_structure.md
```

## Target Businesses

- Real Estate Agencies
- Accountants / CPAs
- Law Firms / Solicitors
- Architects
- Interior Designers
- Marketing Agencies
- Branding Agencies
- Wealth Management

## Excluded

- Cafes
- Restaurants
- Coffee shops
- Any food/beverage businesses

## Documentation

- `CLAUDE.md` - AI memory file with project rules
- `project_spec.md` - Full system specification
- `email_templates.md` - Email templates and response logic
- `hark_brand_guide.md` - Product info and brand guide
- `learning_roadmap.md` - Technical terms explained

---

Built for Hark Coffee Roasters, Adelaide
