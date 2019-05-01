# To make python 2 and python 3 compatible code
from __future__ import division
from __future__ import absolute_import

# Imports
import sys
if sys.version_info[0] < 3:  # e.g python version <3
    import cv2
else:
    import cv2
    from cv2 import cv2
import numpy
import requests
import json
import time
import base64
import time

import VideoStream
from VideoStream import VideoStream
import text2speech

maxRetry = 5
lastTagSpoken = ''
count = 0


class CameraCapture(object):

    def __IsInt(self, string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    def __init__(
            self,
            videoPath,
            azureSpeechServiceKey,
            predictThreshold,
            imageProcessingEndpoint,
            sendToHubCallback=None
    ):
        self.videoPath = videoPath
        self.tts = text2speech.TextToSpeech(azureSpeechServiceKey)
        self.predictThreshold = predictThreshold
        self.imageProcessingEndpoint = imageProcessingEndpoint
        self.imageProcessingParams = ""
        self.sendToHubCallback = sendToHubCallback
        self.tts.play('Starting scanner')

        if self.__IsInt(videoPath):
            # case of a usb camera (usually mounted at /dev/video* where * is an int)
            self.isWebcam = True

        self.vs = None

    def __buildSentence(self, tag):
        vowels = ('a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U')
        sentence = 'You scanned '
        if tag.startswith(vowels):
            sentence = sentence + 'an '
        else:
            sentence = sentence + 'a '
        return sentence + tag

    def __sendFrameForProcessing(self, frame):
        global count, lastTagSpoken
        count = count + 1
        print("sending frame to model: " + str(count))

        headers = {'Content-Type': 'application/octet-stream'}

        retry = 0
        while retry < maxRetry:
            try:
                response = requests.post(self.imageProcessingEndpoint, headers=headers,
                                         params=self.imageProcessingParams, data=frame)
                break
            except:
                retry = retry + 1
                print(
                    'Image Classification REST Endpoint - Retry attempt # ' + str(retry))
                time.sleep(retry)

        if retry >= maxRetry:
            return []

        predictions = response.json()['predictions']
        sortResponse = sorted(
            predictions, key=lambda k: k['probability'], reverse=True)[0]
        probability = sortResponse['probability']

        if probability > self.predictThreshold and sortResponse['tagName'] != lastTagSpoken:
            lastTagSpoken = sortResponse['tagName']
            self.tts.play(self.__buildSentence(sortResponse['tagName']))
            return json.dumps(predictions)
        else:
            return []

    def __displayTimeDifferenceInMs(self, endTime, startTime):
        return str(int((endTime-startTime) * 1000)) + " ms"

    def __enter__(self):
        self.vs = VideoStream(int(self.videoPath)).start()
        # needed to load at least one frame into the VideoStream class
        time.sleep(1.0)

        return self

    def start(self):

        frameCounter = 0
        while True:
            frameCounter += 1
            frame = self.vs.read()

            if self.imageProcessingEndpoint != "":

                encodedFrame = cv2.imencode(".jpg", frame)[1].tostring()
                try:
                    response = self.__sendFrameForProcessing(encodedFrame)
                    # print(response)
                    # forwarding outcome of external processing to the EdgeHub
                    if response != "[]" and self.sendToHubCallback is not None:
                        try:
                            self.sendToHubCallback(response)
                        except:
                            print(
                                'Issue sending telemetry')
                except:
                    print('connectivity issue')

            # slow things down a bit - 2 frame a second is fine for demo purposes and less battery drain and lower Raspberry Pi CPU Temperature
            time.sleep(0.5)

    def __exit__(self, exception_type, exception_value, traceback):
        pass
