#!/usr/bin/env python3
"""
Coffee Lead CRM - Main Scraper Script
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════╗
║   ☕ HARK COFFEE - Lead Scraper                          ║
║   Finding new coffee-loving offices in Adelaide          ║
╚═══════════════════════════════════════════════════════════╝
    """)


def run_scraper(dry_run=False, category_filter=None, max_per_category=20):
    print_banner()
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 Target: Adelaide, South Australia")
    print(f"🧪 Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("-" * 60)

    # Check environment variables
    print("\n🔧 CHECKING CONFIGURATION:")
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    service_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    crm_id = os.getenv('CRM_SHEET_ID')

    print(f"   GOOGLE_MAPS_API_KEY: {'✓ Set' if api_key else '✗ MISSING'}")
    print(f"   GOOGLE_SERVICE_ACCOUNT_JSON: {'✓ Set' if service_json else '✗ MISSING'}")
    print(f"   GOOGLE_SHEET_ID: {'✓ Set' if sheet_id else '✗ MISSING'}")
    print(f"   CRM_SHEET_ID: {'✓ Set' if crm_id else '✗ MISSING'}")

    if not api_key:
        print("\n❌ ERROR: GOOGLE_MAPS_API_KEY is required!")
        return 1

    if not service_json:
        print("\n❌ ERROR: GOOGLE_SERVICE_ACCOUNT_JSON is required!")
        return 1

    # Initialize Google Sheets
    print("\n📊 CONNECTING TO GOOGLE SHEETS...")
    try:
        from sheets.sheets_client import SheetsClient
        sheets = SheetsClient()
        print("   ✓ Connected to Google Sheets")
    except Exception as e:
        print(f"   ✗ Failed to connect: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Load exclusion list
    print("\n📋 LOADING EXCLUSION LIST...")
    try:
        exclusion_emails = sheets.get_exclusion_emails()
        print(f"   ✓ Loaded {len(exclusion_emails)} emails to exclude")
        if exclusion_emails:
            sample = list(exclusion_emails)[:3]
            print(f"   Sample: {sample}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        exclusion_emails = set()

    # Initialize Google Maps scraper
    print("\n🗺️ INITIALIZING GOOGLE MAPS API...")
    try:
        from scraper.places_scraper import PlacesScraper
        scraper = PlacesScraper()
        print("   ✓ Google Maps API ready")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Run the scraper
    print("\n" + "=" * 60)
    print("🔍 STARTING SEARCH")
    print("=" * 60)

    try:
        new_leads = scraper.search_all_categories(
            exclusion_emails=exclusion_emails,
            max_per_category=max_per_category
        )
    except Exception as e:
        print(f"\n✗ Scraper error: {e}")
        import traceback
        traceback.print_exc()
        new_leads = []

    # Summary
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    print(f"   New leads found: {len(new_leads)}")

    if new_leads:
        by_category = {}
        for lead in new_leads:
            cat = lead.get('industry', 'Unknown')
            by_category.setdefault(cat, []).append(lead)

        print("\n   By category:")
        for cat, leads in sorted(by_category.items()):
            print(f"   • {cat}: {len(leads)}")

        print("\n   Sample leads:")
        for lead in new_leads[:5]:
            print(f"   • {lead['business_name']} ({lead.get('email', 'NO EMAIL')})")

        if not dry_run:
            print("\n💾 SAVING TO CRM...")
            try:
                saved = sheets.add_multiple_leads(new_leads)
                print(f"   ✓ Saved {saved} leads")
            except Exception as e:
                print(f"   ✗ Failed to save: {e}")
        else:
            print("\n🧪 Dry run - skipping save")
    else:
        print("\n   No new leads found")

    print("\n" + "-" * 60)
    print(f"✅ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return 0


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description='Hark Coffee Lead Scraper')
    parser.add_argument('--dry-run', action='store_true', help='Test without saving')
    parser.add_argument('--category', type=str, help='Single category only')
    parser.add_argument('--max', type=int, default=20, help='Max per search term')

    args = parser.parse_args()
    return run_scraper(dry_run=args.dry_run, category_filter=args.category, max_per_category=args.max)


if __name__ == '__main__':
    sys.exit(main())
