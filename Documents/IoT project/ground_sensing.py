import geopandas as gpd
import folium
import rasterio
import numpy as np
from rasterio.plot import reshape_as_image
from folium.raster_layers import ImageOverlay
from folium.plugins import MousePosition
from folium import FeatureGroup, LayerControl
from shapely.geometry import mapping

# --- File Paths ---
shapefile_path = "points_complete.shp"  # Your point shapefile
tif_path = "p17 NARC MERGED ALL BANDS.tif"  # Your GeoTIFF file

# --- Load shapefile ---
gdf = gpd.read_file(shapefile_path)
gdf = gdf.to_crs(epsg=4326)  # Ensure WGS84

# --- Inspect column names (for tooltips) ---
print("Shapefile columns:", gdf.columns)

# --- Center of the map ---
map_center = [gdf.geometry.y.mean(), gdf.geometry.x.mean()]
m = folium.Map(
    location=map_center,
    zoom_start=10,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="ESRI World Imagery"
)

# --- Load and overlay raster with toggle ---
with rasterio.open(tif_path) as src:
    bounds = src.bounds
    image = src.read()
    image = reshape_as_image(image)
    image = image[:, :, :3] if image.shape[2] > 3 else image  # Keep RGB only

    # Normalize image if needed
    if image.dtype != np.uint8:
        image = ((image - image.min()) / (image.max() - image.min()) * 255).astype(np.uint8)

    image_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

    # Create toggleable raster group
    raster_group = FeatureGroup(name="Orthomosaic", show=True)
    ImageOverlay(
        image=image,
        bounds=image_bounds,
        opacity=0.6,
        interactive=True,
        cross_origin=False,
    ).add_to(raster_group)
    raster_group.add_to(m)

# --- Create toggleable group for sampling points ---
points_group = FeatureGroup(name="Sampling Points", show=True)

# Use correct column names for tooltips
# Adjust these field names if needed based on actual gdf.columns output
tooltip_fields = {
    "EC": "EC_uScm",
    "Temp": "Temp_C",
    "N": "N_pct",
    "P": "P_pct",
    "K": "K_pct",
    "pH": "pH",
    "Moisture": "Moist_pct"
}

for _, row in gdf.iterrows():
    tooltip_text = "<br>".join(
        f"<b>{label}:</b> {row.get(col, 'N/A')}" for label, col in tooltip_fields.items()
    )

    tooltip = folium.Tooltip(tooltip_text)

    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=5,
        color='blue',
        fill=True,
        fill_color='cyan',
        fill_opacity=0.8,
        tooltip=tooltip
    ).add_to(points_group)

points_group.add_to(m)

# --- Add lat/lon readout ---
MousePosition().add_to(m)

# --- Add layer toggle control ---
LayerControl(collapsed=False).add_to(m)

# --- Save the map ---
output_file = "map_with_basemap.html"
m.save(output_file)
print(f"✅ Map saved to {output_file}")
