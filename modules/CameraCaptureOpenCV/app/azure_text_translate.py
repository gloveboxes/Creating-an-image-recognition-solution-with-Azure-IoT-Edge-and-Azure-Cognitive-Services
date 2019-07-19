import os
import requests
import uuid
import json


class AzureTranslationServices():

    def __init__(self, azureTranslatorServiceKey, language):
        self.azureTranslatorServiceKey = azureTranslatorServiceKey
        self.language = language

    def translate(self, text):

        # If you want to set your subscription key as a string, uncomment the next line.
        #subscriptionKey = 'put_your_key_here'

        # If you encounter any issues with the base_url or path, make sure
        # that you are using the latest endpoint: https://docs.microsoft.com/azure/cognitive-services/translator/reference/v3-0-translate
        base_url = 'https://api.cognitive.microsofttranslator.com'
        path = '/translate?api-version=3.0'
        params = '&to={}'.format(self.language)
        constructed_url = base_url + path + params

        headers = {
            'Ocp-Apim-Subscription-Key': self.azureTranslatorServiceKey,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        # You can pass more than one object in body.
        body = [{
            'text': text
        }]

        request = requests.post(constructed_url, headers=headers, json=body)
        response = request.json()
        if len(response) > 0:
            jsonData = response[0].get('translations')
            if len(jsonData) > 0:
                return jsonData[0]['text']

        return None
