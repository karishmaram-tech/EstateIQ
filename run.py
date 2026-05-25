"""
run.py — EstateIQ Application Entry Point
==========================================
Starts the Flask development server.

Usage:
    python run.py                    # Development
    gunicorn run:app                 # Production (Hugging Face)

The app object is created by the application factory
in app/__init__.py. This file just creates it and
optionally starts the dev server.
"""

import os
import logging

# Set up logging before creating the app
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            "/tmp/app.log" if os.name != "nt" else "app.log",
            mode="a",
            encoding="utf-8"
        )
    ]
)

import config
from app import create_app

config.print_config_summary()

# Create the application instance
# This is what gunicorn imports: gunicorn run:app
app = create_app()

if __name__ == "__main__":
    logger = logging.getLogger("estateiq")
    logger.info(f"Starting {config.APP_NAME} on port {config.PORT}")
    app.run(
        host="0.0.0.0",
        port=config.PORT,
        debug=config.DEBUG
    )