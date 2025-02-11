from io import BytesIO
import base64
from PIL import Image
from fastapi import HTTPException
import httpx


class ImageUtils:
    """Utility class for image processing."""

    @staticmethod
    async def download_image_async(url: str) -> Image.Image:
        """
        Downloads an image from a URL asynchronously.

        Args:
            url (str): The URL of the image.

        Returns:
            Image.Image: The downloaded PIL Image in RGB mode.

        Raises:
            HTTPException: If the image download fails.
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, headers={"User-Agent": "MAIRA-2"})
                response.raise_for_status()
                return Image.open(BytesIO(response.content)).convert("RGB")
        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=f"Failed to download image: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing image: {e}")

    @staticmethod
    def image_to_base64(img: Image.Image) -> str:
        """
        Converts a PIL Image to a base64 encoded string.

        Args:
            img (Image.Image): The PIL Image to convert.

        Returns:
            str: The base64 encoded string of the image.
        """
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()
        return base64.b64encode(img_bytes).decode("utf-8")
