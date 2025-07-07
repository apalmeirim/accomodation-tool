from __future__ import annotations
import requests
import time
from typing import Tuple, Optional

_HEADERS = {"User-Agent" : "AccommodationTool/0.1"}

def geocode (address: str, pause: float = 1.0) -> Optional[Tuple[float, float]]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format" : "json", "limit": 1}

    try:
        resp = requests.get(url, params=params, headers = _HEADERS, timeout = 10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            lat, lon = float(data[0]["lat"]), float (data[0]["lon"])
            return lat, lon
        
    except requests.RequestException:
        pass
    finally:
        time.sleep(pause)
    
    return None