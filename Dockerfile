# Python tabanlı bir imaj kullan
FROM python:3.10-slim

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y build-essential

# Çalışma dizinini ayarla
WORKDIR /app

# Tüm dosyaları konteynıra kopyala
COPY requirements.txt . 

COPY . . 

# Gerekli kütüphaneleri yükle
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Uygulamayı çalıştır
CMD ["python", "main.py"]
