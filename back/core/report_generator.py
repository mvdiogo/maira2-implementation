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
        print("Step 1/15: ReportGenerator.__init__ - Initializing generator")

    def setup(self) -> None:
        """Sets up the generator by retrieving model components."""
        print("Step 2/15: ReportGenerator.setup - Retrieving model components")
        self.device = self.model_loader.get_device()
        print("Step 3/15: ReportGenerator.setup - Device obtained")
        self.model = self.model_loader.get_model()
        print("Step 4/15: ReportGenerator.setup - Model obtained")
        self.processor = self.model_loader.get_processor()
        print("Step 5/15: ReportGenerator.setup - Processor obtained")

    def create_hash(
        self,
        frontal_url: str,
        lateral_url: str,
        indication: str,
        comparison: str,
        technique: str,
    ) -> str:
        """
        Creates a SHA256 hash from the input parameters.

        Returns:
            str: The generated hash.
        """
        print("Step 6/15: ReportGenerator.create_hash - Creating input hash", end=" ")
        combined_string = (
            f"{frontal_url}{lateral_url}{indication}{comparison}{technique}"
        )
        hash_value = hashlib.sha256(combined_string.encode()).hexdigest()
        print("- Hash created")
        return hash_value

    def load_result_from_file(self, hash_value: str) -> Optional[dict]:
        """
        Loads a cached result from a file, if it exists.

        Args:
            hash_value (str): The hash of the input parameters.

        Returns:
            Optional[dict]: The cached result or None if not found.
        """
        step = "Step 7/15"
        print(
            f"{step}: ReportGenerator.load_result_from_file - Loading cached result",
            end=" ",
        )
        filename = path.join(self.results_dir, f"{hash_value}.txt")
        if path.exists(filename):
            try:
                with open(filename, "r") as file:
                    result = json.load(file)
                    print("- Cache hit")
                    return result
            except Exception as e:
                error_msg = f"{step}: Error loading result from file - {e}"
                print(f"\n{error_msg}")
                logger.error(error_msg)
                print(f"{step}: - Cache miss (error)")
                return None
        print("- Cache miss")
        return None

    def save_result_to_file(self, hash_value: str, result: dict) -> None:
        """
        Saves a result to a file for caching.

        Args:
            hash_value (str): The hash of the input parameters.
            result (dict): The result to be saved.
        """
        step = "Step 13/15"
        print(
            f"{step}: ReportGenerator.save_result_to_file - Saving result to file",
            end=" ",
        )
        makedirs(self.results_dir, exist_ok=True)
        filename = path.join(self.results_dir, f"{hash_value}.txt")
        try:
            with open(filename, "w") as file:
                json.dump(result, file)
            print("- Result saved")
        except Exception as e:
            error_msg = f"{step}: Error saving result to file - {e}"
            print(f"\n{error_msg}")
            logger.error(error_msg)

    async def generate_report(
        self,
        frontal_url: str,
        lateral_url: str,
        indication: str,
        comparison: str,
        technique: str,
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
        step = "Step 9/15"
        print(f"{step}: ReportGenerator.generate_report - Generating report")
        if self.model is None or self.processor is None:
            raise HTTPException(status_code=503, detail="Model not loaded.")

        start_time = time.monotonic()
        input_hash = self.create_hash(
            frontal_url, lateral_url, indication, comparison, technique
        )
        cached_result = self.load_result_from_file(input_hash)

        if cached_result:
            logger.info("Result found in cache.")
            print(f"{step}: Cached result found")
            await asyncio.sleep(1)
            print(
                "Step 9/15: ReportGenerator.generate_report - Returning cached result"
            )
            return cached_result

        try:
            print("Step 10/15: ReportGenerator.generate_report - Downloading images")
            frontal_image, lateral_image = await asyncio.gather(
                ImageUtils.download_image_async(frontal_url),
                ImageUtils.download_image_async(lateral_url),
            )

            print("Step 11/15: ReportGenerator.generate_report - Processing inputs")
            processed_inputs = await asyncio.to_thread(
                self.processor.format_and_preprocess_reporting_input,
                current_frontal=frontal_image,
                current_lateral=lateral_image,
                indication=indication,
                technique=technique,
                comparison=comparison,
                prior_frontal=None,
                prior_report=None,
                return_tensors="pt",
            )

            processed_inputs = {
                k: v.to(self.device) for k, v in processed_inputs.items()
            }

            print("Step 12/15: ReportGenerator.generate_report - Generating prediction")
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
                    output_decoding[0][prompt_length:], skip_special_tokens=True
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
                "report": f"{prediction} Time processed: {processing_time} seconds",
            }

            self.save_result_to_file(input_hash, result)
            print(
                "Step 14/15: ReportGenerator.generate_report - Returning generated result"
            )
            return result

        except Exception as e:
            error_msg = "Step 8/15: Error generating report - {}".format(str(e))
            logger.error(error_msg)
            print(error_msg)
            raise HTTPException(
                status_code=500, detail="Error generating report: {}".format(str(e))
            )
        finally:
            print(
                "Step 15/15: ReportGenerator.generate_report - Finished generating report"
            )
