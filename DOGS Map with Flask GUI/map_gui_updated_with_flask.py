import tkinter as tk
from tkinter import filedialog
from tkinter import ttk 
import webbrowser
#import system
import os
import json
import base64
from PIL import Image, ImageTk
import pandas as pd
import folium
from folium.plugins import Draw
from branca.element import Element, MacroElement, Template
from flask import Flask, render_template_string
import threading


flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Flask is running"


def run_flask():
    flask_app.run(debug=True, use_reloader=False)


# if hasattr(sys, '_MEIPASS'):
#     base_path = sys._MEIPASS
# else:
#     base_path = os.path.abspath(".")

# header_path = os.path.join(base_path, "USDA Solid Color Logo.png")
# business_icon_path = os.path.join(base_path, "business programs.png")
# housing_icon_path = os.path.join(base_path, "housing programs.png")
# water_icon_path = os.path.join(base_path, "water.png")
# community_icon_path = os.path.join(base_path, "community programs.png")


# -------------------- Create the main Tkinter window and global StringVars --------------------
app = tk.Tk()
app.title("Spreadsheet Map Generator")
app.geometry("800x600")
app.configure(bg="white")
app.option_add("*Font", "Arial 12")

# Global StringVar objects that will be used in our functions and status updates.
status_var = tk.StringVar(value="Ready")
sheet_path_var = tk.StringVar(value="No file selected")
geojson_path_var = tk.StringVar(value="No file selected")
output_path_var = tk.StringVar(value="No file selected")

# Global variables
spreadsheet_file = ""
geojson_file = ""  # Optional GeoJSON file

def update_status(message):
    """Update the status bar message."""
    status_var.set(message)
    app.update_idletasks()

def select_file():
    """Select a spreadsheet (Excel or CSV file) containing mapping data."""
    global spreadsheet_file
    file_path = filedialog.askopenfilename(
        filetypes=[("Excel Files", "*.xlsx *.xls"), ("CSV Files", "*.csv")],
        title="Select Spreadsheet"
    )
    if file_path:
        spreadsheet_file = file_path
        sheet_path_var.set(file_path)
        print("Selected spreadsheet file:", file_path)

def select_geojson_file():
    """Optionally select a GeoJSON file to overlay counties or other features."""
    global geojson_file
    file_path = filedialog.askopenfilename(
        filetypes=[("GeoJSON Files", "*.geojson"), ("JSON Files", "*.json")],
        title="Select GeoJSON File (Optional)"
    )
    if file_path:
        geojson_file = file_path
        geojson_path_var.set(file_path)
        print("Selected GeoJSON file:", file_path)
    else:
        geojson_file = ""
        geojson_path_var.set("No file selected")

def select_output_file():
    """Select where to save the output HTML map."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".html",
        filetypes=[("HTML files", "*.html")],
        title="Save map as"
    )
    if file_path:
        output_path_var.set(file_path)
        print("Output file selected:", file_path)

def generate_map():
    """Combine folium mapping code with spreadsheet data to produce a custom map."""
    if not spreadsheet_file:
        print("No spreadsheet file selected.")
        return

    output_file = output_path_var.get()
    if not output_file or output_file == "No file selected":
        update_status("Error: No output file specified.")
        print("No output file specified.")
        return

    try:
        update_status("Loading spreadsheet data...")
        # --- Load DataFrame from Spreadsheet ---
        if spreadsheet_file.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(spreadsheet_file)
        elif spreadsheet_file.lower().endswith('.csv'):
            df = pd.read_csv(spreadsheet_file)
        else:
            update_status("Unsupported spreadsheet format.")
            print("Unsupported file format.")
            return

        update_status("Creating base map...")

    
        update_status("Adding drawing tools...")
        # --- Add Drawing Tools ---
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

        # --- Optionally Load Counties GeoJSON ---
        if geojson_file:
            try:
                with open(geojson_file, "r") as geo:
                    counties = json.load(geo)
                folium.GeoJson(
                    counties,
                    name="counties",
                    style_function=lambda feature: {
                        "fillColor": "#16254C",
                        "color": "#26254C",
                        "weight": 1,
                        "fillOpacity": 0.1,
                    }
                ).add_to(fmap)
            except Exception as e:
                print("Error loading GeoJSON file:", e)

        # --- Create Feature Groups by Program ---
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
                if program == 'Business Programs':
                    icon = folium.CustomIcon(r'Icons\business programs.png', icon_size=(20, 20))
                elif program == 'Single Family Housing':
                    icon = folium.CustomIcon(r'Icons\housing programs.png', icon_size=(20, 20))
                elif program == 'Water and Environmental':
                    icon = folium.CustomIcon(r'Icons\water.png', icon_size=(20, 20))
                elif program == 'Community Facilities':
                    icon = folium.CustomIcon(r'Icons\community programs.png', icon_size=(20, 20))
                else:
                    icon = None  # fallback to default marker

                marker_params = dict(
                    location=latlon,
                    tooltip=pname,
                    popup=folium.Popup(pop_text, max_width=300)
                )
                if icon:
                    marker_params['icon'] = icon
                folium.Marker(**marker_params).add_to(fg)
            fg.add_to(fmap)

        update_status("Adding layer controls and legend")
        # --- Add Layer Controls ---
        folium.LayerControl(collapsed=True).add_to(fmap)

        # --- Base64 Encode Images for Legend ---
        def encode_img(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        try:
            encoded = encode_img(r"Icons\water.png")
            encoded2 = encode_img(r"Icons\housing programs.png")
            encoded3 = encode_img(r"Icons\community programs.png")
            encoded4 = encode_img(r"Icons\business programs.png")
        except Exception as e:
            print("Error encoding images for legend:", e)
            encoded = encoded2 = encoded3 = encoded4 = ""

        # --- Add Legend ---
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

        # --- Custom Footer HTML Element ---
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

        update_status("Saving map...")
        # --- Save and Open the Map ---
        fmap.save(output_file)
        output_path_var.set(f"Saved: {output_file}")
        update_status("Map saved successfully.")
        print(f"Map successfully saved to {output_file}")
        full_path = os.path.abspath(output_file)
        webbrowser.open('file://' + full_path)

    except Exception as e:
        update_status("Error generating map.")
        print("Error generating map:", e)

# ------------------- GUI SETUP -------------------


# --- HEADER SECTION ---
header_frame = tk.Frame(app, bg="white")
header_frame.pack(side="top", fill="x", pady=10)
try:
    header_img = Image.open(r"C:\Users\Christopher.Freeman\OneDrive - USDA\Pictures\USDA Solid Color Logo.png")
    header_photo = ImageTk.PhotoImage(header_img)
    header_label = tk.Label(header_frame, image=header_photo, bg="white")
    header_label.image = header_photo  # keep a reference
    header_label.pack()
except Exception as e:
    print("Error loading header image:", e)
    tk.Label(header_frame, text="Header Image", bg="white").pack()

# --- STEP 1: Upload Spreadsheet ---
tk.Label(app, text="Step 1: Upload Spreadsheet", font=("Arial", 12, "bold"), bg="white").pack(pady=5)
tk.Button(app, text="Select File", command=select_file,
          bg="white", activebackground="white", relief="flat", bd=0).pack(pady=5)
sheet_path_var = tk.StringVar(value="No file selected")
tk.Label(app, textvariable=sheet_path_var, font=("Arial", 12), bg="white").pack(pady=5)

# --- STEP 1.5: (Optional) GeoJSON File ---
tk.Label(app, text="Optional: Select GeoJSON File", font=("Arial", 12, "bold"), bg="white").pack(pady=5)
tk.Button(app, text="Select GeoJSON File", command=select_geojson_file,
          bg="white", activebackground="white", relief="flat", bd=0).pack(pady=5)
geojson_path_var = tk.StringVar(value="No file selected")
tk.Label(app, textvariable=geojson_path_var, font=("Arial", 12), bg="white").pack(pady=5)

# --- STEP 2: Filter Options ---

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


def update_map(event=None):
    selected_state = state_var.get()
    if selected_state in state_coords:
        lat, lon = state_coords[selected_state]

        global fmap  # Ensure the map object is updated
        fmap = folium.Map(
            location=[lat, lon],
            control_scale=True,
            zoom_start=6,
            tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attr='OpenStreetMap'
        )

        fmap.save("state_map.html")

# Assuming 'root' is already created
state_var = tk.StringVar()
state_dropdown = ttk.Combobox(app, textvariable=state_var, values=list(state_coords.keys()))
state_dropdown.pack(pady=10)
state_dropdown.bind("<<ComboboxSelected>>", update_map)  # Auto-update on selection

# --- STEP 3: Output File Selection and Generate Map ---
tk.Label(app, text="Step 3: Choose output file name and location", font=("Arial", 12, "bold"), bg="white").pack(pady=5)
output_path_var = tk.StringVar(value="No file selected")
tk.Label(app, textvariable=output_path_var, width=60, relief="sunken", bg="white").pack(pady=5)
tk.Button(app, text="Browse", command=select_output_file,
          bg="white", activebackground="white", relief="flat", bd=0).pack(pady=5)
tk.Button(app, text="Generate Map", command=generate_map,
          bg="white", activebackground="white", relief="flat", bd=0).pack(pady=10)

# --- FOOTER ---
footer = tk.Frame(app, bg="white")
tk.Label(footer, text="Created by ", bg="white").pack(side="left")
hyperlink = tk.Label(footer, text="Christopher Freeman", fg="blue", cursor="hand2",
                      font=("Arial", 12, "underline"), bg="white")
hyperlink.pack(side="left")
tk.Label(footer, text="/ USDA RD ND", bg="white").pack(side="left")
hyperlink.bind("<Button-1>", lambda event: webbrowser.open("mailto:christopher.freeman@usda.gov"))
footer.pack(side="bottom", anchor="e", padx=10, pady=10)

# STATUS BAR
status_label = tk.Label(app, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor="w",
                        bg="lightgrey", font=("Arial", 10))
status_label.pack(side="bottom", fill="x")


# Initialize dark mode state
dark_mode = False

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    
    if dark_mode:
        app.configure(bg="#16254C")  # Set app background to black
        for widget in app.winfo_children():
            try:
                widget.configure(bg="#16254C", fg="white")  # Apply to all widgets
            except:
                pass  # Ignore widgets that don't support bg/fg

    else:
        app.configure(bg="white")  # Reset to light mode
        for widget in app.winfo_children():
            try:
                widget.configure(bg="white", fg="black")  # Apply to all widgets
            except:
                pass  # Ignore unsupported widgets




# Add a button to toggle modes and integrate it into your current layout
toggle_button = tk.Button(app, text="Switch to Dark Mode", bg='lightgray', fg='black', command=toggle_theme)
toggle_button.pack(pady=20)
#End Toggle


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    app.mainloop()




