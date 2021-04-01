import base64
from websocket import create_connection
from picamera import PiCamera

camera = PiCamera()

ws = create_connection("ws://192.168.1.2:8080")
camera.capture('image.jpg')
with open("image.jpg", "rb") as img_file:
    encoded_string = base64.b64encode(img_file.read())
    ws.send(encoded_string)
    print("Processing")
    result =  ws.recv()
    if result:
        print("KEEP")
    else:
        print("DUMP")
    print("Received '%s'" % result)
    ws.close()