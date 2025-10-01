from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from global_variables import VideoParameters

#abstractclass
class CameraClient(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def take_picture(self):
        pass

    @abstractmethod
    def get_frame(self):
        pass

class ComputerVisionCamera(CameraClient):
    def __init__(self):
        try:
            import cv2
        except:
            raise Exception
        self.cv2 = cv2
        self.camera = None

    def start(self):
        self.camera = self.cv2.VideoCapture(0)
        print("Starting Camera")
        if not self.camera.isOpened():
            print("Camera not found")
            raise Exception
        self.camera.set(self.cv2.CAP_PROP_FRAME_WIDTH, VideoParameters.WIDTH)
        self.camera.set(self.cv2.CAP_PROP_FRAME_HEIGHT, VideoParameters.HEIGHT)

    def stop(self):
        self.camera.release()

    def get_frame(self):
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                frame = self.cv2.flip(frame, 0)
                #Rotation not needed
                #frame= self.cv2.rotate(frame, self.cv2.ROTATE_90_CLOCKWISE)
                # Convert to RGB for Kivy
                frame = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
                return frame
            else:
                print("Error: Could not capture photo frame.")

        print("Not returning Photo")
        return None

    def take_picture(self):
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                frame_mirrored = self.cv2.flip(frame, 0)
                frame_rotated = self.cv2.rotate(frame_mirrored, self.cv2.ROTATE_90_CLOCKWISE)
            #TODO: put that in a separate handler this does not belong in the camera client
                filename = datetime.now().strftime(
                    str(Path.cwd().joinpath('Photos').joinpath('photo_%Y%m%d_%H%M%S.jpg')))
                self.cv2.imwrite(filename, frame)
            else:
                print("Error: Could not capture photo frame.")
