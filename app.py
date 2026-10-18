# Entry point for the Hugging Face Space: serves the FastAPI app (UI + API) on port 7860
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import uvicorn
from dl_and_nlp_project import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
