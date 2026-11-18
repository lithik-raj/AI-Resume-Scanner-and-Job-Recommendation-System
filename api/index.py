import os
import sys

# Ensure project root is in python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app


# WSGI middleware to normalize PATH_INFO from Vercel rewrites
class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        # If Vercel rewrote request to /api/index or /api
        if path.startswith("/api/index"):
            remainder = path[len("/api/index"):]
            environ["PATH_INFO"] = remainder if remainder.startswith("/") else ("/" + remainder)
        elif path.startswith("/api"):
            remainder = path[len("/api"):]
            environ["PATH_INFO"] = remainder if remainder.startswith("/") else ("/" + remainder)

        # Check x-matched-path header if present
        x_matched = environ.get("HTTP_X_MATCHED_PATH")
        if x_matched and not x_matched.startswith("/api") and environ.get("PATH_INFO") == "/":
            environ["PATH_INFO"] = x_matched

        environ["SCRIPT_NAME"] = ""
        return self.wsgi_app(environ, start_response)


app.wsgi_app = VercelPathMiddleware(app.wsgi_app)

# Vercel entrypoint (supports both app and handler conventions)
app = app
handler = app
