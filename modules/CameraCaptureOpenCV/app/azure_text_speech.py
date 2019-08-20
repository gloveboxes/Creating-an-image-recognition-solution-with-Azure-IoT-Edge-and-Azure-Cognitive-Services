# https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/rest-text-to-speech#get-a-list-of-voices


import os
import requests
import time
from xml.etree import ElementTree

TOKEN_URL = "https://southeastasia.api.cognitive.microsoft.com/sts/v1.0/issuetoken"
BASE_URL = "https://southeastasia.tts.speech.microsoft.com/"
TEXT_TO_SPEECH_PATH = "cognitiveservices/v1"
VOICES_PATH = "cognitiveservices/voices/list"


class AzureSpeechServices(object):
    # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)'
    def __init__(self, subscription_key, voice='en-US-GuyNeural'):
        self.subscription_key = subscription_key
        self.short_voice_name = voice
        self.access_token = None
        self.access_token_ttl = 0

    def get_token(self):
        '''
        The TTS endpoint requires an access token. This method exchanges your
        subscription key for an access token that is valid for ten minutes.

        If time is less than 10 minutes then use the cached token
        '''

        if self.subscription_key is None:
            return

        # for safety get new token if older than 9 minutes
        if abs(time.time() - self.access_token_ttl) < 9 * 60:
            return

        fetch_token_url = TOKEN_URL
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)
        self.access_token_ttl = time.time()

    def get_audio(self, text):
        if self.subscription_key is None:
            return

        try:
            self.get_token()

            constructed_url = BASE_URL + TEXT_TO_SPEECH_PATH
            headers = {
                'Authorization': 'Bearer ' + self.access_token,
                'Content-Type': 'application/ssml+xml',
                'X-Microsoft-OutputFormat': 'riff-16khz-16bit-mono-pcm',
                'User-Agent': 'YOUR_RESOURCE_NAME'
            }
            xml_body = ElementTree.Element('speak', version='1.0')
            xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
            voice = ElementTree.SubElement(xml_body, 'voice')
            voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
            voice.set('name', self.short_voice_name)
            voice.text = text
            body = ElementTree.tostring(xml_body)

            response = requests.post(
                constructed_url, headers=headers, data=body)

            if response.status_code == 200:
                return response.content
            else:
                print("\nStatus code: " + str(response.status_code) +
                      "\nSomething went wrong. Check your subscription key and headers.\n")
                return None
        except:
            return None
