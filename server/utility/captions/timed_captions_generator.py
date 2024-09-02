import os

import whisper_timestamped as whisper
from whisper_timestamped import load_model, transcribe_timestamped
import re
from openai import OpenAI
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)
 

def generate_timed_captions(audio_filename, model_size="whisper-1"):
    try:
        # videos_folder_path = r'C:\Users\lenovo\Desktop\bounty\server\'
        audio_file_path = os.path.join(os.getcwd(),audio_filename)
        with open(audio_file_path, "rb") as file:
        # with open(audio_filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=file,
                model=model_size,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )
        # whisper_analysis = transcription["results"][0]["alternatives"][0]
        print(transcription)
        return getCaptionsWithTime(transcription)
    except EOFError as e:
        print(f"Error: {e}")


def splitWordsBySize(words, maxCaptionSize):
   
    halfCaptionSize = maxCaptionSize / 2
    captions = []
    while words:
        caption = words[0]
        words = words[1:]
        while words and len(caption + ' ' + words[0]) <= maxCaptionSize:
            caption += ' ' + words[0]
            words = words[1:]
            if len(caption) >= halfCaptionSize and words:
                break
        captions.append(caption)
    return captions
 

def getTimestampMapping(whisper_analysis):
    index = 0
    locationToTimestamp = {}
    for word in whisper_analysis:
        newIndex = index + len(word['word'])+1
        locationToTimestamp[(index, newIndex)] = word['end']
        index = newIndex
    return locationToTimestamp

def cleanWord(word):
   
    return re.sub(r'[^\w\s\-_"\'\']', '', word)

def interpolateTimeFromDict(word_position, d):
   
    for key, value in d.items():
        if key[0] <= word_position <= key[1]:
            return value
    return None

def getCaptionsWithTime(whisper_analysis, maxCaptionSize=15, considerPunctuation=False):
   
    wordLocationToTime = getTimestampMapping(whisper_analysis.words )
    position = 0
    start_time = 0
    CaptionsPairs = []
    text = whisper_analysis.text
    
    if considerPunctuation:
        sentences = re.split(r'(?<=[.!?]) +', text)
        words = [word for sentence in sentences for word in splitWordsBySize(sentence.split(), maxCaptionSize)]
    else:
        words = text.split()
        words = [cleanWord(word) for word in splitWordsBySize(words, maxCaptionSize)]
    
    for word in words:
        position += len(word) + 1
        end_time = interpolateTimeFromDict(position, wordLocationToTime)
        if end_time and word:
            CaptionsPairs.append(((start_time, end_time), word))
            start_time = end_time

    return CaptionsPairs
