# Python tabanlı küçük bir imaj
FROM python:3.11-slim

# Ortam değişkenleri
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Sistem paketleri
RUN apt-get update && apt-get install -y build-essential

# Çalışma dizini oluştur
WORKDIR /app

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Projeyi kopyala
COPY . .

# Django geliştirme sunucusunu başlat
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
