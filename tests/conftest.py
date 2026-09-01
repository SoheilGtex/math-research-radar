import sys
from pathlib import Path

# [Definitive] Add the FastAPI application path to sys.path
# This allows pytest to import 'app.main' exactly as Uvicorn does in Docker
root_dir = Path(__file__).resolve().parent.parent
fastapi_app_dir = root_dir / "future" / "fastapi"

sys.path.insert(0, str(fastapi_app_dir))