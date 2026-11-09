"""
Seed the database with sample data for testing
Run with: python seed_data.py
"""

import sqlite3
from config import Config
from datetime import datetime, timedelta
import random

def seed_database():
    """Populate database with sample data"""
    conn = sqlite3.connect(Config.DB_PATH)
    cur = conn.cursor()
    
    print("Seeding database with sample data...")
    
    # Add sample regions
    regions = [
        ('Lilongwe', 'Lilongwe', 1077116, -13.9833, 33.7833),
        ('Blantyre', 'Blantyre', 800264, -15.7861, 35.0058),
        ('Chikwawa', 'Chikwawa', 115000, -16.0289, 34.7968),
        ('Mzuzu', 'Mzuzu', 133968, -11.4500, 34.0167),
        ('Karonga', 'Karonga', 61609, -9.9333, 33.9333),
        ('Mangochi', 'Mangochi', 51429, -14.4783, 35.2644),
        ('Salima', 'Salima', 37983, -13.7833, 34.4500),
        ('Nkhotakota', 'Nkhotakota', 33150, -12.9167, 34.2833)
    ]
    
    for region in regions:
        cur.execute("""
            INSERT INTO regions (name, district, population, latitude, longitude)
            VALUES (?, ?, ?, ?, ?)
        """, region)
    
    print(f"✓ Added {len(regions)} regions")
    
    # Add rainfall stations
    stations = [
        ('Lilongwe Met Station', 'LLW001', -13.9833, 33.7833, 1, 1),
        ('Chileka Airport', 'BT001', -15.6794, 34.9739, 2, 1),
        ('Chikwawa Station', 'CK001', -16.0289, 34.7968, 3, 1),
        ('Mzuzu Airport', 'MZ001', -11.4444, 34.0119, 4, 1),
        ('Karonga Station', 'KR001', -9.9333, 33.9333, 5, 1),
    ]
    
    for station in stations:
        cur.execute("""
            INSERT INTO rainfall_stations 
            (name, station_code, latitude, longitude, region_id, active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, station)
    
    print(f"✓ Added {len(stations)} rainfall stations")
    
    # Add sample rainfall data
    rainfall_count = 0
    for station_id in range(1, 6):
        for day in range(7):
            rainfall = random.uniform(0, 100)
            recorded_at = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d %H:%M:%S')
            cur.execute("""
                INSERT INTO rainfall_data (station_id, recorded_at, rainfall_mm, duration_hours)
                VALUES (?, ?, ?, ?)
            """, (station_id, recorded_at, rainfall, 24))
            rainfall_count += 1
    
    print(f"✓ Added {rainfall_count} rainfall measurements")
    
    # Add flood risk zones
    risk_zones = [
        (1, 'moderate', 45.5, -13.9833, 33.7833, 'Near river, moderate elevation'),
        (2, 'high', 65.2, -15.7861, 35.0058, 'Low elevation, heavy rainfall'),
        (3, 'low', 20.1, -15.3850, 35.3190, 'High elevation, good drainage'),
        (4, 'moderate', 38.7, -11.4500, 34.0167, 'Moderate risk area'),
        (5, 'critical', 82.3, -9.9333, 33.9333, 'Near lake, flood-prone'),
    ]
    
    for zone in risk_zones:
        cur.execute("""
            INSERT INTO flood_risk_zones 
            (region_id, risk_level, risk_score, latitude, longitude, factors)
            VALUES (?, ?, ?, ?, ?, ?)
        """, zone)
    
    print(f"✓ Added {len(risk_zones)} risk zones")
    
    # Add sample flood alerts (Chikwawa-specific)
    alerts = [
        (3, 'warning', 'Heavy rainfall detected near Shire River. Monitor water levels closely.', 48),
        (3, 'watch', 'Flood watch in effect for low-lying areas of Chikwawa district.', 24),
    ]
    
    for alert in alerts:
        region_id, level, message, duration = alert
        expires_at = (datetime.now() + timedelta(hours=duration)).strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("""
            INSERT INTO flood_alerts 
            (region_id, alert_level, message, expires_at, active, affected_population)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (region_id, level, message, expires_at, random.randint(1000, 50000)))
    
    print(f"✓ Added {len(alerts)} active alerts")
    
    # Add water bodies
    water_bodies = [
        ('Lilongwe River', 'river', 200, -13.9833, 33.7833),
        ('Lake Malawi', 'lake', 500, -12.0, 34.5),
        ('Shire River', 'river', 300, -15.8, 35.2),
    ]
    
    for wb in water_bodies:
        cur.execute("""
            INSERT INTO water_bodies (name, type, buffer_zone_m, latitude, longitude)
            VALUES (?, ?, ?, ?, ?)
        """, wb)
    
    print(f"✓ Added {len(water_bodies)} water bodies")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database seeded successfully!")
    print(f"Database location: {Config.DB_PATH}")

if __name__ == '__main__':
    seed_database()
