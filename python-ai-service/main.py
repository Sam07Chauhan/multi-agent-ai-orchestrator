import os
import ssl

# SSL Certificate verification ko globally bypass karne ke liye
ssl._create_default_https_context = ssl._create_unverified_context

# Hugging Face hub ke liye SSL verify false set karna
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["CURL_CA_BUNDLE"] = ""


from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import torch
# StableDiffusionInstructionPix2PixPipeline ki jagah StableDiffusionInstructPix2PixPipeline use hota hai naye versions mein
# Par safer side ke liye hum common DiffusionPipeline use karenge
from diffusers import DiffusionPipeline, StableDiffusionPipeline
from PIL import Image
import io

app = FastAPI(title="M4 Local AI Service")

# 1. Mac M4 (Metal) Core Graphic System Check
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using Device: {device.upper()} for AI Generation")

# 2. AI Models Loading
print("Loading Image Editing Model (InstructPix2Pix)...")
# Generic DiffusionPipeline standard checkpoint ko sahi se wrap kar leta hai
edit_pipe = DiffusionPipeline.from_pretrained(
    "timbrooks/instruct-pix2pix", 
    torch_dtype=torch.float16 if device == "mps" else torch.float32, 
    safety_checker=None
).to(device)

print("Loading Image Generation Model (Stable Diffusion 1.5)...")
create_pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5", 
    torch_dtype=torch.float16 if device == "mps" else torch.float32,
    safety_checker=None
).to(device)

print("⚡ All Local Models Loaded Successfully on Mac M4 Neural Core!")

# --- ENDPOINTS ---

@app.post("/process")
async def edit_image(file: UploadFile = File(...), prompt: str = Form(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    image.thumbnail((512, 512))

    print(f"[EDIT REQUEST] Prompt: {prompt}")
    edited_image = edit_pipe(
        prompt, 
        image=image, 
        num_inference_steps=15, 
        image_guidance_scale=1.5
    ).images[0]
    
    output_path = "edit_result.jpg"
    edited_image.save(output_path)
    return FileResponse(output_path, media_type="image/jpeg")


@app.post("/generate")
async def generate_image(prompt: str = Form(...)):
    print(f"[CREATE REQUEST] Prompt: {prompt}")
    
    generated_image = create_pipe(
        prompt, 
        num_inference_steps=15,
        width=512,
        height=512
    ).images[0]
    
    output_path = "create_result.jpg"
    generated_image.save(output_path)
    return FileResponse(output_path, media_type="image/jpeg")