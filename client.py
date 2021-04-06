import base64
from websocket import create_connection
from picamera import PiCamera
import random


#This uses the camera on the raspberry pi to take a picture, and then sends it as a base 64 encoded string over a websocket connection
#This also impliments testing protocols, which allowed easy and quick testing and recording

url = "ws://192.168.1.2:8080"

camera = PiCamera()

items = ["paper towel", "platic fork/spoon", "banana", "mint wrappers", "paper cup", "plastic bag", "candy wrapper", "condoment containers"]



count = len(open('results.csv', 'w+').readlines(  ))
rand = random.random()
if rand <= 0.8:
    i = 0
else:
    i = int(random.random() * len(items) + 1)
print(items[i])
input("Press Enter to continue...")
ws = create_connection(url)

camera.capture("image_" + str(count) + ".jpg")
with open("image_" + str(count) + ".jpg", "rb") as img_file:
    encoded_string = base64.b64encode(img_file.read())
    ws.send(encoded_string)
    print("Processing")
    result =  ws.recv()
    f = open("results.csv", "a")
    if result == "True":
        print("KEEP")
        f.write(items[i] + ',' + "Kept" + "," + str(items[i] == "paper towel") + "\n")
    else:
        print("DUMP")
        f.write(items[i] + ',' + "Tossed" + "," + str(items[i] != "paper towel") + "\n")

    print("Received '%s'" % result)
    f.close()
    ws.close()