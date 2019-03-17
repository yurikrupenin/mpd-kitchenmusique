import logging
import time

import cv2
import numpy as np

import kitchenmusique.config as config


class PersonDetector:

    def __init__(self):
        self.logger = logging.getLogger("kitchenmusique")

        self.logger.debug("Initializing neural network...")

        # read detection classes labels
        classdesc = open(config.CONFIG_YOLO_CLASSES_FILE, 'r')
        self.classes = [line.strip() for line in classdesc.readlines()]

        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))

        # initialize neural net
        self.network = cv2.dnn.readNetFromDarknet(config.CONFIG_YOLO_CFG_FILE, config.CONFIG_YOLO_WEIGHTS_FILE)
        self.network.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
        self.network.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        self.logger.debug("Network initialized.")


    def __get_output_layers(self):
        layer_names = self.network.getLayerNames()

        output_layers = [layer_names[i[0] - 1] for i in self.network.getUnconnectedOutLayers()]

        return output_layers


    def __visualize_prediction(self, img, class_id, confidence, x, y, x_plus_w, y_plus_h):

        label = "{0} [{1}]".format(str(self.classes[class_id]), confidence)

        color = self.colors[class_id]

        cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)

        cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return img


    def visualize(self, image):
        width = image.shape[1]
        height = image.shape[0]

        blob = cv2.dnn.blobFromImage(image, 1/255.0, (416,416),  swapRB=True, crop=False)

        self.network.setInput(blob)

        outputs = self.network.forward(self.__get_output_layers())



        class_ids = []
        confidences = []
        boxes = []
        nms_threshold = 0.4

        for out in outputs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > config.CONFIG_YOLO_CONFIDENCE_THRESHOLD:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])


        indices = cv2.dnn.NMSBoxes(boxes, confidences, config.CONFIG_YOLO_CONFIDENCE_THRESHOLD, nms_threshold)

        for i in indices:
            i = i[0]
            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]

            image = self.__visualize_prediction(
                image,
                class_ids[i],
                confidences[i],
                round(x),
                round(y),
                round(x + w),
                round(y + h)
            )

        cv2.imshow("object detection", image)
        cv2.waitKey(1)

