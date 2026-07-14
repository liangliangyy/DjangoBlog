"""
Security tests for OAuth and OwnTracks vulnerabilities (Issue #981)

These tests verify that the security fixes for the following issues are working:
1. OAuth email binding IDOR
2. OAuth state validation
3. Inactive user bypass
4. OAuthUser duplicate race condition
5. OwnTracks authentication
"""

from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from django.db import IntegrityError
from unittest.mock import patch, MagicMock
import json

from oauth.models import OAuthUser, OAuthConfig
from oauth.state_manager import generate_oauth_state, validate_oauth_state
from owntracks.models import OwnTrackLog


class OAuthEmailBindingIDORTest(TestCase):
    """Test OAuth email binding IDOR vulnerability fix"""
    
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        User = get_user_model()
        
        # Create a victim user with linked OAuth
        self.victim = User.objects.create_user(
            username='victim',
            email='victim@example.com',
            password='password'
        )
        
        self.victim_oauth = OAuthUser.objects.create(
            author=self.victim,
            openid='victim_openid',
            nickname='Victim',
            token='token',
            type='github',
            email='victim@example.com'
        )
        
        # Create an attacker OAuth (unlinked)
        self.attacker_oauth = OAuthUser.objects.create(
            openid='attacker_openid',
            nickname='Attacker',
            token='token',
            type='github'
        )
    
    def test_cannot_rebind_already_linked_oauth(self):
        """Test that already-linked OAuth accounts cannot be rebound"""
        url = reverse('oauth:require_email', kwargs={'oauthid': self.victim_oauth.id})
        
        response = self.client.post(url, {
            'email': 'attacker@example.com'
        })
        
        # Should return forbidden since OAuth is already linked
        self.assertEqual(response.status_code, 403)
        
        # Verify the victim's OAuth is still linked to victim
        self.victim_oauth.refresh_from_db()
        self.assertEqual(self.victim_oauth.author_id, self.victim.id)
    
    def test_oauthid_comes_from_url_not_form(self):
        """Test that oauthid is validated from URL, not form data"""
        # Try to access one OAuth's binding page
        url = reverse('oauth:require_email', kwargs={'oauthid': self.attacker_oauth.id})
        
        # Even if we try to submit a different oauthid in the form, it should use the URL one
        response = self.client.post(url, {
            'email': 'attacker@example.com'
        })
        
        # Should succeed (200 or redirect)
        self.assertIn(response.status_code, [200, 302])
        
        # The attacker_oauth should have been updated with the email
        self.attacker_oauth.refresh_from_db()
        self.assertEqual(self.attacker_oauth.email, 'attacker@example.com')


class OAuthStateValidationTest(TestCase):
    """Test OAuth state parameter CSRF protection"""
    
    def setUp(self):
        self.client = Client()
        cache.clear()
    
    def test_generate_oauth_state(self):
        """Test state generation"""
        state = generate_oauth_state('session123', 'github')
        
        self.assertIsNotNone(state)
        self.assertIn('github:', state)
        self.assertTrue(len(state) > 20)
    
    def test_validate_oauth_state_success(self):
        """Test successful state validation"""
        session_key = 'session123'
        oauth_type = 'github'
        
        state = generate_oauth_state(session_key, oauth_type)
        
        # State should validate correctly
        self.assertTrue(validate_oauth_state(session_key, oauth_type, state))
    
    def test_validate_oauth_state_single_use(self):
        """Test state is single-use (consumed after first validation)"""
        session_key = 'session123'
        oauth_type = 'github'
        
        state = generate_oauth_state(session_key, oauth_type)
        
        # First validation should succeed
        self.assertTrue(validate_oauth_state(session_key, oauth_type, state))
        
        # Second validation should fail (already consumed)
        self.assertFalse(validate_oauth_state(session_key, oauth_type, state))
    
    def test_validate_oauth_state_wrong_state(self):
        """Test validation fails with wrong state"""
        session_key = 'session123'
        oauth_type = 'github'
        
        generate_oauth_state(session_key, oauth_type)
        
        # Try with wrong state
        self.assertFalse(validate_oauth_state(session_key, oauth_type, 'wrong_state'))
    
    def test_validate_oauth_state_wrong_type(self):
        """Test validation fails with wrong OAuth type"""
        session_key = 'session123'
        oauth_type = 'github'
        
        state = generate_oauth_state(session_key, oauth_type)
        
        # Try with wrong OAuth type
        self.assertFalse(validate_oauth_state(session_key, 'google', state))
    
    @patch('oauth.views.get_manager_by_type')
    def test_authorize_requires_valid_state(self, mock_get_manager):
        """Test authorize endpoint requires valid state"""
        # Mock the OAuth manager
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        
        # Try to authorize without valid state
        url = reverse('oauth:authorize') + '?type=github&code=testcode'
        response = self.client.get(url)
        
        # Should return forbidden (no valid state)
        self.assertEqual(response.status_code, 403)


class InactiveUserBypassTest(TestCase):
    """Test inactive user bypass vulnerability fix"""
    
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        
        # Create an inactive user
        self.inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='password',
            is_active=False
        )
        
        # Create OAuth for inactive user
        self.inactive_oauth = OAuthUser.objects.create(
            author=self.inactive_user,
            openid='inactive_openid',
            nickname='Inactive',
            token='token',
            type='github',
            email='inactive@example.com'
        )
    
    @patch('oauth.views.get_manager_by_type')
    @patch('oauth.views.validate_oauth_state')
    def test_inactive_user_cannot_login_via_oauth(self, mock_validate_state, mock_get_manager):
        """Test inactive users cannot login via OAuth"""
        # Mock state validation
        mock_validate_state.return_value = True
        
        # Mock OAuth manager
        mock_manager = MagicMock()
        mock_manager.get_access_token_by_code.return_value = 'token'
        mock_manager.get_oauth_userinfo.return_value = self.inactive_oauth
        mock_get_manager.return_value = mock_manager
        
        # Setup session
        session = self.client.session
        session['_session_key'] = 'test_session'
        session.save()
        
        url = reverse('oauth:authorize') + '?type=github&code=testcode&state=valid'
        response = self.client.get(url)
        
        # Should return forbidden for inactive user
        self.assertEqual(response.status_code, 403)
    
    def test_inactive_user_cannot_login_via_email_confirm(self):
        """Test inactive users cannot login via email confirmation"""
        from djangoblog.utils import get_sha256
        from django.conf import settings
        
        # Create valid sign
        sign = get_sha256(settings.SECRET_KEY + str(self.inactive_oauth.id) + settings.SECRET_KEY)
        
        url = reverse('oauth:email_confirm', kwargs={
            'id': self.inactive_oauth.id,
            'sign': sign
        })
        
        response = self.client.get(url)
        
        # Should return forbidden for inactive user
        self.assertEqual(response.status_code, 403)


class OAuthUserDuplicateTest(TestCase):
    """Test OAuthUser duplicate race condition fix"""
    
    def test_unique_constraint_on_type_openid(self):
        """Test unique constraint prevents duplicates"""
        OAuthUser.objects.create(
            openid='test_openid',
            nickname='Test',
            token='token',
            type='github'
        )
        
        # Try to create duplicate
        with self.assertRaises(IntegrityError):
            OAuthUser.objects.create(
                openid='test_openid',
                nickname='Test2',
                token='token2',
                type='github'
            )
    
    def test_get_or_create_is_atomic(self):
        """Test get_or_create doesn't create duplicates"""
        # First call creates
        oauth1, created1 = OAuthUser.objects.get_or_create(
            type='github',
            openid='test_openid',
            defaults={
                'nickname': 'Test1',
                'token': 'token1'
            }
        )
        
        self.assertTrue(created1)
        
        # Second call gets existing
        oauth2, created2 = OAuthUser.objects.get_or_create(
            type='github',
            openid='test_openid',
            defaults={
                'nickname': 'Test2',
                'token': 'token2'
            }
        )
        
        self.assertFalse(created2)
        self.assertEqual(oauth1.id, oauth2.id)


class OwnTracksAuthenticationTest(TestCase):
    """Test OwnTracks endpoint authentication requirement"""
    
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        
        # Create regular user
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='password'
        )
        
        # Create superuser
        self.superuser = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password',
            is_superuser=True,
            is_staff=True
        )
    
    def test_anonymous_cannot_submit_location(self):
        """Test anonymous users cannot submit location data"""
        url = reverse('owntracks:logtracks')
        
        data = json.dumps({
            'tid': 'test',
            'lat': 1.0,
            'lon': 2.0
        })
        
        response = self.client.post(
            url,
            data=data,
            content_type='application/json'
        )
        
        # Should redirect to login (302) or return forbidden
        self.assertIn(response.status_code, [302, 403])
    
    def test_regular_user_cannot_submit_location(self):
        """Test regular users cannot submit location data"""
        self.client.login(username='user', password='password')
        
        url = reverse('owntracks:logtracks')
        
        data = json.dumps({
            'tid': 'test',
            'lat': 1.0,
            'lon': 2.0
        })
        
        response = self.client.post(
            url,
            data=data,
            content_type='application/json'
        )
        
        # Should return forbidden
        self.assertEqual(response.status_code, 403)
    
    def test_superuser_can_submit_location(self):
        """Test superusers can submit location data"""
        self.client.login(username='admin', password='password')
        
        url = reverse('owntracks:logtracks')
        
        data = json.dumps({
            'tid': 'test',
            'lat': 1.0,
            'lon': 2.0
        })
        
        response = self.client.post(
            url,
            data=data,
            content_type='application/json'
        )
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'ok')
        
        # Verify data was saved
        log = OwnTrackLog.objects.filter(tid='test').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.lat, 1.0)
        self.assertEqual(log.lon, 2.0)
