"""
Google Maps Places Scraper for Coffee Lead CRM

This module searches Google Maps for businesses and extracts their details.
Think of it as a robot that goes to Google Maps, searches for "accountants in Adelaide",
and writes down all the business names, addresses, and contact info it finds.

Important: Google Maps doesn't always give emails directly, so we also
visit business websites to find their contact email.
"""

import os
import json
import time
import requests
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin
import re


class PlacesScraper:
    """
    Scrapes business information from Google Maps Places API.

    Usage:
        scraper = PlacesScraper()
        businesses = scraper.search_businesses("accountant", "Adelaide, SA")
    """

    # Google Places API endpoints
    PLACES_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the scraper with Google Maps API key.

        Args:
            api_key: Google Maps API key. If not provided, reads from environment.
        """
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')

        if not self.api_key:
            raise ValueError(
                "Google Maps API key not found. "
                "Set GOOGLE_MAPS_API_KEY environment variable."
            )

        # Load search configuration
        self.config = self._load_config()

        # Rate limiting: be nice to Google's servers
        self.request_delay = 0.2  # 200ms between requests

    def _load_config(self) -> Dict:
        """Load search configuration from JSON file."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'config', 'search_terms.json'
        )

        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default config if file not found
            return {
                "location": {
                    "city": "Adelaide",
                    "state": "South Australia",
                    "country": "Australia"
                },
                "exclude_types": ["cafe", "restaurant", "coffee_shop"]
            }

    def search_businesses(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 60
    ) -> List[Dict]:
        """
        Search for businesses matching the query.

        Args:
            query: Search term (e.g., "accountant", "real estate agent")
            location: Location to search in (default: from config)
            max_results: Maximum number of results (Google returns max 60)

        Returns:
            List of business dictionaries with basic info
        """
        if location is None:
            loc = self.config.get('location', {})
            location = f"{loc.get('city', 'Adelaide')}, {loc.get('state', 'SA')}"

        full_query = f"{query} in {location}"
        print(f"🔍 Searching: {full_query}")

        businesses = []
        next_page_token = None

        while len(businesses) < max_results:
            # Build request parameters
            params = {
                'query': full_query,
                'key': self.api_key,
            }

            if next_page_token:
                params['pagetoken'] = next_page_token
                # Google requires a short delay before using page token
                time.sleep(2)

            # Make the API request
            try:
                response = requests.get(self.PLACES_SEARCH_URL, params=params)
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as e:
                print(f"✗ API request failed: {e}")
                break

            # Check for errors
            if data.get('status') not in ['OK', 'ZERO_RESULTS']:
                print(f"✗ API error: {data.get('status')} - {data.get('error_message', '')}")
                break

            # Process results
            results = data.get('results', [])
            if not results:
                break

            for place in results:
                # Skip excluded business types (cafes, restaurants, etc.)
                place_types = place.get('types', [])
                if self._should_exclude(place_types):
                    continue

                business = {
                    'place_id': place.get('place_id'),
                    'business_name': place.get('name'),
                    'address': place.get('formatted_address'),
                    'types': place_types,
                    'rating': place.get('rating'),
                    'user_ratings_total': place.get('user_ratings_total'),
                }
                businesses.append(business)

            # Check for more pages
            next_page_token = data.get('next_page_token')
            if not next_page_token:
                break

            # Respect rate limits
            time.sleep(self.request_delay)

        print(f"✓ Found {len(businesses)} businesses")
        return businesses[:max_results]

    def _should_exclude(self, place_types: List[str]) -> bool:
        """Check if a place should be excluded based on its types."""
        exclude_types = self.config.get('exclude_types', [])
        return any(
            excluded in place_types
            for excluded in exclude_types
        )

    def get_place_details(self, place_id: str) -> Dict:
        """
        Get detailed information about a specific place.

        This includes phone number, website, and opening hours.

        Args:
            place_id: Google Places ID

        Returns:
            Dictionary with detailed business info
        """
        params = {
            'place_id': place_id,
            'fields': 'name,formatted_address,formatted_phone_number,website,opening_hours,types,business_status',
            'key': self.api_key,
        }

        try:
            response = requests.get(self.PLACES_DETAILS_URL, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"✗ Details request failed: {e}")
            return {}

        if data.get('status') != 'OK':
            return {}

        result = data.get('result', {})
        time.sleep(self.request_delay)

        return {
            'business_name': result.get('name'),
            'address': result.get('formatted_address'),
            'phone': result.get('formatted_phone_number'),
            'website': result.get('website'),
            'types': result.get('types', []),
            'business_status': result.get('business_status'),
        }

    def find_email_from_website(self, website_url: str) -> Optional[str]:
        """
        Attempt to find an email address from a business website.

        This visits the website and looks for email patterns on:
        - The homepage
        - The contact page
        - The about page

        Args:
            website_url: URL of the business website

        Returns:
            Email address if found, None otherwise
        """
        if not website_url:
            return None

        # Common pages to check for contact info
        pages_to_check = [
            '',  # Homepage
            '/contact',
            '/contact-us',
            '/about',
            '/about-us',
        ]

        # Email regex pattern
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

        # Emails to skip (generic, not useful)
        skip_emails = {
            'example@example.com',
            'email@example.com',
            'your@email.com',
            'info@example.com',
            'noreply@',
            'no-reply@',
        }

        found_emails = set()

        for page in pages_to_check:
            url = urljoin(website_url, page)

            try:
                response = requests.get(
                    url,
                    timeout=10,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (compatible; HarkCoffeeCRM/1.0)'
                    }
                )

                if response.status_code != 200:
                    continue

                # Find all email addresses in the page
                emails = re.findall(email_pattern, response.text)

                for email in emails:
                    email_lower = email.lower()
                    # Skip generic/useless emails
                    if any(skip in email_lower for skip in skip_emails):
                        continue
                    # Skip image files mistakenly matched
                    if email_lower.endswith(('.png', '.jpg', '.gif', '.svg')):
                        continue
                    found_emails.add(email_lower)

            except requests.RequestException:
                continue

            time.sleep(self.request_delay)

        # Prefer info@ or contact@ or enquiry@ emails
        priority_prefixes = ['info@', 'contact@', 'enquiry@', 'enquiries@', 'hello@', 'admin@']

        for prefix in priority_prefixes:
            for email in found_emails:
                if email.startswith(prefix):
                    return email

        # Return any email found
        if found_emails:
            return list(found_emails)[0]

        return None

    def scrape_full_lead(self, place_id: str, category: str = '') -> Optional[Dict]:
        """
        Get complete lead information for a business.

        Combines Places API details with website email scraping.

        Args:
            place_id: Google Places ID
            category: Business category (e.g., "Accounting")

        Returns:
            Complete lead dictionary, or None if essential data missing
        """
        # Get details from Google
        details = self.get_place_details(place_id)

        if not details or not details.get('business_name'):
            return None

        # Try to find email from website
        email = None
        website = details.get('website')
        if website:
            email = self.find_email_from_website(website)

        # Build the lead record
        lead = {
            'business_name': details.get('business_name'),
            'industry': category,
            'email': email or '',
            'address': details.get('address', ''),
            'phone': details.get('phone', ''),
            'website': website or '',
            'status': 'new',
            'source': 'google_maps',
        }

        return lead

    def search_all_categories(
        self,
        exclusion_emails: Set[str] = None,
        max_per_category: int = 20
    ) -> List[Dict]:
        """
        Search for businesses in all configured categories.

        Args:
            exclusion_emails: Set of emails to skip (already contacted)
            max_per_category: Max results per search term

        Returns:
            List of new leads (not in exclusion list)
        """
        if exclusion_emails is None:
            exclusion_emails = set()

        all_leads = []
        seen_place_ids = set()

        categories = self.config.get('target_businesses', [])

        for category_config in categories:
            category = category_config.get('category', 'Unknown')
            search_terms = category_config.get('search_terms', [])

            print(f"\n📁 Category: {category}")

            for term in search_terms:
                # Search for businesses
                businesses = self.search_businesses(term, max_results=max_per_category)

                for biz in businesses:
                    place_id = biz.get('place_id')

                    # Skip if already processed
                    if place_id in seen_place_ids:
                        continue
                    seen_place_ids.add(place_id)

                    # Get full details
                    lead = self.scrape_full_lead(place_id, category)

                    if not lead:
                        continue

                    # Skip if no email found
                    if not lead.get('email'):
                        print(f"  ⚠ No email: {lead['business_name']}")
                        continue

                    # Skip if in exclusion list
                    if lead['email'].lower() in exclusion_emails:
                        print(f"  ⏭ Already contacted: {lead['business_name']}")
                        continue

                    print(f"  ✓ New lead: {lead['business_name']} ({lead['email']})")
                    all_leads.append(lead)

        print(f"\n📊 Total new leads found: {len(all_leads)}")
        return all_leads


# Quick test when run directly
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    print("Testing Places Scraper...")
    scraper = PlacesScraper()

    # Test a simple search
    results = scraper.search_businesses("accountant", "Adelaide, SA", max_results=5)

    for biz in results:
        print(f"\n{biz['business_name']}")
        print(f"  Address: {biz['address']}")

        # Get details
        if biz.get('place_id'):
            details = scraper.get_place_details(biz['place_id'])
            print(f"  Phone: {details.get('phone', 'N/A')}")
            print(f"  Website: {details.get('website', 'N/A')}")
