# -*- coding: utf-8 -*-
"""
Created on Sat Nov  8 16:36:30 2025

@author: User
"""

import requests
import pandas as pd
import os
from tqdm import tqdm
import time

# Configuration
API_URL = "http://localhost:8001/asr"
CSV_FILE = "../common_voice/cv-valid-dev.csv"
AUDIO_DIR = "../common_voice/cv-valid-dev/"


def transcribe_file(audio_path):
    """Send audio file to API and get transcription"""
    try:
        with open(audio_path, "rb") as f:
            files = {"file": f}
            response = requests.post(API_URL, files=files, timeout=60)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error processing {audio_path}: {str(e)}")
        return None


def main():
    # Load csv file
    df = pd.read_csv(CSV_FILE)
    print(f"Loaded {len(df)} records from CSV")

    # Add new column for generated text
    df["generated_text"] = ""

    # Process each audio file
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        audio_filename = row["filename"]
        audio_path = os.path.join(AUDIO_DIR, audio_filename)

        if not os.path.exists(audio_path):
            print(f"File not found: {audio_path}")
            continue

        # Call API
        result = transcribe_file(audio_path)

        if result:
            df.at[idx, "generated_text"] = result["transcription"]

        # Small delay to avoid overwhelming the API
        time.sleep(0.1)

        # Save progress every 100 files
        if idx % 100 == 0:
            df.to_csv(CSV_FILE, index=False)
            print(f"Progress saved at {idx} files.")

    # Final save
    df.to_csv(CSV_FILE, index=False)
    print(f"Completed. Results saved to {CSV_FILE}.")


if __name__ == "__main__":
    main()
