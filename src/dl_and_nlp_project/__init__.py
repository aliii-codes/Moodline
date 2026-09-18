from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from keras.models import load_model
import numpy as np
import pickle
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(BASE_DIR, 'static')

model_path = os.path.join(BASE_DIR, "Artifacts", "BiGRU_Model.keras")
tokenizer_path = os.path.join(BASE_DIR, "Artifacts", "tokenizer.pkl")
max_sequence_length = 50
emotion_labels = ["sadness", "joy", "love", "anger", "fear", "surprise"]

EMOTION_EMOJIS = {
    "sadness": "😢",
    "joy": "😄",
    "love": "❤️",
    "anger": "😠",
    "fear": "😨",
    "surprise": "😲",
}


def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"'", "", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class TextInput(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The sentence to analyze",
        json_schema_extra={"example": "I feel so happy and excited"}
    )


class PredictionResponse(BaseModel):
    text: str
    predicted_emotion: str
    confidence: float
    all_probabilites: dict[str, float]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


dl_model = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    dl_model["BiGRU"] = load_model(model_path)
    with open(tokenizer_path, 'rb') as file:
        dl_model["Tokenizer"] = pickle.load(file)
    yield
    dl_model.clear()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.mount('/static', StaticFiles(directory=static_dir), name="static")


import os

PORT = int(os.environ.get("PORT", 8000))


@app.get('/', include_in_schema=False)
def server_ui():
    return FileResponse('static/index.html')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)


@app.get('/health', response_model=HealthResponse)
def health_check():
    return HealthResponse(status="Server is running", model_loaded=bool(dl_model))


@app.post('/predict', response_model=PredictionResponse)
def predict_emotion(text_input: TextInput):
    BiGRU_model = dl_model.get("BiGRU")
    tokenizer_model = dl_model.get("Tokenizer")

    if BiGRU_model is None or tokenizer_model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded yet. Please try again later.")

    cleaned_text = preprocess_text(text_input.text)

    tokenized_text = tokenizer_model.texts_to_sequences([cleaned_text])
    padded_sequence = pad_sequences(
        tokenized_text,
        maxlen=max_sequence_length,
        padding="post",
        truncating="post"
    )

    probabilites = BiGRU_model.predict(padded_sequence)[0]
    top_emotion_index = int(np.argmax(probabilites))
    all_probabilites = {
        label: float(prob) for prob, label in zip(probabilites, emotion_labels)
    }

    return PredictionResponse(
        text=text_input.text,
        predicted_emotion=emotion_labels[top_emotion_index],
        confidence=float(probabilites[top_emotion_index]),
        all_probabilites=all_probabilites
    )