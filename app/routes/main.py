"""
app/routes/main.py
==================
Main application routes — serves the HTML frontend.
"""

import logging
from flask import Blueprint, render_template
from app.services.predictor import get_metrics

logger = logging.getLogger("estateiq")

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """
    Serve the main application UI.
    Passes real model metrics to the template.
    """
    metrics = get_metrics()
    return render_template("index.html", metrics=metrics)