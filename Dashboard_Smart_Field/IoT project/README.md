# 🌾 Agricultural Geospatial Dashboard

An interactive web-based dashboard for visualizing agricultural sensor data overlaid on orthomosaic imagery with computed vegetation indices.

## 📋 Features

- **Multiple Basemaps**: Toggle between OpenStreetMap, ESRI World Imagery, and Google Satellite
- **Vegetation Indices**: 
  - NDVI (Normalized Difference Vegetation Index)
  - NDWI (Normalized Difference Water Index)
  - EVI (Enhanced Vegetation Index)
- **Sensor Data Visualization**: 21 ground sensor points with detailed tooltips
- **Interactive Controls**:
  - Layer toggle (show/hide layers)
  - Opacity control for raster layers
  - Drawing and measurement tools
  - Fullscreen mode
  - Coordinate display
  - Mini-map for navigation

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install geopandas rasterio folium branca pillow numpy matplotlib
```

## 🚀 Usage

### Quick Start (Lightweight Dashboard)

For a fast, lightweight dashboard with sensor points only:

```bash
python dashboard_lightweight.py
```

This creates `geospatial_dashboard.html` (~90 KB) with:
- Sensor points with tooltips
- Multiple basemaps
- Interactive tools
- No vegetation indices (faster loading)

### Full Dashboard with Vegetation Indices

For the complete dashboard with NDVI, NDWI, EVI layers:

```bash
python dashboard_with_indices.py
```

This creates `dashboard_with_indices.html` (~7.4 MB) with:
- All features from lightweight version
- NDVI layer (vegetation health)
- NDWI layer (water content)
- EVI layer (enhanced vegetation)
- RGB orthomosaic composite

**Note**: Processing the 3GB orthomosaic takes 1-2 minutes. The script automatically downsamples the imagery for web display.

### Calculate Vegetation Indices Separately

To pre-calculate and save vegetation indices as GeoTIFF files:

```bash
python vegetation_indices.py
```

This creates:
- `ndvi.tif` - NDVI layer
- `ndwi.tif` - NDWI layer
- `evi.tif` - EVI layer

### Create Cloud Optimized GeoTIFF (COG)

To convert the orthomosaic to COG format for better web performance:

```bash
python create_cog.py
```

This creates `p17 NARC MERGED ALL BANDS_cog.tif` with:
- Internal tiling for efficient access
- Overviews (pyramids) for multi-scale viewing
- Compression to reduce file size

## 📊 Data Files

### Input Files
- `points_complete.shp` - Shapefile with 21 sensor points
- `p17 NARC MERGED ALL BANDS.tif` - Multispectral orthomosaic (3GB, 6 bands)

### Sensor Data Columns
The shapefile contains the following sensor measurements:
- **EC_uScm**: Electrical Conductivity (μS/cm)
- **Temp_C**: Temperature (°C)
- **N_pct**: Nitrogen content (%)
- **P_pct**: Phosphorus content (%)
- **K_pct**: Potassium content (%)
- **pH**: Soil pH
- **Moist_pct**: Moisture content (%)

### Output Files
- `geospatial_dashboard.html` - Lightweight dashboard
- `dashboard_with_indices.html` - Full dashboard with vegetation indices
- `ndvi.tif`, `ndwi.tif`, `evi.tif` - Vegetation index GeoTIFFs
- `temp_*.png` - Temporary PNG files for web display

## 🎨 Dashboard Features

### Basemap Selection
Use the layer control panel (top right) to switch between:
- **OpenStreetMap**: Street map view
- **ESRI World Imagery**: High-resolution satellite imagery
- **Google Satellite**: Google's satellite imagery

### Vegetation Index Layers
Toggle vegetation indices on/off using the layer control:
- **NDVI**: Red (low vegetation) → Yellow → Green (high vegetation)
- **NDWI**: Brown (low water) → Blue (high water)
- **EVI**: Yellow (low) → Green (high)

Each layer has adjustable opacity (use browser's layer control).

### Sensor Points
- **Color-coded by Nitrogen content**:
  - 🟢 Green: High N (> 2.5%)
  - 🟡 Light Green: Medium N (2.0-2.5%)
  - 🟠 Orange: Low N (1.5-2.0%)
  - 🔴 Red: Very Low N (< 1.5%)
- **Click markers** to view detailed sensor data
- **Hover** for quick preview

### Interactive Tools
- **Drawing Tools**: Draw shapes and measure areas
- **Measurement**: Measure distances and areas
- **Fullscreen**: Expand to fullscreen mode
- **Coordinates**: View mouse position coordinates
- **Mini-map**: Navigate with overview map

## 🔧 Customization

### Adjust Downsampling Factor
Edit `dashboard_with_indices.py`, line 88:

```python
downsample = 10  # Change to 5 for higher quality, 20 for faster processing
```

### Change Color Schemes
Edit the colormap in the vegetation index calculation:

```python
cmap = plt.cm.get_cmap('RdYlGn')  # Change to 'viridis', 'plasma', etc.
```

### Modify Sensor Point Colors
Edit the nitrogen thresholds in `dashboard_with_indices.py`, lines 265-268:

```python
marker_color = 'green' if n_value > 2.5 else ...
```

## 📝 File Descriptions

| File | Purpose | Size |
|------|---------|------|
| `dashboard_lightweight.py` | Creates basic dashboard without indices | ~5 KB |
| `dashboard_with_indices.py` | Creates full dashboard with all layers | ~10 KB |
| `vegetation_indices.py` | Calculates NDVI, NDWI, EVI from orthomosaic | ~4 KB |
| `create_cog.py` | Converts GeoTIFF to Cloud Optimized format | ~3 KB |
| `requirements.txt` | Python dependencies | ~1 KB |
| `geospatial_dashboard.html` | Lightweight output | ~90 KB |
| `dashboard_with_indices.html` | Full output with indices | ~7.4 MB |

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'geopandas'"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Dashboard is very large (>100 MB)
**Solution**: Increase downsampling factor in `dashboard_with_indices.py`:
```python
downsample = 20  # or higher
```

### Issue: Vegetation indices look incorrect
**Solution**: Check band order in your orthomosaic. Edit `dashboard_with_indices.py` lines 90-93 to match your band configuration.

### Issue: Orthomosaic processing is too slow
**Solution**: Use the lightweight dashboard or pre-calculate indices:
```bash
python dashboard_lightweight.py
```

## 📚 Technical Details

### Vegetation Index Formulas

**NDVI** (Normalized Difference Vegetation Index):
```
NDVI = (NIR - Red) / (NIR + Red)
```
Range: -1 to 1 (higher = more vegetation)

**NDWI** (Normalized Difference Water Index):
```
NDWI = (Green - NIR) / (Green + NIR)
```
Range: -1 to 1 (higher = more water)

**EVI** (Enhanced Vegetation Index):
```
EVI = 2.5 × ((NIR - Red) / (NIR + 6×Red - 7.5×Blue + 1))
```
Range: -1 to 1 (enhanced sensitivity to vegetation)

### Coordinate Systems
- Input shapefile: UTM Zone 43N (EPSG:32643)
- Input orthomosaic: UTM Zone 43N (EPSG:32643)
- Dashboard output: WGS84 (EPSG:4326)

All data is automatically reprojected to WGS84 for web display.

## 📄 License

This project is provided as-is for agricultural research and monitoring purposes.

## 🤝 Contributing

To improve this dashboard:
1. Modify the Python scripts
2. Test with your data
3. Share improvements

## 📧 Support

For issues or questions, check the troubleshooting section above.

---

**Created with**: Python, Folium, Rasterio, GeoPandas, and ❤️ for precision agriculture
