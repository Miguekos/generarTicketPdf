FROM python:3.8-slim-bullseye

# Install system dependencies for wkhtmltopdf and essential tools
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    xfonts-75dpi \
    xfonts-base \
    libxrender1 \
    libfontconfig1 \
    fontconfig \
    libx11-dev \
    libjpeg62-turbo \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && apt-get update \
    && apt-get install -y ./wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && rm wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements file (note the filename in your repo is requeriments.txt)
COPY requeriments.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requeriments.txt

# Copy application code
COPY . .

# Expose port 80
EXPOSE 5238

# Command to run the application
CMD ["python", "app.py"]
