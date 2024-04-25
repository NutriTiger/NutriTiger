#----------------------------------------------------------------------
# Contributors:
# Oyu Enkhbold
#
# To support personal nutrition information
#----------------------------------------------------------------------
from bson.objectid import ObjectId
from PIL import Image
import io
from bson.binary import Binary
import os


def allowed_file(file):
def allowed_file(file):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic'}
    filename = file.filename
    new_filename = filename
    format = new_filename.rsplit('.', 1)[1].lower()
    filename = file.filename
    new_filename = filename
    format = new_filename.rsplit('.', 1)[1].lower()
    if format == 'jpg':
        format = 'jpeg'
    if format == 'heic':
        new_filename.replace(".heic", ".jpg")
        format = 'jpeg'
    # os.rename(file, new_filename)
    return '.' in filename and format in ALLOWED_EXTENSIONS, format.upper(), file


def edit_photo_width(file, format):
    try:
        im = Image.open(file.stream)
        # Specify the desired width
        desired_width = 210
        # Calculate the new height to maintain the aspect ratio
        ratio = desired_width / im.width
        new_height = int(im.height * ratio)
        # Resize the image
        im = im.resize((desired_width, new_height), Image.Resampling.LANCZOS)

        # Save the resized image to a bytes buffer
        image_bytes = io.BytesIO()
        im.save(image_bytes, format=format) 
        image_bytes.seek(0)
        image_data = Binary(image_bytes.read())

        return image_data
    except IOError:
        return "n/a"