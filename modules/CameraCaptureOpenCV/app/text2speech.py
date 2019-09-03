from azure_text_speech import AzureSpeechServices
from azure_text_translate import AzureTranslationServices
import time
import hashlib
from pathlib import Path
import os
from datetime import datetime
import pyaudio
import wave
import io


class TextToSpeech():
    def __init__(self, azureSpeechServiceKey, voice='en-US-GuyNeural', azureTranslatorServiceKey=None, translateToLanguage=None, enableMemCache=False, enableDiskCache=False):
        self.text2Speech = AzureSpeechServices(azureSpeechServiceKey, voice)
        self.translateText = AzureTranslationServices(
            azureTranslatorServiceKey, translateToLanguage)

        self.azureTranslatorServiceKey = azureTranslatorServiceKey
        self.translateToLanguage = translateToLanguage
        self.voice = voice
        self.enableMemCache = enableMemCache
        self.enableDiskCache = enableDiskCache

        self.ttsAudio = {}

        self.startSoundTime = datetime.min
        self.soundLength = 0.0

        if not Path('.cache-audio').is_dir():
            os.mkdir('.cache-audio')

    def _playAudio(self, audio):
        CHUNK = 1024

        f = io.BytesIO()
        f.write(audio)
        f.seek(0)
        wf = wave.Wave_read(f)

        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(CHUNK)

        while data != b'':
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def play(self, text):
        if text is None or text == '':
            return

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
                        print(
                            'Text to Speech problem: Check internet connection or Translation key or language')
                        return
                else:
                    translatedText = text

                audio = self.text2Speech.get_audio(translatedText)
                if audio is None:
                    print(
                        'Text to Speech problem: Check internet connection or Speech key')
                    return

                if self.enableDiskCache and audio is not None:
                    with open(cacheFileName, 'wb') as audiofile:
                        audiofile.write(audio)
            if self.enableMemCache:
                self.ttsAudio[digestKey] = audio

        self._playAudio(audio)
