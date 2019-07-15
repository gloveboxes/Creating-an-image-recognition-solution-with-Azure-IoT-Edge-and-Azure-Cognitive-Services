from azure_speech import AzureSpeechServices
from pygame import mixer
import time
import hashlib
from pathlib import Path


class TextToSpeech():
    # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)'
    def __init__(self, azureSpeechServiceKey, voice='en-US-GuyNeural'):
        self.text2speech = AzureSpeechServices(azureSpeechServiceKey)
        self.ttsAudio = {}
        mixer.init(frequency=16000, size=-16, channels=1)

    def play(self, text):
        
        digest = hashlib.md5(text.encode()).hexdigest()
        audio = self.ttsAudio.get(digest)

        if audio == None:
            cacheFileName = "{}.wav".format(digest)

            if Path(cacheFileName).is_file():
                with open(cacheFileName, 'rb') as audiofile:
                    audio = audiofile.read()
            else:
                audio = self.text2speech.get_audio(text)

                if audio is not None:
                    with open(cacheFileName, 'wb') as audiofile:
                        audiofile.write(audio)

            self.ttsAudio[digest] = audio

        self.sound = mixer.Sound(audio)
        self.sound.play()

        while mixer.get_busy():
            time.sleep(0.25)
