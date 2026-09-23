#!/usr/bin/env python3
"""Queue research images via Brave's IMAGE_FETCH_COORDINATOR.

Adds image requests to the coordinator's queue for the IMAGE_FETCH_AGENT_POOL to process.
The pool will fetch high-quality images when Muse personas are running.
"""
import sys
import os
from pathlib import Path

# Add brave to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "brave"))

from IMAGE_FETCH_COORDINATOR import ImageFetchCoordinator

RESEARCH_QUERIES = [
    # Moll maps - HIGH PRIORITY
    ("Hermann Moll map North America 1709-1740", "book-of-mormon-research/moll-maps", "HIGH", 1280, 720),
    ("Guillaume Delisle map North America 1700 Lahontan", "book-of-mormon-research/delisle-maps", "HIGH", 1280, 720),
    ("Lahontan Long River nations cardinal direction sea naming", "book-of-mormon-research/lahontan-geography", "HIGH", 1280, 720),

    # Historical cartography
    ("18th century colonial North America map rivers territorial divisions", "book-of-mormon-research/colonial-maps", "NORMAL", 1280, 720),
    ("Historical narrow passage isthmus North America map", "book-of-mormon-research/narrow-passages", "NORMAL", 1280, 720),

    # Comparative geography
    ("Book of Mormon Nephite Lamanite territorial geography map", "book-of-mormon-research/bom-geography", "NORMAL", 1280, 720),
    ("Liahona compass Book of Mormon spiritual navigation instrument", "book-of-mormon-research/liahona", "LOW", 800, 600),
]

def main():
    coordinator = ImageFetchCoordinator()

    print("[QUEUE] Adding research image requests to IMAGE_FETCH_COORDINATOR")
    print(f"[QUEUE] Queue file: {coordinator.queue_file}\n")

    for i, (prompt, subdir, priority, width, height) in enumerate(RESEARCH_QUERIES, 1):
        request_id = coordinator.add_image_request(
            project="book-of-mormon-research",
            prompt=prompt,
            priority=priority,
            width=width,
            height=height,
            provider="gemini-web",
            output_subdir=subdir,
            deadline_minutes=480,  # 8 hour deadline
        )
        print(f"  [{i:2d}] {priority:6s} | {prompt[:70]}...")

    stats = coordinator.get_stats()
    print(f"\n[QUEUE COMPLETE]")
    print(f"  Total pending: {stats['pending']}")
    print(f"  By priority: {stats['by_priority']}")
    print(f"\n[NEXT STEP] Start IMAGE_FETCH_AGENT_POOL when ready:")
    print(f"  cd C:\\projects\\brave")
    print(f"  python IMAGE_FETCH_AGENT_POOL.py")
    print(f"\n[NOTE] Requires Muse persona browser with open Gemini tab (port 9225/9226/etc)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
