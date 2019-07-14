from azure_speech import AzureSpeechServices
from pygame import mixer
import time


class TextToSpeech():
    # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)'
    def __init__(self, azureSpeechServiceKey, voice='en-US-GuyNeural'):
        self.translator = AzureSpeechServices(azureSpeechServiceKey)
        self.ttsAudio = {}
        mixer.init(frequency=16000, size=-16, channels=1)

    def play(self, text):
        text = text.lower()

        audio = self.ttsAudio.get(text)
        if audio == None:
            print('audio not found')
            audio = self.translator.get_audio(text)
            self.ttsAudio[text] = audio

        self.sound = mixer.Sound(audio)
        self.sound.play()

        while mixer.get_busy():
            time.sleep(0.25)
