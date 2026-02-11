import base64
import io
import os
from pathlib import Path
from typing import Union

from PIL import Image


def _load_pil_image_from_path(path: Path) -> Image.Image:
    """Load a PIL image from a file path, with optional PDF support."""
    if path.suffix.lower() == ".pdf":
        poppler_path = os.getenv("POPPLER_PATH")
        try:
            from pdf2image import convert_from_path

            images = convert_from_path(
                str(path),
                first_page=1,
                last_page=1,
                poppler_path=poppler_path,
            )
            if images:
                return images[0]
        except Exception:
            pass

        try:
            import fitz  # PyMuPDF
        except ImportError as exc:
            raise ValueError(
                "PDF support requires Poppler or PyMuPDF. "
                "Install Poppler and set POPPLER_PATH or run: pip install pymupdf"
            ) from exc

        try:
            doc = fitz.open(str(path))
            if doc.page_count == 0:
                raise ValueError("No pages found in PDF.")
            page = doc.load_page(0)
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            return Image.open(io.BytesIO(img_bytes))
        except Exception as exc:
            raise ValueError("Failed to render PDF with PyMuPDF.") from exc

    return Image.open(path)


def encode_image_to_base64(
    image: Union[str, bytes, Image.Image], max_size: int = 1080
) -> str:
    """Encode an image to base64 string.

    Args:
        image: Image source (file path, bytes, or PIL Image)
        max_size: Maximum dimension for resizing (maintains aspect ratio)

    Returns:
        Base64 encoded string of the image
    """
    if isinstance(image, str):
        pil_image = _load_pil_image_from_path(Path(image))
    elif isinstance(image, bytes):
        pil_image = Image.open(io.BytesIO(image))
    elif isinstance(image, Image.Image):
        pil_image = image
    else:
        raise ValueError(f"Unsupported image type: {type(image)}")

    if pil_image.mode not in ("RGB", "L"):
        pil_image = pil_image.convert("RGB")

    if max(pil_image.size) > max_size:
        w, h = pil_image.size
        if w > h:
            new_w = max_size
            new_h = int(h * max_size / w)
        else:
            new_h = max_size
            new_w = int(w * max_size / h)
        pil_image = pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    return base64.b64encode(img_bytes).decode("utf-8")
