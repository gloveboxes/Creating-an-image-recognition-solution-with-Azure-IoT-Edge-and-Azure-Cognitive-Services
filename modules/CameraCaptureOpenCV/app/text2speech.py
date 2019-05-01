from azure_speech import AzureSpeechServices
import pyaudio
import wave
import sys
import io


class TextToSpeech():
    # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)'
    def __init__(self, azureSpeechServiceKey, voice='en-US-GuyNeural'):
        self.translator = AzureSpeechServices(azureSpeechServiceKey)
        self.ttsAudio = {}

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
        text = text.lower()
        audio = self.ttsAudio.get(text)
        if audio == None:
            print('audio not found')
            audio = self.translator.get_audio(text)

            # audio = self.translator.speak(
            #     text, "en-AU", "Catherine", "riff-16khz-16bit-mono-pcm")
            self.ttsAudio[text] = audio
        self._playAudio(audio)
