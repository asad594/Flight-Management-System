"""
Database Seeding Script for SkyBound Flight Management System.
Populates initial superuser administrator accounts and default sample flight schedules into Django ORM.
"""

import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flight_system.settings')
django.setup()

from core.models import Flight
from django.contrib.auth.models import User

# Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@skyglass.com', 'admin123')
    print("Superuser 'admin' created with password 'admin123'")

# Create initial flights
flights_data = [
    {
        'flight_number': 'SG101',
        'origin': 'London',
        'destination': 'Paris',
        'departure_time': timezone.now() + timedelta(days=1, hours=10),
        'arrival_time': timezone.now() + timedelta(days=1, hours=12),
        'price': 150.00,
        'seats_available': 50
    },
    {
        'flight_number': 'SG202',
        'origin': 'New York',
        'destination': 'Tokyo',
        'departure_time': timezone.now() + timedelta(days=2, hours=8),
        'arrival_time': timezone.now() + timedelta(days=2, hours=22),
        'price': 850.00,
        'seats_available': 120
    },
    {
        'flight_number': 'SG303',
        'origin': 'Dubai',
        'destination': 'Singapore',
        'departure_time': timezone.now() + timedelta(days=3, hours=14),
        'arrival_time': timezone.now() + timedelta(days=3, hours=21),
        'price': 420.00,
        'seats_available': 80
    }
]

for data in flights_data:
    Flight.objects.get_or_create(flight_number=data['flight_number'], defaults=data)

print("Sample flights seeded successfully.")
