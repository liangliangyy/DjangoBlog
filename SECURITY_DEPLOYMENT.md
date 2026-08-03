# Security Update - Deployment Guide

## Important: Required Environment Variables

This security update removes hardcoded secrets and requires the following environment variables to be set before deployment:

### Mandatory Environment Variables

```bash
# Django Secret Key (REQUIRED)
# Generate a strong random key, at least 50 characters
# Example: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
export DJANGO_SECRET_KEY="your-very-long-random-secret-key-here"

# Allowed Hosts (REQUIRED in production)
# Comma-separated list of allowed domain names
export DJANGO_ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"

# WeChat Admin Password (REQUIRED if using WeChat bot)
# Must be double MD5 hashed
# To generate: echo -n "your-password" | md5sum | awk '{print $1}' | md5sum | awk '{print toupper($1)}'
export DJANGO_WXADMIN_PASSWORD="YOUR-DOUBLE-MD5-HASHED-PASSWORD"
```

## Quick Start for Production

1. **Set Environment Variables**
   ```bash
   # Create a .env file or set in your deployment platform
   export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
   export DJANGO_ALLOWED_HOSTS="yourdomain.com"
   export DJANGO_WXADMIN_PASSWORD="YOUR-HASHED-PASSWORD"
   export DJANGO_DEBUG=False
   ```

2. **Verify Configuration**
   ```bash
   python manage.py check --deploy
   ```

3. **Deploy**
   Your application should now start with proper security configurations.

## Development Mode

For development/testing, you can run with minimal configuration:

```bash
export DJANGO_SECRET_KEY="dev-secret-key"
export DJANGO_DEBUG=True
# ALLOWED_HOSTS will default to wildcard in DEBUG mode
```

## Migration Notes

### Changes from Previous Versions

1. **SECRET_KEY**: No longer has a default fallback. Must be set via environment variable.

2. **ALLOWED_HOSTS**: No longer defaults to `['*']` in production. Requires explicit configuration.

3. **WXADMIN Password**: No longer has a default password. Must be set if using WeChat bot features.

4. **Cache Endpoint**: Now requires staff authentication. Only admin users can clear cache.

5. **Rate Limiting**: New rate limits on authentication endpoints:
   - Login: 5 attempts per minute per IP
   - Registration: 3 attempts per hour per IP
   - Password Reset: 3 attempts per hour per IP
   - OAuth Email Binding: 5 attempts per hour per IP

### Backward Compatibility

- **Test Mode**: When running tests (`python manage.py test`), default values are allowed
- **DEBUG Mode**: When `DJANGO_DEBUG=True`, more lenient settings apply (wildcards in ALLOWED_HOSTS)
- **Production Mode**: When `DJANGO_DEBUG=False`, all security settings are enforced

## Troubleshooting

### Error: "DJANGO_SECRET_KEY environment variable is not set"

**Solution**: Set the SECRET_KEY environment variable before starting the application.

```bash
export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
```

### Error: "DJANGO_ALLOWED_HOSTS environment variable must be set in production mode"

**Solution**: Set your domain names in ALLOWED_HOSTS.

```bash
export DJANGO_ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
```

### Error: "DJANGO_WXADMIN_PASSWORD environment variable is not set"

**Solution**: If you're not using WeChat bot features, you can ignore this by setting `TESTING=True` or setting a dummy value. If you are using WeChat bot, generate and set a proper password:

```bash
# Generate double MD5 hash of your password
PASSWORD_HASH=$(echo -n "your-password" | md5sum | awk '{print $1}' | md5sum | awk '{print toupper($1)}')
export DJANGO_WXADMIN_PASSWORD="$PASSWORD_HASH"
```

### Rate Limiting Issues

If legitimate users are being rate limited, you can adjust the limits in:
- `accounts/views.py` - for login/registration limits
- `oauth/views.py` - for OAuth limits

Or disable rate limiting by removing the `@ratelimit()` decorators (not recommended for production).

## Docker Deployment

If using Docker, add these to your `docker-compose.yml` or Kubernetes ConfigMap:

```yaml
environment:
  - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
  - DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS}
  - DJANGO_WXADMIN_PASSWORD=${DJANGO_WXADMIN_PASSWORD}
  - DJANGO_DEBUG=False
```

## Security Best Practices

1. **Never commit secrets** to version control
2. **Use strong, random SECRET_KEY** (at least 50 characters)
3. **Regularly rotate secrets** in production
4. **Monitor rate limit logs** for abuse attempts
5. **Use HTTPS** in production (required for secure cookies)
6. **Keep dependencies updated** for security patches

## Support

For issues related to this security update, please refer to:
- `SECURITY_FIXES.md` - Detailed information about fixed vulnerabilities
- GitHub Issues - Report problems or ask questions

## Credits

Security vulnerabilities reported by: logicfuzz
Fixes implemented by: GitHub Copilot
