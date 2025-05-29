# mywebsite/storage.py

from django.core.files.storage import FileSystemStorage

class CustomStorage(FileSystemStorage):
    # Özelleştirilmiş dosya depolama ayarlarını buraya ekleyebilirsiniz
    pass






CKEDITOR_5_FILE_STORAGE = "mywebsite.storage.CustomStorage"  # Özel storage sınıfı (opsiyonel)