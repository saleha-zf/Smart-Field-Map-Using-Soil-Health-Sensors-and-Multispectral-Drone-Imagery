import geopandas as gpd
import json

# Load shapefile
gdf = gpd.read_file('points_complete.shp')

# Extract sensor data
sensor_data = {
    'nitrogen': gdf['N_pct'].tolist() if 'N_pct' in gdf.columns else [],
    'phosphorus': gdf['P_pct'].tolist() if 'P_pct' in gdf.columns else [],
    'potassium': gdf['K_pct'].tolist() if 'K_pct' in gdf.columns else [],
    'ph': gdf['pH'].tolist() if 'pH' in gdf.columns else [],
    'temperature': gdf['Temp_C'].tolist() if 'Temp_C' in gdf.columns else [],
    'ec': gdf['EC_uScm'].tolist() if 'EC_uScm' in gdf.columns else [],
    'moisture': gdf['Moist_pct'].tolist() if 'Moist_pct' in gdf.columns else []
}

# Calculate overall health (normalized average)
# Normalize each metric to 0-100 scale
def normalize(values, min_val, max_val):
    """Normalize values to 0-100 scale"""
    return [(v - min_val) / (max_val - min_val) * 100 if (max_val - min_val) > 0 else 50 for v in values]

# Normalize each metric (using typical ranges)
n_norm = normalize(sensor_data['nitrogen'], 0, 50)  # 0-50% nitrogen range
p_norm = normalize(sensor_data['phosphorus'], 0, 3)  # 0-3% phosphorus range
k_norm = normalize(sensor_data['potassium'], 0, 4)  # 0-4% potassium range
ph_norm = [abs(v - 7) / 3 * 100 for v in sensor_data['ph']]  # pH 7 is ideal, normalize deviation
ph_norm = [100 - v for v in ph_norm]  # Invert so 7 = 100%
temp_norm = [100 - abs(v - 30) / 20 * 100 for v in sensor_data['temperature']]  # 30°C ideal
ec_norm = normalize(sensor_data['ec'], 0, 2000)  # 0-2000 μS/cm range
moist_norm = normalize(sensor_data['moisture'], 0, 20)  # 0-20% moisture range

# Calculate overall health as average
health = []
for i in range(len(n_norm)):
    avg = (n_norm[i] + p_norm[i] + k_norm[i] + ph_norm[i] + temp_norm[i] + ec_norm[i] + moist_norm[i]) / 7
    health.append(round(avg, 1))

sensor_data['health'] = health

# Print as JSON
print(json.dumps(sensor_data, indent=2))
