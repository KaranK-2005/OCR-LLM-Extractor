import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from receipt_ocr.constants import _DEFAULT_OPENAI_MODEL
from receipt_ocr.processors import ReceiptProcessor
from receipt_ocr.providers import OpenAIProvider

load_dotenv()


def main():
    """Main function for the CLI."""
    parser = argparse.ArgumentParser(
        description="Extract information from a receipt image."
    )
    parser.add_argument(
        "image_path",
        type=str,
        help="Path to a receipt image file or a folder of images.",
    )
    parser.add_argument(
        "--schema_path", type=str, help="The path to a custom JSON schema file."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("OPENAI_MODEL", _DEFAULT_OPENAI_MODEL),
        help="The model to use for the LLM.",
    )
    parser.add_argument("--api_key", type=str, help="The API key for the LLM provider.")
    parser.add_argument(
        "--base_url", type=str, help="The base URL for the LLM provider."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="output",
        help="Directory to write JSON outputs (default: output).",
    )
    args = parser.parse_args()

    if args.schema_path:
        with open(args.schema_path, "r") as f:
            json_schema = json.load(f)
    else:
        json_schema = {
            "merchant_name": "string",
            "merchant_address": "string",
            "transaction_date": "string",
            "transaction_time": "string",
            "total_amount": "number",
            "currency": "string",
            "invoice_number": "string",
            "tax_amount": "number",
            "line_items": [
                {
                    "item_name": "string",
                    "item_quantity": "number",
                    "item_price": "number",
                }
            ],
        }

    provider = OpenAIProvider(api_key=args.api_key, base_url=args.base_url)

    processor = ReceiptProcessor(provider)

    input_path = Path(args.image_path)
    if not input_path.is_absolute():
        input_path = (Path("input") / input_path).resolve()
    input_root = Path("input").resolve()
    if input_root not in input_path.parents and input_path != input_root:
        raise SystemExit("Input must be inside the ./input folder.")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    supported_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp", ".pdf"}

    def write_result(path: Path, result: dict) -> None:
        for existing in output_dir.glob("*.json"):
            existing.unlink()
        out_path = output_dir / f"{path.stem}.json"
        out_path.write_text(json.dumps(result, indent=4), encoding="utf-8")

    def write_error(path: Path, exc: Exception) -> None:
        error_payload = {
            "error": "processing_failed",
            "message": str(exc),
            "input_file": str(path),
        }
        write_result(path, error_payload)

    if input_path.is_dir():
        image_files = sorted(
            p for p in input_path.iterdir() if p.is_file() and p.suffix.lower() in supported_exts
        )
        if not image_files:
            raise SystemExit(f"No supported image files found in: {input_path}")

        for image_file in image_files:
            try:
                result = processor.process_receipt(
                    str(image_file), json_schema, args.model
                )
                write_result(image_file, result)
                print(
                    f"Wrote {image_file.name} -> {output_dir / (image_file.stem + '.json')}"
                )
            except Exception as exc:
                write_error(image_file, exc)
                print(
                    f"Failed {image_file.name} -> {output_dir / (image_file.stem + '.json')}"
                )
    else:
        try:
            result = processor.process_receipt(str(input_path), json_schema, args.model)
            write_result(input_path, result)
            print(json.dumps(result, indent=4))
        except Exception as exc:
            write_error(input_path, exc)
            print(json.dumps({"error": "processing_failed", "message": str(exc)}, indent=4))


if __name__ == "__main__":
    main()
