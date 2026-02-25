import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import json
    import uuid
    import httpx

    COUNTRY_CODES = [
        "AFG",
        "ALB",
        "DZA",
        "ASM",
        "AND",
        "AGO",
        "AIA",
        "ATA",
        "ATG",
        "ARG",
        "ARM",
        "ABW",
        "AUS",
        "AUT",
        "AZE",
        "BHS",
        "BHR",
        "BGD",
        "BRB",
        "BLR",
        "BEL",
        "BLZ",
        "BEN",
        "BMU",
        "BTN",
        "BOL",
        "BES",
        "BIH",
        "BWA",
        "BVT",
        "BRA",
        "IOT",
        "BRN",
        "BGR",
        "BFA",
        "BDI",
        "CPV",
        "KHM",
        "CMR",
        "CAN",
        "CYM",
        "CAF",
        "TCD",
        "CHL",
        "CHN",
        "CXR",
        "CCK",
        "COL",
        "COM",
        "COD",
        "COG",
        "COK",
        "CRI",
        "HRV",
        "CUB",
        "CUW",
        "CYP",
        "CZE",
        "CIV",
        "DNK",
        "DJI",
        "DMA",
        "DOM",
        "ECU",
        "EGY",
        "SLV",
        "GNQ",
        "ERI",
        "EST",
        "SWZ",
        "ETH",
        "FLK",
        "FRO",
        "FJI",
        "FIN",
        "FRA",
        "GUF",
        "PYF",
        "ATF",
        "GAB",
        "GMB",
        "GEO",
        "DEU",
        "GHA",
        "GIB",
        "GRC",
        "GRL",
        "GRD",
        "GLP",
        "GUM",
        "GTM",
        "GGY",
        "GIN",
        "GNB",
        "GUY",
        "HTI",
        "HMD",
        "VAT",
        "HND",
        "HKG",
        "HUN",
        "ISL",
        "IND",
        "IDN",
        "IRN",
        "IRQ",
        "IRL",
        "IMN",
        "ISR",
        "ITA",
        "JAM",
        "JPN",
        "JEY",
        "JOR",
        "KAZ",
        "KEN",
        "KIR",
        "PRK",
        "KOR",
        "KWT",
        "KGZ",
        "LAO",
        "LVA",
        "LBN",
        "LSO",
        "LBR",
        "LBY",
        "LIE",
        "LTU",
        "LUX",
        "MAC",
        "MDG",
        "MWI",
        "MYS",
        "MDV",
        "MLI",
        "MLT",
        "MHL",
        "MTQ",
        "MRT",
        "MUS",
        "MYT",
        "MEX",
        "FSM",
        "MDA",
        "MCO",
        "MNG",
        "MNE",
        "MSR",
        "MAR",
        "MOZ",
        "MMR",
        "NAM",
        "NRU",
        "NPL",
        "NLD",
        "NCL",
        "NZL",
        "NIC",
        "NER",
        "NGA",
        "NIU",
        "NFK",
        "MNP",
        "NOR",
        "OMN",
        "PAK",
        "PLW",
        "PSE",
        "PAN",
        "PNG",
        "PRY",
        "PER",
        "PHL",
        "PCN",
        "POL",
        "PRT",
        "PRI",
        "QAT",
        "MKD",
        "ROU",
        "RUS",
        "RWA",
        "REU",
        "BLM",
        "SHN",
        "KNA",
        "LCA",
        "MAF",
        "SPM",
        "VCT",
        "WSM",
        "SMR",
        "STP",
        "SAU",
        "SEN",
        "SRB",
        "SYC",
        "SLE",
        "SGP",
        "SXM",
        "SVK",
        "SVN",
        "SLB",
        "SOM",
        "ZAF",
        "SGS",
        "SSD",
        "ESP",
        "LKA",
        "SDN",
        "SUR",
        "SJM",
        "SWE",
        "CHE",
        "SYR",
        "TWN",
        "TJK",
        "TZA",
        "THA",
        "TLS",
        "TGO",
        "TKL",
        "TON",
        "TTO",
        "TUN",
        "TUR",
        "TKM",
        "TCA",
        "TUV",
        "UGA",
        "UKR",
        "ARE",
        "GBR",
        "UMI",
        "USA",
        "URY",
        "UZB",
        "VUT",
        "VEN",
        "VNM",
        "VGB",
        "VIR",
        "WLF",
        "ESH",
        "YEM",
        "ZMB",
        "ZWE",
        "ALA"
    ]
    return COUNTRY_CODES, httpx, json, mo, uuid


@app.cell(hide_code=True)
def _(json):
    def map_data(response_json) -> str:
        """Fetch anomaly data from the /anomaly endpoint and return a Leaflet map as an HTML string.

        The returned string can be passed directly to mo.Html() inside a Marimo notebook.
        """

        # The server serialises the GeoDataFrame as a JSON string, so the HTTP
        # response body is a JSON-encoded string that itself contains GeoJSON.
        geojson = json.loads(response_json) if isinstance(response_json, str) else response_json
        features = geojson.get("features", [])

        return features

    return (map_data,)


@app.cell(hide_code=True)
def _():
    conn = "https://gis-anomaly-detector.com"
    return (conn,)


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
    USER_ENTRIES = ['user_city', 'user_state', 'user_country', ]
    def is_form_valid() -> bool:
        if form is None:
            return False
        if form.value is None:
            return False
        if any(form.value[entry] is None for entry in USER_ENTRIES):
            return False
        if any(form.value[entry] == "" for entry in USER_ENTRIES):
            return False
        return True

    return (is_form_valid,)


@app.cell
def _(form):
    form
    return


@app.cell(hide_code=True)
def _(conn, form, httpx, is_form_valid, map_data, mo):
    mo.stop(not is_form_valid())

    user_city = form.value['user_city']
    user_state = form.value['user_state']
    user_country = form.value['user_country']

    query = f"{user_city}, {user_state}, {user_country}"

    print(query)

    with httpx.Client(timeout=60 * 5) as client:
        response = client.get(conn + "/anomaly", params={"city": query})
        anomaly_data = map_data(response.json())
    return (anomaly_data,)


@app.cell(hide_code=True)
def _(form, is_form_valid, mo):
    mo.md(f"""
    # {form.value['user_city'] if is_form_valid() else ''}
    """)
    return


@app.cell(hide_code=True)
def _(anomaly_data, json, mo, uuid):
    def build_leaflet_map(features: list) -> str:
        """Return a self-contained HTML snippet that renders a Leaflet map for *features*.

        Each feature is expected to be a GeoJSON Feature whose properties include
        at minimum: name, risk_level, anomaly_score, explanation, suggested_check.
        Geometries must be in WGS84 (EPSG:4326).
        """
        map_id = "map-" + uuid.uuid4().hex[:10]
        geojson_payload = json.dumps({"type": "FeatureCollection", "features": features})

        return f"""
    <div id="{map_id}" style="height:520px;width:100%;border-radius:8px;"></div>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>
    <script>
        var geojson = {geojson_payload};
        var map = L.map('{map_id}');

        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19
        }}).addTo(map);

        var RISK_COLORS = {{ high: '#e74c3c', medium: '#f39c12', low: '#2ecc71' }};
        function riskColor(level) {{ return RISK_COLORS[level] || '#95a5a6'; }}

        function buildPopup(p) {{
            var score = (p.anomaly_score != null) ? Number(p.anomaly_score).toFixed(4) : 'N/A';
            return '<b>' + (p.name || 'Unknown') + '</b><br/>' +
                   '<span style="color:' + riskColor(p.risk_level) + '"><b>Risk: ' + (p.risk_level || 'N/A') + '</b></span><br/>' +
                   '<b>Score:</b> ' + score + '<br/>' +
                   '<b>Explanation:</b> ' + (p.explanation || 'N/A') + '<br/>' +
                   '<b>Suggested Check:</b> ' + (p.suggested_check || 'N/A');
        }}

        var layer = L.geoJSON(geojson, {{
            style: function(f) {{ return {{ color: riskColor(f.properties.risk_level), weight: 2, fillOpacity: 0.55 }}; }},
            pointToLayer: function(f, latlng) {{
                return L.circleMarker(latlng, {{ radius: 11, fillColor: riskColor(f.properties.risk_level), color: '#222', weight: 1, fillOpacity: 0.85 }});
            }},
            onEachFeature: function(f, layer) {{ layer.bindPopup(buildPopup(f.properties)); }}
        }}).addTo(map);

        if (layer.getBounds().isValid()) {{
            map.fitBounds(layer.getBounds(), {{ padding: [30, 30] }});
        }}
    </script>
    """


    map_html = mo.iframe(build_leaflet_map(anomaly_data))
    map_html
    return


@app.cell(hide_code=True)
def _(is_form_valid, mo):
    mo.md(f"""
    # {"Anamolies: " if is_form_valid() else ''}
    """)
    return


@app.cell(hide_code=True)
def _(anomaly_data, mo):
    result = []
    for r in anomaly_data:
        result.append(mo.md(f"#{r['properties']['name']}"))
        result.append(mo.md(f"## Explanation: {r['properties']['explanation']}"))
        result.append(mo.md(f"## Risk Level: {r['properties']['risk_level']}"))
        result.append(mo.md(f"## Suggestion: {r['properties']['suggested_check']}"))
        result.append(mo.md(f"""
        =========================================================================
        """))
    result
    return


if __name__ == "__main__":
    app.run()
