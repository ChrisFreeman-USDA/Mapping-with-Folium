import os
import json
import base64
from flask import Flask, render_template_string, request, redirect, url_for, send_file, flash
import pandas as pd
import folium
from folium.plugins import Draw
from branca.element import Element, MacroElement, Template
from werkzeug.utils import secure_filename
from io import BytesIO

UPLOAD_FOLDER = 'uploads'
MAP_FOLDER = 'maps'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv', 'geojson', 'json'}

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAP_FOLDER'] = MAP_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MAP_FOLDER, exist_ok=True)

state_coords = {
    "Alabama": (32.806671, -86.791130),
    "Alaska": (61.370716, -152.404419),
    "Arizona": (34.168218, -111.930907),
    "Arkansas": (34.746613, -92.288986),
    "California": (37.271874, -119.270415),
    "Colorado": (38.997934, -105.550567),
    "Connecticut": (41.518783, -72.757507),
    "Delaware": (38.989597, -75.505571),
    "Florida": (27.994402, -81.760254),
    "Georgia": (32.165622, -82.900075),
    "Hawaii": (20.798362, -156.331925),
    "Idaho": (44.068203, -114.742043),
    "Illinois": (40.633125, -89.398528),
    "Indiana": (39.849426, -86.258278),
    "Iowa": (42.011539, -93.210526),
    "Kansas": (38.526600, -98.362885),
    "Kentucky": (37.839333, -84.270020),
    "Louisiana": (30.984298, -91.962333),
    "Maine": (45.253783, -69.445469),
    "Maryland": (39.045753, -76.641273),
    "Massachusetts": (42.407211, -71.382437),
    "Michigan": (44.314844, -85.602364),
    "Minnesota": (46.729553, -94.685900),
    "Mississippi": (32.741646, -89.678696),
    "Missouri": (38.573936, -92.603760),
    "Montana": (46.879682, -110.362566),
    "Nebraska": (41.492537, -99.901813),
    "Nevada": (38.802610, -116.419389),
    "New Hampshire": (43.193852, -71.572395),
    "New Jersey": (40.058324, -74.405661),
    "New Mexico": (34.972730, -105.032363),
    "New York": (42.165726, -74.948051),
    "North Carolina": (35.759573, -79.019300),
    "North Dakota": (47.551493, -101.002012),
    "Ohio": (40.417287, -82.907123),
    "Oklahoma": (35.007752, -97.092877),
    "Oregon": (43.804133, -120.554201),
    "Pennsylvania": (41.203323, -77.194525),
    "Rhode Island": (41.580095, -71.477429),
    "South Carolina": (33.836081, -81.163725),
    "South Dakota": (43.969515, -99.901813),
    "Tennessee": (35.517491, -86.580447),
    "Texas": (31.968599, -99.901813),
    "Utah": (39.320980, -111.093731),
    "Vermont": (44.558803, -72.577841),
    "Virginia": (37.431573, -78.656894),
    "Washington": (47.751074, -120.740139),
    "West Virginia": (38.597626, -80.454903),
    "Wisconsin": (43.784439, -88.787868),
    "Wyoming": (43.075968, -107.290283)
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_img(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file uploads
        spreadsheet = request.files.get('spreadsheet')
        geojson = request.files.get('geojson')
        state = request.form.get('state')
        output_name = request.form.get('output_name', 'output_map.html')
        output_name = secure_filename(output_name)
        if not spreadsheet or not allowed_file(spreadsheet.filename):
            flash('Please upload a valid spreadsheet file (.xlsx, .xls, .csv)')
            return redirect(request.url)
        spreadsheet_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(spreadsheet.filename))
        spreadsheet.save(spreadsheet_path)
        geojson_path = None
        if geojson and allowed_file(geojson.filename):
            geojson_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(geojson.filename))
            geojson.save(geojson_path)
        # Generate map
        try:
            lat, lon = state_coords.get(state, (47.551493, -101.002012))  # Default ND
            # Load DataFrame
            if spreadsheet_path.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(spreadsheet_path)
            elif spreadsheet_path.lower().endswith('.csv'):
                df = pd.read_csv(spreadsheet_path)
            else:
                flash("Unsupported spreadsheet format.")
                return redirect(request.url)
            fmap = folium.Map(
                location=[lat, lon],
                control_scale=True,
                zoom_start=6,
                tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                attr='OpenStreetMap'
            )
            draw = Draw(
                draw_options={
                    'polyline': {
                        'shapeOptions': {'color': 'blue', 'weight': 8, 'opacity': 0.7}
                    },
                    'rectangle': False,
                    'circle': False,
                    'marker': False,
                    'polygon': False,
                    'circlemarker': False
                },
                edit_options={'edit': True}
            )
            draw.add_to(fmap)
            # GeoJSON overlay
            if geojson_path:
                with open(geojson_path, "r") as geo:
                    counties = json.load(geo)
                folium.GeoJson(
                    counties,
                    name="counties",
                    style_function=lambda _: {
                        "fillColor": "#16254C",
                        "color": "#26254C",
                        "weight": 1,
                        "fillOpacity": 0.1,
                    }
                ).add_to(fmap)
            # Feature groups by Program
            for program in df['Program'].unique():
                fg = folium.FeatureGroup(name=program)
                subset = df[df['Program'] == program]
                for _, row in subset.iterrows():
                    latlon = (row['latitudes'], row['longitudes'])
                    pname = row['Project Name']
                    pop_text = (
                        f"<b>Project Description:</b> {row['Project Description']}<br>"
                        f"<b>Program:</b> {program}<br>"
                        f"<b>County:</b> {row['County']}<br>"
                        f"<b>Fiscal Year:</b> {row['Fiscal Year']}"
                    )
                    # Custom icons based on program names.
                    icon = None
                    icon_map = {
                        'Business Programs': 'Icons/business programs.png',
                        'Single Family Housing': 'Icons/housing programs.png',
                        'Water and Environmental': 'Icons/water.png',
                        'Community Facilities': 'Icons/community programs.png'
                    }
                    if program in icon_map and os.path.exists(icon_map[program]):
                        icon = folium.CustomIcon(icon_map[program], icon_size=(20, 20))
                    marker_params = dict(
                        location=latlon,
                        tooltip=pname,
                        popup=folium.Popup(pop_text, max_width=300)
                    )
                    if icon:
                        marker_params['icon'] = icon
                    folium.Marker(**marker_params).add_to(fg)
                fg.add_to(fmap)
            folium.LayerControl(collapsed=True).add_to(fmap)
            # Legend
            try:
                encoded = encode_img('Icons/water.png')
                encoded2 = encode_img('Icons/housing programs.png')
                encoded3 = encode_img('Icons/community programs.png')
                encoded4 = encode_img('Icons/business programs.png')
            except Exception:
                encoded = encoded2 = encoded3 = encoded4 = ""
            legend_html = f"""
            {{% macro html(this, kwargs) %}}
            <div style="
                position: fixed; 
                bottom: 0px; left: 0px; width: 195px; height: 120px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color:white; opacity: 0.9;
                padding: 10px;">
            <b>Legend</b><br>
            <img src="data:image/png;base64,{encoded}" style="height:20px;"> Water & Environmental<br>
            <img src="data:image/png;base64,{encoded2}" style="height:20px;"> Housing<br>
            <img src="data:image/png;base64,{encoded3}" style="height:20px;"> Community Facilities<br>
            <img src="data:image/png;base64,{encoded4}" style="height:20px;"> Business Programs<br>
            </div>
            {{% endmacro %}}
            """
            legend = MacroElement()
            legend._template = Template(legend_html)
            fmap.get_root().add_child(legend)
            # Footer
            custom_html = Element("""
                <div style="
                    position: fixed; 
                    bottom: 10px; right: 0px; width: 300px; height: 20px; 
                    border: 2px solid black; z-index: 9999; font-size: 12px;
                    background-color: white; opacity: 0.9;
                    padding: 0px; text-align: center;">
                  Created by <a href="mailto:christopher.freeman@usda.gov?subject=DOGS Map" 
                  style="text-decoration: none; color: blue;"><b>Christopher Freeman</b></a> / USDA RD ND
                </div>
            """)
            fmap.get_root().html.add_child(custom_html)
            # Save map
            # Let user download the generated map directly instead of saving to server
            map_bytes = BytesIO()
            fmap.save(map_bytes, close_file=False)
            map_bytes.seek(0)
            return send_file(
                map_bytes,
                as_attachment=True,
                download_name=output_name,
                mimetype='text/html'
            )
        except Exception as e:
            flash(f"Error generating map: {e}")
            return redirect(request.url)
    # GET request
    return render_template_string('''
    <!doctype html>
    <title>Spreadsheet Map Generator</title>
    <h1>Spreadsheet Map Generator</h1>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul>
        {% for message in messages %}
          <li style="color:red;">{{ message }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    <form method=post enctype=multipart/form-data>
      <label>Step 1: Upload Spreadsheet (Excel or CSV):</label><br>
      <input type=file name=spreadsheet required><br><br>
      <label>Step 1.5: (Optional) Upload GeoJSON File:</label><br>
      <input type=file name=geojson><br><br>
      <label>Step 2: Select State:</label><br>
      <select name="state" required>
        {% for state in states %}
          <option value="{{ state }}">{{ state }}</option>
        {% endfor %}
      </select><br><br>
      <label>Step 3: Output HTML File Name:</label><br>
      <input type=text name=output_name value="output_map.html" required><br><br>
      <input type=submit value="Generate Map">
    </form>
    ''', states=state_coords.keys())

@app.route('/maps/<filename>')
def view_map(filename):
    return send_file(os.path.join(app.config['MAP_FOLDER'], filename))

if __name__ == '__main__':
    app.run(debug=True)
