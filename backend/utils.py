import os
import io
from PIL import Image
from fastapi import UploadFile
from fastapi import HTTPException
from logging_settings import get_logger


logger = get_logger(__name__)


async def save_image_static(path_to_file: str, filename: str, image: UploadFile):
    """Save image to static folder in .jpg format and return path to file."""
    if not path_to_file.startswith('./static/'):
        raise Exception('path_to_file must start with ./static/')

    # check file format
    os.makedirs(path_to_file, exist_ok=True)
    file_path = os.path.join(path_to_file, f'{filename}.jpg')
    try:
        # convert image to .jpg and save
        image = Image.open(io.BytesIO(await image.read()))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(file_path, 'JPEG')
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail='Unknown error occurred')

    return file_path
