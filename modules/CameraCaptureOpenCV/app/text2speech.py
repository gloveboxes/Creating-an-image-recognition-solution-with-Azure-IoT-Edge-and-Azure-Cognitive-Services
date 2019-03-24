from bingtts import Translator
import pyaudio
import wave
import sys
import io
# from cStringIO import StringIO


class TextToSpeech():
    def __init__(self, bingTtsKey):
        self.translator = Translator(bingTtsKey)
        self.ttsAudio = {}

    def playAudio(self, audio):
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

        while data != '':
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def Text2Speech(self, text):
        text = text.lower()
        audio = self.ttsAudio.get(text)
        if audio == None:
            print('not found')
            audio = self.translator.speak(
                text, "en-AU", "Catherine", "riff-16khz-16bit-mono-pcm")
            self.ttsAudio[text] = audio
        self.playAudio(audio)
