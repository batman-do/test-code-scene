import cv2
import requests


class ImageLinker:
    def __init__(
        self, service_url="http://172.18.5.44:8000/mlbigdata/cv/checkin/upload_checkin"
    ):
        self.service_url = service_url

    def create_link(self, image_file):
        image = cv2.imread(image_file)
        image_url = requests.post(
            self.service_url,
            files={"image": cv2.imencode(".jpg", image)[1].tobytes()},
            timeout=60,
        ).json()["url"]["face_image"]

        return image_url
