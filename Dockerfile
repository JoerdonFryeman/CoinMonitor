FROM python:3.14-alpine

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && python -m pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY core/ ./core
COPY config_files/ ./config_files

CMD ["python", "main.py"]
