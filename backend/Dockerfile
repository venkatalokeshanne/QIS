FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Overridden by fly.toml's [mounts] + [env] to point at the persistent
# volume in production; these defaults only matter for `docker run`
# without that config (e.g. local testing of the image itself).
ENV DATA_DIR=/data
ENV DB_PATH=/data/app.db
ENV DATASET_STORAGE_DIR=/data/datasets

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
