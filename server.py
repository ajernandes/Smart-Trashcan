import asyncio
import websockets
import base64
import io
import cv2
from imageio import imread
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.applications import imagenet_utils
from tensorflow.keras.preprocessing.image import img_to_array
from imutils.object_detection import non_max_suppression
import numpy as np
import argparse

print("Num GPU's Avaliable: ", len(tf.config.list_physical_devices('GPU')))
def selective_search(image, method="fast"):
    # initialize OpenCV's selective search implementation and set the
    # input image
    ss = cv2.ximgproc.segmentation.createSelectiveSearchSegmentation()
    ss.setBaseImage(image)
    # check to see if we are using the *fast* but *less accurate* version
    # of selective search
    if method == "fast":
        ss.switchToSelectiveSearchFast()
    # otherwise we are using the *slower* but *more accurate* version
    else:
        ss.switchToSelectiveSearchQuality()
    # run selective search on the input image
    rects = ss.process()
    # return the region proposal bounding boxes
    return rects


async def hello(websocket, path):
    image = await websocket.recv()
    #img = imread(io.BytesIO(base64.b64decode(name)))

        # grab the label filters command line argument
    labelFilters = None
    # if the label filter is not empty, break it into a list
    if labelFilters is not None:
        labelFilters = labelFilters.lower().split(",")

        # load ResNet from disk (with weights pre-trained on ImageNet)
    print("[INFO] loading ResNet...")
    mlabelFilters = None
    # if the label filter is not empty, break it into a list
    if labelFilters is not None:
        labelFilters = labelFilters.lower().split(",")

        # load ResNet from disk (with weights pre-trained on ImageNet)
    print("[INFO] loading ResNet...")
    model = ResNet50(weights="imagenet")
    # load the input image from disk and grab its dimensions
    im_bytes = base64.b64decode(image)
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
    image = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

    image = cv2.resize(image,None,fx=0.1,fy=0.1)
    (H, W) = image.shape[:2]

    # run selective search on the input image
    print("[INFO] performing selective search with '{}' method...".format(
        "quality"))
    rects = selective_search(image, "quality")
    print("[INFO] {} regions found by selective search".format(len(rects)))
    # initialize the list of region proposals that we'll be classifying
    # along with their associated bounding boxes
    proposals = []
    boxes = []

    # loop over the region proposal bounding box coordinates generated by
    # running selective search
    for (x, y, w, h) in rects:
        # if the width or height of the region is less than 10% of the
        # image width or height, ignore it (i.e., filter out small
        # objects that are likely false-positives)
        if w / float(W) < 0.1 or h / float(H) < 0.1:
            continue
        # extract the region from the input image, convert it from BGR to
        # RGB channel ordering, and then resize it to 224x224 (the input
        # dimensions required by our pre-trained CNN)
        roi = image[y:y + h, x:x + w]
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        roi = cv2.resize(roi, (224, 224))
        # further preprocess by the ROI
        roi = img_to_array(roi)
        roi = preprocess_input(roi)
        # update our proposals and bounding boxes lists
        proposals.append(roi)
        boxes.append((x, y, w, h))

        # convert the proposals list into NumPy array and show its dimensions
    proposals = np.array(proposals)
    print("[INFO] proposal shape: {}".format(proposals.shape))
    # classify each of the proposal ROIs using ResNet and then decode the
    # predictions
    print("[INFO] classifying proposals...")
    preds = model.predict(proposals)
    preds = imagenet_utils.decode_predictions(preds, top=1)
    # initialize a dictionary which maps class labels (keys) to any
    # bounding box associated with that label (values)
    labels = {}

    # loop over the predictions
    for (i, p) in enumerate(preds):
        # grab the prediction information for the current region proposal
        (imagenetID, label, prob) = p[0]
        # only if the label filters are not empty *and* the label does not
        # exist in the list, then ignore it
        if labelFilters is not None and label not in labelFilters:
            continue
        # filter out weak detections by ensuring the predicted probability
        # is greater than the minimum probability
        if prob >= 0.9:
            # grab the bounding box associated with the prediction and
            # convert the coordinates
            (x, y, w, h) = boxes[i]
            box = (x, y, x + w, y + h)
            # grab the list of predictions for the label and add the
            # bounding box + probability to the list
            L = labels.get(label, [])
            L.append((box, prob))
            labels[label] = L

            # loop over the labels for each of detected objects in the image
    lst = []
    for label in labels.keys():
        # clone the original image so that we can draw on it
        print("[INFO] showing results for '{}'".format(label))
        clone = image.copy()
        # loop over all bounding boxes for the current label

        # show the results *before* applying non-maxima suppression, then
        # clone the image again so we can display the results *after*
        # applying non-maxima suppression
        lst.append(label)

    await websocket.send(lst)

start_server = websockets.serve(hello, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()