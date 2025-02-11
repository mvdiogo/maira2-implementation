import json
import hashlib
import time
import asyncio
import logging
from os import path, makedirs
from typing import Optional
from fastapi import HTTPException
from config import config
from core.image_utils import ImageUtils

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates chest X-ray reports using the MAIRA-2 model."""

    def __init__(self, model_loader: object, results_dir: str = config.results_dir):
        self.model_loader = model_loader
        self.results_dir = results_dir
        self.device = None
        self.model = None
        self.processor = None

    def setup(self) -> None:
        """Sets up the generator by retrieving model components."""
        self.device = self.model_loader.get_device()
        self.model = self.model_loader.get_model()
        self.processor = self.model_loader.get_processor()

    def create_hash(
        self, frontal_url: str, lateral_url: str, indication: str,
        comparison: str, technique: str
    ) -> str:
        """
        Creates a SHA256 hash from the input parameters.

        Returns:
            str: The generated hash.
        """
        combined_string = f"{frontal_url}{lateral_url}{indication}{comparison}{technique}"
        return hashlib.sha256(combined_string.encode()).hexdigest()

    def load_result_from_file(self, hash_value: str) -> Optional[dict]:
        """
        Loads a cached result from a file, if it exists.

        Args:
            hash_value (str): The hash of the input parameters.

        Returns:
            Optional[dict]: The cached result or None if not found.
        """
        filename = path.join(self.results_dir, f"{hash_value}.txt")
        if path.exists(filename):
            try:
                with open(filename, "r") as file:
                    return json.load(file)
            except Exception as e:
                logger.error(f"Error loading result from file: {e}")
                return None
        return None

    def save_result_to_file(self, hash_value: str, result: dict) -> None:
        """
        Saves a result to a file for caching.

        Args:
            hash_value (str): The hash of the input parameters.
            result (dict): The result to be saved.
        """
        makedirs(self.results_dir, exist_ok=True)
        filename = path.join(self.results_dir, f"{hash_value}.txt")
        try:
            with open(filename, "w") as file:
                json.dump(result, file)
        except Exception as e:
            logger.error(f"Error saving result to file: {e}")

    async def generate_report(
        self, frontal_url: str, lateral_url: str, indication: str,
        comparison: str, technique: str
    ) -> dict:
        """
        Generates a chest X-ray report using the loaded model.

        Args:
            frontal_url (str): URL for the frontal image.
            lateral_url (str): URL for the lateral image.
            indication (str): Indication for the report.
            comparison (str): Comparison details.
            technique (str): Technique used.

        Returns:
            dict: A dictionary containing the images and generated report.
        """
        if self.model is None or self.processor is None:
            raise HTTPException(status_code=503, detail="Model not loaded.")

        start_time = time.monotonic()
        input_hash = self.create_hash(
            frontal_url, lateral_url, indication, comparison, technique
        )
        cached_result = self.load_result_from_file(input_hash)

        if cached_result:
            logger.info("Result found in cache.")
            await asyncio.sleep(2)  # Simulate a small delay
            return cached_result

        try:
            # Download both images concurrently.
            frontal_image, lateral_image = await asyncio.gather(
                ImageUtils.download_image_async(frontal_url),
                ImageUtils.download_image_async(lateral_url)
            )

            # Offload processor formatting to a worker thread.
            processed_inputs = await asyncio.to_thread(
                self.processor.format_and_preprocess_reporting_input,
                current_frontal=frontal_image,
                current_lateral=lateral_image,
                indication=indication,
                technique=technique,
                comparison=comparison,
                prior_frontal=None,
                prior_report=None,
                return_tensors="pt"
            )

            # Move inputs to the designated device.
            processed_inputs = {
                k: v.to(self.device) for k, v in processed_inputs.items()
            }

            # Offload the model.generate call to a thread.
            output_decoding = await asyncio.to_thread(
                lambda: self.model.generate(
                    **processed_inputs,
                    max_new_tokens=512,
                    num_beams=3,
                    early_stopping=True,
                    use_cache=True,
                )
            )
            prompt_length = processed_inputs["input_ids"].shape[-1]
            decoded_text = await asyncio.to_thread(
                lambda: self.processor.tokenizer.decode(
                    output_decoding[0][prompt_length:],
                    skip_special_tokens=True
                )
            )
            prediction = decoded_text.lstrip()

            frontal_image_bytes = ImageUtils.image_to_base64(frontal_image)
            lateral_image_bytes = ImageUtils.image_to_base64(lateral_image)

            end_time = time.monotonic()
            processing_time = round(end_time - start_time, 2)

            result = {
                "frontal_image": frontal_image_bytes,
                "lateral_image": lateral_image_bytes,
                "report": f"{prediction} Time processed: {processing_time} seconds"
            }
            self.save_result_to_file(input_hash, result)
            return result

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise HTTPException(status_code=500, detail=f"Error generating report: {e}")
