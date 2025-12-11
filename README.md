# HTX ASR Project

Automatic Speech Recognition (ASR) service with Elasticsearch search backend and web UI.

## Project Overview

This project implements:
- Speech-to-text transcription using Facebook's wav2vec2 model
- RESTful API for audio transcription
- Elasticsearch backend for storing and searching transcriptions
- Web-based search interface for exploring the Common Voice dataset

## Architecture

**Components:**
- ASR API: FastAPI service for audio transcription
- Elasticsearch: 2-node cluster for data storage and search
- Search UI: React-based web interface

## Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Node.js 16+ (for Search UI)
- 8GB RAM minimum (for running ML model)

## Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/dyhq/htx-asr.git
cd htx-asr
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Extract Dataset
Extract Common Voice dataset to project root.

### 4. Run ASR API
```bash
cd asr
python asr_api.py
# API will be available at http://localhost:8001
```

### 5. Process Audio Files
```bash
cd asr
python cv-decode.py
# This will transcribe all audio files and update cv-valid-dev.csv
```

### 6. Start Elasticsearch
```bash
cd elastic-backend
docker-compose up -d
# Wait 30 seconds for cluster to initialize
python cv-index.py
```

### 7. Start Search UI
```bash
cd search-ui
npm install
npm start
# UI will be available at http://localhost:3000
```

## Docker Deployment

Each component can be deployed using Docker Compose:
```bash
# ASR API
cd asr && docker-compose up -d

# Elasticsearch
cd elastic-backend && docker-compose up -d

# Search UI
cd search-ui && docker-compose up -d
```

## API Documentation

### GET /ping
Health check endpoint.

**Response:**
```json
{"message": "pong"}
```

### POST /asr
Transcribe audio file to text.

**Request:**
- Content-Type: multipart/form-data
- Parameter: `file` (audio file in MP3 format)

**Response:**
```json
{
  "transcription": "TRANSCRIBED TEXT HERE",
  "duration": "20.7"
}
```

**Example:**
```bash
curl -F 'file=@audio.mp3' http://localhost:8001/asr
```

## Project Structure
```
htx-asr-project/
├── README.md
├── requirements.txt
├── .gitignore
├── common_voice/
│   ├── cv-valid-dev/
│   └── cv-valid-dev.csv
├── asr/
│   ├── asr_api.py              # FastAPI service
│   ├── cv-decode.py            # Batch transcription script
│   ├── Dockerfile
│   └── docker-compose.yml
├── elastic-backend/
│   ├── docker-compose.yml      # 2-node ES cluster
│   └── cv-index.py             # Data indexing script
├── search-ui/
│   ├── src/
│   │   ├── App.js              # React search interface
│   │   └── index.js
│   ├── Dockerfile
│   └── docker-compose.yml

```

## Troubleshooting

### Model Loading Issues
If the model fails to load due to memory constraints:
```python
# Reduce model memory usage
torch.set_num_threads(2)
```

### Elasticsearch Won't Start
```bash
# Increase vm.max_map_count
sudo sysctl -w vm.max_map_count=262144
```

### CORS Issues
Ensure Elasticsearch has CORS enabled in docker-compose.yml:
```yaml
- http.cors.enabled=true
- http.cors.allow-origin="*"
```

## Acknowledgments

- Facebook AI for wav2vec2 model
- Mozilla Common Voice dataset
- Elastic Search UI components
