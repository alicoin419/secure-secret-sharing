# DPI Awareness and Multi-Monitor Fix

## Problem Solved
The GUI input boxes were disappearing when moving the application window between monitors with different DPI/scaling settings (e.g., from a 27" external monitor to a laptop's main display).

## Solution Implemented
Added comprehensive DPI awareness and multi-monitor support to the tkinter GUI:

### 1. **DPI Awareness Registration**
- `SetProcessDpiAwarenessContext()` - Modern Windows 10+ DPI awareness
- `SetProcessDpiAwareness()` - Fallback for Windows 8.1+
- `SetProcessDPIAware()` - Final fallback for older Windows versions

### 2. **Dynamic Scaling Configuration**
- Force tkinter to use system scaling settings
- Set minimum window size (800x600) to prevent GUI collapse
- Configure automatic font scaling for system compatibility

### 3. **Monitor Change Detection**
- Bind to `<Configure>` events to detect window moves/resizes
- Automatically refresh widget visibility when moving between monitors
- Force geometry updates to maintain proper rendering

### 4. **Widget Refresh System**
- Refresh all sensitive input widgets (text boxes, etc.) after monitor changes
- Call `update_idletasks()` on critical GUI components
- Maintain visibility of secret input areas across DPI changes

## Technical Details
The fix works by:
1. **Prevention**: Making Windows aware the app handles its own DPI scaling
2. **Detection**: Monitoring when the window is moved/reconfigured  
3. **Recovery**: Forcing widget refresh when DPI changes are detected
4. **Fallback**: Graceful degradation if any DPI APIs are unavailable

## Testing
- Works on both high-DPI (laptop) and standard DPI (external monitor) displays
- Input boxes remain visible when dragging between monitors
- No functionality is lost if DPI awareness fails to initialize
- Compatible with Windows Vista through Windows 11

## Files Modified
- `src/gui/main_window.py`: Added `_make_dpi_aware()`, `_configure_dpi_scaling()`, and `_refresh_widget_visibility()` methods

The application now handles multi-monitor setups reliably while maintaining security and usability.
