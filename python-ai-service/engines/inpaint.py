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

        # Compel handles prompts longer than CLIP's native 77-token limit by
        # chunking into 75-token blocks, encoding each separately, and
        # concatenating the resulting embeddings — instead of truncating or
        # rewriting the prompt. Built lazily/reused across calls.
        from compel import Compel
        self.compel = Compel(tokenizer=self.pipe.tokenizer, text_encoder=self.pipe.text_encoder)

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

        # Build embeddings via Compel (chunks + concatenates automatically
        # for prompts over 75 tokens) instead of passing a raw prompt string,
        # which the pipeline would otherwise silently truncate at 77 tokens.
        prompt_embeds = self.compel(prompt)
        negative_prompt_embeds = self.compel(config.GLOBAL_NEGATIVE_PROMPT)
        # Compel pads the shorter of the two embeddings to match token-chunk
        # count, since prompt/negative_prompt can differ in length.
        [prompt_embeds, negative_prompt_embeds] = self.compel.pad_conditioning_tensors_to_same_length(
            [prompt_embeds, negative_prompt_embeds]
        )

        result_img = self.pipe(
            prompt_embeds=prompt_embeds,
            negative_prompt_embeds=negative_prompt_embeds,
            image=image,
            mask_image=mask_image,
            num_inference_steps=config.INFERENCE_STEPS,
            guidance_scale=config.GUIDANCE_SCALE,
            strength=config.INPAINT_STRENGTH,
        ).images[0]

        return result_img