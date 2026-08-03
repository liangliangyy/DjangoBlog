#!/usr/bin/env python3
"""
Security Configuration Helper

This script helps generate secure configuration values for DjangoBlog.
Run this before deploying to production to generate required secrets.
"""

import hashlib
import secrets
import string


def generate_secret_key(length=50):
    """
    Generate a secure Django SECRET_KEY
    
    Returns a random string suitable for use as Django's SECRET_KEY
    """
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_wxadmin_password(plain_password=None):
    """
    Generate double MD5 hash for WeChat admin password
    
    Args:
        plain_password: Plain text password. If None, generates a random one.
    
    Returns:
        Tuple of (plain_password, double_hashed_password)
    """
    if plain_password is None:
        # Generate a random password
        chars = string.ascii_letters + string.digits
        plain_password = ''.join(secrets.choice(chars) for _ in range(16))
    
    # First MD5
    first_hash = hashlib.md5(plain_password.encode()).hexdigest()
    # Second MD5
    second_hash = hashlib.md5(first_hash.encode()).hexdigest()
    
    return plain_password, second_hash.upper()


def print_env_template():
    """
    Print a template .env file with generated secrets
    """
    secret_key = generate_secret_key()
    wx_plain, wx_hash = generate_wxadmin_password()
    
    print("=" * 70)
    print("Django Blog Security Configuration")
    print("=" * 70)
    print()
    print("Copy the following to your .env file or set as environment variables:")
    print()
    print("# Django Secret Key (REQUIRED)")
    print(f'export DJANGO_SECRET_KEY="{secret_key}"')
    print()
    print("# Allowed Hosts (REQUIRED in production)")
    print("# Replace with your actual domain name(s)")
    print('export DJANGO_ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"')
    print()
    print("# WeChat Admin Password (REQUIRED if using WeChat bot)")
    print(f"# Plain password (DO NOT commit this): {wx_plain}")
    print(f'export DJANGO_WXADMIN_PASSWORD="{wx_hash}"')
    print()
    print("# Other recommended settings")
    print("export DJANGO_DEBUG=False")
    print('export DJANGO_EMAIL_HOST="smtp.example.com"')
    print('export DJANGO_EMAIL_PORT=465')
    print('export DJANGO_EMAIL_USER="noreply@yourdomain.com"')
    print('export DJANGO_EMAIL_PASSWORD="your-email-password"')
    print()
    print("=" * 70)
    print("IMPORTANT: Store these values securely!")
    print("=" * 70)
    print()
    print("Security Tips:")
    print("1. Never commit the .env file to version control")
    print("2. Use different secrets for development and production")
    print("3. Rotate secrets regularly (at least every 6 months)")
    print("4. Store production secrets in a secure vault or secrets manager")
    print("5. Use HTTPS in production for secure cookie transmission")
    print()


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "secret-key":
            print(generate_secret_key())
        elif command == "wx-password":
            if len(sys.argv) > 2:
                plain = sys.argv[2]
                _, hashed = generate_wxadmin_password(plain)
                print(hashed)
            else:
                plain, hashed = generate_wxadmin_password()
                print(f"Plain password: {plain}")
                print(f"Hashed (use this): {hashed}")
        else:
            print(f"Unknown command: {command}")
            print("Usage:")
            print("  python generate_secrets.py              # Generate all configs")
            print("  python generate_secrets.py secret-key   # Generate SECRET_KEY only")
            print("  python generate_secrets.py wx-password [password]  # Generate WX password hash")
            sys.exit(1)
    else:
        # Print complete template
        print_env_template()


if __name__ == "__main__":
    main()
