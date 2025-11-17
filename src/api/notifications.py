#!/usr/bin/env python3

import json
import logging
from flask import Blueprint, current_app
from models.response_models import ErrorResponse
from services.notification_service import NotificationService

_logger = logging.getLogger(__name__)

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route("/notifications", methods=['GET'])
def get_hints_warnings_errors_presence():
    """
    Notifications endpoint for getting notification status.
    """
    # Get services from app context
    context = current_app.config['MODBUS_CONTEXT']
    slave_id = current_app.config['SLAVE_ID']
    notification_service = NotificationService(context, slave_id)
    
    try:
        notification_data = notification_service.get_notification_data()
        return current_app.response_class(
            response=json.dumps(notification_data.to_dict()),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        _logger.error(f"Error getting notification data: {e}")
        return current_app.response_class(
            response=json.dumps(ErrorResponse("Internal server error").to_dict()),
            status=500,
            mimetype='application/json'
        )
