from math import radians, sin, cos, sqrt, atan2

RADIUS = 6371.0

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = (sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon /2) ** 2)
    return 2 * RADIUS * atan2(sqrt(a), sqrt(1 - a))