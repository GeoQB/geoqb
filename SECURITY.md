# GeoQB Security Assessment & OWASP Analysis

## Executive Summary

This document provides a comprehensive security assessment of the GeoQB platform based on OWASP Top 10 2021 guidelines and general security best practices. It identifies current vulnerabilities, provides risk assessments, and recommends remediation strategies.

**Overall Risk Level:** MEDIUM-HIGH

**Critical Issues:** 3
**High Priority Issues:** 7
**Medium Priority Issues:** 5
**Low Priority Issues:** 3

---

## Table of Contents

1. [OWASP Top 10 Analysis](#owasp-top-10-analysis)
2. [Infrastructure Security](#infrastructure-security)
3. [Data Security](#data-security)
4. [Authentication & Authorization](#authentication--authorization)
5. [Recommended Security Controls](#recommended-security-controls)
6. [Security Roadmap](#security-roadmap)

---

## OWASP Top 10 Analysis

### A01:2021 – Broken Access Control

**Risk Level:** MEDIUM

**Current State:**
- No authentication layer for local operations
- File-based credential storage in `env.sh`
- No role-based access control (RBAC)
- No workspace isolation between users
- TigerGraph credentials grant full database access

**Vulnerabilities:**

1. **Unrestricted File System Access**
   ```python
   # Current code allows any file path
   def load_asset(asset_path):
       with open(asset_path, 'r') as f:  # No path validation
           return f.read()
   ```

2. **No User Context**
   - All operations run with same privileges
   - No audit trail of who performed actions

**Recommendations:**

**HIGH PRIORITY:**

```python
# Implement path validation
import os
from pathlib import Path

WORKSPACE_ROOT = Path(os.getenv('GEOQB_WORKSPACE'))

def load_asset(asset_path):
    """Load asset with path validation."""
    abs_path = (WORKSPACE_ROOT / asset_path).resolve()

    # Prevent directory traversal
    if not str(abs_path).startswith(str(WORKSPACE_ROOT)):
        raise SecurityError("Path traversal detected")

    if not abs_path.exists():
        raise FileNotFoundError(f"Asset not found: {asset_path}")

    with open(abs_path, 'r') as f:
        return f.read()
```

**MEDIUM PRIORITY:**

- Implement user authentication for multi-user deployments
- Add RBAC with roles: Admin, Analyst, Viewer
- Create audit log for all write operations
- Implement workspace-level access controls

**Implementation Example:**

```python
# geoqb/security/access_control.py
from enum import Enum
from functools import wraps

class Role(Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class Permission(Enum):
    CREATE_LAYER = "create_layer"
    DELETE_LAYER = "delete_layer"
    QUERY_LAYER = "query_layer"
    MANAGE_USERS = "manage_users"

ROLE_PERMISSIONS = {
    Role.ADMIN: [Permission.CREATE_LAYER, Permission.DELETE_LAYER,
                 Permission.QUERY_LAYER, Permission.MANAGE_USERS],
    Role.ANALYST: [Permission.CREATE_LAYER, Permission.QUERY_LAYER],
    Role.VIEWER: [Permission.QUERY_LAYER]
}

def require_permission(permission):
    """Decorator to enforce permission checks."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if permission not in ROLE_PERMISSIONS[user.role]:
                raise PermissionError(f"User lacks permission: {permission}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@require_permission(Permission.DELETE_LAYER)
def delete_layer(layer_id):
    # Only admin and analyst can delete
    pass
```

---

### A02:2021 – Cryptographic Failures

**Risk Level:** HIGH

**Current State:**
- **CRITICAL**: Credentials stored in plain text in `env.sh`
- No encryption at rest for workspace data
- TLS for external connections but no certificate validation
- No secrets rotation mechanism

**Vulnerabilities:**

1. **Plain Text Credentials**
   ```bash
   # env/env.sh - stored in plain text
   export TG_PASSWORD="mypassword123"
   export sasl_password="kafkapassword"
   export aws_secret_access_key="AKIAIOSFODNN7EXAMPLE"
   ```

2. **No Data Encryption**
   - Cached API responses in `raw/` contain sensitive data
   - Staged data in CSV files unencrypted
   - No encryption for data at rest

**Recommendations:**

**CRITICAL PRIORITY:**

1. **Implement Secrets Management**

```python
# geoqb/security/secrets.py
import os
from cryptography.fernet import Fernet
import keyring
from hashicorp_vault import Vault

class SecretsManager:
    """Secure secrets management."""

    def __init__(self, backend='keyring'):
        self.backend = backend
        if backend == 'vault':
            self.vault = Vault(url=os.getenv('VAULT_URL'))

    def get_secret(self, key):
        """Retrieve secret securely."""
        if self.backend == 'keyring':
            return keyring.get_password('geoqb', key)
        elif self.backend == 'vault':
            return self.vault.read(f'secret/geoqb/{key}')['data']['value']
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def set_secret(self, key, value):
        """Store secret securely."""
        if self.backend == 'keyring':
            keyring.set_password('geoqb', key, value)
        elif self.backend == 'vault':
            self.vault.write(f'secret/geoqb/{key}', value=value)

# Usage
secrets = SecretsManager(backend='keyring')
tg_password = secrets.get_secret('TG_PASSWORD')
```

2. **Encrypt Workspace Data**

```python
# geoqb/security/encryption.py
from cryptography.fernet import Fernet
import os

class WorkspaceEncryption:
    """Encrypt/decrypt workspace files."""

    def __init__(self):
        key = os.getenv('GEOQB_ENCRYPTION_KEY')
        if not key:
            raise ValueError("GEOQB_ENCRYPTION_KEY not set")
        self.cipher = Fernet(key.encode())

    def encrypt_file(self, input_path, output_path):
        """Encrypt file."""
        with open(input_path, 'rb') as f:
            plaintext = f.read()
        ciphertext = self.cipher.encrypt(plaintext)
        with open(output_path, 'wb') as f:
            f.write(ciphertext)

    def decrypt_file(self, input_path, output_path):
        """Decrypt file."""
        with open(input_path, 'rb') as f:
            ciphertext = f.read()
        plaintext = self.cipher.decrypt(ciphertext)
        with open(output_path, 'wb') as f:
            f.write(plaintext)
```

**HIGH PRIORITY:**

- Implement certificate pinning for TigerGraph/Kafka connections
- Add encryption for sensitive cached data
- Implement automatic secrets rotation (90-day cycle)
- Use AWS KMS or Azure Key Vault for production

**Configuration Example:**

```bash
# New env.sh with secrets manager
#!/bin/bash
export SECRETS_BACKEND="vault"  # or "keyring", "aws-secrets-manager"
export VAULT_URL="https://vault.example.com"
export VAULT_TOKEN="s.xxxxxxxxxxxxx"
export GEOQB_ENCRYPTION_KEY=$(openssl rand -base64 32)
```

---

### A03:2021 – Injection

**Risk Level:** MEDIUM-HIGH

**Current State:**
- SPARQL query generation from user input
- File path operations from user input
- No input validation or sanitization
- Potential command injection in bash operations

**Vulnerabilities:**

1. **SPARQL Injection**
   ```python
   # Vulnerable code in geoqb_layers.py
   def create_sophox_query(self, layer):
       tags = layer['tags']
       query = f"""
       SELECT ?place WHERE {{
           ?place osmm:tag:{tags['key']} "{tags['value']}" .
       }}
       """  # User input directly in query!
       return query
   ```

   Attack scenario:
   ```python
   malicious_tag = {'key': 'amenity', 'value': '" . ?place ?p ?o }'}
   # Results in: ?place osmm:tag:amenity "" . ?place ?p ?o } " .
   # Exposes entire graph!
   ```

2. **Path Traversal**
   ```python
   # Vulnerable
   workspace.load_asset(user_provided_path)
   # user_provided_path = "../../../../etc/passwd"
   ```

**Recommendations:**

**HIGH PRIORITY:**

1. **Parameterized SPARQL Queries**

```python
# geoqb/security/query_builder.py
from rdflib.plugins.sparql import prepareQuery

class SafeSPARQLBuilder:
    """Build SPARQL queries safely."""

    @staticmethod
    def escape_literal(value):
        """Escape SPARQL literal."""
        return value.replace('\\', '\\\\') \
                    .replace('"', '\\"') \
                    .replace('\n', '\\n')

    def build_osm_query(self, tag_key, tag_value, bbox):
        """Build OSM query with proper escaping."""
        # Whitelist tag keys
        allowed_keys = ['amenity', 'highway', 'building', 'shop']
        if tag_key not in allowed_keys:
            raise ValueError(f"Invalid tag key: {tag_key}")

        # Escape values
        safe_value = self.escape_literal(tag_value)

        # Use parameterized query
        query_template = """
        SELECT ?place ?location WHERE {
            ?place osmm:tag:%(tag_key)s "%(tag_value)s" .
            ?place osmt:loc ?location .
            FILTER(geof:latitude(?location) > %(lat_min)f)
            FILTER(geof:latitude(?location) < %(lat_max)f)
        }
        """

        return query_template % {
            'tag_key': tag_key,
            'tag_value': safe_value,
            'lat_min': float(bbox[0]),
            'lat_max': float(bbox[2])
        }
```

2. **Input Validation**

```python
# geoqb/security/validation.py
import re
from typing import List

class InputValidator:
    """Validate user inputs."""

    @staticmethod
    def validate_layer_name(name: str) -> bool:
        """Validate layer name (alphanumeric, underscore, hyphen only)."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValueError("Invalid layer name")
        if len(name) > 64:
            raise ValueError("Layer name too long")
        return True

    @staticmethod
    def validate_bbox(bbox: List[float]) -> bool:
        """Validate bounding box."""
        if len(bbox) != 4:
            raise ValueError("Bbox must have 4 elements")

        lat_min, lon_min, lat_max, lon_max = bbox

        if not (-90 <= lat_min <= 90 and -90 <= lat_max <= 90):
            raise ValueError("Invalid latitude")
        if not (-180 <= lon_min <= 180 and -180 <= lon_max <= 180):
            raise ValueError("Invalid longitude")
        if lat_min >= lat_max or lon_min >= lon_max:
            raise ValueError("Invalid bbox bounds")

        return True

    @staticmethod
    def validate_h3_resolution(resolution: int) -> bool:
        """Validate H3 resolution."""
        if not (0 <= resolution <= 15):
            raise ValueError("H3 resolution must be 0-15")
        return True

    @staticmethod
    def sanitize_file_path(path: str, allowed_dirs: List[str]) -> str:
        """Sanitize and validate file path."""
        # Remove null bytes
        path = path.replace('\0', '')

        # Resolve to absolute path
        abs_path = os.path.abspath(path)

        # Check against allowed directories
        if not any(abs_path.startswith(d) for d in allowed_dirs):
            raise ValueError("Path outside allowed directories")

        return abs_path
```

3. **Usage in Modules**

```python
# Updated geoqb_layers.py
from geoanalysis.geoqb.security import InputValidator, SafeSPARQLBuilder

class GeoQbLayers:
    def add_layer(self, name, layer_type, tags, bbox, resolution=9):
        # Validate all inputs
        InputValidator.validate_layer_name(name)
        InputValidator.validate_bbox(bbox)
        InputValidator.validate_h3_resolution(resolution)

        # Safe query building
        builder = SafeSPARQLBuilder()
        query = builder.build_osm_query(
            tag_key=tags['key'],
            tag_value=tags['value'],
            bbox=bbox
        )

        self.layers[name] = {
            'name': name,
            'query': query,
            'bbox': bbox,
            'resolution': resolution
        }
```

---

### A04:2021 – Insecure Design

**Risk Level:** MEDIUM

**Current State:**
- No rate limiting on API calls
- No resource quotas
- Single-threaded operations (DoS risk)
- No circuit breakers for external services

**Recommendations:**

**MEDIUM PRIORITY:**

1. **Rate Limiting**

```python
# geoqb/security/rate_limit.py
from functools import wraps
from time import time
from collections import defaultdict

class RateLimiter:
    """Simple rate limiter."""

    def __init__(self, max_calls=100, period=60):
        self.max_calls = max_calls
        self.period = period
        self.calls = defaultdict(list)

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time()
            user_id = get_current_user_id()  # Implement user identification

            # Remove old calls
            self.calls[user_id] = [
                call_time for call_time in self.calls[user_id]
                if now - call_time < self.period
            ]

            # Check limit
            if len(self.calls[user_id]) >= self.max_calls:
                raise RateLimitError(
                    f"Rate limit exceeded: {self.max_calls} calls per {self.period}s"
                )

            self.calls[user_id].append(now)
            return func(*args, **kwargs)

        return wrapper

# Usage
@RateLimiter(max_calls=10, period=60)
def fetch_osm_data(bbox, tags):
    # Limited to 10 calls per minute per user
    pass
```

2. **Circuit Breaker**

```python
# geoqb/security/circuit_breaker.py
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker for external services."""

    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker."""
        if self.state == CircuitState.OPEN:
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
sophox_breaker = CircuitBreaker(failure_threshold=3, timeout=30)

def fetch_sophox_data(query):
    return sophox_breaker.call(execute_sparql_query, query)
```

---

### A05:2021 – Security Misconfiguration

**Risk Level:** MEDIUM-HIGH

**Current State:**
- Default configurations used
- No security headers
- Debug mode may be enabled in production
- Verbose error messages expose internals
- No security scanning in CI/CD

**Vulnerabilities:**

1. **Verbose Error Messages**
   ```python
   # Current code
   except Exception as e:
       print(f"Error: {e}")  # Exposes stack trace, paths, etc.
   ```

2. **No Security Headers** (future web interface)

**Recommendations:**

**HIGH PRIORITY:**

1. **Secure Error Handling**

```python
# geoqb/security/error_handling.py
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class GeoQBError(Exception):
    """Base exception for GeoQB."""
    pass

class ValidationError(GeoQBError):
    """Input validation error."""
    pass

class AuthenticationError(GeoQBError):
    """Authentication failed."""
    pass

def safe_error_handling(func):
    """Catch exceptions and return safe messages."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            # Safe to show to user
            logger.warning(f"Validation error: {e}")
            raise
        except GeoQBError as e:
            # Internal error - log but show generic message
            logger.error(f"Internal error: {e}", exc_info=True)
            raise GeoQBError("An internal error occurred. Please contact support.")
        except Exception as e:
            # Unexpected error - log and show generic message
            logger.critical(f"Unexpected error: {e}", exc_info=True)
            raise GeoQBError("An unexpected error occurred.")

    return wrapper
```

2. **Security Configuration**

```python
# geoqb/config/security_config.py
from dataclasses import dataclass
from typing import List

@dataclass
class SecurityConfig:
    """Security configuration."""

    # Authentication
    require_auth: bool = True
    session_timeout: int = 3600  # 1 hour
    max_login_attempts: int = 5
    lockout_duration: int = 900  # 15 minutes

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_calls: int = 100
    rate_limit_period: int = 60

    # Encryption
    encrypt_workspace: bool = True
    encryption_algorithm: str = "AES-256-GCM"

    # Logging
    log_level: str = "INFO"  # Never DEBUG in production
    log_sensitive_data: bool = False
    audit_log_enabled: bool = True

    # Network
    tls_verify: bool = True
    allowed_hosts: List[str] = None

    # File operations
    max_file_size: int = 100 * 1024 * 1024  # 100 MB
    allowed_extensions: List[str] = ['.csv', '.json', '.geojson']

    def validate(self):
        """Validate configuration."""
        if self.log_level == "DEBUG":
            raise ValueError("DEBUG log level not allowed in production")
        if not self.tls_verify:
            raise ValueError("TLS verification must be enabled in production")

# Load config
config = SecurityConfig()
config.validate()
```

3. **Add Security Scanning to CI/CD**

```yaml
# .github/workflows/security.yml
name: Security Scanning

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run Bandit (Python security linter)
        run: |
          pip install bandit
          bandit -r pyGeoQB/ -f json -o bandit-report.json

      - name: Run Safety (dependency vulnerability scan)
        run: |
          pip install safety
          safety check --json

      - name: Run Trivy (container scanning)
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'

      - name: OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'GeoQB'
          path: '.'
          format: 'HTML'
```

---

### A06:2021 – Vulnerable and Outdated Components

**Risk Level:** MEDIUM

**Current State:**
- No automated dependency scanning
- Some pinned versions (tornado==5.0) may be outdated
- No vulnerability monitoring

**Recommendations:**

**MEDIUM PRIORITY:**

1. **Add Dependabot**

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/pyGeoQB"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "security"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

2. **Dependency Audit Script**

```bash
#!/bin/bash
# script/audit_dependencies.sh

echo "Running dependency audit..."

# Check for known vulnerabilities
pip install safety
safety check --json > safety-report.json

# Check for outdated packages
pip list --outdated

# Audit specific concerns
echo "Checking critical packages..."
pip show pyTigerGraph confluent-kafka boto3 | grep Version
```

---

### A07:2021 – Identification and Authentication Failures

**Risk Level:** HIGH (for future multi-user deployments)

**Current State:**
- No user authentication mechanism
- Credentials stored in plain text
- No session management
- No MFA support

**Recommendations:**

**HIGH PRIORITY (for production):**

1. **Implement Authentication**

```python
# geoqb/security/authentication.py
from passlib.hash import bcrypt
import jwt
from datetime import datetime, timedelta

class AuthenticationManager:
    """Handle user authentication."""

    def __init__(self, secret_key, token_expiry=3600):
        self.secret_key = secret_key
        self.token_expiry = token_expiry

    def hash_password(self, password):
        """Hash password with bcrypt."""
        return bcrypt.hash(password)

    def verify_password(self, password, password_hash):
        """Verify password against hash."""
        return bcrypt.verify(password, password_hash)

    def create_token(self, user_id, role):
        """Create JWT token."""
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.utcnow() + timedelta(seconds=self.token_expiry),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_token(self, token):
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")

# Usage
auth = AuthenticationManager(secret_key=os.getenv('JWT_SECRET'))
token = auth.create_token(user_id='user123', role='analyst')
```

2. **Multi-Factor Authentication**

```python
# geoqb/security/mfa.py
import pyotp
import qrcode

class MFAManager:
    """Handle multi-factor authentication."""

    def generate_secret(self, user_id):
        """Generate TOTP secret for user."""
        secret = pyotp.random_base32()
        # Store secret securely in database
        return secret

    def generate_qr_code(self, user_id, secret):
        """Generate QR code for authenticator app."""
        uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_id,
            issuer_name='GeoQB'
        )
        qr = qrcode.make(uri)
        return qr

    def verify_totp(self, secret, token):
        """Verify TOTP token."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
```

---

### A08:2021 – Software and Data Integrity Failures

**Risk Level:** MEDIUM

**Current State:**
- No code signing
- No verification of downloaded data
- No integrity checks for cached data

**Recommendations:**

**MEDIUM PRIORITY:**

1. **Data Integrity Checks**

```python
# geoqb/security/integrity.py
import hashlib
import hmac

class IntegrityChecker:
    """Verify data integrity."""

    @staticmethod
    def calculate_hash(file_path, algorithm='sha256'):
        """Calculate file hash."""
        hasher = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def verify_hash(file_path, expected_hash, algorithm='sha256'):
        """Verify file hash."""
        actual_hash = IntegrityChecker.calculate_hash(file_path, algorithm)
        return hmac.compare_digest(actual_hash, expected_hash)

    def save_with_hash(self, data, file_path):
        """Save data with integrity hash."""
        # Save data
        with open(file_path, 'w') as f:
            f.write(data)

        # Calculate and save hash
        file_hash = self.calculate_hash(file_path)
        hash_file = f"{file_path}.sha256"
        with open(hash_file, 'w') as f:
            f.write(file_hash)

        return file_hash

    def load_with_verification(self, file_path):
        """Load data and verify integrity."""
        hash_file = f"{file_path}.sha256"

        if not os.path.exists(hash_file):
            raise IntegrityError("Hash file not found")

        with open(hash_file, 'r') as f:
            expected_hash = f.read().strip()

        if not self.verify_hash(file_path, expected_hash):
            raise IntegrityError("Hash mismatch - data may be corrupted")

        with open(file_path, 'r') as f:
            return f.read()
```

---

### A09:2021 – Security Logging and Monitoring Failures

**Risk Level:** HIGH

**Current State:**
- Basic console logging only
- No centralized logging
- No security event monitoring
- No alerting system

**Recommendations:**

**HIGH PRIORITY:**

1. **Structured Security Logging**

```python
# geoqb/security/audit_log.py
import logging
import json
from datetime import datetime
from enum import Enum

class AuditEventType(Enum):
    """Audit event types."""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    LAYER_CREATED = "layer_created"
    LAYER_DELETED = "layer_deleted"
    DATA_EXPORTED = "data_exported"
    PERMISSION_DENIED = "permission_denied"
    AUTH_FAILURE = "auth_failure"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

class AuditLogger:
    """Security audit logging."""

    def __init__(self, log_file='/var/log/geoqb/audit.log'):
        self.logger = logging.getLogger('geoqb.audit')
        self.logger.setLevel(logging.INFO)

        # File handler
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)

    def log_event(self, event_type, user_id, details=None, severity='info'):
        """Log security event."""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type.value,
            'user_id': user_id,
            'severity': severity,
            'details': details or {},
            'ip_address': self._get_client_ip(),
            'session_id': self._get_session_id()
        }

        log_message = json.dumps(event)

        if severity == 'critical':
            self.logger.critical(log_message)
            self._send_alert(event)
        elif severity == 'error':
            self.logger.error(log_message)
        else:
            self.logger.info(log_message)

    def _send_alert(self, event):
        """Send alert for critical events."""
        # Implement alerting (email, Slack, PagerDuty, etc.)
        pass

# Usage
audit = AuditLogger()

# Log successful login
audit.log_event(
    AuditEventType.USER_LOGIN,
    user_id='user123',
    details={'method': 'password'},
    severity='info'
)

# Log suspicious activity
audit.log_event(
    AuditEventType.SUSPICIOUS_ACTIVITY,
    user_id='user456',
    details={'reason': 'multiple_failed_logins', 'count': 10},
    severity='critical'
)
```

2. **Monitoring Integration**

```python
# geoqb/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
api_requests = Counter('geoqb_api_requests_total', 'Total API requests', ['endpoint', 'status'])
query_duration = Histogram('geoqb_query_duration_seconds', 'Query duration')
active_users = Gauge('geoqb_active_users', 'Number of active users')

# Usage in code
@query_duration.time()
def execute_query(query):
    result = tg.run_query(query)
    api_requests.labels(endpoint='query', status='success').inc()
    return result
```

---

### A10:2021 – Server-Side Request Forgery (SSRF)

**Risk Level:** MEDIUM

**Current State:**
- External API calls to user-provided endpoints
- No URL validation
- Potential SSRF via Sophox/Overpass endpoints

**Vulnerabilities:**

```python
# Vulnerable code
def fetch_data_from_url(url):
    response = requests.get(url)  # No validation!
    return response.json()

# Attack: url = "http://169.254.169.254/latest/meta-data/"  # AWS metadata
```

**Recommendations:**

**MEDIUM PRIORITY:**

```python
# geoqb/security/ssrf_protection.py
from urllib.parse import urlparse
import ipaddress

class SSRFProtection:
    """Protect against SSRF attacks."""

    BLOCKED_NETWORKS = [
        ipaddress.ip_network('10.0.0.0/8'),      # Private
        ipaddress.ip_network('172.16.0.0/12'),   # Private
        ipaddress.ip_network('192.168.0.0/16'),  # Private
        ipaddress.ip_network('127.0.0.0/8'),     # Loopback
        ipaddress.ip_network('169.254.0.0/16'),  # Link-local (AWS metadata)
    ]

    ALLOWED_SCHEMES = ['http', 'https']

    @classmethod
    def validate_url(cls, url, allowed_domains=None):
        """Validate URL against SSRF risks."""
        parsed = urlparse(url)

        # Check scheme
        if parsed.scheme not in cls.ALLOWED_SCHEMES:
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}")

        # Check domain whitelist
        if allowed_domains and parsed.hostname not in allowed_domains:
            raise ValueError(f"Domain not allowed: {parsed.hostname}")

        # Resolve hostname to IP
        try:
            import socket
            ip = socket.gethostbyname(parsed.hostname)
            ip_obj = ipaddress.ip_address(ip)

            # Check if IP is in blocked networks
            for network in cls.BLOCKED_NETWORKS:
                if ip_obj in network:
                    raise ValueError(f"IP address in blocked range: {ip}")

        except socket.gaierror:
            raise ValueError(f"Cannot resolve hostname: {parsed.hostname}")

        return True

# Usage
allowed_endpoints = [
    'overpass.kumi.systems',
    'sophox.org',
    'nominatim.openstreetmap.org'
]

SSRFProtection.validate_url(user_url, allowed_domains=allowed_endpoints)
```

---

## Infrastructure Security

### Cloud Services Security

**TigerGraph Cloud:**
- ✅ Uses TLS for connections
- ✅ Token-based authentication
- ❌ No IP whitelisting configured
- ❌ No VPC peering

**Recommendations:**
- Enable IP whitelisting in TigerGraph Cloud
- Configure VPC peering for production
- Enable audit logging in TigerGraph
- Implement least-privilege tokens (separate read/write tokens)

**Confluent Cloud (Kafka):**
- ✅ SASL/SSL authentication
- ❌ Credentials in plain text

**Recommendations:**
- Use service accounts with limited permissions
- Enable Confluent audit logs
- Implement client-side encryption for sensitive messages

---

## Data Security

### Data Classification

| Category | Sensitivity | Examples | Protection Required |
|----------|-------------|----------|---------------------|
| Public | Low | OSM data, layer definitions | Integrity checks |
| Internal | Medium | Analysis results, cached data | Encryption at rest |
| Confidential | High | User preferences, impact profiles | Encryption + access control |
| Restricted | Critical | Credentials, API keys | Secrets manager + encryption |

### Data Protection Measures

**Current State:**
- ❌ No classification system
- ❌ No data retention policy
- ❌ No data sanitization on delete

**Recommendations:**

1. **Data Retention Policy**

```python
# geoqb/data/retention.py
from datetime import datetime, timedelta

class RetentionPolicy:
    """Manage data retention."""

    RETENTION_PERIODS = {
        'raw': timedelta(days=7),           # Cache for 7 days
        'stage': timedelta(days=30),        # Keep staged data 30 days
        'dumps': timedelta(days=90),        # Keep exports 90 days
        'audit_logs': timedelta(days=365),  # Keep logs 1 year
    }

    def cleanup_expired_data(self, category):
        """Remove data past retention period."""
        cutoff = datetime.now() - self.RETENTION_PERIODS[category]
        workspace_path = Path(os.getenv('GEOQB_WORKSPACE'))
        category_path = workspace_path / category

        for file_path in category_path.glob('**/*'):
            if file_path.is_file():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff:
                    file_path.unlink()  # Secure delete
```

2. **Secure Data Deletion**

```python
# geoqb/data/secure_delete.py
import os

def secure_delete(file_path, passes=3):
    """Securely delete file (overwrite before deletion)."""
    if not os.path.exists(file_path):
        return

    file_size = os.path.getsize(file_path)

    with open(file_path, 'ba+') as f:
        for _ in range(passes):
            f.seek(0)
            f.write(os.urandom(file_size))
            f.flush()
            os.fsync(f.fileno())

    os.remove(file_path)
```

---

## Recommended Security Controls

### Priority Matrix

| Control | Priority | Effort | Impact |
|---------|----------|--------|--------|
| Secrets Management | CRITICAL | Medium | High |
| Input Validation | HIGH | Low | High |
| Access Control | HIGH | High | High |
| Encryption at Rest | HIGH | Medium | Medium |
| Audit Logging | HIGH | Medium | High |
| Rate Limiting | MEDIUM | Low | Medium |
| SSRF Protection | MEDIUM | Low | Medium |
| MFA | MEDIUM | Medium | High |
| Dependency Scanning | MEDIUM | Low | Medium |
| Circuit Breakers | LOW | Medium | Medium |

---

## Security Roadmap

### Phase 1: Critical Fixes (0-30 days)

1. **Implement Secrets Manager**
   - Use system keyring for development
   - Configure Vault for production
   - Migrate all credentials from env.sh

2. **Add Input Validation**
   - Validate all user inputs
   - Escape SPARQL queries
   - Sanitize file paths

3. **Enable Security Scanning**
   - Add Bandit to CI/CD
   - Configure Dependabot
   - Run initial vulnerability scan

### Phase 2: High Priority (30-90 days)

4. **Implement Access Control**
   - Design RBAC model
   - Add authentication layer
   - Implement workspace isolation

5. **Add Audit Logging**
   - Structured security logs
   - Centralized logging (ELK/Splunk)
   - Configure alerts

6. **Encryption at Rest**
   - Encrypt workspace data
   - Implement key management
   - Document encryption procedures

### Phase 3: Medium Priority (90-180 days)

7. **Rate Limiting & Circuit Breakers**
   - Implement rate limiting
   - Add circuit breakers
   - Configure resource quotas

8. **SSRF Protection**
   - URL validation
   - Domain whitelisting
   - Network segmentation

9. **MFA Implementation**
   - TOTP support
   - Backup codes
   - Recovery procedures

### Phase 4: Ongoing

10. **Security Monitoring**
    - Implement SIEM
    - Configure dashboards
    - Regular penetration testing

11. **Compliance**
    - GDPR compliance review
    - Data protection impact assessment
    - Privacy policy

12. **Security Training**
    - Developer security training
    - Security champions program
    - Incident response drills

---

## Security Testing

### Automated Testing

```python
# test/security/test_input_validation.py
import pytest
from geoanalysis.geoqb.security import InputValidator, ValidationError

def test_layer_name_injection():
    """Test SQL injection attempts in layer names."""
    malicious_names = [
        "test'; DROP TABLE layers; --",
        "../../../etc/passwd",
        "test<script>alert('xss')</script>",
    ]

    for name in malicious_names:
        with pytest.raises(ValidationError):
            InputValidator.validate_layer_name(name)

def test_bbox_validation():
    """Test bounding box validation."""
    # Invalid coordinates
    with pytest.raises(ValidationError):
        InputValidator.validate_bbox([200, 0, 201, 1])  # Invalid lat

    # Valid coordinates
    assert InputValidator.validate_bbox([50.0, 8.0, 51.0, 9.0])
```

### Manual Pentesting Checklist

- [ ] Test authentication bypass
- [ ] Test authorization escalation
- [ ] Test SPARQL injection
- [ ] Test path traversal
- [ ] Test SSRF vulnerabilities
- [ ] Test rate limiting
- [ ] Test session management
- [ ] Review cryptographic implementations
- [ ] Test error handling
- [ ] Review logging for sensitive data

---

## Incident Response Plan

### Security Incident Severity Levels

**P0 - Critical:**
- Credential leak
- Data breach
- Active exploitation

**P1 - High:**
- Unauthorized access attempt
- Service disruption
- Malware detection

**P2 - Medium:**
- Failed authentication spike
- Policy violation
- Suspicious activity

**P3 - Low:**
- Configuration drift
- Compliance finding

### Response Procedures

1. **Detection & Analysis**
   - Review audit logs
   - Assess impact and scope
   - Classify severity

2. **Containment**
   - Isolate affected systems
   - Revoke compromised credentials
   - Block malicious IPs

3. **Eradication**
   - Remove malicious artifacts
   - Patch vulnerabilities
   - Update security controls

4. **Recovery**
   - Restore from clean backups
   - Verify system integrity
   - Resume normal operations

5. **Post-Incident**
   - Root cause analysis
   - Update procedures
   - Security improvements

---

## Compliance Considerations

### GDPR Compliance

**Data Subject Rights:**
- Right to access (export user data)
- Right to deletion (secure delete)
- Right to portability (data export format)
- Right to be forgotten (complete data removal)

**Implementation:**

```python
# geoqb/compliance/gdpr.py
class GDPRCompliance:
    """GDPR compliance utilities."""

    def export_user_data(self, user_id):
        """Export all user data in portable format."""
        pass

    def delete_user_data(self, user_id):
        """Securely delete all user data."""
        pass

    def anonymize_user_data(self, user_id):
        """Anonymize user data for analytics retention."""
        pass
```

---

## Security Contact

**Report Security Issues:**
- Email: security@geoqb.org
- PGP Key: [Include public key]
- Responsible disclosure policy: [Link]

**Bug Bounty:**
- Platform: [HackerOne/Bugcrowd]
- Scope: [Define in/out of scope]
- Rewards: [Define reward structure]

---

**Document Version:** 1.0
**Last Security Review:** 2024
**Next Review Due:** [Schedule quarterly reviews]
**Security Team:** [Contact information]
