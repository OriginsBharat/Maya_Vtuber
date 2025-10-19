import torch
from diffusers import AutoPipelineForText2Image

class ImageGenerator:
    """
    Generates images from text prompts using a local Stable Diffusion model.
    """
    def __init__(self):
        print("🎨 Image Generator initialized.")
        self.pipeline = None

    def _load_pipeline(self):
        """Loads the Stable Diffusion pipeline on demand."""
        if self.pipeline:
            return

        print("Loading Stable Diffusion model...")
        model_id = "runwayml/stable-diffusion-v1-5"
        if torch.cuda.is_available():
            device = "cuda"
            dtype = torch.float16
        elif torch.backends.mps.is_available():
            device = "mps"
            dtype = torch.float16
        else:
            device = "cpu"
            dtype = torch.float32

        print(f"Using device: {device} with dtype: {dtype}")

        self.pipeline = AutoPipelineForText2Image.from_pretrained(
            model_id,
            torch_dtype=dtype,
            variant="fp16" if dtype == torch.float16 else None
        ).to(device)
        print("✅ Stable Diffusion model loaded.")

    def generate_image(self, prompt: str, output_path: str = "scene_image.png"):
        """
        Generates an image based on a text prompt.

        Args:
            prompt: The text description of the image to generate.
            output_path: The path to save the generated image.

        Returns:
            The path to the saved image, or None on error.
        """
        try:
            self._load_pipeline()
            print(f"Generating image for prompt: '{prompt}'")

            # Add more detail to the prompt for a consistent anime style
            full_prompt = (
                f"{prompt}, high quality anime art, detailed, cinematic lighting, "
                f"by makoto shinkai, studio ghibli"
            )

            image = self.pipeline(prompt=full_prompt).images[0]
            image.save(output_path)

            print(f"✅ Image generated successfully at '{output_path}'")
            return output_path

        except Exception as e:
            print(f"🚨 An error occurred during image generation: {e}")
            return None