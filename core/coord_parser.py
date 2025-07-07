# core/coord_parser.py
"""
Utility to parse coordinates copied from Google Maps, Wikipedia, etc.

Accepts:
    • 35°38′56.67″N 139°47′22.29″E
    • 35°38'56.67"N, 139°47'22.29"E
    • 35.6490750, 139.7895250
Returns
    (lat_float, lon_float)  or  None if parsing fails
"""

import re
from typing import Optional, Tuple

# Regex for decimal  (lat, lon)
_DECIMAL_RE = re.compile(
    r"""
    (?P<lat>[+-]?\d+(?:\.\d+)?)      # latitude
    [,\s]+
    (?P<lon>[+-]?\d+(?:\.\d+)?)
    """,
    re.VERBOSE,
)

# Regex for DMS 35°38′56.67″N
_DMS_RE = re.compile(
    r"""
    (?P<deg>\d+)[°\s]*
    (?P<min>\d+)[′']?
    (?P<sec>\d+(?:\.\d+)?)[″"]?
    (?P<dir>[NSEW])
    """,
    re.VERBOSE | re.IGNORECASE,
)

def _dms_to_decimal(deg: float, minutes: float, seconds: float, direction: str) -> float:
    val = deg + minutes / 60 + seconds / 3600
    if direction.upper() in ("S", "W"):
        val = -val
    return val

def parse(coord_str: str) -> Optional[Tuple[float, float]]:
    # 1) Try decimal
    m = _DECIMAL_RE.search(coord_str)
    if m:
        return float(m.group("lat")), float(m.group("lon"))

    # 2) Try DMS – need two matches (lat & lon)
    matches = list(_DMS_RE.finditer(coord_str))
    if len(matches) >= 2:
        first, second = matches[0], matches[1]
        lat = _dms_to_decimal(
            float(first.group("deg")),
            float(first.group("min")),
            float(first.group("sec")),
            first.group("dir"),
        )
        lon = _dms_to_decimal(
            float(second.group("deg")),
            float(second.group("min")),
            float(second.group("sec")),
            second.group("dir"),
        )
        return lat, lon

    return None
