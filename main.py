#!/usr/bin/env python3
"""
Coffee Lead CRM - Main Scraper Script
Simplified and robust version with better error handling.
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
            log(f"  ✓ {key}: {preview}")
        else:
            log(f"  ✗ {key}: MISSING!")
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
            log(f"  ✓ Found {len(results)} businesses")
            if results:
                log(f"  Sample: {results[0].get('name', 'Unknown')}")
            return True, data
        elif status == 'REQUEST_DENIED':
            log(f"  ✗ API Error: {data.get('error_message', 'Unknown error')}")
            log("  → Check that Places API is enabled in Google Cloud Console")
            return False, data
        elif status == 'ZERO_RESULTS':
            log("  ⚠ No results found (API works but no matches)")
            return True, data
        else:
            log(f"  ✗ Unexpected status: {status}")
            log(f"  Error: {data.get('error_message', 'No error message')}")
            return False, data

    except Exception as e:
        log(f"  ✗ Request failed: {e}")
        return False, None

def test_sheets_connection(service_json, sheet_id):
    """Test Google Sheets connection."""
    log("\n" + "=" * 60)
    log("TESTING GOOGLE SHEETS CONNECTION")
    log("=" * 60)

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        log("  Parsing service account JSON...")

        # Parse the JSON
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

        log(f"  Opening sheet: {sheet_id[:20]}...")
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.sheet1

        log("  Reading data...")
        # Get column C (emails)
        emails = worksheet.col_values(3)
        log(f"  ✓ Found {len(emails)} rows in email column")

        # Filter to actual emails
        email_set = {e.lower().strip() for e in emails[1:] if e and '@' in e}
        log(f"  ✓ {len(email_set)} unique emails to exclude")

        if email_set:
            sample = list(email_set)[:3]
            log(f"  Sample: {sample}")

        return True, email_set

    except Exception as e:
        log(f"  ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False, set()

def find_email_from_website(url):
    """Find email from a website."""
    if not url:
        return None

    pages = ['', '/contact', '/contact-us', '/about']
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    for page in pages:
        try:
            full_url = urljoin(url, page)
            resp = requests.get(full_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                emails = re.findall(email_pattern, resp.text)
                for email in emails:
                    email = email.lower()
                    if not any(x in email for x in ['example', 'sentry', 'wixpress', '.png', '.jpg']):
                        return email
        except:
            continue
    return None

def scrape_leads(api_key, exclusion_emails):
    """Main scraping function."""
    log("\n" + "=" * 60)
    log("SCRAPING LEADS")
    log("=" * 60)

    search_terms = [
        ("Real Estate", ["real estate agent Adelaide"]),
        ("Accounting", ["accountant Adelaide", "CPA Adelaide"]),
        ("Lawyers", ["lawyer Adelaide", "solicitor Adelaide"]),
        ("Architects", ["architect Adelaide"]),
        ("Marketing", ["marketing agency Adelaide"]),
    ]

    all_leads = []
    seen_ids = set()

    for category, terms in search_terms:
        log(f"\n📁 {category}")

        for term in terms:
            log(f"  🔍 Searching: {term}")

            # Search Google Maps
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {'query': term, 'key': api_key}

            try:
                resp = requests.get(url, params=params, timeout=30)
                data = resp.json()

                if data.get('status') != 'OK':
                    log(f"    ⚠ API status: {data.get('status')}")
                    continue

                results = data.get('results', [])[:10]  # Limit to 10 per term
                log(f"    Found {len(results)} businesses")

                for place in results:
                    place_id = place.get('place_id')
                    name = place.get('name', 'Unknown')

                    if place_id in seen_ids:
                        continue
                    seen_ids.add(place_id)

                    # Skip cafes/restaurants
                    types = place.get('types', [])
                    if any(t in types for t in ['cafe', 'restaurant', 'food', 'bakery']):
                        continue

                    # Get details
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
                    email = find_email_from_website(website) if website else None

                    # Check exclusion
                    if email and email.lower() in exclusion_emails:
                        log(f"    ⏭ Excluded: {name}")
                        continue

                    lead = {
                        'business_name': details.get('name', name),
                        'industry': category,
                        'email': email or '',
                        'address': details.get('formatted_address', place.get('formatted_address', '')),
                        'phone': details.get('formatted_phone_number', ''),
                        'website': website,
                        'status': 'new' if email else 'no_email',
                        'source': 'google_maps',
                    }

                    if email:
                        log(f"    ✓ {name} ({email})")
                    else:
                        log(f"    📝 {name} (no email)")

                    all_leads.append(lead)
                    time.sleep(0.1)  # Rate limiting

            except Exception as e:
                log(f"    ✗ Error: {e}")
                continue

    return all_leads

def save_leads(leads, service_json, crm_sheet_id):
    """Save leads to Google Sheets."""
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
        sheet = client.open_by_key(crm_sheet_id)
        worksheet = sheet.sheet1

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
        log(f"  ✓ Saved {len(rows)} leads")
        return len(rows)

    except Exception as e:
        log(f"  ✗ Failed to save: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("☕ HARK COFFEE LEAD SCRAPER")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check for dry-run
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        log("🧪 DRY RUN MODE - Will not save to sheets")

    # Check environment
    env_ok, env_vars = check_env()
    if not env_ok:
        log("\n❌ Missing required environment variables!")
        return 1

    api_key = env_vars['GOOGLE_MAPS_API_KEY']
    service_json = env_vars['GOOGLE_SERVICE_ACCOUNT_JSON']
    sheet_id = env_vars['GOOGLE_SHEET_ID']
    crm_id = env_vars['CRM_SHEET_ID']

    # Test Google Maps API
    maps_ok, _ = test_google_maps_api(api_key)
    if not maps_ok:
        log("\n❌ Google Maps API not working!")
        log("→ Enable 'Places API' in Google Cloud Console")
        return 1

    # Test Sheets connection
    sheets_ok, exclusion_emails = test_sheets_connection(service_json, sheet_id)
    if not sheets_ok:
        log("\n❌ Google Sheets connection failed!")
        log("→ Check service account has access to the sheet")
        return 1

    # Scrape leads
    leads = scrape_leads(api_key, exclusion_emails)

    # Summary
    log("\n" + "=" * 60)
    log("SUMMARY")
    log("=" * 60)
    log(f"  Total leads found: {len(leads)}")
    log(f"  With email: {len([l for l in leads if l.get('email')])}")
    log(f"  Without email: {len([l for l in leads if not l.get('email')])}")

    # Save
    if leads and not dry_run:
        saved = save_leads(leads, service_json, crm_id)
        log(f"  Saved to CRM: {saved}")
    elif dry_run:
        log("  🧪 Dry run - not saving")

    log(f"\n✅ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
