from rest_framework import serializers
from .models import VehicleSensorData

class VehicleSensorDataSerializer(serializers.ModelSerializer):
    prediction_result_display = serializers.CharField(source='get_prediction_result_display', read_only=True)
    
    class Meta:
        model = VehicleSensorData
        fields = [
            'vehicle_id',
            'timestamp',
            'engine_rpm',
            'lub_oil_pressure',
            'fuel_pressure',
            'coolant_pressure',
            'lub_oil_temp',
            'coolant_temp',
            'prediction_result',
            'prediction_result_display',
            'prediction_score',
        ]
        read_only_fields = ['timestamp', 'prediction_result', 'prediction_result_display', 'prediction_score']