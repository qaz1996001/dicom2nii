#### `.cursor/rules/medical-reformatted-detection.md`
```markdown
description: REFORMATTED medical image detection and processing rules
globs: "**/processing/**/*.py", "**/strategies/**/*.py"
priority: critical
category: medical-accuracy
alwaysApply: true
---

# Medical REFORMATTED Detection Rules

## MANDATORY REFORMATTED Check
Every medical imaging strategy MUST check for REFORMATTED images:

```python
# ✅ MANDATORY: Always check REFORMATTED status
def get_image_orientation_with_reformatted(dicom_ds: DicomDataset) -> ImageOrientation:
    """Get image orientation with REFORMATTED detection - MANDATORY"""
    # Early Return - Check required tags
    image_type = dicom_ds.get((0x08, 0x08))
    if not image_type or len(image_type.value) < 3:
        return get_basic_orientation(dicom_ds)
    
    # MANDATORY: Check REFORMATTED status
    is_reformatted = image_type.value[2] == 'REFORMATTED'
    base_orientation = get_basic_orientation(dicom_ds)
    
    if is_reformatted:
        # MANDATORY: Map to reformatted orientation
        reformatted_map = {
            ImageOrientationEnum.AXI: ImageOrientationEnum.AXIr,
            ImageOrientationEnum.SAG: ImageOrientationEnum.SAGr,
            ImageOrientationEnum.COR: ImageOrientationEnum.CORr,
        }
        return reformatted_map.get(base_orientation, base_orientation)
    
    return base_orientation

# ✅ MANDATORY: Support all REFORMATTED variants
T1_REFORMATTED_SEQUENCES = {
    'T1CUBE_AXIr', 'T1CUBE_CORr', 'T1CUBE_SAGr',
    'T1CUBECE_AXIr', 'T1CUBECE_CORr', 'T1CUBECE_SAGr',
    'T1FLAIRCUBE_AXIr', 'T1FLAIRCUBE_CORr', 'T1FLAIRCUBE_SAGr',
    'T1FLAIRCUBECE_AXIr', 'T1FLAIRCUBECE_CORr', 'T1FLAIRCUBECE_SAGr',
    'T1BRAVO_AXIr', 'T1BRAVO_SAGr', 'T1BRAVO_CORr',
    'T1BRAVOCE_AXIr', 'T1BRAVOCE_SAGr', 'T1BRAVOCE_CORr',
}

T2_REFORMATTED_SEQUENCES = {
    'T2CUBE_AXIr', 'T2CUBE_CORr', 'T2CUBE_SAGr',
    'T2CUBECE_AXIr', 'T2CUBECE_CORr', 'T2CUBECE_SAGr',
    'T2FLAIRCUBE_AXIr', 'T2FLAIRCUBE_CORr', 'T2FLAIRCUBE_SAGr',
    'T2FLAIRCUBECE_AXIr', 'T2FLAIRCUBECE_SAGr', 'T2FLAIRCUBECE_CORr',
}
```
