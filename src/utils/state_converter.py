#!/usr/bin/env python3

"""Utilities for converting operation mode/state integers to readable names and back."""

from __future__ import annotations

from typing import Union

import const


def _normalize_key(value: str) -> str:
    """Normalize incoming string keys to align with constants mapping."""
    normalized = value.strip().lower().replace('-', ' ').replace('_', ' ')
    return ' '.join(normalized.split())


def mode_to_name(mode: int) -> str:
    """Convert an integer operation mode to its human-readable name."""
    if not isinstance(mode, int):
        raise ValueError("operation mode must be an integer")
    try:
        return const.MODE_MAPPING[mode]
    except KeyError as exc:
        raise ValueError(f"unknown operation mode '{mode}'") from exc


def name_to_mode(name: Union[str, int]) -> int:
    """Convert a human-readable operation mode name (or int) to its integer value."""
    if isinstance(name, int):
        return name
    if not isinstance(name, str):
        raise ValueError("operation mode must be provided as string or integer")
    normalized = _normalize_key(name)
    try:
        return const.MODE_MAPPING_REVERSE[normalized]
    except KeyError as exc:
        raise ValueError(f"unknown operation mode '{name}'") from exc


def state_to_name(state: int) -> str:
    """Convert an integer operation state to its human-readable name."""
    if not isinstance(state, int):
        raise ValueError("operation state must be an integer")
    try:
        return const.STATE_MAPPING[state]
    except KeyError as exc:
        raise ValueError(f"unknown operation state '{state}'") from exc


def name_to_state(name: Union[str, int]) -> int:
    """Convert a human-readable operation state name (or int) to its integer value."""
    if isinstance(name, int):
        return name
    if not isinstance(name, str):
        raise ValueError("operation state must be provided as string or integer")
    normalized = _normalize_key(name)
    try:
        return const.STATE_MAPPING_REVERSE[normalized]
    except KeyError as exc:
        raise ValueError(f"unknown operation state '{name}'") from exc


def zone_state_to_name(state: int) -> str:
    """Convert an integer zone state to its human-readable name."""
    if not isinstance(state, int):
        raise ValueError("zone state must be an integer")
    try:
        return const.ZONE_STATE_MAPPING[state]
    except KeyError as exc:
        raise ValueError(f"unknown zone state '{state}'") from exc


def name_to_zone_state(name: Union[str, int]) -> int:
    """Convert a human-readable zone state name (or int) to its integer value."""
    if isinstance(name, int):
        return name
    if not isinstance(name, str):
        raise ValueError("zone state must be provided as string or integer")
    normalized = _normalize_key(name)
    try:
        return const.ZONE_STATE_MAPPING_REVERSE[normalized]
    except KeyError as exc:
        raise ValueError(f"unknown zone state '{name}'") from exc

