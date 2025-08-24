import os
from typing import List, Dict
from app.core.config import settings

def list_local_assets() -> List[str]:
    result = []
    for root, _, files in os.walk(settings.ASSETS_DIR):
        for f in files:
            if f.lower().endswith((".mp4", ".mov", ".mkv", ".jpg", ".jpeg", ".png")):
                result.append(os.path.join(root, f))
    return result

def simple_match_assets(segments: List[Dict]) -> List[str]:
    # A naive matcher: just cycle through available local assets
    assets = list_local_assets()
    if not assets:
        # If no assets present, create placeholder "blank" entries by path-like markers
        return ["" for _ in segments]
    selected = []
    i = 0
    for _ in segments:
        selected.append(assets[i % len(assets)])
        i += 1
    return selected