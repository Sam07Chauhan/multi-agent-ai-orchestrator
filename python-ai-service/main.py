import io
import uuid
import logging
import config
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from PIL import Image

# Modular imports according to project architecture
from engines.inpaint import InpaintEngine
from engines.text_enhancer import LlamaOrchestrator
from services.pre_process import preprocess_image, segment_subject
from services.post_process import apply_face_shield_mask, restore_face

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("m4_nexus")

app = FastAPI(title="M4 Master AI Orchestrator Stack")

# Lazy loading patterns for memory optimization
inpaint_engine = InpaintEngine()
llama_orchestrator = LlamaOrchestrator()

@app.post("/orchestrate")
async def central_orchestrator_endpoint(
    background_tasks: BackgroundTasks,
    prompt: str = Form(...),
    mode: str = Form("auto"),
    schema: str = Form(None),
    file: UploadFile = File(None)
):
    task_id = str(uuid.uuid4())
    logger.info(f"New Central Request Received | Task ID: {task_id} | Mode: {mode}")

    # Step 1: Intent detection Python ki side Llama se natively check karein
    detected_intent = mode.upper()
    if mode == "auto" or not mode:
        detected_intent = await llama_orchestrator.detect_intent(prompt)
    
    logger.info(f"Mapped Engine Routing Execution Pathway: {detected_intent}")

    # Route 1: Database Operations Layer (No Heavy Stable Diffusion Models Loaded)
    if detected_intent == "DATABASE_QUERY" or detected_intent == "DATA":
        if not schema:
            return JSONResponse(status_code=400, content={"error": "Database schema context string missing from .NET layer."})
        
        sql_result = await llama_orchestrator.generate_sql_query(prompt, schema)
        return {"task_id": task_id, "type": "DATABASE_SQL", "payload": sql_result}

    # Route 2: Image Editing Layer (Stable Diffusion Workflow)
    elif detected_intent == "IMAGE_EDIT" or detected_intent == "IMAGE":
        if not file:
            raise HTTPException(status_code=400, detail="Image matrix payload missing for AI Editing flow.")

        try:
            # File data preprocessing pipeline execution
            image_bytes = await file.read()
            input_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            # YOLO auto masking setup
            auto_mask, person_box = segment_subject(input_image)
            
            # Geometric fallback face protection matrix
            final_mask = apply_face_shield_mask(auto_mask, person_box)
            
            # Heavy pipeline processing execution trigger safely 
            edited_image = inpaint_engine.process_inpaint(
                image=input_image,
                mask=final_mask,
                prompt=prompt
            )
            
            # Alpha blending restoration layer
            restored_output = restore_face(input_image, edited_image, person_box)
            
            # Save matrix system output with unique token signatures dynamically
            temp_output_path = f"{config.TEMP_OUTPUT_DIR}/{task_id}.jpg"
            restored_output.save(temp_output_path, quality=95)
            
            # Return base64 stream or direct reference links dynamically to .NET
            with open(temp_output_path, "rb") as image_file:
                import base64
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Queue background task to clean hard disk storage VRAM state 
            background_tasks.add_task(lambda: io.os.remove(temp_output_path) if io.os.path.exists(temp_output_path) else None)
            
            return {"task_id": task_id, "type": "IMAGE_BASE64", "payload": encoded_string}

        except Exception as e:
            logger.critical(f"Critical System Inference Failure: {e}")
            raise HTTPException(status_code=500, detail=f"AI Pipeline Execution Exception: {str(e)}")

    else:
        raise HTTPException(status_code=400, detail="Invalid Intent routing configuration.")