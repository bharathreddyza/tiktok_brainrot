from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import edge_tts
from pydub import AudioSegment
import os

app = Flask(__name__)
CORS(app)

async def generate_audio(text, voice, output_filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_filename)

async def create_test_audio_files(voices, text="visit friend.Ai"):
    audio_files = []
    for i, voice in enumerate(voices):
        output_filename = f"test_audio_{voice}.mp3"
        await generate_audio(text, voice, output_filename)
        audio_files.append(output_filename)
    return audio_files

@app.route('/generate_test_audio', methods=['POST'])
def generate_test_audio():
    data = request.json
    voices = data.get("voices", [])
    if not voices:
        return jsonify({"error": "No voices provided"}), 400

    try:
        # Use asyncio to run the async functions
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_files = loop.run_until_complete(create_test_audio_files(voices))
        return jsonify({"message": "Audio files generated", "files": audio_files}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
