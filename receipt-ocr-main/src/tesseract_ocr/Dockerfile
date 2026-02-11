FROM python:3.12-slim AS base

RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UV_EXTRA_INDEX_URL="https://pypi.org/simple"

FROM base AS builder

RUN pip install uv

RUN uv venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN uv pip install --no-cache-dir -r requirements.txt

FROM base AS runner

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/home/appuser

COPY . tesseract_ocr

EXPOSE 80

CMD ["uvicorn", "tesseract_ocr.app:app", "--host", "0.0.0.0", "--port", "80"]
