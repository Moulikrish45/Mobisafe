from django.urls import path, include
from .views import get_engine_health_prediction

urlpatterns = [
    path('predict/engine/', get_engine_health_prediction, name='predict-engine-health'),
]