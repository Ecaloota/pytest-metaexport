import os
from pathlib import Path

from pytest_metaexport.settings import settings

# ensure the cache exists
os.makedirs(settings.cache_dir, exist_ok=True)
os.chmod(settings.cache_dir, 0o755)

PYTEST_METAEXPORT_CACHE = os.path.join(settings.cache_dir, settings.cache_name)

if not os.path.exists(PYTEST_METAEXPORT_CACHE):
    file_path = Path(PYTEST_METAEXPORT_CACHE)
    file_path.touch()

# remove cached images from previous runs, if any
for file in Path(settings.cache_dir).glob("*.png"):
    file.unlink()
