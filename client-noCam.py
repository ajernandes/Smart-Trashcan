import base64
from websocket import create_connection


ws = create_connection("ws://192.168.1.2:8080")
with open("image.jpg", "rb") as img_file:
    encoded_string = base64.b64encode(img_file.read())
    ws.send(encoded_string)
    print("Sending...")
    result =  ws.recv()
    print("Received '%s'" % result)
    ws.close()