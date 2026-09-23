#!/usr/bin/env python3
"""Image search for Book of Mormon + Lahontan research via Brave's Gemini web photo search.

Fetches real historical maps and images relevant to the transmission hypothesis investigation.
Uses gemini_web_image_search.py from the Brave project.
"""
import sys
import os
from pathlib import Path

# Add brave to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "brave"))

from engine.gemini_web_image_search import search_real_photo

RESEARCH_DIR = Path(__file__).resolve().parent
IMAGE_DIR = RESEARCH_DIR / "research_images"
IMAGE_DIR.mkdir(exist_ok=True)

# Search queries tailored to the research
SEARCH_QUERIES = [
    # Moll maps
    ("Hermann Moll map North America 1720", "01_moll_map_1720.jpg"),
    ("Moll map historical cartography", "02_moll_map_detail.jpg"),

    # Delisle maps
    ("Guillaume Delisle map North America", "03_delisle_map.jpg"),
    ("Delisle cartography 1700s", "04_delisle_cartography.jpg"),

    # Lahontan-related maps
    ("Lahontan map geography", "05_lahontan_map.jpg"),
    ("Lahontan Long River nations map", "06_lahontan_long_river.jpg"),

    # Historical cartography features
    ("18th century North America cardinal direction sea naming", "07_cardinal_seas.jpg"),
    ("Historical map narrow passage land", "08_narrow_passages.jpg"),

    # Book of Mormon geography
    ("Book of Mormon Nephite geography map", "09_bom_geography.jpg"),
    ("Liahona compass Book of Mormon", "10_liahona_compass.jpg"),

    # Period maps
    ("Popple map North America 1740s", "11_popple_map.jpg"),
    ("Senex map North America historical", "12_senex_map.jpg"),

    # Comparison/contextual
    ("River Sidon Book of Mormon", "13_river_sidon.jpg"),
    ("Carver Travels North America", "14_carver_travels.jpg"),
]

def main():
    print(f"[RESEARCH] Fetching historical map images to {IMAGE_DIR}")
    print(f"[RESEARCH] Using Gemini web photo search via port 9225 (Ziggy persona)\n")

    successful = 0
    failed = 0

    for query, filename in SEARCH_QUERIES:
        output_path = IMAGE_DIR / filename

        print(f"[SEARCH] {query}...", end=" ", flush=True)

        try:
            result = search_real_photo(
                query=query,
                save_path=str(output_path),
                port=9225,  # Ziggy persona (from CLAUDE.md reference)
                timeout_s=120
            )

            if result:
                file_size_kb = len(result) / 1024
                print(f"OK ({file_size_kb:.1f} KB)")
                successful += 1
            else:
                print("TIMEOUT/FAILED")
                failed += 1

        except Exception as e:
            print(f"ERROR: {e}")
            failed += 1

    print(f"\n[RESEARCH COMPLETE]")
    print(f"  Successful: {successful}/{len(SEARCH_QUERIES)}")
    print(f"  Failed: {failed}/{len(SEARCH_QUERIES)}")
    print(f"  Images saved to: {IMAGE_DIR}")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
