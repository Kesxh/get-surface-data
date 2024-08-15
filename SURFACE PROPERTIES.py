import iesve   # the VE API
import csv
from pint import UnitRegistry

# Initialize UnitRegistry
ureg = UnitRegistry()
Q_ = ureg.Quantity

# Function to convert metric areas and distances to IP units
def convertAreas(data):
    if ve_display_units == iesve.DisplayUnits.metric:
        return
        
    keywords_area = ['gross', 'net', 'window', 'door', 'hole', 'gross_openings', 'area']
    keywords_distance = ['thickness', 'distance']
            
    for kwa in keywords_area:
        val = data.get(kwa)
        if val is not None:
            data[kwa] = Q_(val, ureg.centiare).to(ureg.sq_ft).magnitude
            
    for kwd in keywords_distance:
        val = data.get(kwd)
        if val is not None:
            data[kwd] = Q_(val, ureg.meter).to(ureg.inches).magnitude
    
# Get the current VE project
project = iesve.VEProject.get_current_project()

# Check what units mode the VE is in
ve_display_units = project.get_display_units()

# Get the list of models
models = project.models

# Prepare the CSV file
with open('surface_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write the header
    writer.writerow([
        "Body ID", "Surface Type", "Total Gross Area'm2'", "Total Net Area'm2'", 
        "Total Window Area'm2'", "Total Door Area'm2'", 
         
        "Surface Area'm2'", "Surface Thickness'mm'", "Orientation", "Tilt"
    ])
    
    # Iterate over each model and body
    for model in models:
        bodies = model.get_bodies_and_ids(False)
        for id, body in bodies.items():
            if body.type != iesve.VEBody_type.room:
                continue

            # Get all surfaces in this room
            surfaces = body.get_surfaces()
            for surface in surfaces:
                
                # Get and convert surface areas
                areas = surface.get_areas()
                convertAreas(areas)

                # Get and convert surface properties
                properties = surface.get_properties()
                convertAreas(properties)
                
                # Get details of openings in surface
                openings = surface.get_opening_totals()

                # Write data to CSV
                writer.writerow([
                    id,properties.get("type"), areas.get("total_gross"), areas.get("total_net"), 
                    areas.get("total_window") , areas.get("total_door"),  
                    properties.get("area"), properties.get("thickness"), properties.get("orientation"), 
                    properties.get("tilt")
                ])

print("Data has been written to surface_data.csv")
