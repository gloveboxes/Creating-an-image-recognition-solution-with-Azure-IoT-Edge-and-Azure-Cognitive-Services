# To make python 2 and python 3 compatible code
from __future__ import absolute_import

from threading import Thread
import time
import sys
if sys.version_info[0] < 3:  # e.g python version <3
    import cv2
else:
    import cv2
    # from cv2 import cv2

# import the Queue class from Python 3
if sys.version_info >= (3, 0):
    from queue import Queue
# otherwise, import the Queue class for Python 2.7
else:
    from Queue import Queue

# This class reads all the video frames in a separate thread and always has the keeps only the latest frame in its queue to be grabbed by another thread


class VideoStream(object):
    def __init__(self, path, queueSize=3):
        print('opening camera')
        self.stream = cv2.VideoCapture(0)
        # self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        # self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        # self.stream.set(cv2.CAP_PROP_SETTINGS, 1 )
        self.stopped = False
        self.Q = Queue(maxsize=queueSize)

    def start(self):
        # start a thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        previousFrame = None
        previousDiff = 0
        delta = 0
        skippedFrames = 0
        queuedFrames = 0

        try:
            while True:
                if self.stopped:
                    return

                if not self.Q.full():
                    (grabbed, frame) = self.stream.read()

                    # if the `grabbed` boolean is `False`, then we have
                    # reached the end of the video file
                    if not grabbed:
                        self.stop()
                        return
                    # new_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    if type(previousFrame) == type(frame):
                        difference = cv2.subtract(frame, previousFrame)
                        b, g, r = cv2.split(difference)
                        diff = cv2.countNonZero(b) + cv2.countNonZero(g) + cv2.countNonZero(r)
                        delta = abs(diff - previousDiff)

                        previousFrame = frame
                        previousDiff = diff
                    else:
                        previousFrame = frame

                    if delta > 200000:
                        # Clean the queue
                        while not self.Q.empty():
                            self.Q.get()
                        self.Q.put(frame)
                        queuedFrames = queuedFrames + 1
                    else:
                        skippedFrames = skippedFrames + 1

        except Exception as e:
            print("got error: "+str(e))

    def read(self):
        return self.Q.get(block=True)

    def more(self):
        return self.Q.qsize() > 0

    def stop(self):
        self.stopped = True

    def __exit__(self, exception_type, exception_value, traceback):
        self.stream.release()
