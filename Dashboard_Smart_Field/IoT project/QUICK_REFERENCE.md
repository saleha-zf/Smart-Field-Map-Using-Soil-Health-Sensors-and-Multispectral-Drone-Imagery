# Quick Reference Guide - Enhanced Dashboard

## Widget Locations

```
┌─────────────────────────────────────────────────────────┐
│  🌱 Plant Health Monitor (Top Left)                     │
│  - Minimizable title widget                             │
│                                                          │
│                                    🌤️ Weather \u0026 Time  │
│                                    (Top Right)           │
│                                    - Real-time clock     │
│                                    - Weather data        │
│                                    - Location info       │
│                                                          │
│                    🗺️ MAP AREA                          │
│                                                          │
│  📊 Sensor Data (Bottom Left)                           │
│  - 8 sensor cards                                       │
│  - Alert icons (!)                                      │
│  - Trend chart                                          │
│                                                          │
│                                    🌱 Plant Health       │
│                                    (Bottom Right)        │
│                                    - 5-tier system       │
│                                    - Avg health: 81.2%   │
└─────────────────────────────────────────────────────────┘
```

## Alert Icons Meaning

🔴 **!** = Critical Alert (Red, Pulsing)
- Appears when sensor values are below threshold
- Current alerts:
  - Nitrogen \u003c 50 mg/kg → "Urea required"
  - Moisture \u003c 40% → "Low moisture"

## Widget Controls

### macOS-Style Buttons
🔴 **Red** = Close (not implemented, visual only)
🟡 **Yellow** = Minimize/Expand widget
🟢 **Green** = Maximize (not implemented, visual only)

### Interaction
- **Click Header**: Toggle minimize/expand
- **Click Yellow Button**: Minimize widget
- **Hover**: Visual feedback (lift \u0026 shadow)

## Sensor Thresholds

| Sensor | Current | Threshold | Status |
|--------|---------|-----------|--------|
| Nitrogen | 45 mg/kg | \u003c 50 | ⚠️ LOW |
| Phosphorus | 28 mg/kg | - | ✅ OK |
| Potassium | 120 mg/kg | - | ✅ OK |
| pH | 6.5 | - | ✅ OK |
| Moisture | 35% | \u003c 40 | ⚠️ LOW |
| Temperature | 28°C | - | ✅ OK |
| EC | 1.2 dS/m | - | ✅ OK |
| NDVI | 0.75 | - | ✅ OK |

## Health Status Colors

| Range | Status | Color | Indicator |
|-------|--------|-------|-----------|
| 80-100% | Excellent | 🟢 Green | #1ca053 |
| 65-79% | Good | 🟢 Light Green | #acda55 |
| 50-64% | Fair | 🟡 Orange | #f39c12 |
| 35-49% | Poor | 🟠 Dark Orange | #e67e22 |
| \u003c35% | Critical | 🔴 Red | #e74c3c |

## Weather Data (Simulated)

Updates every 30 seconds with realistic variations:
- **Temperature**: 26-30°C
- **Humidity**: 60-70%
- **Wind Speed**: 10-15 km/h
- **Condition**: Clear, Partly Cloudy, Sunny

## Chart Information

**Type**: Line Chart (Chart.js)
**Datasets**:
1. Nitrogen (Purple #667eea)
2. Moisture (Deep Purple #764ba2)

**Time Range**: Last 6 hours
**Update**: Real-time capable (currently static demo data)

## Keyboard Shortcuts

Currently none implemented. Future suggestions:
- `M` = Toggle all widgets minimize
- `H` = Hide all widgets
- `R` = Refresh data
- `F` = Fullscreen map

## Mobile Responsiveness

Widgets automatically stack and resize on smaller screens:
- **Desktop**: 4 corner positions
- **Tablet**: Stacked on sides
- **Mobile**: Full-width stack

## Performance Tips

1. **Minimize unused widgets** to reduce visual clutter
2. **Chart updates** are lazy-loaded on window load
3. **Weather updates** happen every 30s (can be adjusted)
4. **Clock updates** every 1s (minimal performance impact)

## Troubleshooting

### Widgets not appearing?
- Check browser console for errors
- Ensure JavaScript is enabled
- Try hard refresh (Ctrl+F5)

### Chart not rendering?
- Verify Chart.js CDN is loaded
- Check browser compatibility
- Ensure canvas element exists

### Styling issues?
- Clear browser cache
- Check for CSS conflicts
- Verify Google Fonts loaded

## File Structure

```
IoT project/
├── enhanced_dashboard.html    ← Main dashboard (ENHANCED)
├── DASHBOARD_ENHANCEMENTS.md  ← Full documentation
├── QUICK_REFERENCE.md         ← This file
├── enhance_dashboard.py       ← Enhancement script 1
├── add_widgets.py             ← Enhancement script 2
└── final_enhance.py           ← Final enhancement script
```

## Quick Start

1. Open `enhanced_dashboard.html` in browser
2. Widgets load automatically
3. Click headers to minimize/expand
4. Watch for red (!) alert icons
5. Check chart for trends

## Color Palette Reference

```css
Primary Purple:    #667eea
Secondary Purple:  #764ba2
Success Green:     #1ca053
Light Green:       #acda55
Warning Orange:    #f39c12
Danger Orange:     #e67e22
Critical Red:      #e74c3c
Alert Red:         #ff3b30
Text Dark:         #1a1a1a
Text Medium:       #666666
Text Light:        #999999
```

## Support

For issues or questions:
1. Check `DASHBOARD_ENHANCEMENTS.md` for detailed info
2. Review browser console for errors
3. Verify all CDN resources loaded
4. Check network connectivity for external resources

---

**Quick Tip**: Minimize widgets you don't need to see more of the map!
