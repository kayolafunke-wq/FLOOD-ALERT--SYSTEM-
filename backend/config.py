"""
Configuration file for Flood Alert System
"""

import os

class Config:
    """Database and API configuration"""
    
    # Database Configuration (SQLite - no setup required!)
    DB_PATH = os.path.join(os.path.dirname(__file__), 'flood_alert.db')
    
    # API Configuration
    API_HOST = '0.0.0.0'
    API_PORT = 5000
    DEBUG = True
    
    # CORS Configuration (allows frontend to connect)
    CORS_ORIGINS = ['*']  # In production, specify exact domains
    
    # Pagination
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 100
    
    # Alert thresholds
    RAINFALL_THRESHOLD = 50.0  # mm in 24 hours
    CRITICAL_RISK_THRESHOLD = 75.0
    HIGH_RISK_THRESHOLD = 50.0
    
    @staticmethod
    def get_db_connection_string():
        """Get SQLite connection string"""
        return f"sqlite:///{Config.DB_PATH}"