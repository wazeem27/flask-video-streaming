import math
import concurrent.futures
import urllib.request
import cv2
import queue
import threading
import time

from temperature import TemperatureQueue


ds_factor = 0.9

# For normalized storing temperature
temperature_queue = TemperatureQueue()
print(temperature_queue)

TEMP_THRESHOLD = 0
DISTANCE_OFFSET = [0, 0, 1, 1, 0, 0, 0, 0, 0, 0]


face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


class VideoCamera(object):

    def __init__(self):
        self.temp_value = 0
        self.cap = cv2.VideoCapture("http://192.168.1.10:8080/video")
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()
        self._temp_api = False
        self._initial_value = 98.40

    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        return self.q.get()
    
    def __del__(self):
        """Release video camera"""
        self.video.release()

    def get_frame(self):
        """
        Process each video frames
        """
        image = self.read()
        image = cv2.resize(image, None, fx=ds_factor, fy=ds_factor, interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_rects = face_cascade.detectMultiScale(gray, 1.3, 5)

        global TEMP_THRESHOLD
        global temperature_queue
        if TEMP_THRESHOLD == 0:
            self.temp_value = float(self.get_temp_value())+1
            TEMP_THRESHOLD += 1
            self._temp_api = True

        elif TEMP_THRESHOLD == 20:
            TEMP_THRESHOLD = 0
            self._temp_api = False

        else:
            TEMP_THRESHOLD += 1
            self._temp_api = False

        for (x,y,w,h) in face_rects:
            cv2.rectangle(image, (x, y),(x+w, y+h), (30, 255, 255), 2)
            distance = int(round(self._pixel_to_distance(w)/25))

            # Check if the temperature value is valid
            if  self._temp_api and temperature_queue.is_valid(self.temp_value):
                temperature = self.temp_value + DISTANCE_OFFSET[distance]

                # Added normalized temperature value into Temperature Queue
                temperature_queue.enqueue(temperature)
                temp_average = temperature_queue.average()
                #cv2.putText(image, str(distance)+" feet", (x, y-30),
                #            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                cv2.putText(image, str(temp_average)+'F', (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            else:
                #temperature_queue.enqueue(self._initial_value)
                #cv2.putText(image, str(distance)+" feet", (x, y-30),
                #            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                # Fetch the prevous temperature value
                temp_average = temperature_queue.average()
                cv2.putText(image, str(temp_average)+'F', (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def get_temp_value(self):
        temp_value = urllib.request.urlopen('http://127.0.0.1:5000/temp')
        if temp_value.status == 200:
            self.temp_value = temp_value.read().decode('utf-8')[:-1]
            #print(self.temp_value)
            return self.temp_value
        return self.temp_value

    @staticmethod
    def _pixel_to_distance(pixel):
        """Converts pixel value to distance in inches
        params:
            pix : pixel value
        """
        return 81.34 * math.pow(math.e, -0.0039646 * pixel)
