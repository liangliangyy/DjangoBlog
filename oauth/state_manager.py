"""
OAuth state parameter management for CSRF protection.
"""
import secrets
import hashlib
from django.core.cache import cache


def generate_oauth_state(session_key, oauth_type):
    """
    Generate a cryptographically secure OAuth state parameter.
    
    Args:
        session_key: Django session key
        oauth_type: OAuth provider type (e.g., 'github', 'google')
    
    Returns:
        A unique, random state string
    """
    # Generate a random token
    random_token = secrets.token_urlsafe(32)
    
    # Create a unique state combining session and random token
    state = f"{oauth_type}:{random_token}"
    
    # Store in cache with 10 minute expiration
    cache_key = f"oauth_state:{session_key}:{oauth_type}"
    cache.set(cache_key, state, 600)  # 10 minutes
    
    return state


def validate_oauth_state(session_key, oauth_type, state):
    """
    Validate an OAuth state parameter.
    
    Args:
        session_key: Django session key
        oauth_type: OAuth provider type
        state: The state parameter from OAuth callback
    
    Returns:
        True if state is valid, False otherwise
    """
    if not state:
        return False
    
    cache_key = f"oauth_state:{session_key}:{oauth_type}"
    stored_state = cache.get(cache_key)
    
    if not stored_state:
        return False
    
    # Validate and delete (single use)
    if stored_state == state:
        cache.delete(cache_key)
        return True
    
    return False
