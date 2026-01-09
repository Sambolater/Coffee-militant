#!/usr/bin/env python3
"""
Coffee Lead CRM - Main Scraper Script
Targets 200+ leads WITH emails per day.
"""

import os
import sys
import json
import time
import requests
import re
from datetime import datetime
from urllib.parse import urljoin

def log(msg):
    """Print with timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()

def load_config():
    """Load search configuration from JSON file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'search_terms.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        log("Config file not found, using defaults")
        return None

def check_env():
    """Check all required environment variables."""
    log("=" * 60)
    log("CHECKING ENVIRONMENT")
    log("=" * 60)

    required = {
        'GOOGLE_MAPS_API_KEY': os.getenv('GOOGLE_MAPS_API_KEY'),
        'GOOGLE_SERVICE_ACCOUNT_JSON': os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON'),
        'GOOGLE_SHEET_ID': os.getenv('GOOGLE_SHEET_ID'),
        'CRM_SHEET_ID': os.getenv('CRM_SHEET_ID'),
    }

    all_set = True
    for key, value in required.items():
        if value:
            preview = value[:20] + "..." if len(value) > 20 else value
            log(f"  {key}: {preview}")
        else:
            log(f"  {key}: MISSING!")
            all_set = False

    return all_set, required

def test_google_maps_api(api_key):
    """Test that the Google Maps API key works."""
    log("\n" + "=" * 60)
    log("TESTING GOOGLE MAPS API")
    log("=" * 60)

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        'query': 'accountant in Adelaide, South Australia',
        'key': api_key,
    }

    try:
        log("  Making test request...")
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        status = data.get('status')
        log(f"  API Status: {status}")

        if status == 'OK':
            results = data.get('results', [])
            log(f"  Found {len(results)} businesses")
            return True, data
        elif status == 'REQUEST_DENIED':
            log(f"  API Error: {data.get('error_message', 'Unknown error')}")
            return False, data
        elif status == 'ZERO_RESULTS':
            log("  No results found (API works but no matches)")
            return True, data
        else:
            log(f"  Unexpected status: {status}")
            return False, data

    except Exception as e:
        log(f"  Request failed: {e}")
        return False, None

def test_sheets_connection(service_json, sheet_id):
    """Test Google Sheets connection and get exclusion emails."""
    log("\n" + "=" * 60)
    log("TESTING GOOGLE SHEETS CONNECTION")
    log("=" * 60)

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        log("  Parsing service account JSON...")

        if os.path.exists(service_json):
            creds = Credentials.from_service_account_file(
                service_json,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
        else:
            creds_dict = json.loads(service_json)
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )

        log("  Connecting to Google Sheets...")
        client = gspread.authorize(creds)

        log(f"  Opening exclusion sheet: {sheet_id[:20]}...")
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.sheet1

        log("  Reading existing contacts...")
        emails = worksheet.col_values(3)  # Column C = emails
        log(f"  Found {len(emails)} rows in email column")

        # Filter to actual emails
        email_set = {e.lower().strip() for e in emails[1:] if e and '@' in e}
        log(f"  {len(email_set)} unique emails to exclude")

        return True, email_set

    except Exception as e:
        log(f"  Failed: {e}")
        import traceback
        traceback.print_exc()
        return False, set()

def test_crm_sheet(service_json, crm_sheet_id):
    """Test that we can write to the CRM sheet BEFORE scraping."""
    log("\n" + "=" * 60)
    log("TESTING CRM SHEET (where leads are saved)")
    log("=" * 60)

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        if os.path.exists(service_json):
            creds = Credentials.from_service_account_file(
                service_json,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
        else:
            creds_dict = json.loads(service_json)
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )

        log("  Connecting to CRM sheet...")
        client = gspread.authorize(creds)

        log(f"  Opening sheet: {crm_sheet_id[:20]}...")
        sheet = client.open_by_key(crm_sheet_id)
        worksheet = sheet.sheet1

        rows = len(worksheet.get_all_values())
        log(f"  CRM sheet accessible: {rows} existing rows")
        return True

    except Exception as e:
        log(f"  FAILED: {e}")
        log("\n  *** CRM SHEET NOT ACCESSIBLE ***")
        log("  The bot found leads but CANNOT save them.")
        log("  Share the CRM sheet with the service account email as Editor.")
        import traceback
        traceback.print_exc()
        return False


def find_email_from_website(url):
    """Find email from a website - checks multiple pages."""
    if not url:
        return None

    pages = ['', '/contact', '/contact-us', '/about', '/about-us', '/team', '/our-team']
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    # Skip these fake/useless emails
    skip_patterns = ['example', 'sentry', 'wixpress', '.png', '.jpg', '.gif',
                     'noreply', 'no-reply', 'test@', 'email@', 'your@']

    for page in pages:
        try:
            full_url = urljoin(url, page)
            resp = requests.get(full_url, timeout=8, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            if resp.status_code == 200:
                emails = re.findall(email_pattern, resp.text)
                for email in emails:
                    email = email.lower()
                    if not any(x in email for x in skip_patterns):
                        return email
        except:
            continue
    return None

def search_with_pagination(api_key, query, max_pages=3):
    """Search Google Maps with pagination to get more results."""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    all_results = []
    next_page_token = None

    for page in range(max_pages):
        params = {'query': query, 'key': api_key}

        if next_page_token:
            params['pagetoken'] = next_page_token
            time.sleep(2)  # Google requires delay before using page token

        try:
            resp = requests.get(url, params=params, timeout=30)
            data = resp.json()

            if data.get('status') != 'OK':
                break

            results = data.get('results', [])
            all_results.extend(results)

            next_page_token = data.get('next_page_token')
            if not next_page_token:
                break

        except Exception as e:
            log(f"    Search error: {e}")
            break

    return all_results

def scrape_leads(api_key, exclusion_emails, config):
    """Main scraping function - targets 200+ leads with emails."""
    log("\n" + "=" * 60)
    log("SCRAPING LEADS (Target: 200+ with emails)")
    log("=" * 60)

    # Get search config
    if config:
        categories = config.get('target_businesses', [])
        location = config.get('location', {})
        location_str = f"{location.get('city', 'Adelaide')}, {location.get('state', 'South Australia')}"
        exclude_types = set(config.get('exclude_types', []))
    else:
        # Fallback defaults
        categories = [
            {"category": "Real Estate", "search_terms": ["real estate agent", "property management", "real estate agency"]},
            {"category": "Accounting", "search_terms": ["accountant", "CPA", "tax accountant", "bookkeeper", "accounting firm"]},
            {"category": "Lawyers", "search_terms": ["lawyer", "solicitor", "law firm", "legal services"]},
            {"category": "Architects", "search_terms": ["architect", "architecture firm"]},
            {"category": "Marketing", "search_terms": ["marketing agency", "digital marketing", "advertising agency"]},
            {"category": "Branding", "search_terms": ["branding agency", "graphic design agency", "creative agency"]},
            {"category": "Interior Design", "search_terms": ["interior designer", "interior design studio"]},
            {"category": "Wealth Management", "search_terms": ["financial advisor", "financial planner", "wealth management"]},
        ]
        location_str = "Adelaide, South Australia"
        exclude_types = {'cafe', 'restaurant', 'food', 'bakery', 'bar', 'coffee_shop'}

    all_leads = []
    seen_ids = set()
    seen_emails = set()
    stats = {'searched': 0, 'found': 0, 'with_email': 0, 'excluded': 0, 'skipped_type': 0}

    log(f"  Location: {location_str}")
    log(f"  Categories: {len(categories)}")
    log(f"  Exclusion list: {len(exclusion_emails)} emails")

    for cat_config in categories:
        category = cat_config.get('category', 'Unknown')
        terms = cat_config.get('search_terms', [])

        log(f"\n{'='*50}")
        log(f"Category: {category} ({len(terms)} search terms)")
        log(f"{'='*50}")

        for term in terms:
            query = f"{term} in {location_str}"
            log(f"\n  Searching: {query}")
            stats['searched'] += 1

            # Get results with pagination (up to 60 per term)
            results = search_with_pagination(api_key, query, max_pages=3)
            log(f"    Found {len(results)} places")

            for place in results:
                place_id = place.get('place_id')
                name = place.get('name', 'Unknown')

                # Skip duplicates
                if place_id in seen_ids:
                    continue
                seen_ids.add(place_id)
                stats['found'] += 1

                # Skip excluded business types (cafes, restaurants, etc.)
                types = place.get('types', [])
                if any(t in exclude_types for t in types):
                    stats['skipped_type'] += 1
                    continue

                # Get place details (phone, website)
                details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                details_params = {
                    'place_id': place_id,
                    'fields': 'name,formatted_address,formatted_phone_number,website',
                    'key': api_key
                }

                try:
                    details_resp = requests.get(details_url, params=details_params, timeout=10)
                    details = details_resp.json().get('result', {})
                except:
                    details = {}

                website = details.get('website', '')

                # Find email from website
                email = find_email_from_website(website) if website else None

                # SKIP if no email found (we only want leads WITH emails)
                if not email:
                    continue

                # Skip duplicates by email
                if email.lower() in seen_emails:
                    continue
                seen_emails.add(email.lower())

                # Check exclusion list
                if email.lower() in exclusion_emails:
                    log(f"    EXCLUDED: {name} ({email})")
                    stats['excluded'] += 1
                    continue

                stats['with_email'] += 1

                lead = {
                    'business_name': details.get('name', name),
                    'industry': category,
                    'email': email,
                    'address': details.get('formatted_address', place.get('formatted_address', '')),
                    'phone': details.get('formatted_phone_number', ''),
                    'website': website,
                    'status': 'new',
                    'source': 'google_maps',
                }

                log(f"    NEW LEAD: {name} ({email})")
                all_leads.append(lead)

                time.sleep(0.1)  # Rate limiting

                # Progress update every 50 leads
                if len(all_leads) % 50 == 0:
                    log(f"\n    === Progress: {len(all_leads)} leads with emails ===\n")

    # Final stats
    log("\n" + "=" * 60)
    log("SCRAPE STATS")
    log("=" * 60)
    log(f"  Search terms processed: {stats['searched']}")
    log(f"  Total places found: {stats['found']}")
    log(f"  Skipped (cafe/restaurant): {stats['skipped_type']}")
    log(f"  Already contacted: {stats['excluded']}")
    log(f"  NEW LEADS WITH EMAIL: {stats['with_email']}")

    return all_leads

def save_leads(leads, service_json, crm_sheet_id):
    """Save leads to Google Sheets CRM."""
    log("\n" + "=" * 60)
    log("SAVING TO CRM")
    log("=" * 60)

    if not leads:
        log("  No leads to save")
        return 0

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        if os.path.exists(service_json):
            creds = Credentials.from_service_account_file(
                service_json,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
        else:
            creds_dict = json.loads(service_json)
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )

        client = gspread.authorize(creds)

        log(f"  Opening CRM sheet: {crm_sheet_id[:20]}...")
        sheet = client.open_by_key(crm_sheet_id)
        worksheet = sheet.sheet1

        # Check if headers exist
        try:
            first_row = worksheet.row_values(1)
        except:
            first_row = []

        if not first_row:
            headers = [
                'Business Name', 'Industry', 'Email', 'Address', 'Phone',
                'Website', 'Status', 'Source', 'Date Added',
                'Date Emailed', 'Response', 'Notes'
            ]
            worksheet.append_row(headers)
            log("  Added headers")

        rows = []
        for lead in leads:
            rows.append([
                lead.get('business_name', ''),
                lead.get('industry', ''),
                lead.get('email', ''),
                lead.get('address', ''),
                lead.get('phone', ''),
                lead.get('website', ''),
                lead.get('status', 'new'),
                lead.get('source', 'google_maps'),
                datetime.now().strftime('%Y-%m-%d'),
                '', '', ''
            ])

        worksheet.append_rows(rows)
        log(f"  SAVED {len(rows)} leads to CRM!")
        return len(rows)

    except Exception as e:
        log(f"  FAILED to save: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("HARK COFFEE LEAD SCRAPER")
    print("Target: 200+ leads WITH emails per day")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check for dry-run
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        log("DRY RUN MODE - Will not save to sheets")

    # Load config
    config = load_config()
    if config:
        log("Loaded config from search_terms.json")

    # Check environment
    env_ok, env_vars = check_env()
    if not env_ok:
        log("\nMissing required environment variables!")
        return 1

    api_key = env_vars['GOOGLE_MAPS_API_KEY']
    service_json = env_vars['GOOGLE_SERVICE_ACCOUNT_JSON']
    sheet_id = env_vars['GOOGLE_SHEET_ID']
    crm_id = env_vars['CRM_SHEET_ID']

    # Test Google Maps API
    maps_ok, _ = test_google_maps_api(api_key)
    if not maps_ok:
        log("\nGoogle Maps API not working!")
        return 1

    # Test Sheets connection and get exclusion list
    sheets_ok, exclusion_emails = test_sheets_connection(service_json, sheet_id)
    if not sheets_ok:
        log("\nGoogle Sheets connection failed!")
        return 1

    # Test CRM sheet connection BEFORE scraping (fail early!)
    crm_ok = test_crm_sheet(service_json, crm_id)
    if not crm_ok:
        log("\nCRM Sheet not accessible! Fix this before scraping.")
        return 1

    # Scrape leads (only those WITH emails)
    leads = scrape_leads(api_key, exclusion_emails, config)

    # Summary
    log("\n" + "=" * 60)
    log("FINAL SUMMARY")
    log("=" * 60)
    log(f"  Total leads WITH EMAIL: {len(leads)}")

    if len(leads) >= 200:
        log("  TARGET MET!")
    else:
        log(f"  ({200 - len(leads)} short of 200 target)")

    # Save
    if leads and not dry_run:
        saved = save_leads(leads, service_json, crm_id)
        log(f"  Saved to CRM: {saved}")
    elif dry_run:
        log("  Dry run - not saving")

    log(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
