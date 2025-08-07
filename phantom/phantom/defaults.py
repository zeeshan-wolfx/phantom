import secrets



def generate_secret_key():
    return secrets.token_urlsafe(50)

OS_PACKAGES = [
    'python3.12-venv', 'python3.12-dev', 'htop', 'btop',
    'nginx', 'curl', 'supervisor', 'certbot', 'python3-certbot-nginx'
]

DEFAULT_DEBUG = True