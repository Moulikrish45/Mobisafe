from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VehicleSensorDataViewSet,
    get_latest_sensor_data,
    get_prediction_history,
    predict_engine_kilometers
)

router = DefaultRouter()
router.register(r'data', VehicleSensorDataViewSet, basename='vehicle-sensor')

urlpatterns = [
    path('', include(router.urls)),
    path('latest/<str:vehicle_id>/', get_latest_sensor_data, name='latest-sensor-data'),
    path('history/<str:vehicle_id>/', get_prediction_history, name='prediction-history'),
    path('remaining-km/<str:vehicle_id>/', predict_engine_kilometers, name='predict-engine-kilometers'),
]
