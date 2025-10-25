#!/usr/bin/env python3

import json
import logging
import os
from flask import Blueprint, request, current_app
from models.zone_models import ZoneRequest
from models.response_models import ErrorResponse
from services.zone_service import ZoneService

_logger = logging.getLogger(__name__)

zones_bp = Blueprint('zones', __name__)

# NOTE: Zone endpoints now return human-readable zone states (e.g. "presence", "away")
# as described in API_DOCS.md, using zone-specific state mappings.


@zones_bp.route("/zones", methods=['GET'])
def get_all_zones():
    """
    Get all configured zones from config system with their current values.
    
    ---
    get:
      summary: List all configured and active zones
      tags:
        - Zones
      description: Retrieves a list of zones that are defined in the configuration file and are currently active.
      responses:
        '200':
          description: A list of configured zones and their status.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ZonesListResponse'
        '503':
          $ref: '#/components/responses/ServiceUnavailable'
    """
    try:
        # Get configuration from app context
        server_config = current_app.config.get('SERVER_CONFIG')
        if not server_config or not server_config.structures:
            return current_app.response_class(
                response=json.dumps(ErrorResponse("Configuration not found").to_dict()),
                status=404,
                mimetype='application/json'
            )
        
        # Get services from app context
        context = current_app.config['MODBUS_CONTEXT']
        slave_id = current_app.config['SLAVE_ID']
        zone_service = ZoneService(context, slave_id)
        
        # Build response with all zones
        zones_response = []
        
        for structure in server_config.structures:
            base_id = structure.get('base_id')
            base_label = structure.get('base_label', f'Base {base_id}')
            
            for zone in structure.get('zones', []):
                zone_id = zone.get('id')
                zone_label = zone.get('label', f'Zone {zone_id}')
                
                try:
                    # Get current zone data from Modbus
                    zone_data = zone_service.get_zone_data(base_id, zone_id)
                    
                    zones_response.append({
                        'baseId': base_id,
                        'baseLabel': base_label,
                        'zoneId': zone_id,
                        'zoneLabel': zone_label,
                        'state': zone_data.to_dict(readable=True)['state'],
                        'setpoint': zone_data.setpoint,
                        'temperature': zone_data.temperature,
                        'relativeHumidity': zone_data.relative_humidity
                    })
                    
                except Exception as e:
                    _logger.warning(f"Could not read data for zone {base_id}/{zone_id}: {e}")
                    # Include zone in response but with null values
                    zones_response.append({
                        'baseId': base_id,
                        'baseLabel': base_label,
                        'zoneId': zone_id,
                        'zoneLabel': zone_label,
                        'state': None,
                        'setpoint': None,
                        'temperature': None,
                        'relativeHumidity': None,
                        'error': f"Could not read zone data: {str(e)}"
                    })
        
        return current_app.response_class(
            response=json.dumps({
                'zones': zones_response,
                'total': len(zones_response)
            }),
            status=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        _logger.error(f"Error getting all zones: {e}")
        return current_app.response_class(
            response=json.dumps(ErrorResponse("Internal server error").to_dict()),
            status=500,
            mimetype='application/json'
        )


@zones_bp.route("/zones/<int:base_id>/<int:zone_id>", methods=['POST', 'GET'])
def zone(base_id=None, zone_id=None):
    """
    Zone endpoint for getting and updating zone data.
    
    ---
    get:
      summary: Get specific zone information
      tags:
        - Zones
      description: Retrieves the current state, temperature, setpoint, and other details for a single configured zone.
      parameters:
        - name: base_id
          in: path
          required: true
          schema:
            type: integer
            minimum: 1
            maximum: 4
        - name: zone_id
          in: path
          required: true
          schema:
            type: integer
            minimum: 1
            maximum: 12
      responses:
        '200':
          description: Detailed information for the specified zone.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Zone'
        '400':
          $ref: '#/components/responses/BadRequest'
        '503':
          $ref: '#/components/responses/ServiceUnavailable'
    post:
      summary: Update zone state or setpoint
      tags:
        - Zones
      description: Update the state and/or setpoint for a specific zone.
      parameters:
        - name: base_id
          in: path
          required: true
          schema:
            type: integer
        - name: zone_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ZoneUpdateRequest'
      responses:
        '200':
          description: Confirmation of the zone update.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ZoneUpdateResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '503':
          $ref: '#/components/responses/ServiceUnavailable'
    
    Args:
        base_id (int): Base ID (1-4)
        zone_id (int): Zone ID (1-12)
    """
    # Get services from app context
    context = current_app.config['MODBUS_CONTEXT']
    slave_id = current_app.config['SLAVE_ID']
    zone_service = ZoneService(context, slave_id)
    
    # Validate parameters
    is_valid, error_msg = zone_service.validate_zone_params(base_id, zone_id)
    if not is_valid:
        return current_app.response_class(
            response=json.dumps(ErrorResponse(error_msg).to_dict()),
            status=400,
            mimetype='application/json'
        )
    
    if request.method == 'GET':
        try:
            zone_data = zone_service.get_zone_data(base_id, zone_id)
            base_label, zone_label = zone_service.get_zone_labels(base_id, zone_id)
            
            # Build response with zone data and labels
            response_data = zone_data.to_dict(readable=True)
            response_data.update({
                'baseId': base_id,
                'baseLabel': base_label,
                'zoneId': zone_id,
                'zoneLabel': zone_label
            })
            
            return current_app.response_class(
                response=json.dumps(response_data),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            _logger.error(f"Error getting zone data: {e}")
            return current_app.response_class(
                response=json.dumps(ErrorResponse("Internal server error").to_dict()),
                status=500,
                mimetype='application/json'
            )
    
    elif request.method == 'POST':
        try:
            payload = request.json
            if not payload:
                return current_app.response_class(
                    response=json.dumps(ErrorResponse("Invalid JSON payload").to_dict()),
                    status=400,
                    mimetype='application/json'
                )
            
            zone_request = ZoneRequest.from_dict(payload)
            is_valid, error_msg = zone_request.validate()
            if not is_valid:
                return current_app.response_class(
                    response=json.dumps(ErrorResponse(error_msg).to_dict()),
                    status=400,
                    mimetype='application/json'
                )
            
            success, message, dpt_9001_setpoint = zone_service.update_zone_data(
                base_id, zone_id, zone_request
            )
            
            response_data = {"message": message}
            if dpt_9001_setpoint is not None:
                response_data["dpt_9001_setpoint"] = dpt_9001_setpoint
            
            return current_app.response_class(
                response=json.dumps(response_data),
                status=202,
                mimetype='application/json'
            )
            
        except Exception as e:
            _logger.error(f"Error updating zone data: {e}")
            return current_app.response_class(
                response=json.dumps(ErrorResponse("Internal server error").to_dict()),
                status=500,
                mimetype='application/json'
            )
