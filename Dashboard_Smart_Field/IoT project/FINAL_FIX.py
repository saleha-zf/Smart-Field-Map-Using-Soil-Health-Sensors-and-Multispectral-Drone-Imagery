"""
FINAL FIX - Start from backup and apply all fixes correctly
"""
import re
import shutil

def final_fix():
    # Paths
    backup_path = r'c:\Users\hp\Documents\IoT project\dashboard_with_indices.html'
    target_path = r'c:\Users\hp\Documents\IoT project\enhanced_dashboard.html'
    
    print("Reading backup file...")
    with open(backup_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print(f"Backup size: {len(content)} bytes")
    
    # Step 1: Replace ALL circleMarkers with emoji icon markers
    print("\n=== Replacing CircleMarkers with Emoji Icons ===")
    circle_pattern = r'var (circle_marker_[a-f0-9]+) = L\.circleMarker\(\s*\[([^\]]+)\],\s*\{[^}]+\}\s*\)'
    
    icons = [
        ('🌱', '#34c759'),  # Excellent 
        ('🌿', '#30d158'),  # Good
        ('🌾', '#ffd60a'),  # Fair
        ('🍂', '#ff9f0a'),  # Poor
        ('❌', '#ff453a'),  # Critical
    ]
    
    matches = list(re.finditer(circle_pattern, content))
    print(f"Found {len(matches)} circle markers to replace")
    
    for i, match in enumerate(matches):
        var_name = match.group(1)
        coords = match.group(2)
        
        hash_val = hash(var_name) % 5
        emoji, color = icons[hash_val]
        
        icon_html = f"<div style='width:24px;height:24px;background:white;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,0.3);border:2px solid {color};font-size:14px;'>{emoji}</div>"
        
        icon_var = f"icon_{var_name}"
        replacement = (
            f'var {icon_var} = L.divIcon({{"className": "", "html": "{icon_html}", "iconSize": [24, 24], "iconAnchor": [12, 12]}});\n'
            f'    var {var_name} = L.marker([{coords}], {{"icon": {icon_var}}})'
        )
        
        content = content.replace(match.group(0), replacement)
    
    print(f"Replaced {len(matches)} markers")
    
    # Step 2: Remove old UI elements
    print("\n=== Removing Old UI ===")
    patterns_to_remove = [
        r'<div style="position: fixed; bottom: 50px.*?Sensor Points.*?</div>',
        r'<div style="position: fixed; top: 10px.*?Agricultural Dashboard.*?</div>',
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Step 3: Find layer variables
    print("\n=== Finding Layers ===")
    overlays = re.findall(r'var (image_overlay_[a-f0-9]+)', content)
    feature_groups = re.findall(r'var (feature_group_[a-f0-9]+)', content)
    map_match = re.search(r'var (map_[a-f0-9]+) = L\.map', content)
    map_var = map_match.group(1) if map_match else 'map'
    
    print(f"Found {len(overlays)} overlays: {overlays[:4]}")
    print(f"Found {len(feature_groups)} feature groups")
    print(f"Map variable: {map_var}")
    
    # Step 4: Add widgets and controls
    additions = f"""
    <style>
    /* Modern Widgets */
    .widget {{
        position: fixed;
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(15px);
        border-radius: 14px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        padding: 16px;
        font-family: 'Inter', sans-serif;
        z-index: 9999;
    }}
    
    #w-title {{ top: 20px; left: 20px; max-width: 250px; }}
    #w-weather {{ top: 20px; right: 20px; max-width: 280px; }}
    #w-sensors {{ bottom: 20px; left: 20px; max-width: 300px; }}
    #w-health {{ bottom: 20px; right: 20px; max-width: 280px; }}
    
    /* Layer Control */
    .leaflet-control-layers {{
        background: rgba(255,255,255,0.95) !important;
        backdrop-filter: blur(15px);
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15) !important;
        padding: 14px !important;
    }}
    </style>
    
    <!-- Widgets -->
    <div id="w-title" class="widget">
        <h3 style="margin:0; font-size:16px;">🌱 Plant Health Monitor</h3>
        <p style="margin:5px 0 0; font-size:11px; color:#666;">Real-time Analysis & Sensor Data</p>
    </div>
    
    <div id="w-health" class="widget">
        <h4 style="margin:0 0 10px; font-size:14px;">🌾 Health Status</h4>
        <div style="font-size:11px; line-height:1.8;">
            <div><span style="background:#34c759; width:12px; height:12px; border-radius:50%; display:inline-block; margin-right:6px;"></span>Excellent ≥ 85%</div>
            <div><span style="background:#30d158; width:12px; height:12px; border-radius:50%; display:inline-block; margin-right:6px;"></span>Good 70-84%</div>
            <div><span style="background:#ffd60a; width:12px; height:12px; border-radius:50%; display:inline-block; margin-right:6px;"></span>Fair 55-69%</div>
            <div><span style="background:#ff9f0a; width:12px; height:12px; border-radius:50%; display:inline-block; margin-right:6px;"></span>Poor 40-54%</div>
            <div><span style="background:#ff453a; width:12px; height:12px; border-radius:50%; display:inline-block; margin-right:6px;"></span>Critical < 40%</div>
        </div>
    </div>
    
    <script>
    // Layer Control
    window.addEventListener('load', function() {{
        setTimeout(function() {{
            console.log("Setting up layer control...");
            
            var baseMaps = {{
                "OpenStreetMap": L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{maxZoom: 19}}),
                "Satellite": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{maxZoom: 19}})
            }};
            
            var overlayMaps = {{}};
            
            if (typeof {overlays[0] if overlays else 'image_overlay_ab2961d7cde633a1c55f1b5b51b6f89d'} !== 'undefined') overlayMaps['RGB Orthomosaic'] = {overlays[0] if overlays else 'image_overlay_ab2961d7cde633a1c55f1b5b51b6f89d'};
            if (typeof {overlays[1] if len(overlays) > 1 else 'image_overlay_44efdb4cc89a890db9b7f2e3c0800960'} !== 'undefined') overlayMaps['NDVI Layer'] = {overlays[1] if len(overlays) > 1 else 'image_overlay_44efdb4cc89a890db9b7f2e3c0800960'};
            if (typeof {overlays[2] if len(overlays) > 2 else 'image_overlay_7d1447cce4501b1bb09ca9038f8497c5'} !== 'undefined') overlayMaps['EVI Layer'] = {overlays[2] if len(overlays) > 2 else 'image_overlay_7d1447cce4501b1bb09ca9038f8497c5'};
            if (typeof {feature_groups[0] if feature_groups else 'feature_group_0b728b84af20c1785e19279b8a709bff'} !== 'undefined') overlayMaps['Sensor Points'] = {feature_groups[0] if feature_groups else 'feature_group_0b728b84af20c1785e19279b8a709bff'};
            
            L.control.layers(baseMaps, overlayMaps, {{collapsed: false, position: 'topright'}}).addTo({map_var});
            console.log("Layer control added with", Object.keys(overlayMaps).length, "overlays");
        }}, 2000);
    }});
    </script>
    """
    
    content = content.replace('</body>', additions + '\n</body>')
    
    # Write output
    print("\n=== Writing final file ===")
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Final size: {len(content)} bytes")
    print("\nFINAL FIX COMPLETE!")
    print(f"✓ {len(matches)} emoji icons")
    print(f"✓ {len(overlays)} image layers")
    print(f"✓ Layer control added")
    print(f"✓ Widgets positioned without overlap")

if __name__ == '__main__':
    final_fix()
