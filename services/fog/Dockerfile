FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY shared/ /app/shared/
RUN pip install -e /app/shared/
COPY services/fog/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/security/ /app/services/security/
COPY services/fog/app/ /app/app/

EXPOSE 8020
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8020"]
