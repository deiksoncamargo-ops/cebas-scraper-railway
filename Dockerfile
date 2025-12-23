FROM python:3.10-slim

# Instalar Chrome e ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium-browser chromium-chromedriver \
    && rm -rf /var/lib/apt/lists/*

# Setup workspace
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar script
COPY scrapper_headless.py .

# Configurar variáveis
ENV WEBHOOK_URL=""

# Rodar o scraper
CMD ["python", "scrapper_headless.py"]
