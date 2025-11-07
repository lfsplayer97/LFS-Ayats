# HTML Interfaces Documentation

## Overview

LFS Ayats provides multiple web-based interfaces for telemetry visualization and configuration. All interfaces support internationalization (i18n) with Catalan and English languages.

## Available Interfaces

### 1. Dashboard (dashboard.html)

**Purpose**: Real-time telemetry dashboard with WebSocket connection to the Python backend.

**Features**:
- Live WebSocket connection to telemetry server (default: ws://127.0.0.1:30333)
- Real-time display of:
  - Speed (km/h)
  - RPM
  - Current gear
  - Lap number
  - Lap time
  - Delta vs personal best
- Proximity radar visualization using Canvas
  - Shows nearby vehicles with distance and bearing
  - Visual representation of surrounding traffic
- Lap history tracking
- Multi-language support (Catalan/English)
- Connection status indicators
- Modern, responsive design

**Usage**:
1. Start the Python backend: `python main.py`
2. Open `dashboard.html` in a web browser
3. Click "Connect" to establish WebSocket connection
4. Data will update in real-time as you drive in LFS

**WebSocket Data Format**:
The dashboard expects JSON data with the following structure:
```json
{
  "timestamp": 1234567890.123,
  "player": {
    "speed": 45.5,
    "lap": {
      "number": 3,
      "current_ms": 65432,
      "progress": 0.45
    },
    "lap_time_ms": 65432,
    "delta_ms": -125,
    "radar_targets": [
      {
        "distance": 25.5,
        "bearing": 0.523,
        "offset": {"x": 10.2, "y": 22.8}
      }
    ]
  }
}
```

---

### 2. Configuration (config.html)

**Purpose**: Visual configuration editor for all LFS Ayats settings.

**Features**:
- **Radar Settings**:
  - Enable/disable radar display
  
- **Beep Settings**:
  - Enable/disable audio beeps
  - Beep mode selection (Standard/Calm/Aggressive)
  - Volume control (0.0 - 1.0)
  - Base frequency adjustment (Hz)
  - Custom interval patterns (milliseconds)
  
- **InSim Settings**:
  - Host configuration
  - Port configuration
  
- **OutSim Settings**:
  - Port configuration
  
- **WebSocket Telemetry**:
  - Enable/disable telemetry server
  - Port configuration
  - Update rate (Hz)
  
- **Live JSON Preview**: Real-time preview of configuration
- **Export Functionality**: Download config.json file
- **Import/Reset**: Load saved settings or reset to defaults
- Multi-language support

**Usage**:
1. Open `config.html` in a web browser
2. Adjust settings as desired
3. Click "Save Configuration" to download config.json
4. Place config.json in the application root directory
5. Restart the Python backend to apply changes

**Configuration File**:
The generated config.json is compatible with the Python backend and follows this structure:
```json
{
  "insim": {
    "host": "127.0.0.1",
    "port": 29999,
    "admin_password": "",
    "interval_ms": 100,
    "timeout": 0.1
  },
  "outsim": {
    "port": 30000,
    "update_hz": 60,
    "allowed_sources": ["127.0.0.1"],
    "max_packets_per_second": 120.0
  },
  "telemetry_ws": {
    "enabled": true,
    "host": "127.0.0.1",
    "port": 30333,
    "update_hz": 15.0
  },
  "sp_radar_enabled": true,
  "sp_beeps_enabled": true,
  "mp_radar_enabled": true,
  "mp_beeps_enabled": false,
  "beep": {
    "mode": "standard",
    "volume": 0.6,
    "base_frequency_hz": 880.0,
    "intervals_ms": [400, 600]
  }
}
```

---

### 3. Simple Interface (simple.html)

**Purpose**: Minimalist telemetry display with WebSocket support.

**Features**:
- Clean, dark-themed interface
- WebSocket connection with configurable URL
- Essential telemetry display:
  - Speed (km/h)
  - Current gear
  - Lap number
  - Delta time
- Connection status with visual feedback
- Error handling and reconnection support

**Usage**:
1. Start the Python backend
2. Open `simple.html` in a web browser
3. Optionally modify the WebSocket URL
4. Click "CONNECTAR" to connect
5. View real-time telemetry data

**Ideal For**:
- Users who want a clean, minimal interface
- Secondary displays or overlays
- Testing WebSocket connections

---

### 4. Portal (index.html)

**Purpose**: Main entry point with navigation to all interfaces.

**Features**:
- Overview of all available applications
- Quick navigation to any interface
- Recommendations for new users
- Modern card-based design

**Applications Listed**:
- Dashboard Telemetria (New!)
- Configuració (New!)
- Versió Simple (Improved!)
- Demo i18n
- Aplicació Clàssica
- LFS Pro

---

## Internationalization (i18n)

All interfaces support multiple languages through the i18n system:

**Supported Languages**:
- Catalan (ca) - Default
- English (en)

**Language Files**:
- `i18n/ca.json` - Catalan translations
- `i18n/en-US.json` - English translations

**Adding New Languages**:
1. Create a new JSON file in the `i18n/` directory
2. Copy the structure from `en-US.json`
3. Translate all values
4. Add language option to HTML files' language selector

**Translation Keys**:
- `app.*` - Application information
- `common.*` - Common actions (connect, disconnect, save, etc.)
- `dashboard.*` - Dashboard-specific text
- `connection.*` - Connection status messages
- `telemetry.*` - Telemetry data labels
- `radar.*` - Radar-related text
- `config.*` - Configuration interface text

---

## Technical Details

### WebSocket Protocol

**Server Endpoint**: `ws://127.0.0.1:30333` (configurable)

**Message Format**: JSON

**Update Frequency**: 15 Hz (configurable in telemetry_ws.update_hz)

**Connection States**:
- `ready` - Ready to connect
- `connecting` - Connection in progress
- `connected` - Active connection
- `error` - Connection error

### Radar Visualization

The radar uses HTML5 Canvas to render:
- Concentric circles representing distance (25m, 50m, 75m, 100m)
- Crosshair for orientation
- Player position at center (green dot)
- Nearby vehicles as colored dots:
  - Red: < 20m (close proximity)
  - Orange: ≥ 20m (safe distance)
- Distance labels for each target

**Coordinate System**:
- Origin at player position
- Y-axis points forward (player heading)
- X-axis points right
- Scale: 1 pixel = 1 meter (up to 100m radius)

### Browser Compatibility

**Minimum Requirements**:
- Modern browser with ES6 support
- WebSocket support
- HTML5 Canvas support

**Tested Browsers**:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera GX

**Not Supported**:
- Internet Explorer (any version)
- Browsers with WebSocket disabled

---

## Development

### File Structure

```
/
├── dashboard.html          # Real-time telemetry dashboard
├── config.html            # Configuration editor
├── simple.html            # Minimalist interface
├── working.html           # Connection test page
├── index.html             # Main portal
├── i18n/
│   ├── ca.json           # Catalan translations
│   └── en-US.json        # English translations
└── docs/
    └── HTML_INTERFACES.md # This file
```

### Code Style

**HTML**:
- UTF-8 encoding
- Self-contained files (inline CSS and JavaScript)
- Responsive design with CSS Grid/Flexbox
- Semantic HTML5 elements

**CSS**:
- Modern CSS (no IE compatibility needed)
- CSS custom properties for theming
- Mobile-first responsive design
- Consistent color scheme across interfaces

**JavaScript**:
- Vanilla JavaScript (no frameworks)
- ES6+ syntax
- Clear separation of concerns
- Comprehensive error handling
- Console logging for debugging

### Adding New Features

1. **Add Translations**: Update `i18n/ca.json` and `i18n/en-US.json`
2. **Update HTML**: Add new elements with `data-i18n` attributes
3. **Add Functionality**: Implement JavaScript handlers
4. **Test**: Verify in multiple browsers and languages
5. **Document**: Update this file with new features

---

## Troubleshooting

### Connection Issues

**Problem**: "Connection error" or "Failed to connect"
- **Solution**: Ensure Python backend is running (`python main.py`)
- **Solution**: Check WebSocket port matches config (default: 30333)
- **Solution**: Verify firewall allows WebSocket connections

**Problem**: "No data received"
- **Solution**: Ensure LFS is running with InSim/OutSim enabled
- **Solution**: Check LFS configuration matches config.json
- **Solution**: Verify you're in a car and on track

### Display Issues

**Problem**: Radar not showing vehicles
- **Solution**: Ensure other cars are nearby (< 100m)
- **Solution**: Check browser console for errors
- **Solution**: Verify radar is enabled in configuration

**Problem**: Translations not working
- **Solution**: Check browser console for i18n errors
- **Solution**: Verify language files are accessible
- **Solution**: Clear browser cache and reload

### Performance Issues

**Problem**: Laggy updates or high CPU usage
- **Solution**: Reduce telemetry update rate in config.html
- **Solution**: Close unnecessary browser tabs
- **Solution**: Disable browser extensions

---

## Screenshots

### Dashboard
![Dashboard Screenshot](https://github.com/user-attachments/assets/a7d84c64-5da0-44e4-8c89-5c441edf76ec)

### Configuration
![Config Screenshot](https://github.com/user-attachments/assets/0f72eb35-aada-4630-8cff-1c7111b8cab9)

### Simple Interface
![Simple Screenshot](https://github.com/user-attachments/assets/57b3c159-b27a-402e-a5e4-c4f741a50238)

### Portal
![Portal Screenshot](https://github.com/user-attachments/assets/39abe7b7-8721-4ec3-9c0f-3ec370026bbd)

---

## Future Enhancements

Potential improvements for future versions:

1. **Historical Data**: Graph lap times over sessions
2. **Track Maps**: Display player position on track layout
3. **Setup Comparison**: Compare car setups and performance
4. **Multiplayer Features**: Show other players' data
5. **Mobile App**: Native mobile application
6. **Dark/Light Themes**: User-selectable themes
7. **Custom Layouts**: Drag-and-drop widget arrangement
8. **Data Export**: Export telemetry to CSV/JSON
9. **Voice Alerts**: Spoken warnings and information
10. **VR Support**: Virtual reality dashboard overlay

---

## License

See main project LICENSE file.

## Credits

Part of the LFS Ayats project - Real-time telemetry system for Live for Speed.
