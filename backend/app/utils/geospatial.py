"""
Geospatial Utilities
PRD Section 16 - Geospatial operations
"""

import math
from typing import Tuple, List, Dict, Optional
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import nearest_points
import pyproj
from geopy.distance import geodesic


class GeospatialUtils:
    """Utility functions for geospatial operations"""
    
    # WGS84 coordinate system
    WGS84 = pyproj.CRS("EPSG:4326")
    
    @staticmethod
    def haversine_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """
        Calculate great circle distance between two points
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
        
        Returns:
            Distance in kilometers
        """
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers
    
    @staticmethod
    def bearing(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """
        Calculate bearing from point 1 to point 2
        
        Returns:
            Bearing in degrees (0-360)
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        lon_diff_rad = math.radians(lon2 - lon1)
        
        x = math.sin(lon_diff_rad) * math.cos(lat2_rad)
        y = (
            math.cos(lat1_rad) * math.sin(lat2_rad)
            - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(lon_diff_rad)
        )
        
        bearing_rad = math.atan2(x, y)
        bearing_deg = (math.degrees(bearing_rad) + 360) % 360
        
        return bearing_deg
    
    @staticmethod
    def destination_point(
        lat: float,
        lon: float,
        bearing: float,
        distance_km: float,
    ) -> Tuple[float, float]:
        """
        Calculate destination point given start point, bearing, and distance
        
        Args:
            lat, lon: Start point coordinates
            bearing: Bearing in degrees
            distance_km: Distance in kilometers
        
        Returns:
            Tuple of (latitude, longitude)
        """
        # Earth radius in km
        R = 6371.0
        
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        bearing_rad = math.radians(bearing)
        
        # Angular distance
        angular_distance = distance_km / R
        
        # Calculate destination latitude
        lat2_rad = math.asin(
            math.sin(lat_rad) * math.cos(angular_distance)
            + math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
        )
        
        # Calculate destination longitude
        lon2_rad = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat_rad),
            math.cos(angular_distance) - math.sin(lat_rad) * math.sin(lat2_rad)
        )
        
        lat2 = math.degrees(lat2_rad)
        lon2 = math.degrees(lon2_rad)
        
        # Normalize longitude to -180 to 180
        lon2 = ((lon2 + 180) % 360) - 180
        
        return lat2, lon2
    
    @staticmethod
    def create_bounding_box(
        lat: float,
        lon: float,
        radius_km: float,
    ) -> Dict[str, float]:
        """
        Create bounding box around a point
        
        Args:
            lat, lon: Center point
            radius_km: Radius in kilometers
        
        Returns:
            Dict with min_lat, max_lat, min_lon, max_lon
        """
        # Approximate degrees per km at this latitude
        lat_rad = math.radians(lat)
        km_per_deg_lat = 111.32
        km_per_deg_lon = 111.32 * math.cos(lat_rad)
        
        delta_lat = radius_km / km_per_deg_lat
        delta_lon = radius_km / km_per_deg_lon
        
        return {
            "min_lat": lat - delta_lat,
            "max_lat": lat + delta_lat,
            "min_lon": lon - delta_lon,
            "max_lon": lon + delta_lon,
        }
    
    @staticmethod
    def point_in_polygon(
        lat: float,
        lon: float,
        polygon_coords: List[Tuple[float, float]],
    ) -> bool:
        """
        Check if point is inside polygon
        
        Args:
            lat, lon: Point coordinates
            polygon_coords: List of (lat, lon) tuples defining polygon
        
        Returns:
            True if point is inside polygon
        """
        point = Point(lon, lat)  # Note: Shapely uses (x, y) = (lon, lat)
        polygon = Polygon([(lon, lat) for lat, lon in polygon_coords])
        
        return polygon.contains(point)
    
    @staticmethod
    def simplify_line(
        coords: List[Tuple[float, float]],
        tolerance: float = 0.01,
    ) -> List[Tuple[float, float]]:
        """
        Simplify line using Douglas-Peucker algorithm
        
        Args:
            coords: List of (lat, lon) coordinates
            tolerance: Simplification tolerance in degrees
        
        Returns:
            Simplified list of coordinates
        """
        line = LineString([(lon, lat) for lat, lon in coords])
        simplified = line.simplify(tolerance, preserve_topology=True)
        
        return [(lat, lon) for lon, lat in simplified.coords]
    
    @staticmethod
    def grid_points(
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        resolution_km: float = 10,
    ) -> List[Tuple[float, float]]:
        """
        Generate grid of points covering bounding box
        
        Args:
            min_lat, max_lat, min_lon, max_lon: Bounding box
            resolution_km: Grid spacing in kilometers
        
        Returns:
            List of (lat, lon) grid points
        """
        # Approximate resolution in degrees
        center_lat = (min_lat + max_lat) / 2
        lat_rad = math.radians(center_lat)
        
        km_per_deg_lat = 111.32
        km_per_deg_lon = 111.32 * math.cos(lat_rad)
        
        delta_lat = resolution_km / km_per_deg_lat
        delta_lon = resolution_km / km_per_deg_lon
        
        # Generate grid
        points = []
        lat = min_lat
        while lat <= max_lat:
            lon = min_lon
            while lon <= max_lon:
                points.append((lat, lon))
                lon += delta_lon
            lat += delta_lat
        
        return points
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """
        Validate latitude and longitude
        
        Returns:
            True if valid coordinates
        """
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    @staticmethod
    def format_coordinates(lat: float, lon: float, precision: int = 4) -> str:
        """
        Format coordinates as string
        
        Args:
            lat, lon: Coordinates
            precision: Decimal places
        
        Returns:
            Formatted string like "19.0760°N, 72.8777°E"
        """
        lat_dir = "N" if lat >= 0 else "S"
        lon_dir = "E" if lon >= 0 else "W"
        
        return f"{abs(lat):.{precision}f}°{lat_dir}, {abs(lon):.{precision}f}°{lon_dir}"
    
    @staticmethod
    def dms_to_decimal(degrees: int, minutes: int, seconds: float, direction: str) -> float:
        """
        Convert DMS (Degrees Minutes Seconds) to decimal degrees
        
        Args:
            degrees: Degrees
            minutes: Minutes
            seconds: Seconds
            direction: 'N', 'S', 'E', or 'W'
        
        Returns:
            Decimal degrees
        """
        decimal = degrees + minutes / 60 + seconds / 3600
        
        if direction in ['S', 'W']:
            decimal = -decimal
        
        return decimal
    
    @staticmethod
    def decimal_to_dms(decimal: float) -> Tuple[int, int, float, str]:
        """
        Convert decimal degrees to DMS
        
        Args:
            decimal: Decimal degrees
        
        Returns:
            Tuple of (degrees, minutes, seconds, direction)
        """
        is_positive = decimal >= 0
        decimal = abs(decimal)
        
        degrees = int(decimal)
        minutes_decimal = (decimal - degrees) * 60
        minutes = int(minutes_decimal)
        seconds = (minutes_decimal - minutes) * 60
        
        # Determine direction (assuming latitude)
        direction = 'N' if is_positive else 'S'
        
        return degrees, minutes, seconds, direction


class MarineZones:
    """Marine zone definitions and checks"""
    
    # Indian EEZ approximate bounds (simplified)
    INDIAN_EEZ_BOUNDS = {
        "west_coast": {
            "min_lat": 8.0,
            "max_lat": 23.5,
            "min_lon": 68.0,
            "max_lon": 75.0,
        },
        "east_coast": {
            "min_lat": 8.0,
            "max_lat": 22.0,
            "min_lon": 80.0,
            "max_lon": 90.0,
        },
        "andaman": {
            "min_lat": 6.0,
            "max_lat": 14.0,
            "min_lon": 92.0,
            "max_lon": 94.0,
        },
    }
    
    @classmethod
    def is_in_indian_eez(cls, lat: float, lon: float) -> bool:
        """Check if point is within Indian EEZ (simplified)"""
        for zone, bounds in cls.INDIAN_EEZ_BOUNDS.items():
            if (
                bounds["min_lat"] <= lat <= bounds["max_lat"]
                and bounds["min_lon"] <= lon <= bounds["max_lon"]
            ):
                return True
        return False
    
    @classmethod
    def get_coastal_zone(cls, lat: float, lon: float) -> Optional[str]:
        """Identify which coastal zone the point belongs to"""
        for zone, bounds in cls.INDIAN_EEZ_BOUNDS.items():
            if (
                bounds["min_lat"] <= lat <= bounds["max_lat"]
                and bounds["min_lon"] <= lon <= bounds["max_lon"]
            ):
                return zone
        return None
