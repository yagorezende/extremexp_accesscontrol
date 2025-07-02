import math

def _to_rad(d):
    """Convert degrees to radians."""
    return d * math.pi / 180

def _haversine_meters(lat1, lon1, lat2, lon2):
    """
    Calculates the distance in meters between two coordinates
    using the Haversine formula.
    """
    R = 6371000  # approximate radius of Earth in meters
    dLat = _to_rad(lat2 - lat1)
    dLon = _to_rad(lon2 - lon1)
    
    a = (math.sin(dLat / 2) ** 2
         + math.cos(_to_rad(lat1))
         * math.cos(_to_rad(lat2))
         * math.sin(dLon / 2) ** 2)
    
    return 2 * R * math.asin(math.sqrt(a))

def _valid(value, is_lat):
    """
    Checks if 'value' is within the valid range for a latitude or longitude.
    is_lat=True => check range -90 to 90.
    is_lat=False => check range -180 to 180.
    """
    return (
        isinstance(value, (int, float))
        and not math.isnan(value)
        and (
            (-90 <= value <= 90) if is_lat else (-180 <= value <= 180)
        )
    )

def checkRadius(centerLat, centerLon, testLat, testLon, radiusMeters, opts=None):
    """
    Determines if (testLat, testLon) is within 'radiusMeters' from (centerLat, centerLon).
    
    :param centerLat: Latitude of the center
    :param centerLon: Longitude of the center
    :param testLat: Latitude of the test point
    :param testLon: Longitude of the test point
    :param radiusMeters: Radius in meters to check
    :param opts: Optional dict; e.g. {"debug": True} for debug output
    :return: A dict with distance info and a boolean indicating if it's within the radius.
    """
    if opts is None:
        opts = {}
    
    debug = opts.get('debug', False)
    
    # Ensure all inputs can be treated as floats
    centerLat, centerLon, testLat, testLon, radiusMeters = map(
        float,
        (centerLat, centerLon, testLat, testLon, radiusMeters)
    )
    
    # Validate latitudes and longitudes
    coords = [centerLat, centerLon, testLat, testLon]
    for i, val in enumerate(coords):
        # Even indices = latitude, odd indices = longitude
        if not _valid(val, i % 2 == 0):
            raise ValueError("Invalid coordinate value encountered.")
    
    # Validate the radius
    if not math.isfinite(radiusMeters):
        raise ValueError("Radius must be a finite number.")
    
    # Calculate the distance using Haversine
    distance = _haversine_meters(centerLat, centerLon, testLat, testLon)
    
    result = {
        "centerCoordinate": {"lat": centerLat, "lon": centerLon},
        "testCoordinate": {"lat": testLat, "lon": testLon},
        "radiusMeters": radiusMeters,
        "distanceMeters": round(distance, 2),
        "isWithinRadius": distance <= radiusMeters
    }
    
    if debug:
        print("Debug info:", result)
    
    return result
