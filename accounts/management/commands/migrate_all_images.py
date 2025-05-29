# accounts/management/commands/migrate_all_images.py

from django.core.management.base import BaseCommand
from django.conf import settings
from cloudinary.uploader import upload
from pathlib import Path
import os
import cloudinary
from accounts.models import CustomUser, PartnerCompany, Venue  # 🔥 venue ve partner import edildi

# 📦 Cloudinary config
cloudinary.config( 
    cloud_name = 'dxkgdz4hb', 
    api_key = '877698811943697', 
    api_secret = '5Vnr5WYZB6nV1MV5qtcsqPqvt9A' 
)

class Command(BaseCommand):
    help = 'Upload profile_images and partner_logos to Cloudinary. Update DB with direct URLs.'

    def handle(self, *args, **kwargs):
        base_media_path = Path(settings.MEDIA_ROOT)

        folders = {
            "profile_images": base_media_path / "profile_images",
            "partner_logos": base_media_path / "partner_logos",
        }

        # 1. CustomUser profil resimleri
        self.stdout.write("📦 Updating CustomUser.profile_image with Cloudinary URLs...")

        for user in CustomUser.objects.exclude(profile_image=''):
            try:
                file_path = base_media_path / user.profile_image
                if file_path.exists():
                    result = upload(str(file_path))
                    image_url = result['secure_url']
                    user.profile_image = image_url
                    user.save()
                    self.stdout.write(f"✅ User {user.id} → {image_url}")
                else:
                    self.stderr.write(f"❌ File not found: {file_path}")
            except Exception as e:
                self.stderr.write(f"❌ User {user.id} failed: {e}")

        # 2. PartnerCompany logo
        self.stdout.write("\n🏢 Uploading PartnerCompany logos...")
        for partner in PartnerCompany.objects.exclude(logo=''):
            try:
                file_path = base_media_path / partner.logo
                if file_path.exists():
                    result = upload(str(file_path))
                    image_url = result['secure_url']
                    partner.logo = image_url
                    partner.save()
                    self.stdout.write(f"✅ Partner {partner.name} → {image_url}")
                else:
                    self.stderr.write(f"❌ File not found: {file_path}")
            except Exception as e:
                self.stderr.write(f"❌ Partner {partner.name} failed: {e}")

        # 3. Venue logo
        self.stdout.write("\n📍 Uploading Venue logos...")
        for venue in Venue.objects.exclude(logo=''):
            try:
                file_path = base_media_path / venue.logo
                if file_path.exists():
                    result = upload(str(file_path))
                    image_url = result['secure_url']
                    venue.logo = image_url
                    venue.save()
                    self.stdout.write(f"✅ Venue {venue.name} → {image_url}")
                else:
                    self.stderr.write(f"❌ File not found: {file_path}")
            except Exception as e:
                self.stderr.write(f"❌ Venue {venue.name} failed: {e}")

        # 4. Bağımsız dosyalar
        self.stdout.write("\n📁 Uploading standalone images (not model-bound):")
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