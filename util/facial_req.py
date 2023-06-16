import os

from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QImage
from imutils.video import VideoStream, FPS
import face_recognition
import sys
import imutils
import pickle
import time
import cv2
from gpiozero import LED, Button
from datetime import datetime


# TODO možda pamtiti svaki put kada je zvono stisnuto


class FacialRecognition(QThread):
    update_frame = pyqtSignal(QImage)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

        self.status = True

        self.LED_R = LED(4)
        self.LED_Y = LED(5)
        self.LED_G = LED(6)

        self.BUTTON_BELL = Button(27)  # ring bell
        # self.BUTTON_UNLOCK = Button(22)  # unlock door by admin
        self.BUTTON_DOOR = Button(26)  # door closed after opening

        self.DOOR_OPENED = None
        self.DOOR_UNLOCKED = None
        self.BELL_PRESSED = None
        self.last_bell = None
        self.last_unlock = None
        self.last_open = None

        self.WAIT_SECONDS_OPEN = 15
        self.WAIT_SECONDS_LOCK = 30
        self.BELL_SECONDS = 30

        self.frame = None

        # load the known faces and embeddings along with OpenCV's Haar cascade for face detection
        self.currentname = "unknown"

        self.encodingsP = "encodings.pickle"
        print(f"[INFO] loading encodings from {self.encodingsP} + face detector...")
        with open(self.encodingsP, "rb") as file:
            self.data = pickle.load(file)
        self.encodings_timestamp = os.path.getmtime(self.encodingsP)  # Store initial modification timestamp

        # initialize the video stream and allow the camera sensor to warm up
        self.vs = VideoStream(src=-1, framerate=10).start()
        time.sleep(2.0)

        # start the FPS counter
        self.fps = FPS().start()

        self.reset()

    def reset(self):
        self.lock_door()
        self.bell_off()

        self.DOOR_OPENED = False
        self.last_bell = None
        self.last_unlock = None

    def set_bell(self, value, user="system"):
        self.BELL_PRESSED = value
        print(f"{datetime.now()} - {user} set bell to {value}")

    def bell_on(self):
        if self.BELL_PRESSED:
            return

        self.LED_Y.on()
        self.last_bell = datetime.now()
        self.set_bell(True)

    def bell_off(self, user="system"):
        self.LED_Y.off()
        self.set_bell(False, user)

    def door_closed(self):
        if self.DOOR_UNLOCKED:
            self.DOOR_OPENED = False
            self.lock_door()
            self.last_open = None
            print(f"{datetime.now()} - door is closed")

    def door_open(self):
        if self.DOOR_UNLOCKED:
            self.DOOR_OPENED = True
            self.last_open = datetime.now()
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
        if self.BELL_PRESSED:
            self.LED_R.off()
            self.LED_Y.off()
            self.LED_G.on()

            self.bell_off()

            self.DOOR_UNLOCKED = True
            self.last_unlock = datetime.now()

            print(f"{datetime.now()} - door unlocked for {name}")

    def facial_recognition(self):

        # Detect the face boxes
        boxes = face_recognition.face_locations(self.frame)
        # compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(self.frame, boxes)
        names = []

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known encodings
            matches = face_recognition.compare_faces(self.data["encodings"],
                                                     encoding)
            name = "Unknown"  # if face is not recognized, then print Unknown

            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for each recognized face
                for i in matchedIdxs:
                    name = self.data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                name = max(counts, key=counts.get)

                # If someone in your dataset is identified, print their name on the screen
                if self.currentname != name:
                    self.currentname = name
                    if self.BELL_PRESSED:
                        self.unlock_door(self.currentname)

            # update the list of names
            names.append(name)
        return names, boxes

    def set_boxes(self, boxes, names):
        # loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
            cv2.rectangle(self.frame,
                          pt1=(left, top),
                          pt2=(right, bottom),
                          color=(0, 255, 225),
                          thickness=2)

            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(self.frame,
                        text=name,
                        org=(left, y),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=.8,
                        color=(0, 255, 255),
                        thickness=2)

    @pyqtSlot()
    def handle_unlock_signal(self):
        self.unlock_door(name="admin")

    @pyqtSlot()
    def handle_bell_silent_signal(self):
        if self.BELL_PRESSED:
            self.bell_off(user="admin")

    def process_frame(self):
        # grab the frame from the threaded video stream
        self.frame = self.vs.read()
        self.frame = imutils.resize(self.frame, width=420)

        # run facial recognition, display names if found
        names, boxes = self.facial_recognition() or (None, None)
        if names is not None and boxes is not None:
            self.set_boxes(boxes, names)

        height, width, channel = self.frame.shape
        bytes_per_line = channel * width
        img = QImage(self.frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
        self.update_frame.emit(img)

    def run(self):
        while self.status:
            # Check if encodingsP file has been modified
            if os.path.getmtime(self.encodingsP) > self.encodings_timestamp:
                print("[INFO] Reloading encodings...")
                with open(self.encodingsP, "rb") as file:
                    self.data = pickle.load(file)
                self.encodings_timestamp = os.path.getmtime(self.encodingsP)  # Update modification timestamp

            self.BUTTON_DOOR.when_pressed = self.door_open
            self.BUTTON_DOOR.when_released = self.door_closed
            self.BUTTON_BELL.when_released = self.bell_on

            # conditions to indicate door open for too long
            if not self.last_open is None:
                time_diff = datetime.now() - self.last_open
                if time_diff.total_seconds() >= self.WAIT_SECONDS_OPEN:
                    print("JESI NA BRODU ROĐEN ZATVARAJ VRATA ALO")

            # conditions to indicate door re-lock
            if self.DOOR_UNLOCKED and not self.last_unlock is None and not self.DOOR_OPENED:
                time_diff = datetime.now() - self.last_unlock
                if time_diff.total_seconds() >= self.WAIT_SECONDS_LOCK:
                    self.lock_door()
                    print(f"{datetime.now()} - timeout: door re-locked")

            # bell timeout
            if self.BELL_PRESSED and not self.last_bell is None:
                time_diff = datetime.now() - self.last_bell
                if time_diff.total_seconds() >= self.BELL_SECONDS:
                    self.bell_off(user="timeout")

            self.process_frame()

        sys.exit(-1)
