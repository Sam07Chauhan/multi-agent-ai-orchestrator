🧠 M4 AI Nexus Core: Multi-Agent AI Orchestrator
A distributed, 3-tier multi-agent orchestration mesh designed for native high-performance execution on Apple Silicon (Mac M4/M-Series). This ecosystem leverages a polyglot microservice architecture combining a high-throughput React UI frontend, a robust .NET 8 routing core, and an optimized Python FastAPI machine learning execution layer utilizing Metal Performance Shaders (MPS).

🏗️ System Architecture & Modalities
The system operates across three fully isolated operational layers communicating via secure local loopback interfaces:

Frontend Layer (React 18 + Vite - Port 5173): A modern, dark-themed asynchronous terminal workspace. It captures text prompts, visual context references (image inputs), and relational database schemas.

Orchestration Layer (.NET 8 Web API - Port 5137): The central decision-making engine. It routes workflows by parsing incoming payloads and using an isolated OllamaSharp client to tap into a local Llama 3 instance (Port 11434) for real-time intent analysis.

AI Worker Layer (FastAPI + PyTorch - Port 8000): An optimized execution core that maps machine learning workloads directly onto the Apple Silicon Neural Core/GPU using the mps execution device context (Stable Diffusion v1.5 / Pix2Pix).

🛠️ Infrastructure Setup & Installation
1. Prerequisites (macOS Environment)
Ensure Node.js and Homebrew are active on your system. Install the system-level LLM engine:

Bash
# Install and initialize the local Ollama daemon
brew install ollama
brew services start ollama

# Pull the core routing model
ollama run llama3
2. Worker Layer Setup (Python FastAPI)
Configure the localized environment wrapper and install optimized matrix-computation pipelines:

Bash
cd python-ai-service
python3 -m venv venv
source venv/bin/activate

# Install native PyTorch with Apple Silicon optimization layers
pip install fastapi uvicorn torch torchvision diffusers transformers huggingface_hub requests urllib3
Launch the operational worker pool:

Bash
uvicorn main:app --port 8000 --reload
3. Core Router Setup (.NET 8 API)
Restore dependencies and initialize the core C# gateway configuration:

Bash
cd DotNetAiOrchestrator
dotnet restore
dotnet build
dotnet run
Note: The orchestrator hosts its REST bindings at http://localhost:5137.

4. Client Dashboard Setup (React Application)
Ensure system-level directory path permissions are mapped to prevent file blocking errors:

Bash
cd react-ai-dashboard
npm install
npm run dev
🏎️ Verification Matrix (Testing Prompts)
Once all tiers are live, test the system routes directly through the React workspace input:

IMAGE_CREATE Route:

Prompt: "Generate a futuristic cyberpunk city covered in heavy snow at night, glowing neon lights."

Behavior: .NET intercepts prompt -> Llama 3 classifies it as generation task -> Dispatches to FastAPI pipeline on Mac M4 GPU.

Payload: High-definition Base64 image payload rendered natively inside chat timeline.

IMAGE_EDIT Route:

Prompt: Attach Photo + "Make it look like a vintage oil painting from the 1800s."

Behavior: .NET checks structural file stream context validation -> Confirms file exists -> Dispatches to InstructPix2Pix pipeline.

Payload: Processed target asset rendered side-by-side with original metadata context.

DATABASE_QUERY Route:

Prompt: Inject Schema Details + "Find all senior developers in Osaka region."

Behavior: .NET catches database query token context -> Maps system model properties.

Payload: Formatted structural JSON query string schema array markup output.

🔒 Security & Runtime Optimizations
Automated Sanitization: The C# processing framework includes a string-parsing mechanism that scrubs quotes, backticks, and descriptive markdown annotations from the LLM routing responses before processing enums.

Memory Shielding: To prevent memory thrashing under severe inference loads on unified configurations, the system enforces a strict exception block if an image editing command is requested without a valid source file, protecting the GPU pipeline from crashing.

Global SSL Bypass: Contains embedded local development environment configurations (ssl._create_unverified_context) to seamlessly handle secure model downloading on secure enterprise connections.