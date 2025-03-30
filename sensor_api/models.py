from django.db import models
from django.utils import timezone # Keep timezone if you use default=timezone.now
                                  # Not strictly needed if using auto_now_add=True

class VehicleSensorData(models.Model):
    # Choices for the prediction result field - good practice
    PREDICTION_CHOICES = [
        ('H', 'Healthy'), # Using single letters is efficient
        ('F', 'Faulty'),
    ]

    # Primary Key
    id = models.AutoField(primary_key=True)

    # --- Core Identifiers ---
    # Django automatically adds an 'id' AutoField as primary key if not specified otherwise.
    # This is standard and usually what you want.

    vehicle_id = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    # --- Sensor Readings ---
    # FloatField is appropriate. null=True allows DB NULL, blank=True allows empty in forms/admin.
    engine_rpm = models.FloatField()
    lub_oil_pressure = models.FloatField()
    fuel_pressure = models.FloatField()
    coolant_pressure = models.FloatField()
    lub_oil_temp = models.FloatField()
    coolant_temp = models.FloatField()

    # --- Prediction Results ---
    prediction_result = models.CharField(
        max_length=1,         # Matches the length of 'H' or 'F'
        choices=PREDICTION_CHOICES,
        null=True,            # Allows records before prediction or failed predictions
        blank=True
    )
    prediction_score = models.FloatField(null=True, blank=True)

    # --- Model Metadata ---
    class Meta:
        ordering = ['-timestamp']  # Default query order: most recent first. Good for history.
        indexes = [
            # Composite index: Speeds up filtering by vehicle_id AND ordering by timestamp.
            # Excellent for fetching specific vehicle history efficiently.
            models.Index(fields=['vehicle_id', '-timestamp'], name='sensor_api_vehicle_ts_idx'),
        ]
        verbose_name = "Vehicle Sensor Reading"
        verbose_name_plural = "Vehicle Sensor Readings"

    # --- String Representation ---
    def __str__(self):
        # Provides a readable representation in admin or debugging.
        # Including prediction result might be useful too, checking if it exists.
        prediction_str = self.get_prediction_result_display() if self.prediction_result else 'N/A'
        return f'Vehicle {self.vehicle_id} @ {self.timestamp}'