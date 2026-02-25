from fastapi import FastAPI
from server.api.anomaly_detection import CityData, get_location_data
from server.api.utilities import serialize_location
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kristianhoward.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "API running"}


@app.get("/anomaly")
def anomaly(city: str):
    city_data = CityData.from_location(city)

    return city_data.ai_anomaly_response().to_crs(epsg=4326).to_json()

@app.get("/osmnx")
def osmnx(city: str):
    dataset, _ = get_location_data(city)
    return dataset.to_json()

@app.get("/debug")
def debug(city: str):
    city_data = CityData.from_location(city)
    return {
        "dataset": city_data.dataset.to_json(),
        "street_lines": city_data.street_graph,
        "street_edges": city_data.street_edges,
        "buildings": city_data.buildings,
        "amenities": city_data.amenities,
    }

@app.get("/place")
def place(city: str, location: str):
    city_data = CityData.from_location(city)
    location_data = city_data.get_place_of_interest(location)

    if len(location_data) == 0:
        return {
            "error": "Location not found"
        }

    return [data.to_json() for data in location_data]


@app.get("/nearest")
def nearest(city: str, location: str, loc_id: int = 1):
    index = loc_id - 1
    city_data = CityData.from_location(city)
    location_data = city_data.get_place_of_interest(location)

    if len(location_data) == 0:
        return {
            "error": "Location not found"
        }

    return {
        "place": serialize_location(location_data[0]),
        "street": serialize_location(city_data.get_nearest_street(location_data[index])),
        "location": serialize_location(city_data.get_nearest_location(location_data[index])[0]),
        "nearby": [serialize_location(s) for s in city_data.get_nearby_locations(location_data[index], meters=500)],
        "intersections": [serialize_location(s) for s in city_data.intersects_other_locations(location_data[index])]
    }