from openai import OpenAI
import os
import edge_tts
import json
import asyncio
from flask import Flask, request, jsonify,send_file
from flask_cors import CORS
from pdfquery import PDFQuery
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.audio.convo_Generator import process_conversation as process_conversation
from utility.audio.convo_Generator import generate_audio as generate_audio
from utility.video.video_with_messages import create_tiktok_conversation_video
from utility.video.video_sync_audio import create_tiktok_sync_audio_video
from PyPDF2 import PdfReader
from ytd import download_video
import argparse
import io
import base64

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


    
@app.route('/conversation', methods=['POST'])
def conversation():
    SAMPLE_FILE_NAME = "audio_tts1.wav"
    SAMPLE_VIDEO_NAME = "video5.mp4"
    output_path = "tiktok_imessage_conversation.mp4"
    CTA_AUDIO_NAME = "cta_tts.wav"

    # Check if the request contains form data
    if request.content_type.startswith('multipart/form-data'):
        data = request.form
        files = request.files
    else:
        data = request.json
        files = None

    voice1 = data.get('voice1')
    voice2 = data.get('voice2')
    cta_text = data.get('cta')
    cta_audio = None

    # Handle PDF upload
    if files and 'pdf' in files:
        pdf_file = files['pdf']
        conversation = extract_text_from_pdf(pdf_file)
    else:
        conversation = data.get('conversation')

    video_ids = json.loads(data.get('videoIds'))
    first_path = video_ids[0]['path']
    filename = os.path.basename(first_path)
    SAMPLE_VIDEO_NAME = filename

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print(conversation)
    result = loop.run_until_complete(process_conversation(conversation, SAMPLE_FILE_NAME, voice1, voice2))

    if data.get('ctaHasAudio') == 'true':
        cta_audio = True
        loop.run_until_complete(generate_audio(cta_text, data.get('ctaVoice'), CTA_AUDIO_NAME))

    timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)

    if data.get('type') == 'messageBubble':
        video_content = create_tiktok_conversation_video(timed_captions, result, SAMPLE_FILE_NAME, SAMPLE_VIDEO_NAME, output_path, (1080, 1920), CTA_AUDIO_NAME if cta_audio else None, cta_text)
    elif data.get('type') == 'syncAudio':
        video_content = create_tiktok_sync_audio_video(timed_captions, result, SAMPLE_FILE_NAME, SAMPLE_VIDEO_NAME, output_path, (1080, 1920), CTA_AUDIO_NAME if cta_audio else None, cta_text)

    print("Video saved to:", video_content)
    loop.close()

    return send_file(
        output_path,
        mimetype='video/mp4',
        as_attachment=True,
        download_name='output.mp4'
    )

 

@app.route('/backgroundVideos', methods=['GET'])
def send_videos():
    video_folder = '/videos'
    videos = [os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.lower().endswith('.mp4')]

    if not videos:
        return jsonify({"error": "no videos found"}), 400

    video_data = []
    for video in videos:
        with open(video, 'rb') as f:
            video_blob = f.read()
            video_data.append({
                "path": video,
                "blob": base64.b64encode(video_blob).decode('utf-8')
            })

    return jsonify({"videos": video_data})

# Route to download YouTube video
@app.route('/download_video', methods=['POST'])
def download_video_route():
    url = request.json.get('youtubeUrl')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    download_video(url)
    return jsonify({"message": "Video downloaded successfully"}),200

      
@app.route('/pdf-extractor', methods=['POST'])
def pdf_extractor():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    pdf_file = request.files['file']
    if pdf_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if pdf_file and pdf_file.filename.endswith('.pdf'):
        pdf_text = extract_text_from_pdf(pdf_file)
        return jsonify({"text": pdf_text})
    else:
        return jsonify({"error": "Invalid file format. Please upload a PDF file"}), 400
    
 
def extract_text_from_pdf(pdf_file):
    pdf_reader = PDFQuery(pdf_file)
    pdf_reader.load()

    # Use CSS-like selectors to locate the elements
    text_elements = pdf_reader.pq('LTTextLineHorizontal')

    # Extract the text from the elements
    text = ' '.join([t.text for t in text_elements])


    return text

if __name__ == "__main__":
    app.run(debug=True)
 
