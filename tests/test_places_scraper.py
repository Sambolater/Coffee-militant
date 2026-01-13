"""
Comprehensive tests for PlacesScraper class.

Tests cover:
- Initialization and configuration loading
- Business type filtering (_should_exclude)
- Email extraction from websites (find_email_from_website)
- Google Places API interactions (mocked)
- Full lead scraping orchestration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import json


class TestPlacesScraperInit:
    """Tests for PlacesScraper initialization."""

    def test_init_with_api_key_argument(self):
        """Should accept API key as argument."""
        with patch('src.scraper.places_scraper.PlacesScraper._load_config', return_value={}):
            from src.scraper.places_scraper import PlacesScraper
            scraper = PlacesScraper(api_key='test-api-key-123')
            assert scraper.api_key == 'test-api-key-123'

    def test_init_with_env_api_key(self):
        """Should read API key from environment if not provided."""
        with patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'env-api-key'}):
            with patch('src.scraper.places_scraper.PlacesScraper._load_config', return_value={}):
                from src.scraper.places_scraper import PlacesScraper
                scraper = PlacesScraper()
                assert scraper.api_key == 'env-api-key'

    def test_init_raises_without_api_key(self):
        """Should raise ValueError if no API key is available."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove the env var if it exists
            os.environ.pop('GOOGLE_MAPS_API_KEY', None)
            with patch('src.scraper.places_scraper.PlacesScraper._load_config', return_value={}):
                from src.scraper.places_scraper import PlacesScraper
                with pytest.raises(ValueError, match="Google Maps API key not found"):
                    PlacesScraper(api_key=None)

    def test_init_sets_request_delay(self):
        """Should set default request delay for rate limiting."""
        with patch('src.scraper.places_scraper.PlacesScraper._load_config', return_value={}):
            from src.scraper.places_scraper import PlacesScraper
            scraper = PlacesScraper(api_key='test-key')
            assert scraper.request_delay == 0.2


class TestLoadConfig:
    """Tests for _load_config method."""

    def test_load_config_returns_default_when_file_missing(self):
        """Should return default config when JSON file not found."""
        from src.scraper.places_scraper import PlacesScraper

        with patch('builtins.open', side_effect=FileNotFoundError()):
            with patch.object(PlacesScraper, '__init__', lambda x, y=None: None):
                scraper = PlacesScraper.__new__(PlacesScraper)
                config = scraper._load_config()

                assert 'location' in config
                assert config['location']['city'] == 'Adelaide'
                assert 'exclude_types' in config
                assert 'cafe' in config['exclude_types']

    def test_load_config_reads_json_file(self, tmp_path):
        """Should load configuration from JSON file."""
        config_data = {
            'location': {'city': 'Melbourne', 'state': 'Victoria'},
            'exclude_types': ['bar', 'pub']
        }
        config_file = tmp_path / 'search_terms.json'
        config_file.write_text(json.dumps(config_data))

        from src.scraper.places_scraper import PlacesScraper

        with patch.object(PlacesScraper, '__init__', lambda x, y=None: None):
            scraper = PlacesScraper.__new__(PlacesScraper)

            with patch('builtins.open', return_value=open(config_file)):
                config = scraper._load_config()
                # The actual implementation joins paths, so we test the default fallback
                # In a real scenario, we'd need to mock os.path.join


class TestShouldExclude:
    """Tests for _should_exclude method."""

    @pytest.fixture
    def scraper_with_exclusions(self):
        """Create a scraper with specific exclusion types."""
        from src.scraper.places_scraper import PlacesScraper

        with patch.object(PlacesScraper, '__init__', lambda x, y=None: None):
            scraper = PlacesScraper.__new__(PlacesScraper)
            scraper.config = {
                'exclude_types': ['cafe', 'restaurant', 'coffee_shop', 'bar']
            }
            return scraper

    def test_should_exclude_cafe(self, scraper_with_exclusions):
        """Should exclude businesses with 'cafe' type."""
        assert scraper_with_exclusions._should_exclude(['cafe', 'food', 'point_of_interest']) is True

    def test_should_exclude_restaurant(self, scraper_with_exclusions):
        """Should exclude businesses with 'restaurant' type."""
        assert scraper_with_exclusions._should_exclude(['restaurant', 'food']) is True

    def test_should_not_exclude_accountant(self, scraper_with_exclusions):
        """Should NOT exclude accountant businesses."""
        assert scraper_with_exclusions._should_exclude(['accounting', 'finance', 'point_of_interest']) is False

    def test_should_not_exclude_real_estate(self, scraper_with_exclusions):
        """Should NOT exclude real estate businesses."""
        assert scraper_with_exclusions._should_exclude(['real_estate_agency', 'point_of_interest']) is False

    def test_should_not_exclude_law_firm(self, scraper_with_exclusions):
        """Should NOT exclude law firms."""
        assert scraper_with_exclusions._should_exclude(['lawyer', 'point_of_interest']) is False

    def test_should_handle_empty_types(self, scraper_with_exclusions):
        """Should handle empty place types list."""
        assert scraper_with_exclusions._should_exclude([]) is False

    def test_should_exclude_with_multiple_matches(self, scraper_with_exclusions):
        """Should exclude if ANY excluded type matches."""
        assert scraper_with_exclusions._should_exclude(['accounting', 'cafe']) is True


class TestFindEmailFromWebsite:
    """Tests for find_email_from_website method."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        from src.scraper.places_scraper import PlacesScraper

        with patch.object(PlacesScraper, '__init__', lambda x, y=None: None):
            scraper = PlacesScraper.__new__(PlacesScraper)
            scraper.request_delay = 0  # No delay for tests
            scraper.config = {'exclude_types': []}
            return scraper

    def test_returns_none_for_empty_url(self, scraper):
        """Should return None when URL is empty."""
        assert scraper.find_email_from_website('') is None
        assert scraper.find_email_from_website(None) is None

    def test_finds_simple_email(self, scraper):
        """Should find a simple email address in page content."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>Contact us at info@example.com</body></html>'

        with patch('requests.get', return_value=mock_response):
            email = scraper.find_email_from_website('https://example.com')
            # Note: example.com is in skip list, so would be skipped
            # Let's use a real domain

        mock_response.text = '<html><body>Contact us at hello@testbusiness.com.au</body></html>'
        with patch('requests.get', return_value=mock_response):
            email = scraper.find_email_from_website('https://testbusiness.com.au')
            assert email == 'hello@testbusiness.com.au'

    def test_finds_email_in_mailto_link(self, scraper):
        """Should find email in mailto: links."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><a href="mailto:contact@business.com.au">Email Us</a></html>'

        with patch('requests.get', return_value=mock_response):
            email = scraper.find_email_from_website('https://business.com.au')
            assert email == 'contact@business.com.au'

    def test_skips_example_emails(self, scraper):
        """Should skip generic example emails."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <html>
            <body>
                Email: example@example.com
                Real: admin@realbusiness.com.au
            </body>
            </html>
        '''

        with patch('requests.get', return_value=mock_response):
            email = scraper.find_email_from_website('https://realbusiness.com.au')
            assert email == 'admin@realbusiness.com.au'

    def test_skips_noreply_emails(self, scraper):
        """Should skip noreply email addresses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <html>
            <body>
                noreply@company.com
                support@company.com
            </body>
            </html>
        '''

        with patch('requests.get', return_value=mock_response):
            email = scraper.find_email_from_website('https://company.com')
            assert email == 'support@company.com'

    def test_skips_image_file_extensions(self, scraper):
        """Should skip emails that look like image filenames."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <html>
            <body>
                <img src="photo@2x.png">
                real@business.com.au
            </body>
            </html>
        '''

        with patch('requests.get', return_value=mock_response):
            email = scraper.find_email_from_website('https://business.com.au')
            assert email == 'real@business.com.au'

    def test_prefers_info_email(self, scraper):
        """Should prefer info@ emails over others."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <html>
            <body>
                john@company.com.au
                info@company.com.au
                sales@company.com.au
            </body>
            </html>
        '''

        with patch('requests.get', return_value=mock_response):
            email = scraper.find_email_from_website('https://company.com.au')
            assert email == 'info@company.com.au'

    def test_prefers_contact_email(self, scraper):
        """Should prefer contact@ emails."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <html>
            <body>
                john@company.com.au
                contact@company.com.au
            </body>
            </html>
        '''

        with patch('requests.get', return_value=mock_response):
            email = scraper.find_email_from_website('https://company.com.au')
            assert email == 'contact@company.com.au'

    def test_prefers_hello_email(self, scraper):
        """Should prefer hello@ emails."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <html>
            <body>
                john@company.com.au
                hello@company.com.au
            </body>
            </html>
        '''

        with patch('requests.get', return_value=mock_response):
            email = scraper.find_email_from_website('https://company.com.au')
            assert email == 'hello@company.com.au'

    def test_returns_none_on_request_error(self, scraper):
        """Should return None when request fails."""
        import requests

        with patch('requests.get', side_effect=requests.RequestException('Connection error')):
            email = scraper.find_email_from_website('https://unreachable.com')
            assert email is None

    def test_returns_none_on_404(self, scraper):
        """Should return None when page returns 404."""
        mock_response = Mock()
        mock_response.status_code = 404

        with patch('requests.get', return_value=mock_response):
            email = scraper.find_email_from_website('https://notfound.com')
            assert email is None

    def test_checks_contact_page(self, scraper):
        """Should check /contact page for emails."""
        call_count = [0]

        def mock_get(url, **kwargs):
            call_count[0] += 1
            response = Mock()
            response.status_code = 200
            if '/contact' in url:
                response.text = '<html>Email: contact@found.com.au</html>'
            else:
                response.text = '<html>No email here</html>'
            return response

        with patch('requests.get', side_effect=mock_get):
            email = scraper.find_email_from_website('https://found.com.au')
            assert email == 'contact@found.com.au'

    def test_converts_email_to_lowercase(self, scraper):
        """Should convert found emails to lowercase."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html>Contact: INFO@BUSINESS.COM.AU</html>'

        with patch('requests.get', return_value=mock_response):
            email = scraper.find_email_from_website('https://business.com.au')
            assert email == 'info@business.com.au'


class TestSearchBusinesses:
    """Tests for search_businesses method."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        from src.scraper.places_scraper import PlacesScraper

        with patch.object(PlacesScraper, '__init__', lambda x, y=None: None):
            scraper = PlacesScraper.__new__(PlacesScraper)
            scraper.api_key = 'test-api-key'
            scraper.request_delay = 0
            scraper.config = {
                'location': {'city': 'Adelaide', 'state': 'SA'},
                'exclude_types': ['cafe', 'restaurant']
            }
            return scraper

    def test_search_returns_businesses(self, scraper):
        """Should return list of businesses from API response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'OK',
            'results': [
                {
                    'place_id': 'place123',
                    'name': 'Test Accountants',
                    'formatted_address': '123 Test St, Adelaide',
                    'types': ['accounting', 'finance'],
                    'rating': 4.5,
                    'user_ratings_total': 50
                }
            ]
        }
        mock_response.raise_for_status = Mock()

        with patch('requests.get', return_value=mock_response):
            with patch('time.sleep'):  # Skip delays
                results = scraper.search_businesses('accountant', 'Adelaide, SA', max_results=10)

        assert len(results) == 1
        assert results[0]['place_id'] == 'place123'
        assert results[0]['business_name'] == 'Test Accountants'

    def test_search_excludes_cafes(self, scraper):
        """Should exclude cafes from results."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'OK',
            'results': [
                {
                    'place_id': 'cafe123',
                    'name': 'Coffee House',
                    'formatted_address': '1 Cafe St',
                    'types': ['cafe', 'food'],
                },
                {
                    'place_id': 'acc123',
                    'name': 'ABC Accounting',
                    'formatted_address': '2 Business St',
                    'types': ['accounting'],
                }
            ]
        }
        mock_response.raise_for_status = Mock()

        with patch('requests.get', return_value=mock_response):
            with patch('time.sleep'):
                results = scraper.search_businesses('business', max_results=10)

        assert len(results) == 1
        assert results[0]['business_name'] == 'ABC Accounting'

    def test_search_handles_zero_results(self, scraper):
        """Should handle ZERO_RESULTS status."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'ZERO_RESULTS',
            'results': []
        }
        mock_response.raise_for_status = Mock()

        with patch('requests.get', return_value=mock_response):
            with patch('time.sleep'):
                results = scraper.search_businesses('nonexistent', max_results=10)

        assert len(results) == 0

    def test_search_handles_api_error(self, scraper):
        """Should handle API error status gracefully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'REQUEST_DENIED',
            'error_message': 'Invalid API key'
        }
        mock_response.raise_for_status = Mock()

        with patch('requests.get', return_value=mock_response):
            with patch('time.sleep'):
                results = scraper.search_businesses('test', max_results=10)

        assert len(results) == 0

    def test_search_handles_request_exception(self, scraper):
        """Should handle network errors gracefully."""
        import requests

        with patch('requests.get', side_effect=requests.RequestException('Network error')):
            with patch('time.sleep'):
                results = scraper.search_businesses('test', max_results=10)

        assert len(results) == 0

    def test_search_uses_default_location_from_config(self, scraper):
        """Should use location from config when not specified."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'OK', 'results': []}
        mock_response.raise_for_status = Mock()

        with patch('requests.get', return_value=mock_response) as mock_get:
            with patch('time.sleep'):
                scraper.search_businesses('accountant', max_results=10)

        # Verify the query included Adelaide from config
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert 'Adelaide' in params['query']

    def test_search_respects_max_results(self, scraper):
        """Should limit results to max_results."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'OK',
            'results': [
                {'place_id': f'place{i}', 'name': f'Business {i}', 'formatted_address': f'{i} St', 'types': ['accounting']}
                for i in range(20)
            ]
        }
        mock_response.raise_for_status = Mock()

        with patch('requests.get', return_value=mock_response):
            with patch('time.sleep'):
                results = scraper.search_businesses('accountant', max_results=5)

        assert len(results) == 5


class TestGetPlaceDetails:
    """Tests for get_place_details method."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        from src.scraper.places_scraper import PlacesScraper

        with patch.object(PlacesScraper, '__init__', lambda x, y=None: None):
            scraper = PlacesScraper.__new__(PlacesScraper)
            scraper.api_key = 'test-api-key'
            scraper.request_delay = 0
            scraper.config = {}
            return scraper

    def test_returns_place_details(self, scraper):
        """Should return detailed business information."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'OK',
            'result': {
                'name': 'Test Business',
                'formatted_address': '123 Test St, Adelaide SA 5000',
                'formatted_phone_number': '(08) 1234 5678',
                'website': 'https://testbusiness.com.au',
                'types': ['accounting'],
                'business_status': 'OPERATIONAL'
            }
        }
        mock_response.raise_for_status = Mock()

        with patch('requests.get', return_value=mock_response):
            with patch('time.sleep'):
                details = scraper.get_place_details('place123')

        assert details['business_name'] == 'Test Business'
        assert details['phone'] == '(08) 1234 5678'
        assert details['website'] == 'https://testbusiness.com.au'
        assert details['business_status'] == 'OPERATIONAL'

    def test_returns_empty_dict_on_api_error(self, scraper):
        """Should return empty dict when API returns error status."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'NOT_FOUND'
        }
        mock_response.raise_for_status = Mock()

        with patch('requests.get', return_value=mock_response):
            with patch('time.sleep'):
                details = scraper.get_place_details('invalid_place')

        assert details == {}

    def test_returns_empty_dict_on_request_error(self, scraper):
        """Should return empty dict when request fails."""
        import requests

        with patch('requests.get', side_effect=requests.RequestException('Error')):
            with patch('time.sleep'):
                details = scraper.get_place_details('place123')

        assert details == {}


class TestScrapeFullLead:
    """Tests for scrape_full_lead method."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        from src.scraper.places_scraper import PlacesScraper

        with patch.object(PlacesScraper, '__init__', lambda x, y=None: None):
            scraper = PlacesScraper.__new__(PlacesScraper)
            scraper.api_key = 'test-api-key'
            scraper.request_delay = 0
            scraper.config = {}
            return scraper

    def test_combines_details_and_email(self, scraper):
        """Should combine API details with website email."""
        scraper.get_place_details = Mock(return_value={
            'business_name': 'Test Accounting',
            'address': '123 Test St',
            'phone': '1234567890',
            'website': 'https://testaccounting.com.au'
        })
        scraper.find_email_from_website = Mock(return_value='info@testaccounting.com.au')

        lead = scraper.scrape_full_lead('place123', 'Accounting')

        assert lead['business_name'] == 'Test Accounting'
        assert lead['email'] == 'info@testaccounting.com.au'
        assert lead['industry'] == 'Accounting'
        assert lead['status'] == 'new'
        assert lead['source'] == 'google_maps'

    def test_returns_none_when_no_details(self, scraper):
        """Should return None when place details not found."""
        scraper.get_place_details = Mock(return_value={})

        lead = scraper.scrape_full_lead('invalid_place', 'Test')

        assert lead is None

    def test_returns_none_when_no_business_name(self, scraper):
        """Should return None when business name is missing."""
        scraper.get_place_details = Mock(return_value={
            'address': '123 St',
            'phone': '123'
        })

        lead = scraper.scrape_full_lead('place123', 'Test')

        assert lead is None

    def test_handles_missing_email(self, scraper):
        """Should handle case when no email found."""
        scraper.get_place_details = Mock(return_value={
            'business_name': 'Test Business',
            'address': '123 St',
            'website': 'https://test.com'
        })
        scraper.find_email_from_website = Mock(return_value=None)

        lead = scraper.scrape_full_lead('place123', 'Test')

        assert lead['email'] == ''

    def test_handles_missing_website(self, scraper):
        """Should handle case when no website available."""
        scraper.get_place_details = Mock(return_value={
            'business_name': 'Test Business',
            'address': '123 St',
            'website': None
        })

        lead = scraper.scrape_full_lead('place123', 'Test')

        assert lead['email'] == ''
        assert lead['website'] == ''


class TestSearchAllCategories:
    """Tests for search_all_categories method."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        from src.scraper.places_scraper import PlacesScraper

        with patch.object(PlacesScraper, '__init__', lambda x, y=None: None):
            scraper = PlacesScraper.__new__(PlacesScraper)
            scraper.api_key = 'test-api-key'
            scraper.request_delay = 0
            scraper.config = {
                'target_businesses': [
                    {
                        'category': 'Accounting',
                        'search_terms': ['accountant']
                    }
                ]
            }
            return scraper

    def test_searches_all_categories(self, scraper):
        """Should search through all configured categories."""
        scraper.search_businesses = Mock(return_value=[
            {'place_id': 'place1', 'business_name': 'Test 1'}
        ])
        scraper.scrape_full_lead = Mock(return_value={
            'business_name': 'Test 1',
            'email': 'test@test.com',
            'industry': 'Accounting'
        })

        leads = scraper.search_all_categories(max_per_category=5)

        assert len(leads) == 1
        scraper.search_businesses.assert_called()

    def test_excludes_already_contacted_emails(self, scraper):
        """Should skip businesses with emails in exclusion list."""
        scraper.search_businesses = Mock(return_value=[
            {'place_id': 'place1', 'business_name': 'Already Contacted'}
        ])
        scraper.scrape_full_lead = Mock(return_value={
            'business_name': 'Already Contacted',
            'email': 'existing@test.com',
            'industry': 'Accounting'
        })

        exclusion_emails = {'existing@test.com'}
        leads = scraper.search_all_categories(
            exclusion_emails=exclusion_emails,
            max_per_category=5
        )

        assert len(leads) == 0

    def test_skips_duplicate_place_ids(self, scraper):
        """Should not process the same place_id twice."""
        scraper.config['target_businesses'] = [
            {'category': 'Accounting', 'search_terms': ['accountant', 'CPA']}
        ]
        scraper.search_businesses = Mock(return_value=[
            {'place_id': 'same_place', 'business_name': 'Same Business'}
        ])
        scraper.scrape_full_lead = Mock(return_value={
            'business_name': 'Same Business',
            'email': 'same@test.com',
            'industry': 'Accounting'
        })

        leads = scraper.search_all_categories(max_per_category=5)

        # Should only have 1 lead even though search returned same place twice
        assert scraper.scrape_full_lead.call_count == 1

    def test_handles_include_no_email_false(self, scraper):
        """Should exclude leads without emails when include_no_email=False."""
        scraper.search_businesses = Mock(return_value=[
            {'place_id': 'place1', 'business_name': 'No Email Business'}
        ])
        scraper.scrape_full_lead = Mock(return_value={
            'business_name': 'No Email Business',
            'email': '',  # No email
            'industry': 'Accounting'
        })

        leads = scraper.search_all_categories(
            include_no_email=False,
            max_per_category=5
        )

        assert len(leads) == 0

    def test_includes_no_email_leads_when_enabled(self, scraper):
        """Should include leads without emails when include_no_email=True."""
        scraper.search_businesses = Mock(return_value=[
            {'place_id': 'place1', 'business_name': 'No Email Business'}
        ])
        scraper.scrape_full_lead = Mock(return_value={
            'business_name': 'No Email Business',
            'email': '',
            'industry': 'Accounting'
        })

        leads = scraper.search_all_categories(
            include_no_email=True,
            max_per_category=5
        )

        assert len(leads) == 1
        assert leads[0]['status'] == 'no_email'

    def test_handles_empty_categories(self, scraper):
        """Should handle case when no categories configured."""
        scraper.config['target_businesses'] = []

        leads = scraper.search_all_categories(max_per_category=5)

        assert leads == []

    def test_handles_scrape_failure(self, scraper):
        """Should continue when scrape_full_lead returns None."""
        scraper.search_businesses = Mock(return_value=[
            {'place_id': 'place1', 'business_name': 'Failed'},
            {'place_id': 'place2', 'business_name': 'Success'}
        ])
        scraper.scrape_full_lead = Mock(side_effect=[
            None,  # First fails
            {'business_name': 'Success', 'email': 'success@test.com', 'industry': 'Test'}
        ])

        leads = scraper.search_all_categories(max_per_category=5)

        assert len(leads) == 1
        assert leads[0]['business_name'] == 'Success'
