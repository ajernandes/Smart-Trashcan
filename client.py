import base64
from websocket import create_connection
ws = create_connection("ws://localhost:8080")
with open("image.jpeg", "rb") as img_file:
    encoded_string = base64.b64encode(img_file.read())
    ws.send(encoded_string)
    print("Sent")
    print("Receiving...")
    result =  ws.recv()
    print("Received '%s'" % result)
    ws.close()



