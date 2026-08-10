import torch
import numpy as np
from diffusers import StableDiffusionInpaintPipeline, DPMSolverMultistepScheduler
import config

class InpaintEngine:
    def __init__(self, device: str):
        self.device = device
        print("⚡ [INPAINT ENGINE] Initializing Stable Diffusion Inpaint Pipeline...")

        dtype = config.TORCH_DTYPE
        self.pipe = StableDiffusionInpaintPipeline.from_pretrained(
            config.INPAINT_MODEL_PATH,
            torch_dtype=dtype,
            safety_checker=None,
        ).to(self.device)

        if self.device == "mps":
            self.pipe.enable_attention_slicing()
            # float32 VAE decode avoids NaN/black output on Apple Silicon
            self.pipe.vae.to(dtype=torch.float32)

        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(self.pipe.scheduler.config)
        print(f"🛡️ [INPAINT ENGINE] Ready on {self.device.upper()} (dtype={dtype})")

    def _sanitize_mask(self, mask_image):
        """Ensure mask is RGB with clean 0/255 values for the pipeline."""
        mask = mask_image.convert("L")
        arr = np.array(mask)
        arr = np.where(arr > 127, 255, 0).astype(np.uint8)
        from PIL import Image
        return Image.fromarray(arr).convert("RGB")

    def process_inpaint(self, image, mask_image, prompt: str):
        print(f"🚀 [INPAINT RUNTIME] Executing inference loop on {self.device.upper()}...")
        mask_image = self._sanitize_mask(mask_image)

        result_img = self.pipe(
            prompt=prompt,
            negative_prompt=config.GLOBAL_NEGATIVE_PROMPT,
            image=image,
            mask_image=mask_image,
            num_inference_steps=config.INFERENCE_STEPS,
            guidance_scale=config.GUIDANCE_SCALE,
        ).images[0]

        return result_img
