#!/usr/bin/env python3
"""
Generate rotated versions of Moll 1732 map for cardinal direction hypothesis testing
"""

from PIL import Image
import os
from pathlib import Path

# Map image path
map_path = Path("map_images_david_rumsey_2026-09-24") / "moll_1732" / "moll_1732_full_standard.png"

if not map_path.exists():
    print(f"Error: Map file not found at {map_path}")
    exit(1)

# Load image
print(f"Loading map: {map_path}")
img = Image.open(map_path)
print(f"Original image size: {img.size} (width x height)")

# Create output directory
output_dir = Path("rotation_tests_2026-09-24")
output_dir.mkdir(exist_ok=True)

# Original (no rotation)
print("\nSaving original (standard orientation)...")
original_path = output_dir / "00_original_standard_orientation.png"
img.save(original_path)
print(f"  Saved: {original_path}")

# 90° clockwise rotation
print("\nGenerating 90° clockwise rotation (East becomes North)...")
rotated_90cw = img.rotate(-90, expand=True)  # -90 for clockwise in PIL
cw_path = output_dir / "01_rotated_90cw_east_becomes_north.png"
rotated_90cw.save(cw_path)
print(f"  Saved: {cw_path}")
print(f"  Size after rotation: {rotated_90cw.size}")

# 90° counterclockwise rotation
print("\nGenerating 90° counterclockwise rotation (West becomes North)...")
rotated_90ccw = img.rotate(90, expand=True)  # +90 for counterclockwise in PIL
ccw_path = output_dir / "02_rotated_90ccw_west_becomes_north.png"
rotated_90ccw.save(ccw_path)
print(f"  Saved: {ccw_path}")
print(f"  Size after rotation: {rotated_90ccw.size}")

# 180° rotation
print("\nGenerating 180° rotation (complete inversion)...")
rotated_180 = img.rotate(180, expand=True)
rot180_path = output_dir / "03_rotated_180_complete_inversion.png"
rotated_180.save(rot180_path)
print(f"  Saved: {rot180_path}")
print(f"  Size after rotation: {rotated_180.size}")

print("\n" + "="*70)
print("ROTATION TESTS COMPLETE")
print("="*70)
print(f"\nGenerated files in: {output_dir.resolve()}")
print("\nFor hypothesis testing:")
print("  00_original = Standard orientation (North at top)")
print("  01_rotated_90cw = Rivers flowing N-S now appear E-W")
print("  02_rotated_90ccw = Alternative E-W river orientation")
print("  03_rotated_180 = Complete mirror image (South at top)")

print("\nNext: Visually compare each rotated version against BoM geographic requirements:")
print("  1. Does river now flow E-W?")
print("  2. Do territorial divisions now orient N-S?")
print("  3. Does narrow passage now separate N-S regions?")
print("  4. Do coastal cities align with rotated geography?")

