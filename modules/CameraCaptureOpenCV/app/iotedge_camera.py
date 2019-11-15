# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import os
import random
import sys
import time
import ptvsd

# ptvsd.enable_attach(address=('0.0.0.0', 5678))
# ptvsd.wait_for_attach()


from iothub_client import IoTHubModuleClient, IoTHubClientError, IoTHubTransportProvider
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError

import CameraCapture
from CameraCapture import CameraCapture


# global counters
SEND_CALLBACKS = 0


def send_to_Hub_callback(strMessage):
    if strMessage == []:
        return
    message = IoTHubMessage(bytearray(strMessage, 'utf8'))
    prop_map = message.properties()
    prop_map.add("appid", "scanner")
    hubManager.send_event_to_output("output1", message, 0)
    print('sent from send_to_Hub_callback')

# Callback received when the message that we're forwarding is processed.


def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    SEND_CALLBACKS += 1


class HubManager(object):

    def __init__(
            self,
            messageTimeout,
            protocol
    ):
        '''
        Communicate with the Edge Hub

        :param str connectionString: Edge Hub connection string
        :param int messageTimeout: the maximum time in milliseconds until a message times out. The timeout period starts at IoTHubClient.send_event_async. By default, messages do not expire.
        :param IoTHubTransportProvider protocol: Choose HTTP, AMQP or MQTT as transport protocol.  Currently only MQTT is supported.
        '''

        self.messageTimeout = messageTimeout
        self.protocol = protocol

        self.client_protocol = self.protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)

        self.client.set_option("messageTimeout", self.messageTimeout)

    def send_event_to_output(self, outputQueueName, event, send_context):
        self.client.send_event_async(
            outputQueueName, event, send_confirmation_callback, send_context)


def main(
        videoPath,
        bingSpeechKey,
        predictThreshold,
        imageProcessingEndpoint="",
        speechMapFileName = None
):
    '''
    Capture a camera feed, send it to processing and forward outputs to EdgeHub

    :param str connectionString: Edge Hub connection string. Mandatory.
    :param int videoPath: camera device path such as /dev/video0 or a test video file such as /TestAssets/myvideo.avi. Mandatory.
    :param str imageProcessingEndpoint: service endpoint to send the frames to for processing. Example: "http://face-detect-service:8080". Leave empty when no external processing is needed (Default). Optional.

    '''
    try:
        print("\nPython %s\n" % sys.version)
        print("Camera Capture Azure IoT Edge Module. Press Ctrl-C to exit.")
        try:
            global hubManager
            hubManager = HubManager(10000, IoTHubTransportProvider.MQTT)
        except IoTHubError as iothub_error:
            print("Unexpected error %s from IoTHub" % iothub_error)
            return
        with CameraCapture(videoPath, bingSpeechKey, predictThreshold, imageProcessingEndpoint, send_to_Hub_callback, speechMapFileName) as cameraCapture:
            cameraCapture.start()
    except KeyboardInterrupt:
        print("Camera capture module stopped")


def __convertStringToBool(env):
    if env in ['True', 'TRUE', '1', 'y', 'YES', 'Y', 'Yes']:
        return True
    elif env in ['False', 'FALSE', '0', 'n', 'NO', 'N', 'No']:
        return False
    else:
        raise ValueError('Could not convert string to bool.')


if __name__ == '__main__':
    try:
        VIDEO_PATH = os.getenv('Video', '0')
        PREDICT_THRESHOLD = os.getenv('Threshold', .75)
        IMAGE_PROCESSING_ENDPOINT = os.getenv('AiEndpoint')
        AZURE_SPEECH_SERVICES_KEY = os.getenv('azureSpeechServicesKey', None)
        SPEECH_MAP_FILENAME = os.getenv('SpeechMapFilename', None)

        print(os.getenv('IOTEDGE_AUTHSCHEME'))

    except ValueError as error:
        print(error)
        sys.exit(1)

    main(VIDEO_PATH, AZURE_SPEECH_SERVICES_KEY,
         PREDICT_THRESHOLD, IMAGE_PROCESSING_ENDPOINT, SPEECH_MAP_FILENAME)
