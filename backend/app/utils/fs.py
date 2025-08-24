import os
from app.core.config import settings

def ensure_storage_dirs():
    for d in [settings.STORAGE_ROOT, settings.ASSETS_DIR, settings.OUTPUTS_DIR, settings.SRT_DIR, settings.COVERS_DIR]:
        os.makedirs(d, exist_ok=True)