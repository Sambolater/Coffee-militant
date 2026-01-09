# Existing Contacts Spreadsheet Reference

## Source
**Google Sheet:** https://docs.google.com/spreadsheets/d/15JmjQjjQIfhY0zKMzqBlvMMRGgJf3VFVgpOut_DG49s/

## Column Structure

| Column | Header | Description | Example |
|--------|--------|-------------|---------|
| A | Business Name | Company name | "TTO Financial Solutions" |
| B | Industry | Business category | "Accounting" |
| C | Contact Email | Primary email | "info@ttoca.com.au" |
| D | Physical Address | Full address | "234 Sturt St, Adelaide SA 5000" |
| E | Phone Number | Contact phone | "(08) 8211 9426" |

## Industry Categories Found

| Industry | Approx Count |
|----------|--------------|
| Accounting | 40+ |
| Wealth Management | 25+ |
| Lawyers | 25+ |
| Real Estate | 25+ |
| Architects | 20+ |
| Marketing | 20+ |
| Interior Design | 15+ |
| Branding | 10+ |
| Agencies | 10+ |
| Other Office | 30+ |

**Total:** ~220 businesses already contacted

## Usage in System

The scraper should:
1. Connect to this Google Sheet via API
2. Extract all emails from Column C
3. Before sending any new outreach, check if the email already exists
4. If email exists → SKIP (already contacted)
5. If email doesn't exist → OK to contact

## Sample Emails to Exclude

These are examples from the existing list (DO NOT contact again):

```
info@ttoca.com.au
no_reply@cpaaustralia.com.au
services@anchorwealth.com.au
accounting@ashmans.com.au
info@pkf.com.au
info@nationalaccounts.com.au
info@sa.nexia.com.au
saki@thetotal.com.au
hello@readymag.com
admin@themoneymatrix.net.au
info@shawandpartners.com.au
info@calmwealth.com.au
office@sawealthgroup.com.au
sally@archaea.com.au
adelaide@dasharchitects.com.au
design@isotta.au
wba@walterbrooke.com.au
hello@freshhouseco.com.au
info@giainterior.com.au
julia@julberry.design
hello@styledhomestaging.com.au
info@designthink.com.au
hello@neontreehouse.com
marketing@purplegiraffe.com.au
info@marketingsweet.com.au
info@figtreedigital.com.au
marketing@lustosamarketing.com
paul@roundhousestudio.com.au
hello@neuestudio.com.au
info@blacksquid.com.au
info@studioband.com.au
info@digitalmarketingadelaide.com.au
info@framecreative.com.au
info@tuckercreative.com
mail@wowcreative.com.au
hello@profilerpr.com.au
info@stanlaw.com.au
mail@johnstonwithers.com.au
lawyers@woodslaw.com.au
tgb@tgb.com.au
info@alslaw.com.au
enquiry@andersons.com.au
info@turnerrealestate.com.au
info@refuelcreative.com.au
korn@korn.com.au
fox@foxrealestate.com.au
info@harcourts.net
info@belleproperty.com
admin@discoveryparks.com.au
info@gpoexchange.com.au
info@bhp.com
enquiries@tabcorp.com.au
enquiry@versace.vbs.com.au
management@treehousefp.com.au
```

*(Full list of 220+ emails in original Google Sheet)*

---

*Last Updated: 2026-01-09*
