 

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import edge_tts
from pydub import AudioSegment
import os
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

async def generate_script(topic):
    prompt = """
    convert this conversation  as JSON with the format {"person1": text, "person2": text}.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": topic}
        ]
    )
    print(response.choices[0].message.content)
    return json.loads(response.choices[0].message.content)

async def generate_audio(text, voice, output_filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_filename)

# async def generate_conversation_audio(conversation,voice1,voice2):
#     audio_files = []
#     for i, item in enumerate(conversation):
#         for person, text in item.items():
#             voice = "en-US-SteffanNeural" if person == "person1" else "en-GB-RyanNeural"
#             output_filename = f"temp_{i}.mp3"
#             await generate_audio(text, voice, output_filename)
#             audio_files.append(output_filename)
#     return audio_files

async def generate_conversation_audio(conversation, voice1, voice2):
    audio_files = []
    for i, item in enumerate(conversation):
        for person, text in item.items():
            voice = voice1 if i % 2 == 0 else voice2
            output_filename = f"temp_{i}.mp3"
            await generate_audio(text, voice, output_filename)
            audio_files.append(output_filename)
    return audio_files

def concatenate_audio_files(audio_files, output_filename):
    combined = AudioSegment.empty()
    for audio_file in audio_files:
        segment = AudioSegment.from_mp3(audio_file)
        combined += segment
    combined.export(output_filename, format="mp3")
    for audio_file in audio_files:
        os.remove(audio_file)

async def process_conversation(conversation,SAMPLE_FILE_NAME,voice1,voice2):
    convo = await generate_script(conversation)
    audio_files = await generate_conversation_audio(convo,voice1,voice2)
    concatenate_audio_files(audio_files, SAMPLE_FILE_NAME)
    return convo



