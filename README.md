# M4 AI Nexus Core

A local, privacy-first **3-tier AI orchestration stack** built for Apple Silicon (M-series Mac). It combines a React dashboard, a .NET gateway, and a Python ML worker to route natural-language requests into image-editing or text-to-SQL workflows — all running on your machine with no cloud dependency.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  React Dashboard          http://localhost:5173                 │
│  Prompt input · Image upload · Mode selection · Result display  │
└──────────────────────────────┬──────────────────────────────────┘
                               │ POST /api/orchestrator/process
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  .NET 9 Gateway               http://localhost:5137             │
│  CORS proxy · MySQL schema fetch · Multipart forwarding         │
└──────────────────────────────┬──────────────────────────────────┘
                               │ POST /orchestrate
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Python FastAPI Worker        http://localhost:8000             │
│  Intent routing · Stable Diffusion inpainting · Text-to-SQL     │
└──────────────┬───────────────────────────────┬──────────────────┘
               │                               │
               ▼                               ▼
   Ollama (Llama 3) :11434          PyTorch MPS · YOLOv8 · Diffusers
```

### Request flow

1. The React UI sends a multipart form request (prompt, mode, optional image) to the .NET gateway.
2. The gateway forwards the payload to the Python worker. For database mode, it attaches a live MySQL schema fetched from `INFORMATION_SCHEMA`.
3. The Python worker classifies intent via Ollama (in auto mode) or uses the explicit mode from the UI.
4. Depending on intent, it runs either the image inpainting pipeline or a Llama 3 text-to-SQL generation step.
5. Results (base64 image or SQL string) are returned through the gateway to the UI.

---

## Features

| Mode | UI label | What it does |
|------|----------|--------------|
| `auto` | Auto Agent | Llama 3 classifies intent as image edit or database query |
| `image` | AI Canvas | YOLOv8 segmentation → face shield → Stable Diffusion inpainting → face restoration |
| `data` | DB Engine | Live MySQL schema + Llama 3 text-to-SQL generation |

### Image editing pipeline

- **YOLOv8 segmentation** — detects the main person and builds an inpainting mask
- **Face shield** — protects the face region from being altered
- **Stable Diffusion inpainting** — applies the user's style/clothing prompt on the masked area
- **Face restoration** — blends the original face back onto the edited image

### Database query pipeline

- .NET reads table/column metadata from the connected MySQL database
- Llama 3 generates an executable SQL query from the user's natural-language question

---

## Project structure

```
AI/
├── react-ai-dashboard/       # React 19 + Vite + Tailwind frontend
│   └── src/App.jsx           # Main dashboard UI
├── DotNetAiOrchestrator/     # .NET 9 Web API gateway
│   ├── Controllers/          # REST endpoints
│   ├── Services/             # Python proxy + MySQL schema fetch
│   └── appsettings.json      # DB connection string
└── python-ai-service/        # FastAPI ML worker
    ├── main.py               # Central /orchestrate endpoint
    ├── config.py             # Device, model paths, inference params
    ├── engines/              # InpaintEngine, LlamaOrchestrator
    └── services/             # Pre/post-processing (YOLO, face restore)
```

---

## Prerequisites

- **macOS** with Apple Silicon (M1/M2/M3/M4) recommended for MPS GPU acceleration
- [Node.js](https://nodejs.org/) 18+
- [.NET 9 SDK](https://dotnet.microsoft.com/download)
- Python 3.10+
- [Homebrew](https://brew.sh/)

External services (local):

| Service | Purpose | Default port |
|---------|---------|--------------|
| [Ollama](https://ollama.com/) | Llama 3 for intent routing and SQL generation | 11434 |
| MySQL | Schema metadata for text-to-SQL (DB mode only) | 3306 |

---

## Installation

### 1. Ollama (LLM engine)

```bash
brew install ollama
brew services start ollama
ollama pull llama3
```

### 2. Python AI worker

```bash
cd python-ai-service
python3 -m venv venv
source venv/bin/activate

pip install fastapi uvicorn httpx pillow torch torchvision diffusers transformers huggingface_hub ultralytics
```

On first run, Stable Diffusion weights are downloaded from Hugging Face. The YOLO model (`yolov8n-seg.pt`) should be present in the project directory.

Start the worker:

```bash
uvicorn main:app --port 8000 --reload
```

### 3. .NET gateway

Update the MySQL connection string in `DotNetAiOrchestrator/appsettings.json` if you plan to use DB mode:

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

The API listens at **http://localhost:5137**.

### 4. React dashboard

```bash
cd react-ai-dashboard
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## Usage

Start all three services (Python → .NET → React) before submitting requests.

### Image edit

1. Select **AI Canvas** (or **Auto Agent** with an image attached).
2. Upload a photo containing a person.
3. Enter a prompt, for example:
   > Transform the casual outfit into an elegant formal navy blue blazer with fine silk texture.
4. Click **Compile & Execute Request**.
5. The edited image appears in the output panel as a base64 render.

### Database query

1. Select **DB Engine** (or **Auto Agent** with a database-related prompt).
2. Ensure MySQL is running and the connection string in `appsettings.json` is correct.
3. Enter a prompt, for example:
   > Find all users who registered in the last 30 days with more than 5 orders.
4. The generated SQL appears in the output panel.

---

## API reference

### .NET gateway

```
POST http://localhost:5137/api/orchestrator/process
Content-Type: multipart/form-data

Fields:
  prompt  (string, required)  — User instruction
  mode    (string, optional)  — "auto" | "image" | "data"  (default: "auto")
  file    (file, optional)    — Image file for inpainting
```

### Python worker (called internally by .NET)

```
POST http://localhost:8000/orchestrate
Content-Type: multipart/form-data

Fields:
  prompt  (string, required)
  mode    (string, optional)
  schema  (string, optional)  — MySQL schema string (injected by .NET for DB mode)
  file    (file, optional)
```

**Response shapes:**

```json
{ "task_id": "uuid", "type": "IMAGE_BASE64", "payload": "<base64 string>" }
```

```json
{ "task_id": "uuid", "type": "DATABASE_SQL", "payload": "SELECT ..." }
```

---

## Configuration

Key settings live in `python-ai-service/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `DEVICE` | `mps` (fallback: `cpu`) | PyTorch execution device |
| `INPAINT_MODEL_PATH` | `runwayml/stable-diffusion-inpainting` | Hugging Face model ID |
| `IMAGE_SIZE` | `512` | Inference resolution |
| `INFERENCE_STEPS` | `35` | Diffusion steps |
| `GUIDANCE_SCALE` | `12.5` | Classifier-free guidance |
| `LLAMA_OLLAMA_URL` | `http://localhost:11434/api/generate` | Ollama API endpoint |

---

## Tech stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 19, Vite 8, Tailwind CSS 4, Lucide icons |
| Gateway | .NET 9, ASP.NET Core Web API, MySql.Data |
| AI Worker | FastAPI, PyTorch (MPS), Diffusers, Ultralytics YOLOv8, Ollama Llama 3 |
| Models | Stable Diffusion Inpainting, YOLOv8n-seg, Llama 3 |

---

## Development notes

- All services communicate over **localhost loopback** — no external API keys required.
- The .NET layer acts as a **gateway and schema provider**; intent classification and ML inference run in Python.
- Image inpainting is memory-intensive. A 5-minute HTTP timeout is configured on the .NET → Python client for long-running generations.
- Temporary output files in `python-ai-service/temp_outputs/` are cleaned up automatically after each request.
- CORS is enabled for `http://localhost:5173` in the .NET gateway.

---

## License

Private project — all rights reserved.
