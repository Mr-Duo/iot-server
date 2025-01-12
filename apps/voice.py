import json
import numpy as np
from vosk import KaldiRecognizer, Model
from fastapi import HTTPException

import random
import numpy as np

import librosa
import noisereduce as nr
import soundfile as sf

from deep_speaker.audio import read_mfcc
from deep_speaker.batcher import sample_from_mfcc
from deep_speaker.conv_models import DeepSpeakerModel
from deep_speaker.test import batch_cosine_similarity

# Reproducible results.
np.random.seed(123)
random.seed(123)

def clean_voice(input_wav, input_rate=8000, output_rate=16000):
    audio, sr = librosa.load(input_wav, sr=input_rate)
    reduced_noise = nr.reduce_noise(y=audio, sr=sr)
    cleaned_path =  input_wav.rsplit("/", 1)[0] + "/" + "cleaned.wav"
    sf.write(cleaned_path, reduced_noise, output_rate)
    print(f"Noise cleaned. Saved as: {cleaned_path}")
    
    return cleaned_path

def similarity(predict_001, predict_002):
    return batch_cosine_similarity(predict_001, predict_002)

class VoiceModel:
    SAMPLE_RATE = 16000
    NUM_FRAMES = 160
    
    def __init__(self, voice_model_path: str, speaker_model_path: str):
        self.voice_model = Model(model_path= voice_model_path)
        self.speaker_model = DeepSpeakerModel()
        self.speaker_model.m.load_weights(speaker_model_path, by_name=True)
        self.rec = KaldiRecognizer(self.voice_model, self.SAMPLE_RATE)
    
    def recognize(self, audio_file):
        try:
            mfcc_001 = sample_from_mfcc(read_mfcc(audio_file, self.SAMPLE_RATE), self.NUM_FRAMES)
            predict_001 = self.speaker_model.m.predict(np.expand_dims(mfcc_001, axis=0))
            
            return predict_001
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"[Transcribe] Error processing file: {str(e)}")
        
    def transcribe(self, audio_file):
        try:
            with open(audio_file, "rb") as wf:
                wf.read(44) # skip header
                read_rate = int(self.SAMPLE_RATE / 4)
                while True:
                    data = wf.read(read_rate)
                    if len(data) == 0:
                        break
                    self.rec.AcceptWaveform(data)

                res = json.loads(self.rec.FinalResult())
                return res["text"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"[Transcribe] Error processing file: {str(e)}")
    
    def process(self, audio_file):
        try:
            clean_audio_file = clean_voice(audio_file)
            speaker = self.recognize(clean_audio_file)
            text = self.transcribe(clean_audio_file)
            
            return {
                "text": text,
                "spk": speaker
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"[Transcribe] Error processing file: {str(e)}")