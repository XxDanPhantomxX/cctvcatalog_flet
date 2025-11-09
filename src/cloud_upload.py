import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import os
import pathlib

# Intentar cargar .env solo si existe (útil para entorno local)
env_path = pathlib.Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  # Esto permite leer variables del entorno en Render

# Configurar Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_image_to_cloudinary(file_source):
    """Sube imagen a Cloudinary desde ruta o BytesIO."""
    try:
        if isinstance(file_source, (bytes, bytearray)):
            result = cloudinary.uploader.upload(file_source)
        elif hasattr(file_source, "read"):  # BytesIO
            result = cloudinary.uploader.upload(file_source)
        elif isinstance(file_source, str) and os.path.exists(file_source):
            result = cloudinary.uploader.upload(file_source)
        else:
            raise ValueError("Fuente de archivo no válida")

        print("✅ Imagen subida:", result["secure_url"])
        return result["secure_url"]

    except Exception as e:
        print("❌ Error al subir imagen:", e)
        return None



