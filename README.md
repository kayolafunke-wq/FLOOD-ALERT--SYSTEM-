# Flood Alert System - Malawi

Real-time flood risk monitoring and alert system using SQLite, Flask API, and web mapping.

## Problem Statement
Flooding is a recurring problem in Malawi, particularly in low-lying areas. Communities need real-time information about flood risks to take preventive measures and save lives.

## Solution
A web-based flood alert system that:
- Analyzes spatial data (elevation, water bodies, rainfall)
- Calculates flood risk scores for any location
- Displays risk zones on an interactive map
- Issues automated alerts for high-risk areas
- Tracks rainfall data from weather stations

## Technologies Used
- **Database:** SQLite (no installation required!)
- **Backend:** Python Flask REST API
- **Frontend:** HTML, CSS, JavaScript, Leaflet.js
- **Mapping:** OpenStreetMap with Leaflet

## Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Backend
```bash
python app.py
```
The database will be created automatically on first run!

### 3. (Optional) Add Sample Data
```bash
python seed_data.py
```

### 4. Open the Frontend
Open `frontend/index.html` in a web browser

## API Endpoints
- `GET /api/health` - Check API status
- `GET /api/statistics` - System statistics
- `GET /api/regions` - All regions
- `GET /api/risk-zones` - Flood risk zones
- `GET /api/alerts/active` - Active alerts
- `GET /api/rainfall` - Recent rainfall data
- `GET /api/rainfall/stations` - All weather stations
- `POST /api/calculate-risk` - Calculate risk for coordinates
- `POST /api/rainfall/add` - Add rainfall measurement
- `POST /api/alerts/create` - Create new alert

## Features
✅ No database server setup required (uses SQLite)  
✅ Interactive map with flood risk visualization  
✅ Real-time rainfall monitoring  
✅ Risk calculator for any location  
✅ Alert management system  
✅ RESTful API for easy integration  

## Project Structure
```
flood-alert-system/
├── backend/
│   ├── app.py              # Main Flask API
│   ├── config.py           # Configuration
│   ├── seed_data.py        # Sample data script
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main UI
│   ├── css/styles.css      # Styling
│   └── js/app.js           # Frontend logic
└── README.md
```

## Future Improvements
- SMS alert integration
- Mobile application
- Machine learning for flood prediction
- Historical flood analysis dashboard
- Integration with government weather APIs

## Contributors
- Your Team Name

## License
MIT License
