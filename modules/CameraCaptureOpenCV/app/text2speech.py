from azure_text_speech import AzureSpeechServices
from azure_text_translate import AzureTranslationServices
from pygame import mixer
import time
import hashlib
from pathlib import Path
import os
from datetime import datetime


class TextToSpeech():
    def __init__(self, azureSpeechServiceKey, voice='en-US-JessaNeural', azureTranslatorServiceKey=None, translateToLanguage=None, enableMemCache=False, enableDiskCache=False):
        self.text2Speech = AzureSpeechServices(azureSpeechServiceKey, voice)
        self.translateText = AzureTranslationServices(
            azureTranslatorServiceKey, translateToLanguage)

        self.azureTranslatorServiceKey = azureTranslatorServiceKey
        self.translateToLanguage = translateToLanguage
        self.voice = voice
        self.enableMemCache = enableMemCache
        self.enableDiskCache = enableDiskCache

        self.ttsAudio = {}

        mixer.init(frequency=16000, size=-16, channels=1)
        self.startSoundTime = datetime.min
        self.soundLength = 0.0

        if not Path('.cache-audio').is_dir():
            os.mkdir('.cache-audio')

    def play(self, text):
        digestKey = hashlib.md5(text.encode()).hexdigest()

        audio = self.ttsAudio.get(digestKey) if self.enableMemCache else None

        if audio is None:
            cacheFileName = "{}-{}.wav".format(
                self.voice, digestKey)

            cacheFileName = os.path.join('.cache-audio', cacheFileName)

            if self.enableDiskCache and Path(cacheFileName).is_file():
                with open(cacheFileName, 'rb') as audiofile:
                    audio = audiofile.read()
            else:
                if self.azureTranslatorServiceKey is not None and self.translateToLanguage is not None:
                    translatedText = self.translateText.translate(text)

                    if translatedText is None:
                        translatedText = text
                else:
                    translatedText = text

                audio = self.text2Speech.get_audio(translatedText)

                if self.enableDiskCache and audio is not None:
                    with open(cacheFileName, 'wb') as audiofile:
                        audiofile.write(audio)
            if self.enableMemCache:
                self.ttsAudio[digestKey] = audio

        if self.startSoundTime != datetime.min:
            self.deltaSeconds = (
                datetime.now() - self.startSoundTime).total_seconds()
            if self.deltaSeconds < self.soundLength:
                delay = self.soundLength - self.deltaSeconds
                time.sleep(delay)

        self.startSoundTime = datetime.now()

        self.sound = mixer.Sound(audio)
        self.sound.play()

        self.soundLength = self.sound.get_length()
        return self.soundLength
