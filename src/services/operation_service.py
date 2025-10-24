#!/usr/bin/env python3

"""Service layer for global operation mode and state interactions."""

from __future__ import annotations

import logging
from typing import Protocol

import const
from utils import state_converter

_logger = logging.getLogger(__name__)


class ModbusContext(Protocol):
    def getValues(self, slave_id: int, address: int, count: int = 1):
        ...

    def setValues(self, slave_id: int, address: int, values):
        ...


class OperationService:
    """Facade responsible for reading and writing global operation mode/state."""

    def __init__(self, context, slave_id: int):
        self._context = context
        self._slave_id = slave_id

    # Mode helpers --------------------------------------------------
    def get_mode(self) -> int:
        mode_value = self._context[self._slave_id].getValues(
            const.READ_HR_CODE,
            const.GLOBAL_OP_MODE_ADDR,
            count=1,
        )[0]
        _logger.debug("Fetched operation mode value %s", mode_value)
        return mode_value

    def get_mode_name(self) -> str:
        return state_converter.mode_to_name(self.get_mode())

    def set_mode(self, value: int) -> None:
        _logger.debug("Writing operation mode value %s", value)
        self._context[self._slave_id].setValues(
            const.WRITE_HR_CODE,
            const.GLOBAL_OP_MODE_ADDR,
            [value] if not isinstance(value, list) else value,
        )

    # State helpers -------------------------------------------------
    def get_state(self) -> int:
        state_value = self._context[self._slave_id].getValues(
            const.READ_HR_CODE,
            const.GLOBAL_OP_STATE_ADDR,
            count=1,
        )[0]
        _logger.debug("Fetched operation state value %s", state_value)
        return state_value

    def get_state_name(self) -> str:
        return state_converter.state_to_name(self.get_state())

    def set_state(self, value: int) -> None:
        _logger.debug("Writing operation state value %s", value)
        self._context[self._slave_id].setValues(
            const.WRITE_HR_CODE,
            const.GLOBAL_OP_STATE_ADDR,
            [value] if not isinstance(value, list) else value,
        )

