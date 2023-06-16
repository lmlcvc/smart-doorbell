import os
import pickle

import cv2
import face_recognition
from imutils import paths


def get_users():
    users = []
    dataset_folder = "dataset"
    if os.path.exists(dataset_folder) and os.path.isdir(dataset_folder):
        users = [{"name": user_folder, "image": os.path.join(dataset_folder, user_folder, images[0])}
                 for user_folder in os.listdir(dataset_folder)
                 if os.path.isdir(os.path.join(dataset_folder, user_folder))
                 for images in [os.listdir(os.path.join(dataset_folder, user_folder))]
                 if images]
    return users


class TrainModel:
    def __init__(self):
        self.dataset_path = "dataset"
        self.model_path = "haarcascade_frontalface_default.xml"
        self.encodings_path = "encodings.pickle"
        self.known_names = []
        self.known_encodings = []
        self.load_encodings()

    def load_encodings(self):
        self.known_encodings = []
        self.known_names = []
        if os.path.exists(self.encodings_path):
            with open(self.encodings_path, 'rb') as file:
                data = pickle.load(file)
                if isinstance(data, dict) and "encodings" in data and "names" in data:
                    self.known_encodings = data["encodings"]
                    self.known_names = data["names"]

    def save_encodings(self):
        data = {"encodings": self.known_encodings, "names": self.known_names}
        with open(self.encodings_path, "wb") as f:
            f.write(pickle.dumps(data))

    def user_exists(self, username):
        user_directory = os.path.join(self.dataset_path, username)
        return os.path.isdir(user_directory)

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
        self.save_encodings()

    def rename_user(self, old_name, new_name):
        print(f"Renaming {old_name} to {new_name}\n")

        if old_name in self.known_names:
            for index, name in enumerate(self.known_names):
                if name == old_name:
                    self.known_names[index] = new_name

            self.save_encodings()
            self.load_encodings()

    def delete_user(self, name):
        print(f"Deleting user {name}")

        print(self.known_names, len(self.known_encodings))
        if name in self.known_names:
            for index, known_name in enumerate(self.known_names):
                if known_name == name:
                    del self.known_names[index]
                    del self.known_encodings[index]
        print(self.known_names, len(self.known_encodings))

        # index = self.known_names.index(name)
        # del self.known_names[index]
        # del self.known_encodings[index]
        self.save_encodings()
        self.load_encodings()
