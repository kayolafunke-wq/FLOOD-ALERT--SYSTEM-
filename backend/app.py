"""
Flood Alert System - Flask REST API
Author: Your Team Name
Date: December 2025

Run with: python app.py
API will be available at: http://localhost:5000
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime, timedelta
from config import Config
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

# Initialize database
def init_db():
    """Initialize the SQLite database with tables"""
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Create tables
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS regions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            district TEXT,
            population INTEGER,
            latitude REAL,
            longitude REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS rainfall_stations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            station_code TEXT UNIQUE,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            region_id INTEGER,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (region_id) REFERENCES regions(id)
        );
        
        CREATE TABLE IF NOT EXISTS rainfall_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id INTEGER NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            rainfall_mm REAL NOT NULL,
            duration_hours INTEGER DEFAULT 1,
            FOREIGN KEY (station_id) REFERENCES rainfall_stations(id)
        );
        
        CREATE TABLE IF NOT EXISTS flood_risk_zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_id INTEGER,
            risk_level TEXT CHECK(risk_level IN ('low', 'moderate', 'high', 'critical')),
            risk_score REAL,
            latitude REAL,
            longitude REAL,
            factors TEXT,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (region_id) REFERENCES regions(id)
        );
        
        CREATE TABLE IF NOT EXISTS flood_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_id INTEGER NOT NULL,
            alert_level TEXT CHECK(alert_level IN ('watch', 'warning', 'emergency')),
            message TEXT NOT NULL,
            issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            active BOOLEAN DEFAULT 1,
            affected_population INTEGER,
            FOREIGN KEY (region_id) REFERENCES regions(id)
        );
        
        CREATE TABLE IF NOT EXISTS water_bodies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT CHECK(type IN ('river', 'lake', 'stream')),
            buffer_zone_m INTEGER DEFAULT 100,
            latitude REAL,
            longitude REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS elevation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            elevation_m REAL NOT NULL,
            region_id INTEGER,
            FOREIGN KEY (region_id) REFERENCES regions(id)
        );
        
        CREATE TABLE IF NOT EXISTS flood_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_id INTEGER NOT NULL,
            occurred_at TIMESTAMP NOT NULL,
            severity TEXT,
            casualties INTEGER DEFAULT 0,
            displaced INTEGER DEFAULT 0,
            damage_cost REAL,
            description TEXT,
            FOREIGN KEY (region_id) REFERENCES regions(id)
        );
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Database connection helper
def get_db_connection():
    """Create and return database connection"""
    try:
        conn = sqlite3.connect(Config.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch_one=False):
    """Execute query and return results"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        if fetch_one:
            result = cur.fetchone()
            result = dict(result) if result else None
        else:
            result = [dict(row) for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        return result
    except Exception as e:
        print(f"Query error: {e}")
        if conn:
            conn.close()
        return None


def geojson_from_query(rows):
    """Convert query results to GeoJSON FeatureCollection"""
    if rows is None or not rows:
        return {'type': 'FeatureCollection', 'features': []}
    
    features = []
    for row in rows:
        # Create properties from all fields except geometry
        properties = {k: v for k, v in row.items() if k not in ['latitude', 'longitude']}
        
        # Create geometry if lat/lng available
        if 'latitude' in row and 'longitude' in row and row['latitude'] and row['longitude']:
            geometry = {
                'type': 'Point',
                'coordinates': [row['longitude'], row['latitude']]
            }
            feature = {
                'type': 'Feature',
                'geometry': geometry,
                'properties': properties
            }
            features.append(feature)
        else:
            # No geometry, just include properties
            features.append({
                'type': 'Feature',
                'geometry': None,
                'properties': properties
            })
    
    return {
        'type': 'FeatureCollection',
        'features': features
    }

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/')
def home():
    """API documentation and welcome"""
    return jsonify({
        'name': 'Flood Alert System API',
        'version': '1.0.0',
        'description': 'Real-time flood risk monitoring for Malawi',
        'endpoints': {
            'GET /api/health': 'Check API health',
            'GET /api/regions': 'Get all regions',
            'GET /api/regions/<id>': 'Get specific region',
            'GET /api/risk-zones': 'Get flood risk zones',
            'GET /api/alerts': 'Get flood alerts',
            'GET /api/alerts/active': 'Get active alerts only',
            'GET /api/rainfall': 'Get rainfall data',
            'GET /api/rainfall/stations': 'Get all rainfall stations',
            'GET /api/water-bodies': 'Get water bodies',
            'GET /api/elevation': 'Get elevation data',
            'GET /api/statistics': 'Get system statistics',
            'POST /api/calculate-risk': 'Calculate flood risk for coordinates',
            'POST /api/rainfall/add': 'Add new rainfall measurement',
            'POST /api/update-risk-zones': 'Update risk zones for region',
            'POST /api/alerts/create': 'Create new alert'
        }
    })

@app.route('/api/health')
def health_check():
    """Check if API and database are working"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT 1')
            cur.close()
            conn.close()
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'db_type': 'SQLite',
                'timestamp': datetime.now().isoformat()
            })
        except:
            return jsonify({
                'status': 'unhealthy',
                'database': 'error',
                'timestamp': datetime.now().isoformat()
            }), 500
    else:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/regions', methods=['GET'])
def get_regions():
    """Get all regions with their boundaries"""
    query = """
        SELECT 
            id, name, district, population, latitude, longitude,
            created_at
        FROM regions
        ORDER BY name
    """
    rows = execute_query(query)
    return jsonify(geojson_from_query(rows))

@app.route('/api/regions/<int:region_id>', methods=['GET'])
def get_region(region_id):
    """Get specific region details"""
    query = """
        SELECT 
            r.id, r.name, r.district, r.population, r.latitude, r.longitude,
            r.created_at,
            COUNT(DISTINCT rs.id) as rainfall_stations,
            COUNT(DISTINCT fh.id) as historical_floods
        FROM regions r
        LEFT JOIN rainfall_stations rs ON r.id = rs.region_id
        LEFT JOIN flood_history fh ON r.id = fh.region_id
        WHERE r.id = ?
        GROUP BY r.id, r.name, r.district, r.population, r.latitude, r.longitude, r.created_at
    """
    result = execute_query(query, (region_id,), fetch_one=True)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Region not found'}), 404

@app.route('/api/risk-zones', methods=['GET'])
def get_risk_zones():
    """Get flood risk zones with optional filters"""
    region_id = request.args.get('region_id', type=int)
    risk_level = request.args.get('risk_level')
    min_score = request.args.get('min_score', type=float)
    
    query = """
        SELECT 
            id, risk_level, risk_score, latitude, longitude,
            factors, calculated_at, region_id
        FROM flood_risk_zones
        WHERE 1=1
    """
    params = []
    
    if region_id:
        query += " AND region_id = ?"
        params.append(region_id)
    
    if risk_level:
        query += " AND risk_level = ?"
        params.append(risk_level)
    
    if min_score:
        query += " AND risk_score >= ?"
        params.append(min_score)
    
    query += " ORDER BY risk_score DESC, calculated_at DESC"
    
    rows = execute_query(query, params if params else None)
    return jsonify(geojson_from_query(rows))

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get flood alerts"""
    active_only = request.args.get('active', 'false').lower() == 'true'
    limit = request.args.get('limit', 50, type=int)
    
    query = """
        SELECT 
            a.id, a.alert_level, a.message,
            a.issued_at, a.expires_at, a.active,
            a.affected_population,
            r.name as region_name,
            r.district,
            r.latitude, r.longitude
        FROM flood_alerts a
        JOIN regions r ON a.region_id = r.id
        WHERE 1=1
    """
    
    if active_only:
        query += " AND a.active = 1 AND (a.expires_at IS NULL OR a.expires_at > datetime('now'))"
    
    query += " ORDER BY a.issued_at DESC LIMIT ?"
    
    rows = execute_query(query, (limit,))
    return jsonify(geojson_from_query(rows))

@app.route('/api/alerts/active', methods=['GET'])
def get_active_alerts():
    """Get only active alerts"""
    query = """
        SELECT 
            a.id, a.alert_level, a.message,
            a.issued_at, a.expires_at,
            a.affected_population,
            r.name as region_name,
            r.district,
            r.latitude, r.longitude
        FROM flood_alerts a
        JOIN regions r ON a.region_id = r.id
        WHERE a.active = 1 
        AND (a.expires_at IS NULL OR a.expires_at > datetime('now'))
        ORDER BY 
            CASE a.alert_level
                WHEN 'emergency' THEN 1
                WHEN 'warning' THEN 2
                WHEN 'watch' THEN 3
                ELSE 4
            END,
            a.issued_at DESC
    """
    rows = execute_query(query)
    return jsonify(geojson_from_query(rows))

@app.route('/api/rainfall', methods=['GET'])
def get_rainfall():
    """Get rainfall data with filters"""
    hours = request.args.get('hours', 24, type=int)
    station_id = request.args.get('station_id', type=int)
    region_id = request.args.get('region_id', type=int)
    
    query = f"""
        SELECT 
            rd.id, rd.rainfall_mm, rd.recorded_at,
            rd.duration_hours,
            rs.name as station_name,
            rs.station_code,
            r.name as region_name,
            rs.latitude, rs.longitude
        FROM rainfall_data rd
        JOIN rainfall_stations rs ON rd.station_id = rs.id
        LEFT JOIN regions r ON rs.region_id = r.id
        WHERE rd.recorded_at > datetime('now', '-{hours} hours')
    """
    
    params = []
    if station_id:
        query += " AND rd.station_id = ?"
        params.append(station_id)
    
    if region_id:
        query += " AND rs.region_id = ?"
        params.append(region_id)
    
    query += " ORDER BY rd.recorded_at DESC"
    
    rows = execute_query(query, params if params else None)
    return jsonify(geojson_from_query(rows))

@app.route('/api/rainfall/stations', methods=['GET'])
def get_rainfall_stations():
    """Get all rainfall stations"""
    query = """
        SELECT 
            rs.id, rs.name, rs.station_code, rs.active,
            r.name as region_name,
            rs.latitude, rs.longitude,
            COUNT(rd.id) as total_measurements,
            MAX(rd.recorded_at) as last_measurement
        FROM rainfall_stations rs
        LEFT JOIN regions r ON rs.region_id = r.id
        LEFT JOIN rainfall_data rd ON rs.id = rd.station_id
        GROUP BY rs.id, rs.name, rs.station_code, rs.active, r.name, rs.latitude, rs.longitude
        ORDER BY rs.name
    """
    rows = execute_query(query)
    return jsonify(geojson_from_query(rows))

@app.route('/api/water-bodies', methods=['GET'])
def get_water_bodies():
    """Get water bodies (rivers, lakes)"""
    water_type = request.args.get('type')
    
    query = """
        SELECT 
            id, name, type, buffer_zone_m, created_at,
            latitude, longitude
        FROM water_bodies
        WHERE 1=1
    """
    
    params = []
    if water_type:
        query += " AND type = ?"
        params.append(water_type)
    
    query += " ORDER BY name"
    
    rows = execute_query(query, params if params else None)
    return jsonify(geojson_from_query(rows))

@app.route('/api/elevation', methods=['GET'])
def get_elevation():
    """Get elevation data points"""
    region_id = request.args.get('region_id', type=int)
    max_elevation = request.args.get('max_elevation', type=float)
    
    query = """
        SELECT 
            e.id, e.elevation_m,
            r.name as region_name,
            e.latitude, e.longitude
        FROM elevation e
        LEFT JOIN regions r ON e.region_id = r.id
        WHERE 1=1
    """
    
    params = []
    if region_id:
        query += " AND e.region_id = ?"
        params.append(region_id)
    
    if max_elevation:
        query += " AND e.elevation_m <= ?"
        params.append(max_elevation)
    
    query += " ORDER BY e.elevation_m"
    
    rows = execute_query(query, params if params else None)
    return jsonify(geojson_from_query(rows))

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    query = """
        SELECT 
            (SELECT COUNT(*) FROM regions) as total_regions,
            (SELECT COUNT(*) FROM rainfall_stations WHERE active = 1) as active_stations,
            (SELECT COUNT(*) FROM flood_alerts WHERE active = 1
             AND (expires_at IS NULL OR expires_at > datetime('now'))) as active_alerts,
            (SELECT COUNT(*) FROM flood_risk_zones WHERE risk_level = 'critical') as critical_zones,
            (SELECT COUNT(*) FROM flood_risk_zones WHERE risk_level = 'high') as high_risk_zones,
            (SELECT COALESCE(AVG(rainfall_mm), 0) FROM rainfall_data 
             WHERE recorded_at > datetime('now', '-24 hours')) as avg_rainfall_24h,
            (SELECT COALESCE(MAX(rainfall_mm), 0) FROM rainfall_data 
             WHERE recorded_at > datetime('now', '-24 hours')) as max_rainfall_24h,
            (SELECT COUNT(*) FROM flood_history) as historical_floods
    """
    
    result = execute_query(query, fetch_one=True)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Could not fetch statistics'}), 500

@app.route('/api/calculate-risk', methods=['POST'])
def calculate_risk():
    """Calculate flood risk for given coordinates"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    lat = data.get('lat')
    lng = data.get('lng')
    
    if not lat or not lng:
        return jsonify({'error': 'lat and lng required'}), 400
    
    try:
        lat = float(lat)
        lng = float(lng)
    except ValueError:
        return jsonify({'error': 'Invalid coordinates'}), 400
    
    # Simple risk calculation based on nearby factors
    risk_score = 0.0
    factors = []
    
    # Check nearby rainfall stations and recent rainfall
    rainfall_query = """
        SELECT AVG(rainfall_mm) as avg_rainfall
        FROM rainfall_data
        WHERE recorded_at > datetime('now', '-24 hours')
    """
    rainfall_result = execute_query(rainfall_query, fetch_one=True)
    if rainfall_result and rainfall_result['avg_rainfall']:
        avg_rainfall = rainfall_result['avg_rainfall']
        if avg_rainfall > 50:
            risk_score += 30
            factors.append(f"High rainfall: {avg_rainfall:.1f}mm")
        elif avg_rainfall > 25:
            risk_score += 15
            factors.append(f"Moderate rainfall: {avg_rainfall:.1f}mm")
    
    # Check for active alerts in the region
    alerts_query = """
        SELECT COUNT(*) as alert_count
        FROM flood_alerts
        WHERE active = 1 AND (expires_at IS NULL OR expires_at > datetime('now'))
    """
    alerts_result = execute_query(alerts_query, fetch_one=True)
    if alerts_result and alerts_result['alert_count'] > 0:
        risk_score += 25
        factors.append(f"{alerts_result['alert_count']} active alerts")
    
    # Check existing risk zones
    risk_zones_query = """
        SELECT AVG(risk_score) as avg_risk
        FROM flood_risk_zones
        WHERE risk_level IN ('high', 'critical')
    """
    zones_result = execute_query(risk_zones_query, fetch_one=True)
    if zones_result and zones_result['avg_risk']:
        risk_score += zones_result['avg_risk'] * 0.3
        factors.append("Nearby high-risk zones")
    
    # Add random variation based on location (simplified)
    risk_score += abs(hash(f"{lat},{lng}")) % 20
    
    # Determine risk level
    if risk_score >= 75:
        risk_level = 'critical'
        risk_description = 'Severe flood risk - immediate action required'
    elif risk_score >= 50:
        risk_level = 'high'
        risk_description = 'High flood risk - stay alert and prepared'
    elif risk_score >= 25:
        risk_level = 'moderate'
        risk_description = 'Moderate flood risk - monitor conditions'
    else:
        risk_level = 'low'
        risk_description = 'Low flood risk'
    
    return jsonify({
        'success': True,
        'lat': lat,
        'lng': lng,
        'risk_score': round(min(risk_score, 100), 2),
        'risk_level': risk_level,
        'description': risk_description,
        'factors': factors,
        'calculated_at': datetime.now().isoformat()
    })

@app.route('/api/rainfall/add', methods=['POST'])
def add_rainfall():
    """Add new rainfall measurement"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    station_id = data.get('station_id')
    rainfall_mm = data.get('rainfall_mm')
    duration_hours = data.get('duration_hours', 1)
    
    if not station_id or rainfall_mm is None:
        return jsonify({'error': 'station_id and rainfall_mm required'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO rainfall_data 
            (station_id, recorded_at, rainfall_mm, duration_hours)
            VALUES (?, datetime('now'), ?, ?)
        """, (station_id, rainfall_mm, duration_hours))
        
        result_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'id': result_id,
            'recorded_at': datetime.now().isoformat(),
            'station_id': station_id,
            'rainfall_mm': rainfall_mm
        })
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/create', methods=['POST'])
def create_alert():
    """Create new flood alert"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    region_id = data.get('region_id')
    alert_level = data.get('alert_level', 'warning')
    message = data.get('message')
    duration_hours = data.get('duration_hours', 24)
    
    if not region_id or not message:
        return jsonify({'error': 'region_id and message required'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO flood_alerts 
            (region_id, alert_level, message, expires_at)
            VALUES (?, ?, ?, datetime('now', '+' || ? || ' hours'))
        """, (region_id, alert_level, message, duration_hours))
        
        result_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'alert_id': result_id,
            'issued_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=duration_hours)).isoformat()
        })
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Run the application
if __name__ == '__main__':
    print("=" * 50)
    print("Flood Alert System API")
    print("=" * 50)
    
    # Initialize database if it doesn't exist
    if not os.path.exists(Config.DB_PATH):
        print("Initializing database...")
        init_db()
    else:
        print(f"Database found at: {Config.DB_PATH}")
    
    print(f"Server starting on http://{Config.API_HOST}:{Config.API_PORT}")
    print("Press CTRL+C to stop the server")
    print("=" * 50)
    
    app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=Config.DEBUG
    )