"""
Input Validation Utilities
PRD Section 18 - Input validation and sanitization
"""

import re
from typing import Optional, Tuple
from datetime import datetime, timedelta


class InputValidator:
    """Validators for API inputs and user queries"""
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> Tuple[bool, Optional[str]]:
        """
        Validate latitude and longitude
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(lat, (int, float)):
            return False, "Latitude must be a number"
        
        if not isinstance(lon, (int, float)):
            return False, "Longitude must be a number"
        
        if not -90 <= lat <= 90:
            return False, f"Latitude {lat} is out of range (-90 to 90)"
        
        if not -180 <= lon <= 180:
            return False, f"Longitude {lon} is out of range (-180 to 180)"
        
        return True, None
    
    @staticmethod
    def validate_time_range(
        start: datetime,
        end: datetime,
        max_days: int = 30,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate time range
        
        Args:
            start: Start datetime
            end: End datetime
            max_days: Maximum allowed range in days
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(start, datetime):
            return False, "Start time must be a datetime object"
        
        if not isinstance(end, datetime):
            return False, "End time must be a datetime object"
        
        if end <= start:
            return False, "End time must be after start time"
        
        duration = (end - start).days
        if duration > max_days:
            return False, f"Time range too large: {duration} days (max {max_days})"
        
        return True, None
    
    @staticmethod
    def validate_radius(radius_km: float, max_km: float = 500) -> Tuple[bool, Optional[str]]:
        """Validate search radius"""
        if not isinstance(radius_km, (int, float)):
            return False, "Radius must be a number"
        
        if radius_km <= 0:
            return False, "Radius must be positive"
        
        if radius_km > max_km:
            return False, f"Radius {radius_km} km exceeds maximum {max_km} km"
        
        return True, None
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """
        Sanitize user input string
        
        Args:
            text: Input string
            max_length: Maximum allowed length
        
        Returns:
            Sanitized string
        """
        if not isinstance(text, str):
            return ""
        
        # Truncate to max length
        text = text[:max_length]
        
        # Remove control characters except newline and tab
        text = "".join(char for char in text if char.isprintable() or char in ['\n', '\t'])
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def validate_source_id(source_id: str) -> Tuple[bool, Optional[str]]:
        """Validate source identifier"""
        if not isinstance(source_id, str):
            return False, "Source ID must be a string"
        
        if not source_id:
            return False, "Source ID cannot be empty"
        
        # Only allow alphanumeric, underscore, hyphen
        if not re.match(r'^[a-z0-9_-]+$', source_id):
            return False, "Source ID contains invalid characters"
        
        if len(source_id) > 50:
            return False, "Source ID too long (max 50 characters)"
        
        return True, None
    
    @staticmethod
    def validate_variable_name(variable: str) -> Tuple[bool, Optional[str]]:
        """Validate variable name"""
        if not isinstance(variable, str):
            return False, "Variable name must be a string"
        
        if not variable:
            return False, "Variable name cannot be empty"
        
        # Allow alphanumeric, underscore
        if not re.match(r'^[a-z0-9_]+$', variable):
            return False, "Variable name contains invalid characters"
        
        if len(variable) > 100:
            return False, "Variable name too long (max 100 characters)"
        
        return True, None
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validate email address"""
        if not isinstance(email, str):
            return False, "Email must be a string"
        
        # Simple email regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str, min_length: int = 8) -> Tuple[bool, Optional[str]]:
        """
        Validate password strength
        
        Requirements:
        - Minimum length
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        """
        if not isinstance(password, str):
            return False, "Password must be a string"
        
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        return True, None


class QuerySanitizer:
    """Sanitize user queries for agent processing"""
    
    # Potentially harmful patterns
    SQL_INJECTION_PATTERNS = [
        r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b',
        r'[;\'"\\]',
        r'--',
        r'/\*',
        r'\*/',
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r'[;&|`$()]',
        r'\b(eval|exec|system|shell)\b',
    ]
    
    @classmethod
    def sanitize_query(cls, query: str, max_length: int = 5000) -> str:
        """
        Sanitize user query for safe processing
        
        Args:
            query: User input query
            max_length: Maximum allowed length
        
        Returns:
            Sanitized query
        """
        if not isinstance(query, str):
            return ""
        
        # Truncate
        query = query[:max_length]
        
        # Remove control characters
        query = "".join(char for char in query if char.isprintable() or char.isspace())
        
        # Strip excessive whitespace
        query = " ".join(query.split())
        
        return query
    
    @classmethod
    def contains_sql_injection(cls, text: str) -> bool:
        """Check if text contains SQL injection patterns"""
        text_upper = text.upper()
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_upper, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def contains_command_injection(cls, text: str) -> bool:
        """Check if text contains command injection patterns"""
        for pattern in cls.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def is_safe_query(cls, query: str) -> Tuple[bool, Optional[str]]:
        """
        Check if query is safe to process
        
        Returns:
            Tuple of (is_safe, reason)
        """
        if cls.contains_sql_injection(query):
            return False, "Query contains potential SQL injection"
        
        if cls.contains_command_injection(query):
            return False, "Query contains potential command injection"
        
        return True, None
