#!/usr/bin/env python3

import pytest
from app_factory import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()


def test_operation_mode_v1_get_returns_integer(client):
    response = client.get('/api/operation/mode')
    assert response.status_code == 200
    payload = response.get_json()
    assert 'mode' in payload
    assert isinstance(payload['mode'], int)


def test_operation_mode_v2_get_returns_readable_string(client):
    response = client.get('/api/v2/operation/mode')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['mode'] in {'off', 'auto', 'heating', 'cooling', 'manual heating', 'manual cooling'}


def test_operation_mode_v2_post_accepts_string(client):
    response = client.post('/api/v2/operation/mode', json={'mode': 'heating'})
    assert response.status_code == 202
    payload = response.get_json()
    assert payload['mode'] == 'heating'


def test_operation_state_v2_post_accepts_integer(client):
    response = client.post('/api/v2/operation/state', json={'state': 1})
    assert response.status_code == 202
    payload = response.get_json()
    assert payload['state'] == 'normal'

