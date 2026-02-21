import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import osmnx
    import geodatasets
    import folium
    import anthropic
    import json

    from api.constants import COUNTRY_CODES, CSV_HEADERS
    from api.dataset import CityData
    from api.claude_client import ClaudeClient


    return (
        COUNTRY_CODES,
        CSV_HEADERS,
        CityData,
        ClaudeClient,
        anthropic,
        folium,
        json,
        mo,
    )


@app.cell(hide_code=True)
def _(ClaudeClient, anthropic):
    claude_client = ClaudeClient(anthropic.Anthropic())
    return (claude_client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Welcome to the OpenStreetMap Data Validation Tool!
    This tool is designed to help you validate and clean OpenStreetMap (OSM) data. It provides a user-friendly interface for checking the quality of OSM data, identifying errors, and making necessary corrections.

    To get started, enter your city name in the input field below and click the "Validate" button. The tool will analyze the OSM data for that city and provide you with a report of any issues found, along with suggestions for how to fix them.
    """)
    return


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
def _(folium, results):
    anomalies = results.detect_anomalies().to_crs(epsg=4326).nsmallest(5, "anomaly_score")
    center_lon = anomalies.union_all().centroid.x
    center_lat = anomalies.union_all().centroid.y
    m = folium.Map(location=(center_lat, center_lon), zoom_start=13)
    folium.Choropleth(
        geo_data=anomalies,
        name="TBD",
    ).add_to(m)
    m
    return


@app.cell(hide_code=True)
def _(CSV_HEADERS, claude_client, json, results):
    filtered = results.detect_anomalies().nsmallest(5, "anomaly_score")
    data_dict = json.loads(filtered[CSV_HEADERS].to_json(orient="records"))
    responses = claude_client.explain_anomaly(data_dict)
    return filtered, responses


@app.cell(hide_code=True)
def _(is_form_valid, mo):
    mo.md(f"""
    # {"Anamolies: " if is_form_valid() else ''}
    """)
    return


@app.cell(hide_code=True)
def _(filtered, mo, responses):
    result = []
    for r in range(len(responses)):
        result.append(mo.md(f"#{filtered['name'].iloc[r]}"))
        result.append(mo.md(f"## Explanation: {responses[r]['explanation']}"))
        result.append(mo.md(f"## Risk Level: {responses[r]['risk_level']}"))
        result.append(mo.md(f"## Suggestion: {responses[r]['suggested_check']}"))
        result.append(mo.md(f"""
        =========================================================================
        """))
    result
    return


if __name__ == "__main__":
    app.run()
