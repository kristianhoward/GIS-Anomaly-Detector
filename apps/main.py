
import geopandas
import osmnx
from numpy.testing.overrides import get_overridable_numpy_ufuncs

"""
Implement a script that:

Loads it with geopandas
Detects missing fields
Outputs a JSON report
"""



G = osmnx.features_from_place("Beaumont, California, USA", tags=tags)
E = osmnx.features_from_place("Beaumont, California, USA", tags=places_to_eat)



"""
Dev notes, my first time using OSMnx, which the crowdsourced OpenStreetMaps data, I began querying for businesses in my local town.
I found the first entry was titled "Moon Dogs", a barbeque eatery that I have never heard of or driven by in my year of living here.
When putting it into Google, the AI hallucinated the business, even gave it an address. When I plotted it in Google Maps, it was pointed to the business
Mr. Taco. Perhaps it was out of date? 

Get all names of the buildings in the query:

[E.iloc[x]['name'] for x in range(len(E))]

This list was filled with recognizable locations, but a lot of "nan" entries! 

"""