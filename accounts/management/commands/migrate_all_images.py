from django.core.management.base import BaseCommand
from django.conf import settings
from cloudinary.uploader import upload
from django.core.files.base import ContentFile
from urllib.parse import urlparse
import requests
from pathlib import Path
import os
import cloudinary
from accounts.models import CustomUser

# 📦 Cloudinary config (manuel)
cloudinary.config( 
    cloud_name = 'dxkgdz4hb', 
    api_key = '877698811943697', 
    api_secret = '5Vnr5WYZB6nV1MV5qtcsqPqvt9A' 
)

class Command(BaseCommand):
    help = 'Upload profile_images and partner_logos to Cloudinary. Update DB for model-bound images.'

    def handle(self, *args, **kwargs):
        base_media_path = Path(__file__).resolve().parent.parent.parent.parent / "media"

        folders = {
            "profile_images": base_media_path / "profile_images",
            "partner_logos": base_media_path / "partner_logos",
        }

        # ---------------------------
        # 1. CustomUser.profile_image Cloudinary'ye aktarımı ve güncelleme
        # ---------------------------
        self.stdout.write("📦 Updating CustomUser.profile_image with Cloudinary URLs...")

        for user in CustomUser.objects.exclude(profile_image=''):
            try:
                file_path = Path(settings.MEDIA_ROOT) / user.profile_image.name
                if file_path.exists():
                    result = upload(str(file_path))
                    image_url = result['secure_url']

                    response = requests.get(image_url)
                    filename = os.path.basename(urlparse(image_url).path)

                    user.profile_image.save(filename, ContentFile(response.content), save=True)
                    self.stdout.write(f"✅ User {user.id} → {image_url}")
                else:
                    self.stderr.write(f"❌ File not found: {file_path}")
            except Exception as e:
                self.stderr.write(f"❌ User {user.id} failed: {e}")

        # ---------------------------
        # 2. Model bağlantısı olmayan dosyaları Cloudinary'ye yükle (log amaçlı)
        # ---------------------------
        self.stdout.write("\n📁 Uploading standalone images (not model-bound):\n")

        for folder_name, folder_path in folders.items():
            if not folder_path.exists():
                self.stderr.write(f"⚠️  Folder not found: {folder_path}")
                continue

            for file_name in os.listdir(folder_path):
                file_path = folder_path / file_name
                if not file_path.is_file():
                    continue
                if file_path.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.gif']:
                    continue
                try:
                    result = upload(str(file_path))
                    url = result.get("secure_url")
                    self.stdout.write(f"✅ {file_name} uploaded → {url}")
                except Exception as e:
                    self.stderr.write(f"❌ Failed to upload {file_name}: {e}")

        self.stdout.write(self.style.SUCCESS("\n🎉 Tüm model ve bağımsız görseller başarıyla Cloudinary'ye taşındı!"))