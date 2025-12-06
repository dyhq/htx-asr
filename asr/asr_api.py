# -*- coding: utf-8 -*-
"""
Created on Wed Nov  5 21:32:09 2025

@author: User
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import librosa
from pydub import AudioSegment
import io
import os
import tempfile

# Initialize FastAPI app
app = FastAPI()

# Load the AI model
print("Loading model...")
MODEL_NAME = "facebook/wav2vec2-large-960h"
processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)
print("Model loaded successfully")


@app.get("/ping")
async def ping():
    """Health check endpoint - returns 'pong' if service is running"""
    return {"message": "pong"}


@app.post("/asr")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe an audio file to text

    Args:
        file: MP3 audio file

    Returns:
        JSON with transcription and duration
    """
    try:
        # Read the uploaded file
        audio_bytes = await file.read()

        # Convert MP3 to WAV format (model needs WAV)
        audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        ) as temp_wav:
            temp_wav_path = temp_wav.name
            audio.export(temp_wav_path, format="wav")

        # Load audio and resample to 16kHz (model requirement)
        speech, sample_rate = librosa.load(temp_wav_path, sr=16000)

        # Calculate duration
        duration = len(speech) / sample_rate

        # Process audio through the model
        inputs = processor(
            speech, sampling_rate=16000, return_tensors="pt", padding=True
        )

        with torch.no_grad():
            logits = model(inputs.input_values).logits

        # Decode the prediction
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]

        # Clean up temporary file
        os.unlink(temp_wav_path)

        return {
            "transcription": transcription,
            "duration": str(round(duration, 1)),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing audio: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
