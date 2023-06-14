#! /usr/bin/python
import sys

from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtGui import QImage
# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2

from gpiozero import LED, Button
from datetime import datetime


# TODO alarm if door open for too long
# TODO zvono vrijedi koliko sekundi amin
# TODO možda pamtiti svaki put kada je zvono stisnuto


class FacialRecognition(QThread):
    update_names = pyqtSignal(str, int, int)
    update_frame = pyqtSignal(QImage)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

        self.LED_R = LED(4)
        self.LED_Y = LED(5)
        self.LED_G = LED(6)

        self.BUTTON_BELL = Button(27)  # ring bell
        # self.BUTTON_UNLOCK = Button(22)  # unlock door by admin
        self.BUTTON_DOOR = Button(26)  # door closed after opening

        self.DOOR_OPENED = None
        self.DOOR_UNLOCKED = None
        self.BELL_PRESSED = None
        self.FACE_FOUND = None
        self.last_bell = None
        self.last_unlock = None

        self.WAIT_SECONDS = 15
        self.BELL_SECONDS = 30

        self.frame = None

        # Initialize 'currentname' to trigger only when a new person is identified.
        self.currentname = "unknown"
        # Determine faces from encodings.pickle file model created from train_model.py
        self.encodingsP = "encodings.pickle"

        # load the known faces and embeddings along with OpenCV's Haar
        # cascade for face detection
        print("[INFO] loading encodings + face detector...")
        self.data = pickle.loads(open(self.encodingsP, "rb").read())

        # initialize the video stream and allow the camera sensor to warm up
        self.vs = VideoStream(src=-1, framerate=10).start()
        # self.vs = VideoStream(usePiCamera=True).start()
        time.sleep(2.0)

        # start the FPS counter
        self.fps = FPS().start()

        self.reset()

        self.status = True
        # while self.status:
        # self.run()

    def reset(self):
        self.lock_door()
        self.bell_off()

        self.DOOR_OPENED = False
        self.FACE_FOUND = False
        self.last_bell = None
        self.last_unlock = None

    def set_bell(self, value):
        self.BELL_PRESSED = value
        print(f"{datetime.now()} - bell set to {value}")

    def bell_on(self):
        if self.BELL_PRESSED:
            return

        self.LED_Y.on()
        self.last_bell = datetime.now()
        self.set_bell(True)

    def bell_off(self):
        self.LED_Y.off()
        self.set_bell(False)

    def door_closed(self):
        if self.DOOR_UNLOCKED:
            self.DOOR_OPENED = False
            self.lock_door()
            print(f"{datetime.now()} - door is closed")

    def door_open(self):
        if self.DOOR_UNLOCKED:
            self.DOOR_OPENED = True
            self.FACE_FOUND = False
            print(f"{datetime.now()} - door is opened")
        else:
            print(f"{datetime.now()} - cannot open locked door")

    def lock_door(self):
        self.LED_R.on()
        self.LED_Y.off()
        self.LED_G.off()

        self.DOOR_UNLOCKED = False
        self.last_unlock = None  # TODO should we check both for last unlock and last open

        print(f"{datetime.now()} - door locked")

    def unlock_door(self, name):
        self.LED_R.off()
        self.LED_Y.off()
        self.LED_G.on()

        self.bell_off()

        self.DOOR_UNLOCKED = True
        self.last_unlock = datetime.now()

        print(f"{datetime.now()} - door unlocked for {name}")

    def facial_recognition(self):
        # Detect the fce boxes
        boxes = face_recognition.face_locations(self.frame)
        # compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(self.frame, boxes)
        names = []

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known
            # encodings
            matches = face_recognition.compare_faces(self.data["encodings"],
                                                     encoding)
            name = "Unknown"  # if face is not recognized, then print Unknown

            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces then initialize a
                # dictionary to count the total number of times each face
                # was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for
                # each recognized face
                for i in matchedIdxs:
                    name = self.data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number
                # of votes (note: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                name = max(counts, key=counts.get)

                # If someone in your dataset is identified, print their name on the screen
                if self.currentname != name:
                    currentname = name

                    self.unlock_door(currentname)

            # update the list of names
            names.append(name)
            return names, boxes

    def set_box_names(self, boxes, names):
        # loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
            y = top - 15 if top - 15 > 15 else top + 15
            self.update_names.emit(name, left, y)  # TODO coordinates

    def run(self):
        # loop over frames from the video file stream
        while self.status:
            self.BUTTON_DOOR.when_pressed = self.door_open
            self.BUTTON_DOOR.when_released = self.door_closed
            if not self.BELL_PRESSED:
                self.BUTTON_BELL.when_released = self.bell_on

            # conditions to indicate door re-lock
            if not self.last_unlock is None:
                time_diff = datetime.now() - self.last_unlock
                if time_diff.total_seconds() >= self.WAIT_SECONDS:
                    print("JESI NA BRODU ROĐEN ZATVARAJ VRATA ALO")

            # bell timeout
            if self.BELL_PRESSED and not self.last_bell is None:
                time_diff = datetime.now() - self.last_bell
                if time_diff.total_seconds() >= self.BELL_SECONDS:
                    self.bell_off()

            # grab the frame from the threaded video stream and resize it
            # to 500px (to speedup processing)
            self.frame = self.vs.read()
            self.frame = imutils.resize(self.frame, width=420)

            if self.BELL_PRESSED is True:
                names, boxes = self.facial_recognition() or (None, None)
                if names is not None and boxes is not None:
                    self.set_box_names(boxes, names)

            # print(type(self.frame))
            # print(type(self.frame.data))
            # print(self.frame)
            height, width, channel = self.frame.shape
            bytes_per_line = channel * width
            img = QImage(self.frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
            self.update_frame.emit(img)

        sys.exit(-1)

    #     # display the image to our screen
    #     cv2.imshow("Camera stream", self.frame)
    #     key = cv2.waitKey(1) & 0xFF
    #
    #     # quit when 'q' key is pressed
    #     if key == ord("q"):
    #         break
    #
    #     # update the FPS counter
    #     self.fps.update()
    #
    # # stop the timer and display FPS information
    # self.fps.stop()
    # print("[INFO] elasped time: {:.2f}".format(self.fps.elapsed()))
    # print("[INFO] approx. FPS: {:.2f}".format(self.fps.fps()))
    #
    # # do a bit of cleanup
    # cv2.destroyAllWindows()
    # self.vs.stop()

# TODO remove when integrated to main.py
# if __name__ == "__main__":
#     facial_recognition = FacialRecognition()
#     facial_recognition.run()
