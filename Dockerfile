# Python tabanlı küçük bir imaj
FROM python:3.11-slim

# Ortam değişkenleri
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Sistem paketleri
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini oluştur
WORKDIR /app

# Bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Projeyi kopyala
COPY . .

# Statik dosyaları topla
RUN python manage.py collectstatic --noinput

# Port aç
EXPOSE 8000

# WSGI sunucusu ile başlat
CMD ["gunicorn", "mywebsite.wsgi:application", "--bind", "0.0.0.0:8000"]
