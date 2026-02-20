import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


@app.cell
def _():
    return


@app.cell
def _():
    import marimo as mo
    import osmnx
    import geodatasets
    import folium
    import anthropic
    import json
    import geopandas
    from shapely import Point, Polygon

    from api.constants import COUNTRY_CODES, CSV_HEADERS
    from api.dataset import CityData

    return COUNTRY_CODES, CityData, Polygon, folium, geopandas, mo


@app.cell
def _(COUNTRY_CODES, mo):
    form = (
        mo.md(
            """
                ### Please enter your city: {user_city}
                ### Please enter your state, no abbreviations: {user_state}
                ### Please enter your country: {user_country}
            """
        ).batch(
            user_city=mo.ui.text(),
            user_state=mo.ui.text(),
            user_country=mo.ui.dropdown(COUNTRY_CODES),
        ).form(
            show_clear_button=True, 
            bordered=False,
        )
    )
    return (form,)


@app.cell
def _(form):
    user_entries = ['user_city', 'user_state', 'user_country', ]
    def is_form_valid() -> bool:
        if form is None:
            return False
        if form.value is None:
            return False
        if any(form.value[entry] is None for entry in user_entries):
            return False
        if any(form.value[entry] == "" for entry in user_entries):
            return False
        return True

    return (is_form_valid,)


@app.cell
def _(CityData):
    def request(value) -> CityData:
        user_city = value['user_city']
        user_state = value['user_state']
        user_country = value['user_country']

        query = f"{user_city}, {user_state}, {user_country}"

        print(query)
        assert isinstance(query, str)

        return CityData(query)

    return (request,)


@app.cell
def _(form):
    form
    return


@app.cell
def _(form, is_form_valid, mo, request):
    mo.stop(not is_form_valid())

    results = request(form.value)
    return (results,)


@app.cell
def _():
    # Beaumont Street Test
    """mo.stop(True)
    edges_wgs84 = results.get_street_edges_dataset().to_crs("EPSG:4326")
    place = results.get_place_of_interest("Calvary Chapel Beaumont")[0]
    point_wgs84 = geopandas.GeoSeries(place["geometry"], crs=results.get_street_edges_dataset().crs).to_crs("EPSG:4326")

    a = folium.Map(location=[point_wgs84.iloc[0].y, point_wgs84.iloc[0].x], zoom_start=13)
    folium.Choropleth(
        geo_data=results.get_street_edges_dataset(),
        name="TBD",
    ).add_to(a)
    a"""
    return


@app.cell
def _(Polygon, folium, geopandas, results):
    # Cherry Valley Street Test
    edges_wgs84 = results.get_street_edges_dataset().to_crs("EPSG:4326")
    location = results.get_place_of_interest("Grace Community Church")[0]

    p = location["geometry"]

    if isinstance(location["geometry"], Polygon):
        p = results.get_center_of_polygon(location)

    point_wgs84 = geopandas.GeoSeries(p, crs=results.get_street_edges_dataset().crs).to_crs("EPSG:4326")

    a = folium.Map(location=[point_wgs84.iloc[0].y, point_wgs84.iloc[0].x], zoom_start=13, control_scale=True)
    folium.Choropleth(
        geo_data=results.get_street_edges_dataset(),
        name="TBD",
    ).add_to(a)
    a
    return


if __name__ == "__main__":
    app.run()
