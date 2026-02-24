import math
from typing import Dict

import numpy as np
from geopandas import GeoDataFrame
from pandas import Series
from shapely import Point, Polygon


def is_geometrical_entry(location: Series) -> bool:
    try:
        return hasattr(location['geometry'], 'x') and hasattr(location['geometry'], 'y')
    except (AttributeError, KeyError):
        return False


def to_meters(map_data: GeoDataFrame) -> GeoDataFrame:
    return map_data.to_crs(map_data.estimate_utm_crs())


def get_center_of_polygon(location: Series) -> Point:
    p = location['geometry']
    assert isinstance(p, Polygon)

    return p.centroid


def serialize_location(location: Series) -> Dict:
    result = {}
    for key, value in location.items():
        if isinstance(value, np.integer):
            result[key] = int(value)
        elif isinstance(value, (np.floating, float)):
            result[key] = None if math.isnan(value) else float(value)
        elif isinstance(value, np.bool_):
            result[key] = bool(value)
        elif hasattr(value, '__geo_interface__'):  # Shapely geometry
            result[key] = value.__geo_interface__
        else:
            result[key] = value
    return result
