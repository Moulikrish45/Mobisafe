import random
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import VehicleSensorData
from .serializers import VehicleSensorDataSerializer
import logging
import numpy as np

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

def generate_random_engine_data(vehicle_id):
    """
    Generate random engine sensor data within realistic ranges.
    All pressure values are in kPa, temperatures in °C, and RPM in revolutions per minute.
    """
    return {
        "vehicle_id": str(vehicle_id),
        "engine_rpm": random.uniform(400, 1500),      # RPM
        "lub_oil_pressure": random.uniform(2, 30), # kPa (36-65 PSI)
        "fuel_pressure": random.uniform(2, 30),    # kPa (43-58 PSI)
        "coolant_pressure": random.uniform(2, 30),  # kPa (13-17 PSI)
        "lub_oil_temp": random.uniform(20, 90),      # °C (158-212 °F)
        "coolant_temp": random.uniform(20, 90),      # °C (185-221 °F)
        "timestamp": timezone.now().isoformat()
    }

# ViewSet for CRUD

class VehicleSensorDataViewSet(viewsets.ModelViewSet):
    queryset = VehicleSensorData.objects.all().order_by('-timestamp')
    serializer_class = VehicleSensorDataSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

# API to get latest sensor data for a specific vehicle

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_sensor_data(request, vehicle_id):
    """
    Generate random sensor data for testing. Does not save to database.
    This endpoint is for providing test input data only.
    """
    try:
        data = generate_random_engine_data(vehicle_id)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': f'Error generating sensor data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_prediction_history(request, vehicle_id):
    """Get historical prediction records for a specific vehicle."""
    try:
        queryset = VehicleSensorData.objects.filter(
            vehicle_id=str(vehicle_id)
        ).order_by('-timestamp')

        paginator = StandardResultsSetPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = VehicleSensorDataSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
        return Response(
            {'error': f'Error retrieving prediction history: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def predict_engine_kilometers(request, vehicle_id):
    """
    Predict remaining kilometers and provide comprehensive engine analysis based on current sensor data.
    Includes health metrics, maintenance recommendations, and operational insights.
    """
    try:
        # Get the latest sensor data
        data = generate_random_engine_data(vehicle_id)
        
        # Rename keys to match expected format
        sensor_data = {
            'Engine rpm': data['engine_rpm'],
            'Lub oil pressure': data['lub_oil_pressure'],
            'Fuel pressure': data['fuel_pressure'],
            'Coolant pressure': data['coolant_pressure'],
            'Lub oil temp': data['lub_oil_temp'],
            'Coolant temp': data['coolant_temp']
        }
        
        # Calculate health metrics
        health_score = calculate_engine_health(sensor_data)
        remaining_km = calculate_remaining_kilometers(health_score)
        maintenance_info = get_maintenance_recommendations(sensor_data)
        performance_analysis = analyze_engine_performance(sensor_data)
        
        response_data = {
            'vehicle_id': vehicle_id,
            'timestamp': data['timestamp'],
            
            # Basic health metrics
            'health_metrics': {
                'overall_score': health_score,
                'status': get_health_status(health_score),
                'remaining_kilometers': remaining_km,
                'estimated_maintenance_due_km': max(0, remaining_km - maintenance_info['urgent_maintenance_threshold'])
            },
            
            # Current sensor readings with status indicators
            'current_readings': {
                param: {
                    'value': value,
                    'unit': get_parameter_unit(param),
                    'status': get_parameter_status(param, value),
                    'deviation_from_ideal': calculate_deviation(param, value)
                }
                for param, value in sensor_data.items()
            },
            
            # Maintenance recommendations
            'maintenance_recommendations': {
                'urgent_actions': maintenance_info['urgent_actions'],
                'preventive_actions': maintenance_info['preventive_actions'],
                'next_service_estimate_km': maintenance_info['next_service_km'],
                'risk_level': maintenance_info['risk_level']
            },
            
            # Performance analysis
            'performance_analysis': {
                'efficiency_score': performance_analysis['efficiency_score'],
                'power_output_status': performance_analysis['power_output_status'],
                'thermal_balance': performance_analysis['thermal_balance'],
                'pressure_systems': performance_analysis['pressure_systems'],
                'operational_state': performance_analysis['operational_state']
            },
            
            # Operational recommendations
            'operational_recommendations': get_operational_recommendations(sensor_data, health_score)
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error predicting engine kilometers for vehicle {vehicle_id}: {str(e)}")
        return Response(
            {'error': 'Error calculating engine analysis'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def calculate_engine_health(data):
    """
    Calculate engine health score based on sensor readings.
    Returns a score between 0 (poor) and 1 (excellent).
    """
    # Define ideal ranges and weights for each parameter
    params = {
        'Engine rpm': {
            'ideal': (800, 2200),  # More lenient RPM range
            'acceptable': (600, 2800),
            'weight': 0.2
        },
        'Lub oil pressure': {
            'ideal': (2.0, 5.0),  # Wider pressure range
            'acceptable': (1.8, 5.5),
            'weight': 0.2
        },
        'Fuel pressure': {
            'ideal': (3.0, 16.0),  # More lenient fuel pressure
            'acceptable': (2.5, 18.0),
            'weight': 0.15
        },
        'Coolant pressure': {
            'ideal': (1.2, 3.5),  # Adjusted coolant pressure
            'acceptable': (1.0, 4.0),
            'weight': 0.15
        },
        'Lub oil temp': {
            'ideal': (70.0, 85.0),  # Wider temperature range
            'acceptable': (65.0, 90.0),
            'weight': 0.15
        },
        'Coolant temp': {
            'ideal': (70.0, 88.0),  # More lenient coolant temp
            'acceptable': (65.0, 92.0),
            'weight': 0.15
        }
    }
    
    total_score = 0
    for param, config in params.items():
        value = data[param]
        ideal_min, ideal_max = config['ideal']
        acceptable_min, acceptable_max = config['acceptable']
        weight = config['weight']
        
        # Calculate parameter score
        if ideal_min <= value <= ideal_max:
            # Value is in ideal range
            score = 1.0
        elif acceptable_min <= value <= acceptable_max:
            # Value is in acceptable range - calculate proportional score
            if value < ideal_min:
                score = 0.7 + 0.3 * (value - acceptable_min) / (ideal_min - acceptable_min)
            else:
                score = 0.7 + 0.3 * (acceptable_max - value) / (acceptable_max - ideal_max)
        else:
            # Value is outside acceptable range
            if value < acceptable_min:
                score = max(0, 0.7 * (value / acceptable_min))
            else:
                score = max(0, 0.7 * (acceptable_max / value))
        
        total_score += score * weight
    
    # Round to 2 decimal places
    return round(total_score, 2)

def calculate_remaining_kilometers(health_score):
    """
    Convert health score to estimated remaining kilometers.
    Uses a more optimistic non-linear scale.
    """
    # Base maximum kilometers for a perfect health score
    MAX_KM = 8000  # Increased from 5000
    
    # Apply non-linear scaling with more optimistic curve
    if health_score >= 0.7:
        # Excellent/Good condition - bonus distance
        remaining_km = int(MAX_KM * (1 + (health_score - 0.7) * 0.5))
    else:
        # Fair/Poor condition - gradual decrease
        remaining_km = int(MAX_KM * (health_score ** 1.2))
    
    # Add some randomness (±5%)
    variation = random.uniform(0.95, 1.05)
    remaining_km = int(remaining_km * variation)
    
    return remaining_km

def get_health_status(health_score):
    """
    Convert health score to a descriptive status with more balanced ranges.
    """
    if health_score >= 0.85:
        return "Excellent"
    elif health_score >= 0.70:
        return "Good"
    elif health_score >= 0.50:
        return "Fair"
    elif health_score >= 0.30:
        return "Poor"
    else:
        return "Critical"

def get_parameter_unit(param):
    """Return the appropriate unit for each parameter."""
    units = {
        'Engine rpm': 'RPM',
        'Lub oil pressure': 'kPa',
        'Fuel pressure': 'kPa',
        'Coolant pressure': 'kPa',
        'Lub oil temp': '°C',
        'Coolant temp': '°C'
    }
    return units.get(param, '')

def get_parameter_status(param, value):
    """Determine the status of a parameter based on its value with more lenient ranges."""
    ranges = {
        'Engine rpm': {
            'optimal': (800, 2200),
            'warning': (600, 2800),
            'critical': (400, 3200)
        },
        'Lub oil pressure': {
            'optimal': (2.0, 5.0),
            'warning': (1.8, 5.5),
            'critical': (1.5, 6.0)
        },
        'Fuel pressure': {
            'optimal': (3.0, 16.0),
            'warning': (2.5, 18.0),
            'critical': (2.0, 20.0)
        },
        'Coolant pressure': {
            'optimal': (1.2, 3.5),
            'warning': (1.0, 4.0),
            'critical': (0.8, 4.5)
        },
        'Lub oil temp': {
            'optimal': (70.0, 85.0),
            'warning': (65.0, 90.0),
            'critical': (60.0, 95.0)
        },
        'Coolant temp': {
            'optimal': (70.0, 88.0),
            'warning': (65.0, 92.0),
            'critical': (60.0, 97.0)
        }
    }
    
    range_info = ranges.get(param, {})
    if not range_info:
        return 'Unknown'
        
    if value >= range_info['optimal'][0] and value <= range_info['optimal'][1]:
        return 'Optimal'
    elif value >= range_info['warning'][0] and value <= range_info['warning'][1]:
        return 'Warning'
    else:
        return 'Critical'

def calculate_deviation(param, value):
    """Calculate the percentage deviation from optimal range."""
    optimal_ranges = {
        'Engine rpm': (700, 2500),
        'Lub oil pressure': (2.5, 4.5),
        'Fuel pressure': (3.5, 15.0),
        'Coolant pressure': (1.5, 3.0),
        'Lub oil temp': (75.0, 82.0),
        'Coolant temp': (75.0, 85.0)
    }
    
    optimal_range = optimal_ranges.get(param)
    if not optimal_range:
        return 0
        
    optimal_mid = (optimal_range[0] + optimal_range[1]) / 2
    deviation = ((value - optimal_mid) / optimal_mid) * 100
    return round(deviation, 1)

def get_maintenance_recommendations(data):
    """Generate maintenance recommendations based on sensor data."""
    urgent_actions = []
    preventive_actions = []
    risk_level = "Low"
    next_service_km = 5000
    urgent_maintenance_threshold = 1000

    # Check each parameter and add recommendations
    for param, value in data.items():
        status = get_parameter_status(param, value)
        if status == 'Critical':
            urgent_actions.append(f"Immediate inspection of {param.lower()} required")
            risk_level = "High"
            next_service_km = 0
        elif status == 'Warning':
            preventive_actions.append(f"Schedule {param.lower()} inspection")
            risk_level = max(risk_level, "Medium")
            next_service_km = min(next_service_km, 2500)

    return {
        'urgent_actions': urgent_actions,
        'preventive_actions': preventive_actions,
        'risk_level': risk_level,
        'next_service_km': next_service_km,
        'urgent_maintenance_threshold': urgent_maintenance_threshold
    }

def analyze_engine_performance(data):
    """Analyze engine performance metrics."""
    # Calculate efficiency score based on RPM and pressures
    rpm = data['Engine rpm']
    lub_pressure = data['Lub oil pressure']
    fuel_pressure = data['Fuel pressure']
    
    efficiency_score = round(
        (get_parameter_status('Engine rpm', rpm) == 'Optimal') * 0.4 +
        (get_parameter_status('Lub oil pressure', lub_pressure) == 'Optimal') * 0.3 +
        (get_parameter_status('Fuel pressure', fuel_pressure) == 'Optimal') * 0.3,
        2
    )
    
    # Analyze thermal balance
    thermal_balance = "Optimal"
    if abs(data['Lub oil temp'] - data['Coolant temp']) > 10:
        thermal_balance = "Suboptimal"
    
    # Analyze pressure systems
    pressure_status = "Normal"
    if any(get_parameter_status(p, data[p]) == 'Critical' 
           for p in ['Lub oil pressure', 'Fuel pressure', 'Coolant pressure']):
        pressure_status = "Critical"
    elif any(get_parameter_status(p, data[p]) == 'Warning' 
            for p in ['Lub oil pressure', 'Fuel pressure', 'Coolant pressure']):
        pressure_status = "Warning"
    
    return {
        'efficiency_score': efficiency_score,
        'power_output_status': get_power_output_status(rpm),
        'thermal_balance': thermal_balance,
        'pressure_systems': pressure_status,
        'operational_state': get_operational_state(data)
    }

def get_power_output_status(rpm):
    """Determine power output status based on RPM."""
    if rpm < 600:
        return "Low - Potential stalling risk"
    elif rpm <= 1500:
        return "Normal - Optimal operating range"
    elif rpm <= 2500:
        return "High - Increased wear risk"
    else:
        return "Critical - Immediate attention required"

def get_operational_state(data):
    """Determine overall operational state."""
    statuses = [get_parameter_status(param, value) for param, value in data.items()]
    critical_count = statuses.count('Critical')
    warning_count = statuses.count('Warning')
    
    if critical_count > 0:
        return "Requires immediate attention"
    elif warning_count > 1:
        return "Maintenance recommended"
    elif warning_count == 1:
        return "Monitor closely"
    else:
        return "Normal operation"

def get_operational_recommendations(data, health_score):
    """Generate operational recommendations based on sensor data and health score."""
    recommendations = []
    
    # RPM-based recommendations
    rpm = data['Engine rpm']
    if rpm < 600:
        recommendations.append("Increase engine RPM to prevent stalling")
    elif rpm > 2500:
        recommendations.append("Reduce engine load to prevent excessive wear")
    
    # Temperature-based recommendations
    if data['Lub oil temp'] > 82:
        recommendations.append("Monitor oil temperature - Consider reducing load")
    if data['Coolant temp'] > 85:
        recommendations.append("Check cooling system efficiency")
    
    # Pressure-based recommendations
    if data['Lub oil pressure'] < 2.5:
        recommendations.append("Check oil level and pressure system")
    if data['Fuel pressure'] < 3.5:
        recommendations.append("Inspect fuel delivery system")
    
    # Health score based recommendations
    if health_score < 0.4:
        recommendations.append("Schedule immediate maintenance inspection")
    elif health_score < 0.6:
        recommendations.append("Plan maintenance within next 1000 km")
    
    return recommendations