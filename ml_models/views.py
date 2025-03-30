from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ml_models.engine_health_model.predict import predict_engine_health
from sensor_api.models import VehicleSensorData

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_engine_health_prediction(request):
    """
    Make a prediction about engine health and save the record to history.
    Expected request data format:
    {
        "vehicle_id": "string",
        "Engine rpm": float,
        "Lub oil pressure": float,  # kPa
        "Fuel pressure": float,     # kPa
        "Coolant pressure": float,  # kPa
        "Lub oil temp": float,      # °C
        "Coolant temp": float       # °C
    }
    """
    try:
        data = request.data
        vehicle_id = data.get('vehicle_id')
        
        if not vehicle_id:
            return Response(
                {'error': 'vehicle_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get prediction from ML model
        predictions = predict_engine_health(
            data['Engine rpm'],
            data['Lub oil pressure'],
            data['Fuel pressure'],
            data['Coolant pressure'],
            data['Lub oil temp'],
            data['Coolant temp']
        )

        # Determine prediction result
        prediction_status = 'H' if predictions['engine_condition'] == 1 else 'F'
        prediction_score = float(predictions['lstm_prediction'])

        # Save to history
        try:
            VehicleSensorData.objects.create(
                vehicle_id=str(vehicle_id),
                engine_rpm=float(data['Engine rpm']),
                lub_oil_pressure=float(data['Lub oil pressure']),
                fuel_pressure=float(data['Fuel pressure']),
                coolant_pressure=float(data['Coolant pressure']),
                lub_oil_temp=float(data['Lub oil temp']),
                coolant_temp=float(data['Coolant temp']),
                prediction_result=prediction_status,
                prediction_score=prediction_score
            )
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Error saving prediction history: {e}")

        return Response({
            'prediction': predictions,
            'status': prediction_status,
            'score': prediction_score
        })

    except KeyError as e:
        return Response(
            {'error': f'Missing required field: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Error processing prediction: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )