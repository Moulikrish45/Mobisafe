# Generated by Django 5.1.7 on 2025-03-30 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleSensorData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('vehicle_id', models.CharField(max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('engine_rpm', models.FloatField()),
                ('lub_oil_pressure', models.FloatField()),
                ('fuel_pressure', models.FloatField()),
                ('coolant_pressure', models.FloatField()),
                ('lub_oil_temp', models.FloatField()),
                ('coolant_temp', models.FloatField()),
                ('prediction_result', models.CharField(blank=True, choices=[('H', 'Healthy'), ('F', 'Faulty')], max_length=1, null=True)),
                ('prediction_score', models.FloatField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Vehicle Sensor Reading',
                'verbose_name_plural': 'Vehicle Sensor Readings',
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['vehicle_id', '-timestamp'], name='sensor_api_vehicle_ts_idx')],
            },
        ),
    ]
