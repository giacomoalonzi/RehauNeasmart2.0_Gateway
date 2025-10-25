#!/usr/bin/env python3

"""
OpenAPI specification generator for the Rehau Neasmart Gateway API.

This module automatically generates OpenAPI 3.0 specifications from Flask routes
and provides schemas for all API models.
"""

import yaml
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask
from marshmallow import Schema, fields


class OperationStateSchema(Schema):
    """Schema for operation state enum."""
    state = fields.Str(enum=['normal', 'reduced', 'standby', 'scheduled', 'party', 'holiday'])


class BaseInfoSchema(Schema):
    """Schema for base information."""
    id = fields.Int(example=1)
    label = fields.Str(example='First Floor')


class ZoneInfoSchema(Schema):
    """Schema for zone information."""
    id = fields.Int(example=1)
    label = fields.Str(example='Living Room')


class TemperatureSchema(Schema):
    """Schema for temperature values."""
    value = fields.Float(example=21.5)
    unit = fields.Str(enum=['°C', '°F'], example='°C')


class ZoneSchema(Schema):
    """Schema for zone data."""
    base = fields.Nested(BaseInfoSchema)
    zone = fields.Nested(ZoneInfoSchema)
    baseId = fields.Int(example=1, description="Base ID for the zone")
    baseLabel = fields.Str(example="First Floor", description="Human-readable label for the base")
    zoneId = fields.Int(example=1, description="Zone ID within the base")
    zoneLabel = fields.Str(example="Living Room", description="Human-readable label for the zone")
    state = fields.Nested(OperationStateSchema)
    temperature = fields.Nested(TemperatureSchema)
    setpoint = fields.Nested(TemperatureSchema, allow_none=True)
    relative_humidity = fields.Int(example=45)
    address = fields.Int(example=1300)


class ZonesListResponseSchema(Schema):
    """Schema for zones list response."""
    zones = fields.List(fields.Nested(ZoneSchema))
    count = fields.Int(example=8)


class ZoneUpdateRequestSchema(Schema):
    """Schema for zone update request."""
    state = fields.Str(enum=['normal', 'reduced', 'standby', 'scheduled', 'party', 'holiday'], description="Zone operation state")
    setpoint = fields.Float(description="New temperature setpoint. Ignored if state is set to 'off'.", example=22.5)


class ZoneUpdateResponseSchema(Schema):
    """Schema for zone update response."""
    base = fields.Nested(BaseInfoSchema)
    zone = fields.Nested(ZoneInfoSchema)
    updated = fields.Dict(keys=fields.Str(), values=fields.Raw)


class OperationStateResponseSchema(Schema):
    """Schema for operation state response."""
    state = fields.Str(enum=['normal', 'reduced', 'standby', 'scheduled', 'party', 'holiday'], description="Current operation state")


class OperationStateUpdateRequestSchema(Schema):
    """Schema for operation state update request."""
    state = fields.Str(enum=['normal', 'reduced', 'standby', 'scheduled', 'party', 'holiday'], required=True, description="Operation state")


class OperationStateUpdateResponseSchema(Schema):
    """Schema for operation state update response."""
    status = fields.Str(example='success')
    state = fields.Str(enum=['normal', 'reduced', 'standby', 'scheduled', 'party', 'holiday'], description="Updated operation state")


class DatabaseHealthSchema(Schema):
    """Schema for database health information."""
    healthy = fields.Bool()
    type = fields.Str()
    details = fields.Str()


class CircuitBreakerSchema(Schema):
    """Schema for circuit breaker information."""
    state = fields.Str()
    failures = fields.Int()


class ModbusHealthSchema(Schema):
    """Schema for Modbus health information."""
    healthy = fields.Bool()
    circuit_breaker = fields.Nested(CircuitBreakerSchema)


class ConfigurationSchema(Schema):
    """Schema for configuration information."""
    server_type = fields.Str()
    api_auth_enabled = fields.Bool()
    fallback_enabled = fields.Bool()


class HealthResponseSchema(Schema):
    """Schema for health response."""
    status = fields.Str(enum=['healthy', 'degraded', 'unhealthy'], example='healthy')
    version = fields.Str(example='2.1.0')
    database = fields.Nested(DatabaseHealthSchema)
    modbus = fields.Nested(ModbusHealthSchema)
    configuration = fields.Nested(ConfigurationSchema)


class ErrorSchema(Schema):
    """Schema for error responses."""
    error = fields.Str(required=True)
    status = fields.Int(required=True)
    details = fields.Dict(allow_none=True)


def create_openapi_spec(app: Flask) -> APISpec:
    """
    Create OpenAPI specification for the Flask application.
    
    Args:
        app: Flask application instance
        
    Returns:
        APISpec: Configured OpenAPI specification
    """
    spec = APISpec(
        title='Rehau Neasmart 2.0 Gateway API',
        version='2.1.0',
        openapi_version='3.0.0',
        description='API for controlling a Rehau Neasmart 2.0 system via a Modbus gateway.',
        plugins=[
            FlaskPlugin(),
            MarshmallowPlugin()
        ],
        servers=[{'url': '', 'description': 'API'}],
        tags=[
            {'name': 'Zones', 'description': 'Operations related to heating/cooling zones'},
            {'name': 'Operation', 'description': 'Endpoints for managing global system operation mode and state'},
            {'name': 'System', 'description': 'System-level information like temperature, notifications, and health'}
        ]
    )
    
    # Register schemas
    spec.components.schema('OperationState', schema=OperationStateSchema)
    spec.components.schema('BaseInfo', schema=BaseInfoSchema)
    spec.components.schema('ZoneInfo', schema=ZoneInfoSchema)
    spec.components.schema('Temperature', schema=TemperatureSchema)
    spec.components.schema('Zone', schema=ZoneSchema)
    spec.components.schema('ZonesListResponse', schema=ZonesListResponseSchema)
    spec.components.schema('ZoneUpdateRequest', schema=ZoneUpdateRequestSchema)
    spec.components.schema('ZoneUpdateResponse', schema=ZoneUpdateResponseSchema)
    spec.components.schema('OperationStateResponse', schema=OperationStateResponseSchema)
    spec.components.schema('OperationStateUpdateRequest', schema=OperationStateUpdateRequestSchema)
    spec.components.schema('OperationStateUpdateResponse', schema=OperationStateUpdateResponseSchema)
    spec.components.schema('HealthResponse', schema=HealthResponseSchema)
    spec.components.schema('Error', schema=ErrorSchema)
    
    # Add common responses
    spec.components.response('BadRequest', {
        'description': 'Bad request (e.g., validation error)',
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/Error'}
            }
        }
    })
    
    spec.components.response('ServiceUnavailable', {
        'description': 'Service unavailable (e.g., Modbus communication error)',
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/Error'}
            }
        }
    })
    
    spec.components.response('InternalError', {
        'description': 'Internal server error',
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/Error'}
            }
        }
    })
    
    return spec


def generate_openapi_yaml(app: Flask) -> str:
    """
    Generate OpenAPI YAML specification from Flask application.
    
    Args:
        app: Flask application instance
        
    Returns:
        str: OpenAPI specification in YAML format
    """
    spec = create_openapi_spec(app)
    
    # Generate spec from Flask app routes
    with app.test_request_context():
        # Register all routes from blueprints
        for rule in app.url_map.iter_rules():
            if rule.endpoint.startswith('api.'):
                try:
                    view_func = app.view_functions[rule.endpoint]
                    spec.path(view=view_func)
                except Exception as e:
                    # Skip routes that can't be documented
                    continue
    
    return yaml.dump(spec.to_dict(), default_flow_style=False, sort_keys=False)


def get_openapi_dict(app: Flask) -> dict:
    """
    Get OpenAPI specification as dictionary.
    
    Args:
        app: Flask application instance
        
    Returns:
        dict: OpenAPI specification dictionary
    """
    spec = create_openapi_spec(app)
    
    # Generate spec from Flask app routes
    with app.test_request_context():
        # Register all routes from blueprints
        for rule in app.url_map.iter_rules():
            if rule.endpoint.startswith('api.'):
                try:
                    view_func = app.view_functions[rule.endpoint]
                    spec.path(view=view_func)
                except Exception as e:
                    # Skip routes that can't be documented
                    continue
    
    return spec.to_dict()
