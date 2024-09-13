#----------------------------------------------------------------------
# Contributors:
# Oyu Enkhbold
#
# To upload images as a part of custom nutrition information
#----------------------------------------------------------------------
import os
import cloudinary.uploader
import cloudinary.api
import dotenv
import sys

dotenv.load_dotenv()
cloudinary.config(
    cloud_name=os.getenv("cloud_name"), 
    api_key=os.getenv("api_key"), 
    api_secret=os.getenv("api_secret")
)

# Inputs a file filename and returns whether or not it
# is an allowed files type, as well as adjusting
# file extension to be readable by cloudinary API
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic'}
    new_filename = filename
    format = new_filename.rsplit('.', 1)[1].lower()

    if format == 'jpg':
        format = 'jpeg'
    if format == 'heic':
        new_filename.replace(".heic", ".jpg")
        format = 'jpeg'
    return '.' in filename and format in ALLOWED_EXTENSIONS, format.upper()

# Takes an image and returns whether or not it is within
# the 10 MB limit
def allowed_size(photo):
    max_size = 10 * 1024 * 1024  # 10 MB in bytes

    # Move the read cursor to the end of the file
    photo.seek(0, 2)
    # Get the position of the cursor—this is the file's size in bytes
    file_size = photo.tell()
    # Reset the cursor to the start of the file
    photo.seek(0)

    return file_size <= max_size

# Takes a photo id and deletes it from Cloudinary,
# returns response or error message.
def delete_one_photo(public_id):
    dotenv.load_dotenv()
    cloudinary.config(
        cloud_name=os.getenv("cloud_name"), 
        api_key=os.getenv("api_key"), 
        api_secret=os.getenv("api_secret")
    )
    try:
        response = cloudinary.uploader.destroy(public_id)
        return response  # This will return the result of the delete operation
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    
# Takes a list of photo ids and deletes them from Cloudinary,
# returns response or error message.
def delete_many_photos(public_ids):
    dotenv.load_dotenv()
    cloudinary.config(
        cloud_name=os.getenv("cloud_name"), 
        api_key=os.getenv("api_key"), 
        api_secret=os.getenv("api_secret")
    )

    try:
        # Ensure that the 'public_ids' parameter name is used correctly
        response = cloudinary.api.delete_resources(public_ids=public_ids)
        return True
    except Exception as e:
        print("fails in delete_many_photos")
        print(f"An error occurred: {str(e)}", file = sys.stderr)
        return False


    



