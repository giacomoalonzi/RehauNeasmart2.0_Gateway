#!/usr/bin/env python3

import logging
from flask import Blueprint

_logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


@health_bp.route("/health")
def get_health():
    """
    Health check endpoint.
    """
    return "OK"
