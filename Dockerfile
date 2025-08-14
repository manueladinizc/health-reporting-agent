FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for playwright
RUN apt-get update && apt-get install -y \
    wget curl gnupg build-essential libglib2.0-0 libnss3 libgdk-pixbuf2.0-0 libgtk-3-0 libxss1 libasound2 libatk-bridge2.0-0 libdrm2 libgbm1 libxcomposite1 libxdamage1 libxrandr2 libu2f-udev libvulkan1 libxshmfence1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN python -m playwright install --with-deps

COPY . .

CMD ["tail", "-f", "/dev/null"]
