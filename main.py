#!/usr/bin/env python3
"""
Coffee Lead CRM - Main Scraper Script

This is the main entry point for the lead scraping system.
It connects Google Maps scraping with Google Sheets storage.

What it does:
1. Loads your existing contacts (exclusion list)
2. Searches Google Maps for target businesses
3. Finds email addresses from business websites
4. Filters out already-contacted businesses
5. Saves new leads to your CRM sheet

Usage:
    python main.py                    # Run full scrape
    python main.py --dry-run          # Test without saving
    python main.py --category "Accounting"  # Single category
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sheets.sheets_client import SheetsClient
from scraper.places_scraper import PlacesScraper


def print_banner():
    """Print a nice startup banner."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ☕ HARK COFFEE - Lead Scraper                          ║
║   Finding new coffee-loving offices in Adelaide          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)


def run_scraper(
    dry_run: bool = False,
    category_filter: str = None,
    max_per_category: int = 20
):
    """
    Main scraping function.

    Args:
        dry_run: If True, don't save to sheets (just show what would be found)
        category_filter: Only scrape this category (e.g., "Accounting")
        max_per_category: Maximum leads to find per search term
    """
    print_banner()
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 Target: Adelaide, South Australia")
    print(f"{'🧪 DRY RUN MODE - Not saving to sheets' if dry_run else '💾 Will save new leads to CRM'}")
    print("-" * 60)

    # Initialize clients
    try:
        print("\n📊 Connecting to Google Sheets...")
        sheets = SheetsClient()

        print("🔑 Initializing Google Maps API...")
        scraper = PlacesScraper()
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return 1

    # Load exclusion list
    print("\n📋 Loading exclusion list (already contacted businesses)...")
    exclusion_emails = sheets.get_exclusion_emails()
    print(f"   Found {len(exclusion_emails)} emails to exclude")

    # Filter categories if specified
    if category_filter:
        # Modify scraper config to only include matching category
        original_categories = scraper.config.get('target_businesses', [])
        scraper.config['target_businesses'] = [
            cat for cat in original_categories
            if cat.get('category', '').lower() == category_filter.lower()
        ]
        if not scraper.config['target_businesses']:
            print(f"✗ Category '{category_filter}' not found in config")
            return 1
        print(f"🎯 Filtering to category: {category_filter}")

    # Run the scraper
    print("\n" + "=" * 60)
    print("🔍 STARTING SEARCH")
    print("=" * 60)

    new_leads = scraper.search_all_categories(
        exclusion_emails=exclusion_emails,
        max_per_category=max_per_category
    )

    # Summary
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    print(f"   New leads found: {len(new_leads)}")

    if new_leads:
        # Group by category
        by_category = {}
        for lead in new_leads:
            cat = lead.get('industry', 'Unknown')
            by_category.setdefault(cat, []).append(lead)

        print("\n   By category:")
        for cat, leads in sorted(by_category.items()):
            print(f"   • {cat}: {len(leads)}")

        # Show sample leads
        print("\n   Sample leads:")
        for lead in new_leads[:5]:
            print(f"   • {lead['business_name']} ({lead['email']})")

        # Save to CRM (unless dry run)
        if not dry_run:
            print("\n💾 Saving to CRM sheet...")
            saved = sheets.add_multiple_leads(new_leads)
            print(f"   ✓ Saved {saved} leads to CRM")
        else:
            print("\n🧪 Dry run - skipping save")

    else:
        print("\n   No new leads found (all businesses may already be contacted)")

    print("\n" + "-" * 60)
    print(f"✅ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return 0


def main():
    """Parse arguments and run the scraper."""
    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Hark Coffee Lead Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                        Run full scrape
  python main.py --dry-run              Test without saving
  python main.py --category Accounting  Only scrape accountants
  python main.py --max 10               Limit to 10 per search term
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without saving to Google Sheets'
    )

    parser.add_argument(
        '--category',
        type=str,
        help='Only scrape a specific category (e.g., "Accounting")'
    )

    parser.add_argument(
        '--max',
        type=int,
        default=20,
        help='Maximum results per search term (default: 20)'
    )

    args = parser.parse_args()

    # Run the scraper
    return run_scraper(
        dry_run=args.dry_run,
        category_filter=args.category,
        max_per_category=args.max
    )


if __name__ == '__main__':
    sys.exit(main())
