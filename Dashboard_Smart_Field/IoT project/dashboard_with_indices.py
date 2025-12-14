"""
Add Vegetation Indices to Dashboard
Processes orthomosaic and adds NDVI, NDWI, EVI layers to the dashboard
"""
import folium
from folium import plugins
import geopandas as gpd
import rasterio
from rasterio.warp import transform_bounds, calculate_default_transform, reproject, Resampling
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from branca.colormap import LinearColormap
from PIL import Image
import os
import pandas as pd

def calculate_and_add_indices(shapefile_path, orthomosaic_path, output_html="dashboard_with_indices.html"):
    """
    Create dashboard with vegetation indices calculated on-the-fly
    Uses downsampled versions for web display
    """
    print("🗺️  Creating dashboard with vegetation indices...")
    
    # Load shapefile
    print(f"\n📍 Loading shapefile: {shapefile_path}")
    gdf = gpd.read_file(shapefile_path)
    
    if gdf.crs and gdf.crs != 'EPSG:4326':
        print(f"   Reprojecting from {gdf.crs} to EPSG:4326")
        gdf = gdf.to_crs('EPSG:4326')
    
    print(f"   Points loaded: {len(gdf)}")
    
    # Get center point
    center_lat = gdf.geometry.y.mean()
    center_lon = gdf.geometry.x.mean()
    
    # Create base map
    print("\n🗺️  Creating base map...")
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=18,
        control_scale=True,
        prefer_canvas=True
    )
    
    # Add basemaps
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap', overlay=False, control=True).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='ESRI World Imagery',
        overlay=False,
        control=True
    ).add_to(m)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Process orthomosaic and calculate indices
    if os.path.exists(orthomosaic_path):
        print(f"\n🌍 Processing orthomosaic: {orthomosaic_path}")
        
        try:
            with rasterio.open(orthomosaic_path) as src:
                print(f"   Bands: {src.count}")
                print(f"   Size: {src.width} x {src.height}")
                print(f"   CRS: {src.crs}")
                
                # Get bounds in WGS84
                bounds_wgs84 = transform_bounds(src.crs, 'EPSG:4326', *src.bounds)
                bounds = [[bounds_wgs84[1], bounds_wgs84[0]], [bounds_wgs84[3], bounds_wgs84[2]]]
                
                # Downsample factor for web display
                downsample = 10
                print(f"\n   Downsampling by factor of {downsample} for web display...")
                
                # Read bands (assuming Red, Green, Blue, NIR order - adjust if needed)
                if src.count >= 4:
                    # Read with downsampling
                    red = src.read(1, out_shape=(src.height // downsample, src.width // downsample))
                    green = src.read(2, out_shape=(src.height // downsample, src.width // downsample))
                    blue = src.read(3, out_shape=(src.height // downsample, src.width // downsample))
                    nir = src.read(4, out_shape=(src.height // downsample, src.width // downsample))
                    
                    # Convert to float and create nodata mask
                    red = red.astype('float32')
                    green = green.astype('float32')
                    blue = blue.astype('float32')
                    nir = nir.astype('float32')
                    
                    # Create mask for null/nodata values (assuming 0 or nodata value)
                    nodata_mask = (red == 0) & (green == 0) & (blue == 0) & (nir == 0)
                    if src.nodata is not None:
                        nodata_mask = nodata_mask | (red == src.nodata) | (green == src.nodata) | (blue == src.nodata) | (nir == src.nodata)
                    
                    # Calculate NDVI
                    print("\n🌿 Calculating NDVI...")
                    ndvi = np.where((nir + red) != 0, (nir - red) / (nir + red), 0)
                    ndvi = np.clip(ndvi, -1, 1)
                    ndvi[nodata_mask] = np.nan  # Set nodata to NaN
                    
                    # Create NDVI overlay with transparency
                    cmap = plt.cm.get_cmap('RdYlGn')
                    norm = mcolors.Normalize(vmin=-1, vmax=1)
                    rgba = cmap(norm(np.nan_to_num(ndvi, nan=0)))
                    rgba[:, :, 3] = np.where(nodata_mask, 0, 255)  # Set alpha channel
                    rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
                    alpha = rgba[:, :, 3].astype(np.uint8)
                    
                    # Save as PNG with transparency
                    img = Image.fromarray(rgb, 'RGB')
                    img_alpha = Image.fromarray(alpha, 'L')
                    img.putalpha(img_alpha)
                    ndvi_png = "temp_ndvi.png"
                    img.save(ndvi_png, 'PNG')
                    
                    # Add to map
                    ndvi_layer = folium.raster_layers.ImageOverlay(
                        image=ndvi_png,
                        bounds=bounds,
                        opacity=0.7,
                        name='NDVI',
                        overlay=True,
                        control=True
                    )
                    ndvi_layer.add_to(m)
                    
                    # Add NDVI colormap legend
                    ndvi_colormap = LinearColormap(
                        colors=['red', 'yellow', 'green'],
                        vmin=-1,
                        vmax=1,
                        caption='NDVI (Vegetation Index)'
                    )
                    ndvi_colormap.add_to(m)
                    
                    print(f"   ✅ NDVI layer added (range: {np.nanmin(ndvi):.3f} to {np.nanmax(ndvi):.3f})")
                    
                    # Calculate NDWI
                    print("\n💧 Calculating NDWI...")
                    ndwi = np.where((green + nir) != 0, (green - nir) / (green + nir), 0)
                    ndwi = np.clip(ndwi, -1, 1)
                    ndwi[nodata_mask] = np.nan
                    
                    # Create NDWI overlay with transparency
                    cmap = plt.cm.get_cmap('BrBG')
                    rgba = cmap(norm(np.nan_to_num(ndwi, nan=0)))
                    rgba[:, :, 3] = np.where(nodata_mask, 0, 255)
                    rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
                    alpha = rgba[:, :, 3].astype(np.uint8)
                    
                    img = Image.fromarray(rgb, 'RGB')
                    img_alpha = Image.fromarray(alpha, 'L')
                    img.putalpha(img_alpha)
                    ndwi_png = "temp_ndwi.png"
                    img.save(ndwi_png, 'PNG')
                    
                    ndwi_layer = folium.raster_layers.ImageOverlay(
                        image=ndwi_png,
                        bounds=bounds,
                        opacity=0.7,
                        name='NDWI',
                        overlay=True,
                        control=True,
                        show=False
                    )
                    ndwi_layer.add_to(m)
                    
                    print(f"   ✅ NDWI layer added (range: {np.nanmin(ndwi):.3f} to {np.nanmax(ndwi):.3f})")
                    
                    # Calculate EVI
                    print("\n🌾 Calculating EVI...")
                    evi_denominator = nir + 6 * red - 7.5 * blue + 1
                    evi = np.where(evi_denominator != 0, 2.5 * ((nir - red) / evi_denominator), 0)
                    evi = np.clip(evi, -1, 1)
                    evi[nodata_mask] = np.nan
                    
                    # Create EVI overlay with transparency
                    cmap = plt.cm.get_cmap('YlGn')
                    rgba = cmap(norm(np.nan_to_num(evi, nan=0)))
                    rgba[:, :, 3] = np.where(nodata_mask, 0, 255)
                    rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
                    alpha = rgba[:, :, 3].astype(np.uint8)
                    
                    img = Image.fromarray(rgb, 'RGB')
                    img_alpha = Image.fromarray(alpha, 'L')
                    img.putalpha(img_alpha)
                    evi_png = "temp_evi.png"
                    img.save(evi_png, 'PNG')
                    
                    evi_layer = folium.raster_layers.ImageOverlay(
                        image=evi_png,
                        bounds=bounds,
                        opacity=0.7,
                        name='EVI',
                        overlay=True,
                        control=True,
                        show=False
                    )
                    evi_layer.add_to(m)
                    
                    print(f"   ✅ EVI layer added (range: {np.nanmin(evi):.3f} to {np.nanmax(evi):.3f})")
                    
                    # Create RGB composite with transparency
                    print("\n🖼️  Creating RGB composite...")
                    # Mask nodata values first
                    red_masked = np.where(nodata_mask, 0, red)
                    green_masked = np.where(nodata_mask, 0, green)
                    blue_masked = np.where(nodata_mask, 0, blue)
                    
                    # Calculate percentiles excluding nodata
                    red_valid = red_masked[~nodata_mask]
                    green_valid = green_masked[~nodata_mask]
                    blue_valid = blue_masked[~nodata_mask]
                    
                    red_p98 = np.percentile(red_valid, 98) if len(red_valid) > 0 else 1
                    green_p98 = np.percentile(green_valid, 98) if len(green_valid) > 0 else 1
                    blue_p98 = np.percentile(blue_valid, 98) if len(blue_valid) > 0 else 1
                    
                    rgb_composite = np.dstack([
                        np.clip(red_masked / red_p98 * 255, 0, 255).astype(np.uint8),
                        np.clip(green_masked / green_p98 * 255, 0, 255).astype(np.uint8),
                        np.clip(blue_masked / blue_p98 * 255, 0, 255).astype(np.uint8)
                    ])
                    
                    img = Image.fromarray(rgb_composite, 'RGB')
                    alpha_channel = np.where(nodata_mask, 0, 255).astype(np.uint8)
                    img_alpha = Image.fromarray(alpha_channel, 'L')
                    img.putalpha(img_alpha)
                    rgb_png = "temp_rgb.png"
                    img.save(rgb_png, 'PNG')
                    
                    rgb_layer = folium.raster_layers.ImageOverlay(
                        image=rgb_png,
                        bounds=bounds,
                        opacity=0.8,
                        name='RGB Orthomosaic',
                        overlay=True,
                        control=True,
                        show=False
                    )
                    rgb_layer.add_to(m)
                    
                    print(f"   ✅ RGB composite added")
                    
                else:
                    print(f"   ⚠️  Expected at least 4 bands, got {src.count}")
                    
        except Exception as e:
            print(f"   ❌ Error processing orthomosaic: {e}")
            import traceback
            traceback.print_exc()
    
    # Extract sensor data for graphs
    print(f"\n📊 Extracting sensor data for charts...")
    sensor_data_json = {
        'nitrogen': gdf['N_pct'].tolist() if 'N_pct' in gdf.columns else [],
        'phosphorus': gdf['P_pct'].tolist() if 'P_pct' in gdf.columns else [],
        'potassium': gdf['K_pct'].tolist() if 'K_pct' in gdf.columns else [],
        'ph': gdf['pH'].tolist() if 'pH' in gdf.columns else [],
        'temperature': gdf['Temp_C'].tolist() if 'Temp_C' in gdf.columns else [],
        'ec': gdf['EC_uScm'].tolist() if 'EC_uScm' in gdf.columns else [],
        'moisture': gdf['Moist_pct'].tolist() if 'Moist_pct' in gdf.columns else []
    }
    
    # Calculate overall health (0-100 scale)
    def calc_health(row):
        """Calculate health score from all sensor values"""
        scores = []
        
        # Nitrogen (optimal: 30-45%)
        if 'N_pct' in row and pd.notna(row['N_pct']):
            n = row['N_pct']
            if 30 <= n <= 45:
                scores.append(100)
            elif 20 <= n < 30 or 45 < n <= 50:
                scores.append(70)
            elif 15 <= n < 20 or 50 < n <= 55:
                scores.append(50)
            else:
                scores.append(30)
        
        # Phosphorus (optimal: 50-65)
        if 'P_pct' in row and pd.notna(row['P_pct']):
            p = row['P_pct']
            if 50 <= p <= 65:
                scores.append(100)
            elif 40 <= p < 50 or 65 < p <= 70:
                scores.append(70)
            else:
                scores.append(50)
        
        # Potassium (optimal: 80-120)
        if 'K_pct' in row and pd.notna(row['K_pct']):
            k = row['K_pct']
            if 80 <= k <= 120:
                scores.append(100)
            elif 60 <= k < 80 or 120 < k <= 130:
                scores.append(70)
            else:
                scores.append(50)
        
        # pH (optimal: 6.5-7.5)
        if 'pH' in row and pd.notna(row['pH']):
            ph = row['pH']
            if 6.5 <= ph <= 7.5:
                scores.append(100)
            elif 6.0 <= ph < 6.5 or 7.5 < ph <= 8.0:
                scores.append(70)
            else:
                scores.append(50)
        
        # Temperature (optimal: 30-36°C)
        if 'Temp_C' in row and pd.notna(row['Temp_C']):
            temp = row['Temp_C']
            if 30 <= temp <= 36:
                scores.append(100)
            elif 25 <= temp < 30 or 36 < temp <= 40:
                scores.append(70)
            else:
                scores.append(50)
        
        # EC (optimal: 300-600 μS/cm)
        if 'EC_uScm' in row and pd.notna(row['EC_uScm']):
            ec = row['EC_uScm']
            if 300 <= ec <= 600:
                scores.append(100)
            elif 200 <= ec < 300 or 600 < ec <= 800:
                scores.append(70)
            else:
                scores.append(50)
        
        # Moisture (optimal: 8-12%)
        if 'Moist_pct' in row and pd.notna(row['Moist_pct']):
            moist = row['Moist_pct']
            if 8 <= moist <= 12:
                scores.append(100)
            elif 5 <= moist < 8 or 12 < moist <= 15:
                scores.append(70)
            else:
                scores.append(50)
        
        return sum(scores) / len(scores) if scores else 50
    
    # Calculate health for each point
    gdf['health'] = gdf.apply(calc_health, axis=1)
    sensor_data_json['health'] = [round(h, 1) for h in gdf['health'].tolist()]
    
    print(f"   Health scores range: {gdf['health'].min():.1f} - {gdf['health'].max():.1f}")
    
    # Add sensor points
    print(f"\n📍 Adding sensor points...")
    
    column_map = {
        "EC (μS/cm)": "EC_uScm",
        "Temperature (°C)": "Temp_C",
        "Nitrogen (%)": "N_pct",
        "Phosphorus (%)": "P_pct",
        "Potassium (%)": "K_pct",
        "pH": "pH",
        "Moisture (%)": "Moist_pct"
    }
    
    points_layer = folium.FeatureGroup(name='Sensor Points', show=True)
    
    for idx, row in gdf.iterrows():
        popup_html = f"""
        <div style='font-family: Arial, sans-serif; min-width: 250px;'>
            <h4 style='margin: 0 0 10px 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;'>
                📍 Sensor Point {idx + 1}
            </h4>
            <table style='width: 100%; border-collapse: collapse;'>
        """
        
        for label, col in column_map.items():
            if col in row and pd.notna(row[col]):
                value = row[col]
                if 'N_pct' in col or 'P_pct' in col or 'K_pct' in col:
                    color = '#27ae60'
                elif 'Temp' in col:
                    color = '#e74c3c'
                elif 'Moist' in col:
                    color = '#3498db'
                elif 'pH' in col:
                    color = '#9b59b6'
                elif 'EC' in col:
                    color = '#f39c12'
                else:
                    color = '#34495e'
                
                popup_html += f"""
                <tr style='border-bottom: 1px solid #ecf0f1;'>
                    <td style='padding: 5px; font-weight: bold; color: {color};'>{label}:</td>
                    <td style='padding: 5px; text-align: right;'>{value:.2f}</td>
                </tr>
                """
        
        popup_html += "</table></div>"
        
        tooltip_text = f"Point {idx + 1}"
        if 'N_pct' in row and pd.notna(row['N_pct']):
            tooltip_text += f" | N: {row['N_pct']:.1f}%"
        
        # Color code by health score
        if 'health' in row and pd.notna(row['health']):
            health_value = row['health']
            # Green: 85+, Light Green: 70-85, Yellow: 55-70, Orange: 40-55, Red: <40
            if health_value >= 85:
                marker_color = '#34c759'  # Green
            elif health_value >= 70:
                marker_color = '#30d158'  # Light green
            elif health_value >= 55:
                marker_color = '#ffd60a'  # Yellow (70% values will show here)
            elif health_value >= 40:
                marker_color = '#ff9f0a'  # Orange
            else:
                marker_color = '#ff453a'  # Red
        else:
            marker_color = 'blue'
        
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=10,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=tooltip_text,
            color='white',
            fill=True,
            fillColor=marker_color,
            fillOpacity=0.8,
            weight=2
        ).add_to(points_layer)
    
    points_layer.add_to(m)
    print(f"   ✅ Added {len(gdf)} sensor points")
    
    # Add controls (single consolidated layer control)
    plugins.Draw(export=True, position='topleft').add_to(m)
    plugins.Fullscreen(position='topleft', force_separate_button=True).add_to(m)
    plugins.MousePosition(position='bottomleft', separator=' | ', lng_first=True, num_digits=6).add_to(m)
    plugins.MeasureControl(position='topleft', primary_length_unit='meters', primary_area_unit='sqmeters').add_to(m)
    plugins.MiniMap(position='bottomright', width=150, height=150).add_to(m)
    
    # Single layer control at the end (consolidated)
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    
    # Add macOS-styled widgets and enhanced UI
    widgets_html = '''
    <!-- Chart.js for graphs -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js"></script>
    
    <style>
    /* macOS-styled CSS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    }
    
    .macos-widget {
        position: fixed;
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 12px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08);
        padding: 16px;
        color: #1d1d1f;
        z-index: 9999;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(0, 0, 0, 0.04);
    }
    
    .macos-widget.minimized {
        height: 45px !important;
        overflow: hidden;
    }
    
    .widget-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    }
    
    .widget-title {
        font-size: 14px;
        font-weight: 600;
        color: #1d1d1f;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .widget-controls {
        display: flex;
        gap: 6px;
    }
    
    .widget-btn {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        border: none;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .widget-btn.minimize {
        background: #ffbd2e;
    }
    
    .widget-btn.minimize:hover {
        background: #f5a623;
    }
    
    .widget-content {
        font-size: 12px;
        line-height: 1.6;
    }
    
    .stat-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(0, 0, 0, 0.04);
    }
    
    .stat-row:last-child {
        border-bottom: none;
    }
    
    .stat-label {
        font-weight: 500;
        color: #6e6e73;
    }
    
    .stat-value {
        font-weight: 600;
        color: #1d1d1f;
    }
    
    .health-indicator {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    
    /* Layer Control Styling */
    .leaflet-control-layers {
        background: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid rgba(0, 0, 0, 0.04) !important;
        padding: 12px !important;
    }
    
    .leaflet-control-layers-toggle {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 8px !important;
    }
    
    .leaflet-bar {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        border: none !important;
        border-radius: 8px !important;
    }
    
    .leaflet-bar a {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1d1d1f !important;
        border: none !important;
    }
    
    .leaflet-bar a:hover {
        background-color: rgba(245, 245, 247, 0.95) !important;
    }
    </style>
    
    <!-- Dashboard Title Widget -->
    <div class="macos-widget" id="title-widget" style="top: 20px; left: 20px; max-width: 300px;">
        <div class="widget-header">
            <div class="widget-title">🌱 Plant Health Monitor</div>
            <div class="widget-controls">
                <button class="widget-btn minimize" onclick="toggleWidget('title-widget')"></button>
            </div>
        </div>
        <div class="widget-content">
            <div style="font-size: 11px; color: #6e6e73;">Real-time IoT Sensor Analysis</div>
        </div>
    </div>
    
    <!-- Health Status Widget -->
    <div class="macos-widget" id="health-widget" style="top: 20px; right: 20px; max-width: 280px;">
        <div class="widget-header">
            <div class="widget-title">🌾 Health Status</div>
            <div class="widget-controls">
                <button class="widget-btn minimize" onclick="toggleWidget('health-widget')"></button>
            </div>
        </div>
        <div class="widget-content">
            <div class="stat-row">
                <span class="stat-label"><span class="health-indicator" style="background: #34c759;"></span>Excellent</span>
                <span class="stat-value">≥ 85%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label"><span class="health-indicator" style="background: #30d158;"></span>Good</span>
                <span class="stat-value">70-84%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label"><span class="health-indicator" style="background: #ffd60a;"></span>Fair</span>
                <span class="stat-value">55-69%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label"><span class="health-indicator" style="background: #ff9f0a;"></span>Poor</span>
                <span class="stat-value">40-54%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label"><span class="health-indicator" style="background: #ff453a;"></span>Critical</span>
                <span class="stat-value">&lt; 40%</span>
            </div>
        </div>
    </div>
    
    <!-- Sensor Graphs Widget -->
    <div class="macos-widget" id="graph-widget" style="bottom: 20px; left: 20px; width: 420px; max-height: 400px;">
        <div class="widget-header">
            <div class="widget-title">📊 Sensor Readings</div>
            <div class="widget-controls">
                <button class="widget-btn minimize" onclick="toggleWidget('graph-widget')"></button>
            </div>
        </div>
        <div class="widget-content">
            <div style="margin-bottom: 12px;">
                <label for="sensorSelect" style="font-size: 11px; color: #6e6e73; font-weight: 500; display: block; margin-bottom: 6px;">Select Metric:</label>
                <select id="sensorSelect" onchange="updateSensorChart()" style="width: 100%; padding: 8px 12px; border: 1px solid rgba(0, 0, 0, 0.1); border-radius: 8px; font-family: 'Inter', sans-serif; font-size: 12px; background: rgba(255, 255, 255, 0.95); cursor: pointer; transition: all 0.2s;">
                    <option value="nitrogen">Nitrogen (%)</option>
                    <option value="ec">EC (μS/cm)</option>
                    <option value="temperature">Temperature (°C)</option>
                    <option value="phosphorus">Phosphorus (%)</option>
                    <option value="potassium">Potassium (%)</option>
                    <option value="ph">pH</option>
                    <option value="moisture">Moisture (%)</option>
                    <option value="health">Overall Health</option>
                </select>
            </div>
            <canvas id="sensorChart" height="220"></canvas>
        </div>
    </div>
    
    <!-- Statistics Widget -->
    <div class="macos-widget" id="stats-widget" style="bottom: 20px; right: 20px; max-width: 280px;">
        <div class="widget-header">
            <div class="widget-title">📈 Statistics</div>
            <div class="widget-controls">
                <button class="widget-btn minimize" onclick="toggleWidget('stats-widget')"></button>
            </div>
        </div>
        <div class="widget-content">
            <div class="stat-row">
                <span class="stat-label">Total Points</span>
                <span class="stat-value">21</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Avg Nitrogen</span>
                <span class="stat-value">27.2%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Avg Moisture</span>
                <span class="stat-value">9.1%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Avg Temp</span>
                <span class="stat-value">35.5°C</span>
            </div>
        </div>
    </div>
    
    <!-- Layers Widget -->
    <div class="macos-widget" id="layers-widget" style="top: 220px; right: 20px; max-width: 280px;">
        <div class="widget-header">
            <div class="widget-title">🗺️ Map Layers</div>
            <div class="widget-controls">
                <button class="widget-btn minimize" onclick="toggleWidget('layers-widget')"></button>
            </div>
        </div>
        <div class="widget-content" style="max-height: 300px; overflow-y: auto;">
            <div style="margin-bottom: 12px;">
                <div style="font-size: 11px; font-weight: 600; color: #1d1d1f; margin-bottom: 6px;">Base Maps</div>
                <label style="display: flex; align-items: center; padding: 6px 0; cursor: pointer;">
                    <input type="radio" name="basemap" value="osm" checked onchange="switchBasemap('osm')" style="margin-right: 8px;">
                    <span style="font-size: 12px;">OpenStreetMap</span>
                </label>
                <label style="display: flex; align-items: center; padding: 6px 0; cursor: pointer;">
                    <input type="radio" name="basemap" value="esri" onchange="switchBasemap('esri')" style="margin-right: 8px;">
                    <span style="font-size: 12px;">ESRI World Imagery</span>
                </label>
                <label style="display: flex; align-items: center; padding: 6px 0; cursor: pointer;">
                    <input type="radio" name="basemap" value="google" onchange="switchBasemap('google')" style="margin-right: 8px;">
                    <span style="font-size: 12px;">Google Satellite</span>
                </label>
            </div>
            <div style="border-top: 1px solid rgba(0, 0, 0, 0.06); padding-top: 12px;">
                <div style="font-size: 11px; font-weight: 600; color: #1d1d1f; margin-bottom: 6px;">Overlays</div>
                <label style="display: flex; align-items: center; padding: 6px 0; cursor: pointer;">
                    <input type="checkbox" id="layer-rgb" onchange="toggleLayer('RGB Orthomosaic')" style="margin-right: 8px;">
                    <span style="font-size: 12px;">RGB Orthomosaic</span>
                </label>
                <label style="display: flex; align-items: center; padding: 6px 0; cursor: pointer;">
                    <input type="checkbox" id="layer-ndvi" checked onchange="toggleLayer('NDVI')" style="margin-right: 8px;">
                    <span style="font-size: 12px;">NDVI</span>
                </label>
                <label style="display: flex; align-items: center; padding: 6px 0; cursor: pointer;">
                    <input type="checkbox" id="layer-ndwi" onchange="toggleLayer('NDWI')" style="margin-right: 8px;">
                    <span style="font-size: 12px;">NDWI</span>
                </label>
                <label style="display: flex; align-items: center; padding: 6px 0; cursor: pointer;">
                    <input type="checkbox" id="layer-evi" onchange="toggleLayer('EVI')" style="margin-right: 8px;">
                    <span style="font-size: 12px;">EVI</span>
                </label>
                <label style="display: flex; align-items: center; padding: 6px 0; cursor: pointer;">
                    <input type="checkbox" id="layer-points" checked onchange="toggleLayer('Sensor Points')" style="margin-right: 8px;">
                    <span style="font-size: 12px;">Sensor Points</span>
                </label>
            </div>
        </div>
    </div>
    
    <script>
    // Widget minimize/maximize functionality
    function toggleWidget(widgetId) {
        const widget = document.getElementById(widgetId);
        widget.classList.toggle('minimized');
    }
    
    // Sensor data for all metrics (from actual shapefile data)
    const sensorDatasets = ''' + f'''{{
        nitrogen: {{
            label: 'Nitrogen (%)',
            data: {sensor_data_json['nitrogen']},
            borderColor: '#30d158',
            backgroundColor: 'rgba(48, 209, 88, 0.1)'
        }},
        ec: {{
            label: 'EC (μS/cm)',
            data: {sensor_data_json['ec']},
            borderColor: '#f39c12',
            backgroundColor: 'rgba(243, 156, 18, 0.1)'
        }},
        temperature: {{
            label: 'Temperature (°C)',
            data: {sensor_data_json['temperature']},
            borderColor: '#e74c3c',
            backgroundColor: 'rgba(231, 76, 60, 0.1)'
        }},
        phosphorus: {{
            label: 'Phosphorus',
            data: {sensor_data_json['phosphorus']},
            borderColor: '#9b59b6',
            backgroundColor: 'rgba(155, 89, 182, 0.1)'
        }},
        potassium: {{
            label: 'Potassium',
            data: {sensor_data_json['potassium']},
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.1)'
        }},
        ph: {{
            label: 'pH',
            data: {sensor_data_json['ph']},
            borderColor: '#9b59b6',
            backgroundColor: 'rgba(155, 89, 182, 0.1)'
        }},
        moisture: {{
            label: 'Moisture (%)',
            data: {sensor_data_json['moisture']},
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.1)'
        }},
        health: {{
            label: 'Overall Health (%)',
            data: {sensor_data_json['health']},
            borderColor: '#34c759',
            backgroundColor: 'rgba(52, 199, 89, 0.1)'
        }}
    }}''' + ''';
    
    // Initialize chart
    const ctx = document.getElementById('sensorChart');
    let sensorChart = null;
    
    if (ctx) {
        const initialData = sensorDatasets['nitrogen'];
        sensorChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21'],
                datasets: [{
                    label: initialData.label,
                    data: initialData.data,
                    borderColor: initialData.borderColor,
                    backgroundColor: initialData.backgroundColor,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: {
                                family: 'Inter',
                                size: 11
                            },
                            usePointStyle: true,
                            boxHeight: 6
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.04)'
                        },
                        ticks: {
                            font: {
                                family: 'Inter',
                                size: 10
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                family: 'Inter',
                                size: 10
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Update chart when dropdown changes
    function updateSensorChart() {
        const select = document.getElementById('sensorSelect');
        const selectedMetric = select.value;
        const dataset = sensorDatasets[selectedMetric];
        
        if (sensorChart && dataset) {
            sensorChart.data.datasets[0] = {
                label: dataset.label,
                data: dataset.data,
                borderColor: dataset.borderColor,
                backgroundColor: dataset.backgroundColor,
                tension: 0.4,
                fill: true
            };
            sensorChart.update();
        }
    }
    
    // Layer control functions
    function switchBasemap(basemapType) {
        // This will interact with Leaflet's layer control
        // We'll trigger clicks on the appropriate layer control radio buttons
        const layerControlInputs = document.querySelectorAll('.leaflet-control-layers-base input');
        layerControlInputs.forEach(input => {
            const label = input.parentElement.textContent.trim();
            if ((basemapType === 'osm' && label === 'OpenStreetMap') ||
                (basemapType === 'esri' && label === 'ESRI World Imagery') ||
                (basemapType === 'google' && label === 'Google Satellite')) {
                input.click();
            }
        });
    }
    
    function toggleLayer(layerName) {
        // This will interact with Leaflet's layer control checkboxes
        const layerControlInputs = document.querySelectorAll('.leaflet-control-layers-overlays input');
        layerControlInputs.forEach(input => {
            const label = input.parentElement.textContent.trim();
            if (label === layerName) {
                input.click();
            }
        });
    }
    </script>
    '''
    
    # Save the base map first
    print(f"\n💾 Saving dashboard to{output_html}")
    m.save(output_html)
    print("   Base map saved, injecting widgets...")
    
    # Add a small delay to ensure file is flushed
    import time
    time.sleep(0.5)
    
    # Now inject the widgets HTML into the saved file
    with open(output_html, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"   Read HTML file: {len(html_content)} bytes")
    print(f"   Contains </html>: {'</html>' in html_content}")
    
    # Insert widgets HTML just before closing </html> tag (Folium doesn't use </body>)
    if '</html>' in html_content:
        html_content = html_content.replace('</html>', widgets_html + '\n</html>')
        print(f"   Injected widgets, new size: {len(html_content)} bytes")
    else:
        print("   WARNING: </html> tag not found!")
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("   Widgets injected successfully!")
    
    file_size = os.path.getsize(output_html) / (1024 * 1024)
    print(f"\n✅ Dashboard created successfully!")
    print(f"   File size: {file_size:.2f} MB")
    print(f"\n📂 Open {output_html} in your web browser")
    
    return output_html

if __name__ == "__main__":
    shapefile = "points_complete.shp"
    orthomosaic = "p17 NARC MERGED ALL BANDS.tif"
    
    if not os.path.exists(shapefile):
        print(f"❌ Shapefile not found: {shapefile}")
        exit(1)
    
    if not os.path.exists(orthomosaic):
        print(f"⚠️  Orthomosaic not found: {orthomosaic}")
        print("   Creating dashboard without vegetation indices...")
        from dashboard_lightweight import create_lightweight_dashboard
        create_lightweight_dashboard(shapefile)
    else:
        calculate_and_add_indices(shapefile, orthomosaic)
