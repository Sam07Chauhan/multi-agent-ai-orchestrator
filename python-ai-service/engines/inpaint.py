from diffusers import StableDiffusionInpaintPipeline
import config

class InpaintEngine:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InpaintEngine, cls).__new__(cls)
            cls._instance.pipe = StableDiffusionInpaintPipeline.from_pretrained(
                config.INPAINT_MODEL_PATH, torch_dtype=config.TORCH_DTYPE, safety_checker=None
            ).to(config.DEVICE)
        return cls._instance

    def inference(self, prompt, image, mask):
        return self.pipe(
            prompt=prompt, negative_prompt=config.GLOBAL_NEGATIVE_PROMPT,
            image=image, mask_image=mask,
            num_inference_steps=config.INFERENCE_STEPS, guidance_scale=config.GUIDANCE_SCALE, strength=config.INPAINT_STRENGTH
        ).images[0]