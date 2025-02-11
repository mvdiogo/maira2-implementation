import torch
from logging import getLogger
from transformers import AutoModelForCausalLM, AutoProcessor
from config import config

logger = getLogger(__name__)


class ModelLoader:
    """Loads and manages the MAIRA-2 model and processor."""

    def __init__(self, hf_token: str = config.hf_token, model_name: str = config.model_name):
        self.hf_token = hf_token
        self.model_name = model_name
        self.model = None
        self.processor = None
        self.device = None

    def load_model(self) -> None:
        """
        Loads the model and processor from the Hugging Face Hub.
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("Starting model download...")
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                token=self.hf_token,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            )
            logger.info("Model loaded, now loading processor...")
            self.processor = AutoProcessor.from_pretrained(
                self.model_name, trust_remote_code=True, token=self.hf_token
            )
        except Exception as e:
            raise RuntimeError(f"Error loading model/processor: {e}")

        self.model.to(self.device)
        if torch.cuda.is_available():
            self.model.half()
        else:
            # Optionally compile model for CPU if using PyTorch 2.0+
            try:
                if torch.__version__ >= "2.0.0":
                    self.model = torch.compile(self.model)
                    logger.info("Model compiled with torch.compile for CPU inference.")
                else:
                    logger.info("Skipping model compilation. Requires PyTorch 2.0+")
            except Exception as e:
                logger.warning(f"Model compilation skipped or failed: {e}")
        logger.info("Model and processor loaded successfully.")

    def get_model(self):
        """Returns the loaded model."""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        return self.model

    def get_processor(self):
        """Returns the loaded processor."""
        if self.processor is None:
            raise ValueError("Processor not loaded. Call load_model() first.")
        return self.processor

    def get_device(self):
        """Returns the device the model is loaded on."""
        if self.device is None:
            raise ValueError("Device not initialized. Call load_model() first.")
        return self.device
