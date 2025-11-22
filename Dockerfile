FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      poppler-utils \
      tesseract-ocr \
      libtesseract-dev \
      build-essential \
      pkg-config \
      poppler-utils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt gunicorn

COPY . .

CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker main:app -b 0.0.0.0:${PORT:-8000} --workers 1"]