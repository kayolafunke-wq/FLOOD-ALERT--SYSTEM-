# How the Flood Detection System Works

## 🎯 Overview
This system monitors and predicts flood risks in **Chikwawa district** by analyzing multiple data sources in real-time.

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (Frontend)                 │
│  • Interactive Map (Leaflet.js)                             │
│  • Risk Calculator                                           │
│  • Alert Dashboard                                           │
│  • Rainfall Monitor                                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ HTTP/REST API
                  │
┌─────────────────▼───────────────────────────────────────────┐
│              FLASK API SERVER (Backend)                      │
│  • Processes requests                                        │
│  • Calculates flood risk                                     │
│  • Manages alerts                                            │
│  • Aggregates data                                           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ SQL Queries
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                  SQLITE DATABASE                             │
│  • Regions & Districts                                       │
│  • Rainfall Stations & Data                                  │
│  • Flood Risk Zones                                          │
│  • Active Alerts                                             │
│  • Water Bodies (rivers, lakes)                              │
│  • Historical Flood Data                                     │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 How Flood Risk Detection Works

### 1. **Data Collection**
```
Rainfall Stations → Record rainfall amounts → Store in database
    ↓
Weather sensors measure:
  • Rainfall amount (mm)
  • Duration (hours)
  • Location (GPS coordinates)
```

### 2. **Risk Calculation** (The Core Algorithm)
When you click on the map or enter coordinates, the system:

```python
STEP 1: Check Recent Rainfall (24 hours)
  - Average rainfall > 50mm  → +30 risk points (HIGH)
  - Average rainfall > 25mm  → +15 risk points (MODERATE)
  
STEP 2: Check Active Alerts
  - Active emergency alerts  → +25 risk points
  
STEP 3: Check Historical Risk Zones
  - Near high-risk zones     → +20-30 risk points
  
STEP 4: Location Factors
  - Proximity to water bodies
  - Elevation level
  - Historical flood data
  
TOTAL RISK SCORE = Sum of all factors (0-100)
```

### 3. **Risk Levels**
```
0-24:   🟢 LOW       - Safe, monitor conditions
25-49:  🟡 MODERATE  - Stay informed, prepare
50-74:  🟠 HIGH      - Be alert, evacuation ready
75-100: 🔴 CRITICAL  - Immediate action required!
```

---

## 🗺️ Frontend Features

### **Interactive Map**
- **Base Layer**: OpenStreetMap showing Chikwawa
- **Risk Zones**: Color-coded areas
  - 🔴 Red = Critical risk
  - 🟠 Orange = High risk
  - 🟡 Yellow = Moderate risk
  - 🟢 Green = Low risk

### **Risk Calculator**
Click anywhere on the map to:
1. Get coordinates (latitude, longitude)
2. System calculates risk score
3. Shows risk level and factors
4. Displays recommendations

### **Alert Dashboard**
Real-time display of:
- Active flood warnings
- Emergency alerts
- Affected regions
- Population at risk

### **Rainfall Monitor**
Shows:
- Last 24 hours rainfall
- Active weather stations
- Current measurements

---

## 📡 API Endpoints

### Get System Statistics
```bash
GET /api/statistics
Response: {
  "total_regions": 8,
  "active_alerts": 2,
  "avg_rainfall_24h": 37.5,
  "critical_zones": 1,
  "high_risk_zones": 1
}
```

### Calculate Risk for Location
```bash
POST /api/calculate-risk
Body: {
  "lat": -16.0289,
  "lng": 34.7968
}
Response: {
  "risk_score": 65.2,
  "risk_level": "high",
  "description": "High flood risk - stay alert",
  "factors": ["High rainfall: 60mm", "Active alerts in region"]
}
```

### Get Active Alerts
```bash
GET /api/alerts/active
Response: {
  "features": [
    {
      "type": "Feature",
      "properties": {
        "alert_level": "warning",
        "message": "Heavy rainfall expected",
        "region": "Chikwawa"
      }
    }
  ]
}
```

### Get Rainfall Data
```bash
GET /api/rainfall?hours=24
Response: Recent rainfall measurements from all stations
```

---

## 🎬 Real-World Usage Scenario

### Scenario: Heavy Rain in Chikwawa

```
TIME: 06:00 AM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1: Rainfall Station Records Data
  • Station: Chikwawa Station (CK001)
  • Rainfall: 55mm in last 6 hours
  • Status: ACTIVE
  
  ↓ [POST /api/rainfall/add]
  
STEP 2: System Updates Database
  • New rainfall record created
  • Timestamp: 2026-11-09 06:00
  • Stored in rainfall_data table

TIME: 06:05 AM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3: Automatic Risk Assessment
  • System calculates: 55mm > 50mm threshold
  • Risk score increases: +30 points
  • Total risk: 65 (HIGH)
  
  ↓ [POST /api/alerts/create]
  
STEP 4: Alert Generated
  • Alert Level: WARNING
  • Region: Chikwawa
  • Message: "Heavy rainfall detected"
  • Expires: 24 hours

TIME: 06:10 AM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 5: User Opens Website
  • Map loads centered on Chikwawa
  • Orange zone displayed (HIGH risk)
  • Alert banner shows warning
  
STEP 6: User Clicks on Their Location
  • Coordinates: -16.0289, 34.7968
  • System calculates personal risk
  • Shows: "High flood risk - stay alert"
  • Recommends: Prepare evacuation bag

TIME: 12:00 PM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 7: Rain Continues
  • Total rainfall: 85mm (12 hours)
  • Risk increases to 82 (CRITICAL)
  • Alert upgraded to EMERGENCY
  
STEP 8: Emergency Alert Sent
  • Level: EMERGENCY
  • Message: "Evacuate immediately!"
  • Red zone on map
  • Affected population: ~30,000
```

---

## 💾 Database Tables

### **regions**
```
id | name      | district  | population | latitude  | longitude
1  | Chikwawa  | Chikwawa  | 115000    | -16.0289  | 34.7968
```

### **rainfall_stations**
```
id | name             | station_code | latitude  | longitude
1  | Chikwawa Station | CK001       | -16.0289  | 34.7968
```

### **rainfall_data**
```
id | station_id | recorded_at         | rainfall_mm | duration_hours
1  | 1          | 2026-11-09 06:00:00 | 55.0       | 6
```

### **flood_risk_zones**
```
id | region_id | risk_level | risk_score | latitude  | longitude
1  | 3         | high       | 65.2      | -16.0289  | 34.7968
```

### **flood_alerts**
```
id | region_id | alert_level | message              | active | expires_at
1  | 3         | warning     | Heavy rainfall...    | 1      | 2026-11-10
```

---

## 🔧 Key Technologies

- **SQLite**: Lightweight database, no server needed
- **Flask**: Python web framework for REST API
- **Leaflet.js**: Interactive maps
- **GeoJSON**: Geographic data format
- **REST API**: Standard communication protocol

---

## 📱 How to Use the System

1. **Open the Website**: `frontend/index.html`
2. **View the Map**: See Chikwawa and surrounding areas
3. **Check Alerts**: Red banner shows active warnings
4. **Calculate Risk**: Click anywhere on map
5. **See Rainfall**: View recent weather station data
6. **Monitor Stats**: Dashboard shows system status

---

## 🚀 Future Enhancements

1. **SMS Alerts**: Send text messages to residents
2. **Mobile App**: Android/iOS applications
3. **Machine Learning**: Predict floods based on patterns
4. **Integration**: Connect to government weather APIs
5. **Historical Analysis**: Learn from past flood events
6. **Community Reports**: Allow citizens to report flooding

---

## 📞 Emergency Contact Info

- **District Disaster Management**: [Phone]
- **Police**: 997
- **Ambulance**: 998
- **Fire Service**: 999

---

**Remember**: This system is a tool to help make informed decisions. Always follow official government guidance during emergencies! 🚨
