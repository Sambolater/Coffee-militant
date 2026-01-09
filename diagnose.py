#!/usr/bin/env python3
"""
Diagnostic script - tests ALL connections before scraping.
Run this locally to find exactly what's broken.
"""

import os
import sys
import json

def test_env():
    """Check environment variables."""
    print("\n=== 1. ENVIRONMENT VARIABLES ===")

    required = {
        'GOOGLE_MAPS_API_KEY': os.getenv('GOOGLE_MAPS_API_KEY'),
        'GOOGLE_SERVICE_ACCOUNT_JSON': os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON'),
        'GOOGLE_SHEET_ID': os.getenv('GOOGLE_SHEET_ID'),
        'CRM_SHEET_ID': os.getenv('CRM_SHEET_ID'),
    }

    all_ok = True
    for key, val in required.items():
        if val:
            print(f"  OK: {key} = {val[:30]}...")
        else:
            print(f"  MISSING: {key}")
            all_ok = False

    return all_ok, required

def test_maps_api(api_key):
    """Test Google Maps API."""
    print("\n=== 2. GOOGLE MAPS API ===")

    import requests
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {'query': 'accountant Adelaide', 'key': api_key}

    resp = requests.get(url, params=params, timeout=30)
    data = resp.json()
    status = data.get('status')

    if status == 'OK':
        print(f"  OK: Found {len(data.get('results', []))} results")
        return True
    else:
        print(f"  FAILED: {status}")
        print(f"  Error: {data.get('error_message', 'unknown')}")
        return False

def test_exclusion_sheet(service_json, sheet_id):
    """Test exclusion sheet (GOOGLE_SHEET_ID)."""
    print("\n=== 3. EXCLUSION SHEET ===")
    print(f"  Sheet ID: {sheet_id}")

    import gspread
    from google.oauth2.service_account import Credentials

    creds_dict = json.loads(service_json)
    print(f"  Service account: {creds_dict.get('client_email')}")

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    client = gspread.authorize(creds)

    try:
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.sheet1
        rows = len(worksheet.get_all_values())
        print(f"  OK: Opened sheet, {rows} rows")
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

def test_crm_sheet(service_json, crm_id):
    """Test CRM sheet (CRM_SHEET_ID) - THIS IS WHERE LEADS GO."""
    print("\n=== 4. CRM SHEET (where leads are saved) ===")
    print(f"  Sheet ID: {crm_id}")

    import gspread
    from google.oauth2.service_account import Credentials

    creds_dict = json.loads(service_json)
    print(f"  Service account: {creds_dict.get('client_email')}")

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    client = gspread.authorize(creds)

    try:
        sheet = client.open_by_key(crm_id)
        worksheet = sheet.sheet1
        rows = len(worksheet.get_all_values())
        print(f"  OK: Opened sheet, {rows} rows")

        # Try to write a test row
        print("  Testing write access...")
        worksheet.append_row(["TEST", "DELETE THIS ROW", "", "", "", "", "", "", ""])
        print("  OK: Write successful! Delete the test row from your sheet.")
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        print("\n  *** THIS IS YOUR PROBLEM ***")
        print("  The bot cannot write to your CRM sheet.")
        print(f"  Share this sheet with: {creds_dict.get('client_email')}")
        return False

def main():
    print("=" * 60)
    print("HARK COFFEE - DIAGNOSTIC TEST")
    print("=" * 60)

    # 1. Check env
    env_ok, env = test_env()
    if not env_ok:
        print("\nFix missing environment variables first.")
        return 1

    # 2. Test Maps API
    if not test_maps_api(env['GOOGLE_MAPS_API_KEY']):
        return 1

    # 3. Test exclusion sheet
    if not test_exclusion_sheet(env['GOOGLE_SERVICE_ACCOUNT_JSON'], env['GOOGLE_SHEET_ID']):
        return 1

    # 4. Test CRM sheet
    if not test_crm_sheet(env['GOOGLE_SERVICE_ACCOUNT_JSON'], env['CRM_SHEET_ID']):
        return 1

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print("If the workflow still fails, check GitHub Actions logs.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
