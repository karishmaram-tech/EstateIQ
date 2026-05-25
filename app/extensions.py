"""
app/extensions.py
=================
Flask extension instances.

Extensions are created here without being bound to an app.
The create_app() factory in app/__init__.py calls .init_app()
on each one to bind them to the specific app instance.

WHY THIS PATTERN?
If you create extensions directly on the app object, you can
only ever have one app instance. This breaks testing (each test
needs a fresh app), and it breaks advanced patterns like having
separate apps for API and admin. The init_app pattern solves this.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Create limiter without attaching to an app yet
# The key_func and storage are configured in create_app()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://"
)