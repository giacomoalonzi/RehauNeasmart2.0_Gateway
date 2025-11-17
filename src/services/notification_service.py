#!/usr/bin/env python3

import logging
from models.response_models import NotificationData
import const

_logger = logging.getLogger(__name__)


class NotificationService:
    """Service for notification-related business logic."""
    
    def __init__(self, context, slave_id: int):
        """
        Initialize notification service.
        
        Args:
            context: Modbus context
            slave_id (int): Modbus slave ID
        """
        self.context = context
        self.slave_id = slave_id
    
    def get_notification_data(self) -> NotificationData:
        """
        Get notification data from Modbus registers.
        
        Returns:
            NotificationData: Notification data object
        """
        hints_present = self.context[self.slave_id].getValues(
            const.READ_HR_CODE,
            const.HINTS_PRESENT_ADDR,
            count=1
        )[0] == 1
        
        warnings_present = self.context[self.slave_id].getValues(
            const.READ_HR_CODE,
            const.WARNINGS_PRESENT_ADDR,
            count=1
        )[0] == 1
        
        error_present = self.context[self.slave_id].getValues(
            const.READ_HR_CODE,
            const.ERRORS_PRESENT_ADDR,
            count=1
        )[0] == 1
        
        return NotificationData(
            hints_present=hints_present,
            warnings_present=warnings_present,
            error_present=error_present
        )
