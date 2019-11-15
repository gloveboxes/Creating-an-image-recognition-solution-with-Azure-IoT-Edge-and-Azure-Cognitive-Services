# To make python 2 and python 3 compatible code
# from __future__ import division
# from __future__ import absolute_import

# Imports
import text2speech
from VideoStream import VideoStream
# import VideoStream
import os.path
import base64
import time
import json
import requests
import numpy
import sys
if sys.version_info[0] < 3:  # e.g python version <3
    import cv2
else:
    import cv2
    from cv2 import cv2


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

    def __localize_text(self, key):
        value = None
        if self.speech_map is not None:
            result = list(
                filter(lambda text: text['key'] == key, self.speech_map))
            if len(result) > 0:
                value = result[0]['value']
        return value

    def __init__(
            self,
            videoPath,
            azureSpeechServiceKey,
            predictThreshold,
            imageProcessingEndpoint,
            sendToHubCallback,
            speechMapFileName
    ):
        self.videoPath = videoPath

        self.predictThreshold = predictThreshold
        self.imageProcessingEndpoint = imageProcessingEndpoint
        self.imageProcessingParams = ""
        self.sendToHubCallback = sendToHubCallback


        if self.__IsInt(videoPath):
            # case of a usb camera (usually mounted at /dev/video* where * is an int)
            self.isWebcam = True

        self.vs = None

        self.speech_map = None
        self.speech_voice = 'en-AU-Catherine'

        self.speech_map_filename = speechMapFileName

        if speechMapFileName is not None and os.path.isfile(self.speech_map_filename):
            with open(self.speech_map_filename, encoding='utf-8') as f:
                json_data = json.load(f)
                self.speech_voice = json_data.get('voice')
                self.speech_map = json_data.get('map')

        self.tts = text2speech.TextToSpeech(
            azureSpeechServiceKey, enableMemCache=True, enableDiskCache=True, voice=self.speech_voice)
        
        text = self.__localize_text('Starting scanner')
        self.tts.play('Starting scanner' if text is None else text)


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
            print("retry inference")
            return []

        predictions = response.json()['predictions']
        sortResponse = sorted(
            predictions, key=lambda k: k['probability'], reverse=True)[0]
        probability = sortResponse['probability']

        print("label: {}, probability {}".format(
            sortResponse['tagName'], sortResponse['probability']))

        if sortResponse['tagName'] == 'Hand':
            lastTagSpoken = sortResponse['tagName']
            return []

        if probability > self.predictThreshold and sortResponse['tagName'] != lastTagSpoken:
            lastTagSpoken = sortResponse['tagName']
            print('text to speech ' + lastTagSpoken)

            text = self.__localize_text(lastTagSpoken)
            self.tts.play(self.__buildSentence(lastTagSpoken) if text is None else text)

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

            # slow things down a bit - 4 frame a second is fine for demo purposes and less battery drain and lower Raspberry Pi CPU Temperature
            time.sleep(0.25)

    def __exit__(self, exception_type, exception_value, traceback):
        pass
