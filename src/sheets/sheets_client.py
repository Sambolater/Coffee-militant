"""
Google Sheets Client for Coffee Lead CRM

This module handles all interactions with Google Sheets:
- Reading existing contacts (exclusion list)
- Writing new leads to the CRM sheet
- Updating lead statuses

Think of this as your "filing cabinet assistant" that reads and organizes
all your lead data in Google Sheets.
"""

import os
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional, Set
import json


class SheetsClient:
    """
    Connects to Google Sheets and manages lead data.

    Usage:
        client = SheetsClient()
        existing_emails = client.get_exclusion_emails()
        client.add_new_lead(lead_data)
    """

    # Google Sheets API permissions we need
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.readonly'
    ]

    def __init__(self):
        """
        Initialize the Sheets client.
        Connects to Google using service account credentials.
        """
        self.client = self._authenticate()

        # Sheet IDs from environment
        # GOOGLE_SHEET_ID = existing contacts (exclusion list)
        # CRM_SHEET_ID = new leads sheet
        self.exclusion_sheet_id = os.getenv(
            'GOOGLE_SHEET_ID',  # Using your existing secret name
            '15JmjQjjQIfhY0zKMzqBlvMMRGgJf3VFVgpOut_DG49s'
        )
        self.crm_sheet_id = os.getenv('CRM_SHEET_ID')

        # Cache for exclusion emails (so we don't keep re-reading)
        self._exclusion_cache: Optional[Set[str]] = None

    def _authenticate(self) -> gspread.Client:
        """
        Authenticate with Google using service account.

        Returns:
            Authenticated gspread client
        """
        # Try to get credentials from environment variable (for GitHub Actions)
        creds_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')

        if creds_json:
            # If it's a path to a file
            if os.path.exists(creds_json):
                creds = Credentials.from_service_account_file(
                    creds_json,
                    scopes=self.SCOPES
                )
            else:
                # If it's the JSON content itself (from GitHub Secrets)
                try:
                    creds_dict = json.loads(creds_json)
                    creds = Credentials.from_service_account_info(
                        creds_dict,
                        scopes=self.SCOPES
                    )
                except json.JSONDecodeError:
                    raise ValueError(
                        "GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON or a valid file path"
                    )
        else:
            # Try default locations
            default_paths = [
                'service-account.json',
                'credentials.json',
                os.path.expanduser('~/.config/gspread/service_account.json')
            ]

            for path in default_paths:
                if os.path.exists(path):
                    creds = Credentials.from_service_account_file(
                        path,
                        scopes=self.SCOPES
                    )
                    break
            else:
                raise FileNotFoundError(
                    "No Google service account credentials found. "
                    "Please set GOOGLE_SERVICE_ACCOUNT_JSON environment variable "
                    "or place service-account.json in the project root."
                )

        return gspread.authorize(creds)

    def get_exclusion_emails(self, force_refresh: bool = False) -> Set[str]:
        """
        Get all emails from the exclusion list (already contacted businesses).

        This reads Column C (Contact Email) from your existing contacts sheet.
        Results are cached to avoid repeated API calls.

        Args:
            force_refresh: If True, re-read from sheet even if cached

        Returns:
            Set of email addresses (lowercase) to exclude
        """
        if self._exclusion_cache is not None and not force_refresh:
            return self._exclusion_cache

        try:
            # Open the exclusion sheet
            sheet = self.client.open_by_key(self.exclusion_sheet_id)
            worksheet = sheet.sheet1  # First worksheet

            # Get all values from Column C (Contact Email)
            # Column C is index 3 (1-indexed in gspread)
            email_column = worksheet.col_values(3)

            # Skip header row, convert to lowercase, remove empty values
            emails = {
                email.lower().strip()
                for email in email_column[1:]  # Skip header
                if email and email.strip()
            }

            # Cache the results
            self._exclusion_cache = emails

            print(f"✓ Loaded {len(emails)} emails from exclusion list")
            return emails

        except Exception as e:
            print(f"✗ Error reading exclusion list: {e}")
            return set()

    def is_already_contacted(self, email: str) -> bool:
        """
        Check if an email is in the exclusion list.

        Args:
            email: Email address to check

        Returns:
            True if already contacted, False if new
        """
        exclusion_list = self.get_exclusion_emails()
        return email.lower().strip() in exclusion_list

    def add_new_lead(self, lead: Dict) -> bool:
        """
        Add a new lead to the CRM sheet.

        Args:
            lead: Dictionary with lead data:
                - business_name: str
                - industry: str
                - email: str
                - address: str
                - phone: str
                - website: str (optional)
                - status: str (default: 'new')
                - source: str (default: 'google_maps')

        Returns:
            True if added successfully, False otherwise
        """
        if not self.crm_sheet_id:
            print("✗ CRM_SHEET_ID not set. Cannot add lead.")
            return False

        try:
            sheet = self.client.open_by_key(self.crm_sheet_id)
            worksheet = sheet.sheet1

            # Prepare row data
            row = [
                lead.get('business_name', ''),
                lead.get('industry', ''),
                lead.get('email', ''),
                lead.get('address', ''),
                lead.get('phone', ''),
                lead.get('website', ''),
                lead.get('status', 'new'),
                lead.get('source', 'google_maps'),
                '',  # date_emailed
                '',  # email_status
                '',  # response
                '',  # notes
            ]

            # Append to sheet
            worksheet.append_row(row)
            print(f"✓ Added lead: {lead.get('business_name')}")
            return True

        except Exception as e:
            print(f"✗ Error adding lead: {e}")
            return False

    def add_multiple_leads(self, leads: List[Dict]) -> int:
        """
        Add multiple leads at once (more efficient than one at a time).

        Args:
            leads: List of lead dictionaries

        Returns:
            Number of leads successfully added
        """
        if not self.crm_sheet_id:
            print("✗ CRM_SHEET_ID not set. Cannot add leads.")
            return 0

        if not leads:
            return 0

        try:
            sheet = self.client.open_by_key(self.crm_sheet_id)
            worksheet = sheet.sheet1

            # Prepare all rows
            rows = []
            for lead in leads:
                row = [
                    lead.get('business_name', ''),
                    lead.get('industry', ''),
                    lead.get('email', ''),
                    lead.get('address', ''),
                    lead.get('phone', ''),
                    lead.get('website', ''),
                    lead.get('status', 'new'),
                    lead.get('source', 'google_maps'),
                    '',  # date_emailed
                    '',  # email_status
                    '',  # response
                    '',  # notes
                ]
                rows.append(row)

            # Append all rows at once
            worksheet.append_rows(rows)
            print(f"✓ Added {len(rows)} leads to CRM")
            return len(rows)

        except Exception as e:
            print(f"✗ Error adding leads: {e}")
            return 0

    def update_lead_status(self, email: str, status: str, notes: str = '') -> bool:
        """
        Update the status of a lead by email.

        Args:
            email: Email of the lead to update
            status: New status value
            notes: Optional notes to add

        Returns:
            True if updated, False if not found or error
        """
        if not self.crm_sheet_id:
            print("✗ CRM_SHEET_ID not set.")
            return False

        try:
            sheet = self.client.open_by_key(self.crm_sheet_id)
            worksheet = sheet.sheet1

            # Find the row with this email (Column C)
            cell = worksheet.find(email, in_column=3)

            if cell:
                # Update status (Column G) and notes (Column L)
                worksheet.update_cell(cell.row, 7, status)
                if notes:
                    worksheet.update_cell(cell.row, 12, notes)
                print(f"✓ Updated {email} to status: {status}")
                return True
            else:
                print(f"✗ Email not found: {email}")
                return False

        except Exception as e:
            print(f"✗ Error updating lead: {e}")
            return False

    def get_leads_by_status(self, status: str) -> List[Dict]:
        """
        Get all leads with a specific status.

        Args:
            status: Status to filter by (e.g., 'waiting_sample', 'delivered')

        Returns:
            List of lead dictionaries
        """
        if not self.crm_sheet_id:
            return []

        try:
            sheet = self.client.open_by_key(self.crm_sheet_id)
            worksheet = sheet.sheet1

            # Get all records
            records = worksheet.get_all_records()

            # Filter by status
            filtered = [
                record for record in records
                if record.get('status', '').lower() == status.lower()
            ]

            return filtered

        except Exception as e:
            print(f"✗ Error getting leads: {e}")
            return []


# Quick test when run directly
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    print("Testing Sheets Client...")
    client = SheetsClient()

    # Test exclusion list
    emails = client.get_exclusion_emails()
    print(f"Found {len(emails)} emails in exclusion list")

    # Show a few examples
    sample = list(emails)[:5]
    print(f"Sample emails: {sample}")
