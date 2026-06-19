# SPSS → Makale (iPhone PWA) backend — herhangi bir bulut host'unda çalışır.
FROM python:3.11-slim

WORKDIR /app

# Bilimsel paketlerin tekerlek (wheel) dışı derlemesi gerekirse diye derleyiciler:
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY webapp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY sav2q1 /app/sav2q1
COPY webapp /app/webapp
COPY scripts /app/scripts

ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn webapp.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
