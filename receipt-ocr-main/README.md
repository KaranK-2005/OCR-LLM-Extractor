# 🧾 OCR Receipt & Invoice Data Extraction System

## 📌 Overview

This project extracts key fields from receipt and invoice images/PDFs and returns structured JSON.

It is designed for **real-world variability** and can handle:
- Different document layouts
- Printed and scanned inputs
- Digital invoices
- Varying fonts and resolutions

It uses a **multimodal LLM** for vision + structured extraction, with a JSON schema that enforces the output shape.

---

## 🎯 Objective

To build a practical and robust pipeline that:

- Accepts images and PDFs  
- Extracts key fields  
- Produces machine-readable JSON  
- Works across multiple document styles without being tuned to a single template  

---

## 📥 Input

The system accepts:

- Receipt or invoice images (`.jpg`, `.jpeg`, `.png`)
- PDF documents (single-page; multi-page handled by first page)
- Mixed formats within the same folder

### Example
```
input/
├── receipt1.png
├── receipt2.jpg
├── invoice.pdf
```

---

## 📤 Output

For each run, a corresponding JSON file is generated in the `output/` directory.
Only **one** JSON file is kept there at a time (each run overwrites the previous JSON).

### Extracted Fields
- Merchant / Vendor Name  
- Invoice Number (if present)  
- Date  
- Total Amount  
- Currency  
- Tax Amount (if present)  
- Line Items (best-effort)

---

### Sample Output
```json
{
  "merchant_name": "RELIANCE",
  "merchant_address": "123 Market Road, Mumbai",
  "transaction_date": "2025-01-28",
  "transaction_time": "",
  "total_amount": 189.0,
  "currency": "INR",
  "invoice_number": "INV123456",
  "tax_amount": 12.0,
  "line_items": [
    {
      "item_name": "Milk",
      "item_quantity": 2,
      "item_price": 60.0
    }
  ]
}
```

---

## 🧠 Key Design Principles

- Robustness over perfection  
- Graceful handling of noisy inputs  
- Work across diverse real-world formats  
- Keep logic explainable and maintainable  

---

## 🛠️ Technologies Used

- Python  
- OpenAI-compatible multimodal LLM (Gemini supported via OpenAI-style endpoint)  
- Pillow (image handling)  
- pdf2image + PyMuPDF fallback for PDFs  

---

## 📁 Project Structure

```
ocr-extractor/
│
├── input/               # Documents to process
├── output/              # JSON output (single file per run)
│
├── src/
│   └── receipt_ocr/      # Core logic + CLI
│
├── pyproject.toml
└── README.md
```

---

## ⚙️ Installation

```powershell
cd c:\Users\rajuk\Downloads\receipt-ocr-main\receipt-ocr-main
python -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -e .
```

Create a `.env` file:
```env
OPENAI_API_KEY="YOUR_API_KEY"
OPENAI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
OPENAI_MODEL="gemini-2.5-flash"
```

Security note: do not commit `.env` or your API key.

---

## ▶️ How to Run

### Process a single file
```powershell
.\.venv\Scripts\ocr-extractor.exe sample_1.png
```

Outputs will be saved as:
```
output/<filename>.json
```

Only one JSON is kept in `output/`. Each run replaces the previous output file.

---

## 🔁 Batch Processing Capability

You can iterate over all files in `input/` and run them one by one.  
Each file is processed independently; failures produce an error JSON output.

PDFs are supported via `pdf2image` with a PyMuPDF fallback. Poppler is optional.

If you get connection errors, check for proxy env vars and run:
```powershell
Remove-Item Env:HTTP_PROXY, Env:HTTPS_PROXY, Env:ALL_PROXY
```

---

## ⚠️ Limitations

- Line-item extraction is best-effort  
- OCR accuracy depends on image quality  
- Some documents may require manual review  

---

## 🚀 Possible Future Enhancements

- Confidence scoring for extracted fields  
- Multi-page PDF merging  
- REST API / UI interface  
