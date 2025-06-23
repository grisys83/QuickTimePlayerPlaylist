# ROI-Based AirPlay Detection

## Overview

The ROI (Region of Interest) based detection approach solves the problem of checkbox detection being confused by menu bar icons. Instead of searching the entire screen, we use a hierarchical approach:

1. Find AirPlay icon
2. Define ROI where menu should appear (above the icon)
3. Find Apple TV text within ROI
4. Define smaller ROI around Apple TV text
5. Find checkbox within that smaller ROI

## Coordinate System

**Important**: CV2 uses a different coordinate system than macOS:
- CV2: Y=0 at TOP, Y increases DOWNWARD
- macOS: Different, and Retina displays have 2x scaling

The `CoordinateConverter` handles this automatically.

## Testing

### Quick Test
```bash
python3 test_roi_detection.py
```

### Comprehensive Test Suite
```bash
python3 test_airplay_detectors.py
```

### Visual Detector V2 (Most Thorough)
```bash
python3 visual_airplay_detector_v2.py
```

## Debug Images

Debug images are saved to:
- `~/airplay_debug/` - CV2 enabler images
- `./debug_output_v2/` - Visual detector V2 images

The images show:
1. Full menu screenshot
2. ROI visualization (green box)
3. Extracted ROI
4. Apple TV text detection
5. Checkbox ROI (purple box)
6. Extracted checkbox area
7. Final detection result

## ROI Logic

### Menu ROI
- **Width**: 300 pixels (150 left/right of AirPlay)
- **Height**: 280 pixels (from 300 above to 20 above AirPlay)
- **Why**: AirPlay menu appears above the icon

### Checkbox ROI
- **Width**: 80 pixels (100 to 20 pixels left of Apple TV text)
- **Height**: 40 pixels (20 above/below Apple TV text)
- **Why**: Checkbox is always to the left of the text

## Troubleshooting

### "ROI is empty"
- QuickTime window may be too close to top of screen
- Try moving window down

### "Apple TV not found in ROI"
- Menu may not be open
- Apple TV template may need updating
- Check debug image #3 to see what's in the ROI

### "Checkbox not found"
- Checkbox may be checked already
- Template may need updating
- Check debug image #6 to see checkbox area

## Implementation Files

- `cv2_airplay_enabler.py` - Main implementation with ROI approach
- `visual_airplay_detector_v2.py` - Interactive detector with user confirmation
- `coordinate_converter.py` - Handles CV2/screen coordinate conversion
- `test_airplay_detectors.py` - Test suite for all approaches