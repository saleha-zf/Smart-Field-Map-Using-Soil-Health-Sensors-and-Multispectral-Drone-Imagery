import geopandas as gpd
import pandas as pd

# --- File Paths ---
shapefile_path = "shapefile of points.shp"          # Your shapefile with 21 points
excel_path = "Book1.xlsx"        # Your Excel file with sample data
output_shapefile = "points_complete.shp"  # Output path

# --- Load the shapefile ---
gdf = gpd.read_file(shapefile_path)

# --- Load the Excel file ---
df = pd.read_excel(excel_path)

# --- Drop the "Average" row from Excel ---
df = df[df['Samples'] != "Average"]  # If 'Samples' is stored as strings

# --- Ensure Samples column is numeric ---
df['Samples'] = pd.to_numeric(df['Samples'])

# --- Optional: Rename Excel columns for shapefile compatibility (max 10 chars, no symbols) ---
df.columns = [
    "Samples", "N_pct", "P_pct", "K_pct", "Temp_C", 
    "Moist_pct", "EC_uScm", "pH"
]

# --- Check common key ---
# Ensure both have matching 'Samples' field
# If your shapefile has a different field name, adjust below

# --- Merge using shapefile.id == Excel.Samples ---
gdf_merged = gdf.merge(df, left_on="id", right_on="Samples", how="left")
# --- Save as new shapefile ---
gdf_merged.to_file(output_shapefile)

print(f"✅ Combined shapefile saved as: {output_shapefile}")
