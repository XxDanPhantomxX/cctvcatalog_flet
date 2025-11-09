from PIL import Image
from datetime import datetime
import os

IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

def save_uploaded_file(file_result):
    if not file_result:
        return None
    fname = f"{int(datetime.now().timestamp())}_{file_result.name}"
    path = os.path.join(IMAGES_DIR, fname)
    bytes_data = file_result.read_bytes()
    with open(path, 'wb') as f:
        f.write(bytes_data)
    try:
        im = Image.open(path)
        im.thumbnail((800,800))
        im.save(path)
    except Exception:
        pass
    return path