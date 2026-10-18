# Entry point for the Hugging Face Space: serves the FastAPI app (UI + API) on port 7860
import os
import sys

# ZeroGPU Spaces must register at least one @spaces.GPU function at startup.
# The model runs on CPU, so this placeholder is never called.
import spaces


@spaces.GPU
def _zerogpu_placeholder():
    pass


sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import uvicorn
from dl_and_nlp_project import app

if __name__ == "__main__":
    # spaces normally reports startup from inside gr.Blocks.launch(); we serve
    # with uvicorn instead, so trigger that report ourselves.
    zerogpu_startup = getattr(spaces.zero, "startup", None)
    if zerogpu_startup is not None:
        zerogpu_startup()
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
