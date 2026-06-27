FROM python:3.12-slim

WORKDIR /app

# build-essential and libpq-dev are required to compile the C extensions
# inside psycopg and some cryptography packages; they are not needed at runtime
# but must be present when pip builds the wheels from source
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copying requirements before the application code means Docker reuses this cached
# layer on subsequent builds when only source files change but requirements.txt hasn't
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# PYTHONPATH ensures Python finds the `app` package regardless of the working directory
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
