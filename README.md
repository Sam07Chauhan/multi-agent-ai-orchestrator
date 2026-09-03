# M4 AI Nexus Core

A local, privacy-first **3-tier AI orchestration stack** built for Apple Silicon (M-series Mac). It combines a modular React conversational chat dashboard, a .NET 9 gateway, and a Python ML worker to route natural-language requests into image-editing, computer-vision analysis, or text-to-SQL workflows — all running locally on your machine with no cloud dependencies or API subscription costs.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  React Chat Dashboard     http://localhost:5173                 │
│  Conversation feed · Multi-mode selector · Image upload & render│
└──────────────────────────────┬──────────────────────────────────┘
                               │ POST /api/orchestrator/process
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  .NET 9 Gateway               http://localhost:5137             │
│  CORS proxy · MySQL schema fetch · Multipart stream forwarding  │
└──────────────────────────────┬──────────────────────────────────┘
                               │ POST /orchestrate
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Python FastAPI Worker        http://localhost:8000             │
│  Intent routing · SD Inpainting · MediaPipe/YOLO CV · Text-to-SQL│
└──────────────┬───────────────────────────────┬──────────────────┘
               │                               │
               ▼                               ▼
   Ollama (Llama 3) :11434          PyTorch MPS · YOLOv8 · Compel · MediaPipe
```

### Request flow

1. The React UI sends a multipart request (`prompt`, `mode`, optional `file`) via `src/services/api.js` to the .NET gateway.
2. The .NET gateway injects live relational MySQL schema metadata (from `INFORMATION_SCHEMA`) for database queries and forwards the request to the Python AI worker.
3. The Python worker routes requests either explicitly or dynamically using local Llama 3 intent classification.
4. Depending on intent, it executes:
   - **Stable Diffusion inpainting** with Compel multi-chunk embedding support (handles 1000+ words).
   - **Computer Vision Analysis** (Face & Hand landmarks, Body Pose, Object Dimensions, or CLIP Zero-Shot Classification).
   - **Text-to-SQL Generation** using Llama 3 and live schema context.
5. Structured results (Base64 image, SQL string, or analysis metrics) flow back through the gateway into the React conversational feed.

---

## Features & Orchestration Modes

| Mode | UI Label | Capabilities |
|------|----------|--------------|
| `auto` | Auto Agent | Llama 3 automatically classifies intent (Edit, Analyze, or Database Query). |
| `image` | AI Canvas | YOLOv8 segmentation → Face shield → Compel multi-chunk SD Inpainting → Face restoration. |
| `image_analysis` | Analyze | MediaPipe Tasks (Face/Hand mesh) + YOLOv8 (Pose/Objects) + CLIP Zero-Shot building classifier. |
| `data` | DB Engine | Live MySQL schema extraction + Llama 3 natural language text-to-SQL generator. |

### 1. Image Editing Pipeline (`image`)
- **YOLOv8 segmentation** — Segments the person and synthesizes an accurate inpainting mask.
- **Face shield protection** — Extracts and shields the facial bounding box to avoid unintended distortions.
- **Compel Multi-Chunk Inpainting** — Overcomes standard 77-token limits, encoding long 1000+ word prompts into concatenated CLIP cross-attention embeddings without data loss.
- **Face restoration & dimension finalization** — Restores the original face seamlessly onto the newly synthesized clothing/scene.

### 2. Computer Vision Analysis Pipeline (`image_analysis`)
- **Face Landmarks** — Uses MediaPipe Tasks `FaceLandmarker` to measure facial proportions, jaw width, and eye distance.
- **Hand Landmarks** — Uses MediaPipe Tasks `HandLandmarker` for palm width, finger lengths, and handedness.
- **Body Pose & Proportions** — Uses YOLOv8-pose to compute shoulder-to-hip ratios and posture balance.
- **Object Dimensions** — Uses YOLOv8 object detection for aspect ratios and bounding box sizing.
- **Structure Classification** — Zero-shot architectural style classification via OpenAI CLIP.

### 3. Database Query Pipeline (`data`)
- Reads schema definitions directly from MySQL `INFORMATION_SCHEMA.COLUMNS`.
- Prompts local Llama 3 to output executable raw SQL without hallucinating nonexistent tables or columns.

---

## Project Structure

```
AI/
├── react-ai-dashboard/           # React 19 + Vite + Tailwind CSS Frontend
│   ├── src/
│   │   ├── components/           # Modular UI Components
│   │   │   ├── Header.jsx        # App header & status badge
│   │   │   ├── ChatEmptyState.jsx# Quick preset suggestions
│   │   │   ├── ChatMessage.jsx   # Polymorphic chat bubble renderer
│   │   │   └── ChatInput.jsx     # Bottom prompt bar & mode pills
│   │   ├── services/
│   │   │   └── api.js            # Dedicated HTTP client for .NET Gateway
│   │   ├── App.jsx               # Main state orchestrator & message history
│   │   └── main.jsx
├── DotNetAiOrchestrator/         # .NET 9 ASP.NET Core Web API Gateway
│   ├── Controllers/
│   │   └── OrchestratorController.cs # Multipart REST endpoint
│   ├── Services/
│   │   └── AiOrchestratorService.cs  # MySQL schema fetcher & Python proxy
│   └── appsettings.json          # Database connection strings
└── python-ai-service/            # FastAPI ML Worker
    ├── main.py                   # Central /orchestrate API endpoint
    ├── config.py                 # Device configs, MPS settings, inference parameters
    ├── engines/
    │   ├── inpaint.py            # Compel-powered Stable Diffusion inpainting
    │   ├── analysis.py           # MediaPipe Tasks, YOLOv8 Pose, CLIP analyzers
    │   ├── text_enhancer.py      # Ollama Llama 3 intent & SQL generator
    │   └── prompt_utils.py       # Multi-chunk token budget manager
    ├── models/                   # Local MediaPipe task asset cache
    └── services/
        ├── pre_process.py        # Segmentation & mask generation
        └── post_process.py       # Face recovery & dimension finalization
```

---

## Prerequisites

- **macOS** with Apple Silicon (M1/M2/M3/M4) recommended for MPS GPU acceleration
- [Node.js](https://nodejs.org/) 18+
- [.NET 9 SDK](https://dotnet.microsoft.com/download)
- Python 3.10+
- [Homebrew](https://brew.sh/)

External services (local):

| Service | Purpose | Default Port |
|---------|---------|--------------|
| [Ollama](https://ollama.com/) | Llama 3 for routing and SQL generation | 11434 |
| MySQL | Schema metadata for text-to-SQL (DB mode) | 3306 |

---

## Installation & Setup

### 1. Ollama (LLM Engine)

```bash
brew install ollama
brew services start ollama
ollama pull llama3
```

### 2. Python AI Worker

```bash
cd python-ai-service
python3 -m venv venv
source venv/bin/activate

pip install fastapi uvicorn httpx pillow torch torchvision diffusers transformers huggingface_hub ultralytics compel mediapipe
```

Start the FastAPI worker:

```bash
uvicorn main:app --port 8000 --reload
```

### 3. .NET Gateway

Update the MySQL connection string in `DotNetAiOrchestrator/appsettings.json` if using DB mode:

```json
"ConnectionStrings": {
  "DefaultConnection": "Server=localhost;Port=3306;Database=YourAiProjectDb;Uid=root;Pwd=YourPassword;"
}
```

Then build and run:

```bash
cd DotNetAiOrchestrator
dotnet restore
dotnet run
```
The gateway listens at **http://localhost:5137**.

### 4. React Dashboard

```bash
cd react-ai-dashboard
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## API Reference

### .NET Gateway
```http
POST http://localhost:5137/api/orchestrator/process
Content-Type: multipart/form-data

Fields:
  prompt  (string, required)  — User instruction query
  mode    (string, optional)  — "auto" | "image" | "image_analysis" | "data"
  file    (file, optional)    — Image file for inpainting or analysis
```

### Python Worker (Internal)
```http
POST http://localhost:8000/orchestrate
Content-Type: multipart/form-data

Fields:
  prompt  (string, required)
  mode    (string, optional)
  schema  (string, optional)  — Live MySQL schema context
  file    (file, optional)
```

**Response Payloads:**

*Image Generation:*
```json
{ "task_id": "uuid", "type": "IMAGE_BASE64", "payload": "<base64 string>" }
```

*Text-to-SQL:*
```json
{ "task_id": "uuid", "type": "DATABASE_SQL", "payload": "SELECT ..." }
```

*Image Analysis:*
```json
{
  "task_id": "uuid",
  "type": "IMAGE_ANALYSIS",
  "payload": {
    "summary": "...",
    "face_detected": true,
    "face_length_to_width_ratio": 1.35
  }
}
```

---

## Configuration Settings

Key configuration variables in `python-ai-service/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `DEVICE` | `mps` (fallback: `cpu`) | PyTorch execution device for Apple Silicon |
| `INPAINT_MODEL_PATH` | `runwayml/stable-diffusion-inpainting` | Hugging Face inpainting weights |
| `IMAGE_SIZE` | `512` | Inference generation resolution |
| `INFERENCE_STEPS` | `35` | Diffusion denoising step count |
| `GUIDANCE_SCALE` | `8.5` | Classifier-free guidance prompt adherence scale |
| `LLAMA_OLLAMA_URL` | `http://localhost:11434/api/generate` | Local Ollama endpoint |

---

## License

Private project — all rights reserved.
