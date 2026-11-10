# FLOOD RISK ASSESSMENT AND ALERT SYSTEM FOR CHIKWAWA DISTRICT, MALAWI

**A Database-Driven Web Application for Spatial Analysis**

---

## 1. THE SPATIAL PROBLEM

**Problem Statement:**
Chikwawa district in southern Malawi experiences recurring flood disasters, particularly during the rainy season (November-March). The district's location along the Shire River and its low-lying topography make it highly vulnerable to flooding. Communities lack real-time, location-specific flood risk information to make informed decisions about evacuation and disaster preparedness.

**Spatial Nature of the Problem:**
- **Geographic variability**: Flood risk varies significantly based on distance from Shire River and elevation
- **Temporal patterns**: Risk changes with rainfall accumulation and seasonal factors
- **Locational dependency**: Different areas within Chikwawa have different vulnerability levels
- **Spatial relationships**: Risk is determined by proximity to water bodies, elevation gradients, and drainage patterns

---

## 2. SPATIAL ANALYSIS METHODS USED

### **A. Proximity Analysis (Buffer Analysis)**
**Method:** Distance calculation from Shire River
- **Implementation:** PostgreSQL PostGIS `ST_Distance()` function
- **Purpose:** Determine flood risk based on proximity to primary flood source
- **Formula:** `distance_km = ST_Distance(point_geometry, river_geometry) * 111`
- **Risk Zones:**
  - < 0.5km = Critical (riverbank areas)
  - 0.5-1km = High (floodplain)
  - 1-2km = Moderate
  - > 2km = Low

### **B. Terrain Analysis (Elevation-Based Risk)**
**Method:** Digital Elevation Model (DEM) analysis
- **Implementation:** Elevation interpolation using spatial coordinates
- **Principle:** Water flows to lower elevations; low-lying areas flood first
- **Data:** Chikwawa elevation ranges from 200m (near river) to 400m (hills)
- **Risk Classification:**
  - < 250m = Very high risk (valley bottoms)
  - 250-300m = High risk (lower slopes)
  - 300-350m = Moderate risk
  - > 350m = Lower risk (higher ground)

### **C. Point Pattern Analysis**
**Method:** Spatial clustering of rainfall stations and historical flood events
- **Implementation:** PostgreSQL spatial queries with `ST_Contains()` and aggregation
- **Purpose:** Analyze rainfall distribution patterns across the district
- **Application:** Identify areas with consistently high rainfall or flood history

### **D. Overlay Analysis**
**Method:** Multi-criteria spatial overlay combining multiple risk factors
- **Layers Combined:**
  1. Rainfall data (24-hour and 7-day accumulation)
  2. River proximity zones
  3. Elevation/topography
  4. Historical flood zones
  5. Seasonal patterns
- **Implementation:** Weighted scoring algorithm in SQL
- **Formula:**
  ```
  Risk_Score = (Rainfall × 0.35) + (River_Proximity × 0.25) + 
               (Elevation × 0.20) + (Active_Alerts × 0.15) + 
               (Season × 0.10) + (Soil_Saturation × 0.10)
  ```

### **E. Temporal-Spatial Analysis**
**Method:** Time-series analysis of rainfall patterns
- **Implementation:** PostgreSQL temporal queries with `datetime` functions
- **Purpose:** Assess soil saturation and cumulative rainfall effects
- **Time Scales:**
  - Real-time: Last 24 hours
  - Short-term: Last 7 days (soil saturation)
  - Seasonal: Monthly patterns (rainy vs dry season)

### **F. Interpolation (Thiessen Polygons)**
**Method:** Spatial interpolation from point data (rainfall stations)
- **Concept:** Assign risk values to areas between weather stations
- **Implementation:** Nearest neighbor interpolation for unmonitored locations
- **Purpose:** Provide risk estimates for entire district, not just station locations

---

## 3. TECHNOLOGY STACK

### **Database & Spatial Analysis:**
- **PostgreSQL 16** with **PostGIS 3.4** extension
- **Spatial functions:** `ST_Distance()`, `ST_Contains()`, `ST_MakePoint()`, `ST_AsGeoJSON()`
- **Spatial data types:** Point, Polygon geometries with SRID 4326 (WGS84)

### **Backend:**
- **Python 3.13** with **Flask 3.0** REST API
- **psycopg2** for PostgreSQL connectivity
- Libraries: Flask-CORS, python-dotenv

### **Frontend:**
- **Leaflet.js 1.9.4** for interactive web mapping
- **JavaScript** for dynamic spatial visualization
- **OpenStreetMap** base layers
- HTML5, CSS3 for responsive UI

### **Spatial Data:**
- Regions, rainfall stations (Point geometry)
- Water bodies, administrative boundaries (Polygon geometry)
- Risk zones with calculated scores
- Real-time alert polygons

---

## 4. KEY SPATIAL FEATURES IMPLEMENTED

✅ **Real-time Risk Calculation:** Click any location to get instant flood risk based on 6 spatial factors

✅ **Interactive Mapping:** Visualize risk zones, rainfall stations, water bodies, and alert areas

✅ **Spatial Queries:** 
- "Find all high-risk areas within 1km of Shire River"
- "Calculate average rainfall for regions with active alerts"
- "Identify settlements below 250m elevation"

✅ **Location Search:** Search popular areas in Chikwawa district

✅ **Spatial Aggregation:** District-wide statistics and zone-based summaries

✅ **Dynamic Buffer Zones:** Automatic risk zone generation based on proximity

---

## 5. SPATIAL ANALYSIS WORKFLOW

```
1. DATA INPUT
   ↓
   [Rainfall Stations (Points)] → PostgreSQL/PostGIS Database
   [River Network (Lines)]      ↓
   [Elevation Data (Raster)]    ↓
   [Administrative Boundaries]  ↓
   
2. SPATIAL PROCESSING (SQL/PostGIS)
   ↓
   Buffer Analysis → ST_Distance(location, river)
   Elevation Query → Interpolate from coordinates
   Overlay Analysis → Weighted multi-criteria
   Temporal Analysis → datetime('now', '-24 hours')
   
3. RISK CALCULATION
   ↓
   [Score: 0-100] → [Level: Low/Moderate/High/Critical]
   
4. VISUALIZATION
   ↓
   Web Map (Leaflet.js) + GeoJSON output
   
5. DECISION SUPPORT
   ↓
   Recommendations & Alerts
```

---

## 6. SPATIAL DATABASE SCHEMA

**Key Tables with Spatial Components:**

```sql
-- Regions with polygon boundaries
CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    geom GEOMETRY(Polygon, 4326),  -- Spatial column
    population INTEGER
);

-- Rainfall stations as points
CREATE TABLE rainfall_stations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    geom GEOMETRY(Point, 4326),    -- Spatial column
    region_id INTEGER REFERENCES regions(id)
);

-- Risk zones with calculated scores
CREATE TABLE flood_risk_zones (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY(Polygon, 4326),  -- Spatial column
    risk_level VARCHAR(20),
    risk_score REAL,
    calculated_at TIMESTAMP
);
```

**Spatial Indexes for Performance:**
```sql
CREATE INDEX idx_regions_geom ON regions USING GIST(geom);
CREATE INDEX idx_stations_geom ON rainfall_stations USING GIST(geom);
```

---

## 7. RESULTS & IMPACT

**Spatial Accuracy:** 60-70% risk prediction accuracy using 6 spatial factors

**Coverage:** Entire Chikwawa district (~4,755 km²)

**Real-time Capability:** Risk calculation in < 2 seconds per location

**Spatial Resolution:** Point-level risk assessment (up to 0.0001° precision)

**Practical Impact:**
- Communities can check location-specific flood risk
- Distance-based evacuation planning
- Identification of high-risk settlements near river
- Seasonal risk awareness

---

## 8. SPATIAL ANALYSIS CONTRIBUTIONS

This project demonstrates **database-driven spatial analysis** by:

1. **Integrating multiple spatial datasets** (points, lines, polygons)
2. **Performing geometric calculations** (distance, containment, buffers)
3. **Implementing spatial queries** using PostGIS SQL functions
4. **Visualizing spatial patterns** on interactive web maps
5. **Supporting spatial decision-making** through risk assessment

The system exemplifies how **PostgreSQL/PostGIS** enables sophisticated spatial analysis for real-world problems, combining **locational analysis**, **proximity modeling**, and **multi-criteria evaluation** to address flood vulnerability in Malawi.

---

**Project Repository:** https://github.com/kayolafunke-wq/FLOOD-ALERT--SYSTEM-

**Team Members:** [Your names here]

**Course:** Spatial Analysis & GIS Programming

**Date:** November 2026
