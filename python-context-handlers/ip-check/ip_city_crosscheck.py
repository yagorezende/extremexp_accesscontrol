#!/usr/bin/env python3
import re
import math
import asyncio
import aiohttp

# Regex for IPv4 and IPv6
_ipv4_regex = re.compile(r'^(25[0-5]|2[0-4]\d|[01]?\d?\d)(\.(25[0-5]|2[0-4]\d|[01]?\d?\d)){3}$')
_ipv6_regex = re.compile(
    r'^(([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:)|'
    r'(([0-9A-Fa-f]{1,4}:){1,7}:)|'
    r'(([0-9A-Fa-f]{1,4}:){1,6}:[0-9A-Fa-f]{1,4})|'
    r'(([0-9A-Fa-f]{1,4}:){1,5}(:[0-9A-Fa-f]{1,4}){1,2})|'
    r'(([0-9A-Fa-f]{1,4}:){1,4}(:[0-9A-Fa-f]{1,4}){1,3})|'
    r'(([0-9A-Fa-f]{1,4}:){1,3}(:[0-9A-Fa-f]{1,4}){1,4})|'
    r'(([0-9A-Fa-f]{1,4}:){1,2}(:[0-9A-Fa-f]{1,4}){1,5})|'
    r'([0-9A-Fa-f]{1,4}:){1,6}:[0-9A-Fa-f]{1,4}|'
    r'::([0-9A-Fa-f]{1,4}:){1,5}[0-9A-Fa-f]{1,4}|'
    r'([0-9A-Fa-f]{1,4}:){1,7}:|:)'
    r'((25[0-5]|2[0-4]\d|[01]?\d?\d)(\.(25[0-5]|2[0-4]\d|[01]?\d?\d)){3})?$',
    re.IGNORECASE
)

# Synonyms and known city coords
_city_synonyms = {
    'athens': 'athens',
    'marousi': 'athens',
    'amarousion': 'athens',
    'piraeus': 'athens',
    'patra': 'patra',
    'patras': 'patra',
    'patra city': 'patra',
    'thessaloniki': 'thessaloniki',
    'thessalonica': 'thessaloniki',
    'salonika': 'thessaloniki',
    'salonica': 'thessaloniki'
}
_city_coords = {
    'athens':       {'lat': 37.9838, 'lon': 23.7275},
    'patra':        {'lat': 38.2466, 'lon': 21.7346},
    'thessaloniki': {'lat': 40.6401, 'lon': 22.9444}
}

DEFAULT_DISTANCE_KM = 20
DEFAULT_TIMEOUT_MS = 7000

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = (lat2 - lat1) * math.pi / 180
    d_lon = (lon2 - lon1) * math.pi / 180
    a = (
        math.sin(d_lat / 2)**2
        + math.cos(lat1 * math.pi / 180)
        * math.cos(lat2 * math.pi / 180)
        * math.sin(d_lon / 2)**2
    )
    return 2 * R * math.asin(math.sqrt(a))

async def _fetch(session, url, ms, debug=False):
    try:
        resp = await asyncio.wait_for(
            session.get(url, headers={"User-Agent": "node-fetch/1.0", "Accept": "*/*"}, ssl=False),
            timeout=ms / 1000
        )
        if resp.status == 200:
            return await resp.json()
        if debug:
            print(f"HTTP {resp.status} from {url}")
    except Exception as e:
        if debug:
            print(f"Request failed: {e}")
    return None

async def checkIpCity(ip, expectedCity, opts=None):
    if opts is None:
        opts = {}
    distanceKm = opts.get("distanceKm", DEFAULT_DISTANCE_KM)
    timeoutMs = opts.get("timeoutMsPerFetch", DEFAULT_TIMEOUT_MS)
    debug = opts.get("debug", False)

    if not isinstance(ip, str) or not isinstance(expectedCity, str):
        raise TypeError("ip and expectedCity must be strings")

    ip_stripped = ip.strip()
    if not _ipv4_regex.match(ip_stripped) and not _ipv6_regex.match(ip_stripped):
        raise ValueError("Invalid IP format")

    canonicalExpected = expectedCity.strip().lower()
    canonicalExpected = _city_synonyms.get(canonicalExpected, canonicalExpected)
    if canonicalExpected not in _city_coords:
        raise ValueError(f'Unknown expected city "{expectedCity}".')

    async def api1(ip_):
        return await _fetch(session, f"https://ip-api.com/json/{ip_}?fields=status,message,city,lat,lon", timeoutMs, debug)
    async def api2(ip_):
        return await _fetch(session, f"https://ipapi.co/{ip_}/json/", timeoutMs, debug)
    async def api3(ip_):
        return await _fetch(session, f"https://ipwho.is/{ip_}", timeoutMs, debug)
    async def api4(ip_):
        return await _fetch(session, f"https://freeipapi.com/api/json/{ip_}", timeoutMs, debug)
    async def api5(ip_):
        return await _fetch(session, f"https://www.geoplugin.net/json.gp?ip={ip_}", timeoutMs, debug)

    api_endpoints = [api1, api2, api3, api4, api5]
    detailLines = []
    successful = 0
    matches = 0

    async with aiohttp.ClientSession() as session:
        tasks = [api(ip_stripped) for api in api_endpoints]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, r in enumerate(results, 1):
        if isinstance(r, Exception) or r is None:
            detailLines.append(f"API #{i}: failed or empty")
            continue

        successful += 1
        city = (r.get("city") or "").strip()
        lat = r.get("lat")
        lon = r.get("lon")
        cityCanon = city.lower()
        cityCanon = _city_synonyms.get(cityCanon, cityCanon)

        if cityCanon == canonicalExpected:
            matches += 1
            detailLines.append(f'API #{i}: "{city}" (name match)')
            continue

        if isinstance(lat, (float, int)) and isinstance(lon, (float, int)):
            if math.isfinite(lat) and math.isfinite(lon):
                refLat = _city_coords[canonicalExpected]["lat"]
                refLon = _city_coords[canonicalExpected]["lon"]
                d = haversine(lat, lon, refLat, refLon)
                if d <= distanceKm:
                    matches += 1
                    detailLines.append(f'API #{i}: "{city}" (distance {d:.1f} km → {canonicalExpected})')
                    continue

        detailLines.append(f'API #{i}: "{city}" (no match)')

    if successful == 0:
        if debug:
            print("\n".join(detailLines))
        return {
            "ok": False,
            "matchRatio": 0,
            "matchingCount": 0,
            "successfulLookups": 0,
            "details": detailLines
        }

    ratio = matches / successful
    ok = ratio > 0.5

    if debug:
        print("\n".join(detailLines))

    return {
        "ok": ok,
        "matchRatio": ratio,
        "matchingCount": matches,
        "successfulLookups": successful,
        "details": detailLines
    }
