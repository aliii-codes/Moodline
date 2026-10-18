---
title: Moodline
emoji: 🎭
colorFrom: purple
colorTo: pink
sdk: gradio
sdk_version: 6.30.0
python_version: "3.12"
app_file: app.py
pinned: false
---

# Moodline

Type a sentence and a BiGRU model reads the emotion in it: sadness, joy, love, anger, fear, or surprise.

Built with TensorFlow/Keras and FastAPI.

## Run locally

```bash
uv sync
cd src && uv run uvicorn dl_and_nlp_project:app --port 7860
```
