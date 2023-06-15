import os
import shutil
from imutils import paths
import face_recognition
import pickle
import cv2

class TrainModel:
    def __init__(self):
        self.dataset_path = "dataset"
        self.encodings_path = "encodings.pickle"

    def train(self):
        # Collect user information
        image_paths = list(paths.list_images(self.dataset_path))
        known_encodings = []
        known_names = []

        # Loop over the image paths
        for (i, image_path) in enumerate(image_paths):
            # Extract the person name from the image path
            print("[INFO] Processing image {}/{}".format(i + 1, len(image_paths)))
            name = image_path.split(os.path.sep)[-2]

            # Load the input image and convert it from RGB (OpenCV ordering)
            # to dlib ordering (RGB)
            image = cv2.imread(image_path)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input image
            boxes = face_recognition.face_locations(rgb, model="hog")

            # Compute the facial embedding for the face
            encodings = face_recognition.face_encodings(rgb, boxes)

            # Loop over the encodings
            for encoding in encodings:
                # Add each encoding + name to our set of known names and encodings
                known_encodings.append(encoding)
                known_names.append(name)

        # Dump the facial encodings + names to disk
        print("[INFO] Serializing encodings...")
        data = {"encodings": known_encodings, "names": known_names}
        with open(self.encodings_path, "wb") as f:
            f.write(pickle.dumps(data))

    def delete_user(self, user_name):
        folder_path = os.path.join(self.dataset_path, user_name)
        shutil.rmtree(folder_path)
        self.train()
