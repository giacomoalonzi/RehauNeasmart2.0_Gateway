#!/usr/bin/env python3

import pytest

from utils import state_converter


def test_mode_to_name_success():
    assert state_converter.mode_to_name(1) == "auto"


def test_mode_to_name_invalid_int():
    with pytest.raises(ValueError):
        state_converter.mode_to_name(99)


def test_name_to_mode_accepts_string_and_int():
    assert state_converter.name_to_mode("auto") == 1
    assert state_converter.name_to_mode("manual_heating") == state_converter.name_to_mode("manual heating")
    assert state_converter.name_to_mode(3) == 3


def test_name_to_mode_invalid():
    with pytest.raises(ValueError):
        state_converter.name_to_mode("invalid-mode")


def test_state_to_name_and_back():
    assert state_converter.state_to_name(1) == "presence"
    assert state_converter.name_to_state("standby") == 3


def test_state_conversion_invalid():
    with pytest.raises(ValueError):
        state_converter.state_to_name(42)
    with pytest.raises(ValueError):
        state_converter.name_to_state("unknown")

