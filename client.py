import base64

with open("image.jpeg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())
