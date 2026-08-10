# config.py
import torch

# 1. Hardware Optimization Setup
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
TORCH_DTYPE = torch.float32 if DEVICE == "mps" else torch.float16

# 2. Local AI Engines Models References (FIXED: Added explicitly)
YOLO_SEG_MODEL_PATH = "yolov8n-seg.pt"
YOLO_FACE_MODEL_PATH = "yolov8n-face.pt"  # currently unused: face box is derived geometrically (see engines/face_detection.py)
INPAINT_MODEL_PATH = "runwayml/stable-diffusion-inpainting"
LLAMA_OLLAMA_URL = "http://localhost:11434/api/generate"

# 3. Stable Diffusion Parameters
IMAGE_SIZE = 512
INFERENCE_STEPS = 35
GUIDANCE_SCALE = 8.5
INPAINT_STRENGTH = 1.0

# 4. Face Recovery & Blending Tuning
FEATHER_BLUR_RADIUS = 5  
FACE_BOX_PADDING = 10    

# 5. Ultra Clean Custom Negative Prompt
GLOBAL_NEGATIVE_PROMPT = (
    "blurry, low quality, bad anatomy, deformed, ugly, watermark, text, "
    "logo, cropped, plastic skin, jpeg artifacts"
)