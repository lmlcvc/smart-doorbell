# Smart Doorbell Project

The Smart Doorbell project is a Raspberry Pi-based application developed as part of a Programming of Embedded Systems course. The project integrates facial recognition to provide a secure and convenient doorbell system that allows authorized users to ring the doorbell and unlock the door. It utilizes a Haar cascade front face model trained on a dataset of allowed users' images to recognize authorized individuals. The project also includes administrative functionalities to manage users, such as adding, editing, and deleting user profiles and doorbell silencing.

## Requirements

To set up and run the Smart Doorbell project, you will need the following:

- Raspberry Pi 3 (or compatible device)
- Camera module compatible with the Raspberry Pi
- Touchscreen display compatible with the Raspberry Pi
- Python 3.x
- OpenCV library
- PyQt5 library

For detailed instructions on installing the required dependencies, refer to the packet installations outlined in the [Tom's Hardware tutorial on Raspberry Pi facial recognition](https://www.tomshardware.com/how-to/raspberry-pi-facial-recognition).

## Use Case

The Smart Doorbell project is designed to enhance home security and provide seamless access control. Here is a typical use case scenario:

1. A homeowner installs the Smart Doorbell system at their front door, which consists of a Raspberry Pi 3 connected to a camera module and a touchscreen display.
2. Authorized users, such as family members or trusted individuals, are enrolled in the system by capturing and storing their facial images.
3. When an authorized user arrives at the door, they can ring the doorbell by pressing the doorbell button located near the camera.
4. The camera captures the user's face, and the facial recognition algorithm matches it against the stored profiles.
5. If the user's face is recognized as an authorized user, the door is automatically unlocked, allowing the user to enter.
6. The system also provides an administrative interface accessible through the touchscreen display, allowing the administrator to manage users, adjust settings, and perform other actions.
7. The administrator can add new users to the system by capturing their facial images or selecting images from the gallery.
8. In case of any issues or the need for manual control, the administrator can manually unlock the door or ignore the doorbell ring without unlocking the door.

The Smart Doorbell project offers an efficient and secure solution for door access control, ensuring that only authorized individuals can enter the premises.


## Usage

Follow the steps below to use the Smart Doorbell application:

1. Connect the Raspberry Pi to the camera module and touchscreen display.
2. Clone the project repository to the Raspberry Pi.
3. Install the required dependencies on the Raspberry Pi using the provided packet installations or instructions from the tutorial.
4. Navigate to the project directory on the Raspberry Pi.
5. Run the application using the following command:

   ```
   python main.py
   ```

6. The Smart Doorbell application window will open, displaying the camera feed and control buttons on the touchscreen display.
7. Users can ring the doorbell by pressing the dedicated doorbell button.
8. The camera captures the user's face, and the facial recognition algorithm identifies the user if they are authorized.
9. If the user is recognized as authorized, the door is automatically unlocked.
10. The administrator can access additional features and functionalities through the control buttons on the touchscreen display.
11. The system can be stopped or closed by clicking the "Stop/Close" button.



## Acknowledgments

The Smart Doorbell project was developed based on the guidance and resources provided by the OpenAI community, the [Tom's

 Hardware tutorial on Raspberry Pi facial recognition](https://www.tomshardware.com/how-to/raspberry-pi-facial-recognition), and the [Qt for Python Examples on integrating OpenCV](https://doc.qt.io/qtforpython-6/examples/example_external_opencv.html).
