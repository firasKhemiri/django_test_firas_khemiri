import base64
from io import BytesIO
from PIL import Image as Pil


def encode_to_base64(image):
    input_file = BytesIO(image.read())  # Original image file.
    image_file = BytesIO()  # An in-memory file where the compressed image will be saved.

    img = Pil.open(input_file)
    img.save(image_file, format="jpeg", quality=80, optimize=False)  # The compressed image is saved in 'image_file'.

    binary = image_file.getvalue()  # The binary value of image_file is saved in 'binary'.
    encoded = base64.b64encode(binary)  # Encodes the binary with base64.
    decoded = encoded.decode('ascii')  # Decodes the encoded binary.

    return decoded
