import marimo

__generated_with = "0.19.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import osmnx
    import geodatasets
    import folium

    from api.constants import COUNTRY_CODES
    from api.dataset import CityData


    return COUNTRY_CODES, CityData, folium, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Welcome to the OpenStreetMap Data Validation Tool!
    This tool is designed to help you validate and clean OpenStreetMap (OSM) data. It provides a user-friendly interface for checking the quality of OSM data, identifying errors, and making necessary corrections.

    To get started, enter your city name in the input field below and click the "Validate" button. The tool will analyze the OSM data for that city and provide you with a report of any issues found, along with suggestions for how to fix them.
    """)
    return


@app.cell(hide_code=True)
def _():
    tags = {
        "amenity": False,
        "shop": False,
        "office": False
    }
    return (tags,)


@app.cell(hide_code=True)
def _(COUNTRY_CODES, mo, tags):
    form = (
        mo.md(
            """
                ### Please enter your city: {user_city}
                ### Please enter your state, no abbreviations: {user_state}
                ### Please enter your country: {user_country}
                ### Please enter which businesses to include in your search: {multiselect}
            """
        ).batch(
            user_city=mo.ui.text(),
            user_state=mo.ui.text(),
            user_country=mo.ui.dropdown(COUNTRY_CODES),
            multiselect=mo.ui.multiselect(options=tags.keys())
        ).form(
            show_clear_button=True, 
            bordered=False,
        )
    )
    return (form,)


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
def _(CityData, tags):
    def request(value) -> CityData:
        user_city = value['user_city']
        user_state = value['user_state']
        user_country = value['user_country']
        user_selection = value['multiselect']

        user_tags = {s: s in tags.keys() for s in user_selection}
        query = f"{user_city}, {user_state}, {user_country}"

        print(query)
        print(user_tags)
        assert isinstance(query, str)

        return CityData(query, tags=user_tags)

    return (request,)


@app.cell
def _(form):
    form
    return


@app.cell(hide_code=True)
def _(form, is_form_valid, mo, request):
    mo.stop(not is_form_valid())

    results = request(form.value)
    return (results,)


@app.cell(hide_code=True)
def _(form, is_form_valid, mo):
    mo.md(f"""
    # {form.value['user_city'] if is_form_valid() else ''}
    """)
    return


@app.cell
def _(folium, results):
    center_lon = results.get_centroid().x
    center_lat = results.get_centroid().y
    m = folium.Map(location=(center_lat, center_lon), zoom_start=13)
    folium.Choropleth(
        geo_data=results.get_geo_dataframe(),
        name="TBD",
    ).add_to(m)
    m
    return


@app.cell(hide_code=True)
def _(mo, results):
    places = ", <br> ".join(results.get_places_of_interest_names())
    mo.md(places)
    return


if __name__ == "__main__":
    app.run()
