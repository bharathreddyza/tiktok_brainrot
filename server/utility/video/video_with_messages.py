import moviepy.editor as mp
from moviepy.video.tools.subtitles import SubtitlesClip
import PIL
import json
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import textwrap
from pkg_resources import parse_version
from moviepy.editor import (AudioFileClip, CompositeVideoClip, CompositeAudioClip, ImageClip,
                            TextClip, VideoFileClip)
if parse_version(PIL.__version__)>=parse_version('10.0.0'):
    Image.ANTIALIAS=Image.LANCZOS
    
def create_imessage_bubble(text, max_width=300, font_size=48, color="blue"):
    font = ImageFont.load_default().font_variant(size=font_size)
    
    # Wrap text
    wrapped_text = textwrap.fill(text, width=30)  # Adjust width as needed
    lines = wrapped_text.split('\n')
    
    # Calculate bubble dimensions
    line_heights = [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
    bubble_width = min(max(font.getbbox(line)[2] for line in lines) + 40, max_width)
    bubble_height = sum(line_heights) + 20 + (10 * (len(lines) - 1))  # Add padding and inter-line spacing
    
    bubble = Image.new('RGBA', (bubble_width, bubble_height), color=(255, 255, 255, 0))
    d = ImageDraw.Draw(bubble)
    
    bubble_color = (0, 122, 255, 255) if color == "blue" else (229, 229, 234, 255)
    d.rounded_rectangle([(0, 0), (bubble_width, bubble_height)], fill=bubble_color, radius=15)
    
    y_text = 10
    for line in lines:
        line_bbox = font.getbbox(line)
        line_width = line_bbox[2] - line_bbox[0]
        x_text = (bubble_width - line_width) // 2
        text_color = (255, 255, 255, 255) if color == "blue" else (0, 0, 0, 255)
        d.text((x_text, y_text), line, font=font, fill=text_color)
        y_text += line_bbox[3] - line_bbox[1] + 10  # Add some interline spacing
    
    return np.array(bubble)

def make_imessage_clip(text, start_time, end_time, position, color):
    bubble = create_imessage_bubble(text, max_width=800, color=color)  # Increased max_width for longer messages
    clip = (mp.ImageClip(bubble)
            .set_position(position)
            .set_start(start_time) #)
            .set_duration(end_time - start_time)
            .crossfadein(0.5))  # Add a 0.5 second fade-in effect
            # .set_duration(end_time - start_time)
            # .crossfadein(0.5))  # Add a 0.5 second fade-in effect
    return clip


def group_messages_into_thoughts(messages):
    thoughts = []
    current_thought = []
    for (start, end), text in messages:
        current_thought.append(((start, end), text))
        if text.strip().endswith(('.', '?', '!')):
            thoughts.append(current_thought)
            current_thought = []
    if current_thought:
        thoughts.append(current_thought)
    return thoughts

def match_timestamps_to_conversation(timestamps, conversation):
    print("Timestamps:", timestamps)
    print("Conversation:", conversation)
    
    matched_messages = []
    conv_index = 0
    current_person = list(conversation[0].keys())[0]
     # Calculate the total duration of the audio file
    total_duration = timestamps[-1][0][1]
     # Calculate the offset between audio and message timestamps
    offset = timestamps[0][0][0]

    for (start, end), text in timestamps:
        if conv_index >= len(conversation):
            break

        expected_text = conversation[conv_index][current_person].lower()
        current_message = text.strip().lower()

        if current_message == expected_text:
            matched_messages.append({
                "person": current_person,
                "text": conversation[conv_index][current_person],
                "start": start,
                "end": end
            })
            conv_index += 1
            if conv_index < len(conversation):
                current_person = list(conversation[conv_index].keys())[0]
    
   # If we haven't matched all messages, add the remaining ones with estimated timestamps
    while conv_index < len(conversation):
        last_end = matched_messages[-1]["end"] if matched_messages else 0
        remaining_duration = total_duration - last_end
        estimated_duration = remaining_duration / (len(conversation) - conv_index)
        matched_messages.append({
            "person": list(conversation[conv_index].keys())[0],
            "text": list(conversation[conv_index].values())[0],
            "start": last_end + offset,
            "end": last_end + estimated_duration + offset
        })
        conv_index += 1


    print(f"Matched messages: {json.dumps(matched_messages, indent=2)}")
    return matched_messages

def create_cta_text_overlay(text, video_size, font_size=60, color="white", background_color="black"):
    from PIL import Image, ImageDraw, ImageFont, ImageColor
    import numpy as np
    import textwrap

    # Use a default font or specify a path to a custom font
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default().font_variant(size=font_size)
    
    # Wrap text
    max_width = int(video_size[0] * 0.8)  # Use 80% of video width
    wrapped_text = textwrap.fill(text, width=30)  # Adjust width as needed
    lines = wrapped_text.split('\n')
    
    # Calculate text dimensions
    line_heights = [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
    text_width = max(font.getbbox(line)[2] for line in lines)
    text_height = sum(line_heights) + (10 * (len(lines) - 1))  # Add inter-line spacing
    
    # Create image with video dimensions and transparent background
    image = Image.new('RGBA', video_size, color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Calculate position to center the text
    x = (video_size[0] - text_width) // 2
    y = (video_size[1] - text_height) // 2
    
    # Draw semi-transparent background
    bg_color = tuple(list(ImageColor.getrgb(background_color)) + [128])  # 50% opacity
    draw.rectangle([x-20, y-20, x+text_width+20, y+text_height+20], fill=bg_color)
    
    # Draw text
    y_offset = y
    for line in lines:
        line_width = font.getbbox(line)[2]
        line_x = (video_size[0] - line_width) // 2  # Center each line
        draw.text((line_x, y_offset), line, font=font, fill=color)
        y_offset += font.getbbox(line)[3] - font.getbbox(line)[1] + 10  # Add inter-line spacing
    
    return np.array(image)

def create_tiktok_conversation_video(timestamps, conversation, audio_file_path, background_video_path, output_path, video_size=(1080, 1920), optional_cta_audio=None, cta_text=""):
    print("Adding CTA audio:", optional_cta_audio)
    matched_messages = match_timestamps_to_conversation(timestamps, (conversation))
    IMAGEMAGICK_BINARY = "C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
    os.environ['IMAGEMAGICK_BINARY'] = IMAGEMAGICK_BINARY
    if not matched_messages:
        print("Error: No messages were matched. Check your timestamps and conversation data.")
        return
    
    # add paths
    videos_folder_path = r'C:\Users\lenovo\Desktop\bounty\server\videos'

    audio_file_path = os.path.join(os.getcwd(),audio_file_path)
    # background_video_path = os.path.join(os.getcwd(),background_video_path)
    background_video_path = os.path.join(videos_folder_path, background_video_path)

    output_path= os.path.join(os.getcwd(), output_path)
    if optional_cta_audio:
        optional_cta_audio = os.path.join(os.getcwd(), optional_cta_audio)
    # Load the audio file to get its duration
    audio_clip = mp.AudioFileClip(audio_file_path)
    total_duration = audio_clip.duration  

    background_video = mp.VideoFileClip(background_video_path).resize(video_size)
    # background_video = mp.VideoFileClip(background_video_path) 
    print("Adding CTA audio:", optional_cta_audio)

    # Calculate the end time of the last message
    last_message_end = max(message["end"] for message in matched_messages)

    # Add CTA duration to total duration
    # if cta_text:
    #     total_duration +=  +1  # Add 5 seconds for CTA text
    if optional_cta_audio:
        cta_audio_clip = mp.AudioFileClip(optional_cta_audio)
        total_duration += cta_audio_clip.duration  # Add CTA audio duration
        background_video = background_video.loop(duration=total_duration)
    else:
    # Load the background video
        background_video = background_video.loop(duration=total_duration)
    
    print("Adding CTA audio:", optional_cta_audio)

    # Create a list to store the text overlay clips
    clips = [background_video]
    y_offset = 10  # Start messages a bit lower to leave space for TikTok UI
    left_x = 20
    right_x = video_size[0] - 700  # Adjust based on max bubble width
    gap_size = 10  # Add a gap of 50 pixels between messages
    
    for i, message in enumerate(matched_messages):
          # Increment y_offset for the next message
        if i % 2 == 0:  # Left message
            y_offset += 100 + gap_size
        else:  # Right message
            y_offset += 90 + gap_size
        color = "blue" if message["person"] == "person1" else "gray"
        position = (left_x, y_offset) if message["person"] == "person1" else (right_x, y_offset)
        
        # Create a text clip for the message
        text_clip = make_imessage_clip(message["text"], message["start"], message["end"], position, color)
        
        # Set the duration of the text clip to match the audio duration
        # cta_audio_clip = mp.AudioFileClip(optional_cta_audio)
        text_clip = text_clip.set_start(message["start"]).set_end( audio_clip.duration  )
        
        # Add the text clip to the list of clips
        clips.append(text_clip)
        
        # Increment y_offset for the next message
        y_offset += 100 + gap_size
    
   # Add CTA clip
    if cta_text:
        cta_start_time = matched_messages[-1]["end"] if matched_messages else 0
        print("Adding CTA text:", cta_text,cta_start_time,total_duration - cta_start_time)
        print("Adding CTA audio:", optional_cta_audio)

        try:
            # cta_clip = mp.TextClip(cta_text, fontsize=70, color='white', font="Arial-Bold")
            # cta_clip = TextClip(cta_text, fontsize=70, color='white', font='Arial', size=video_size)
            # cta_clip = cta_clip.set_position('center').set_start(cta_start_time).set_duration(total_duration - cta_start_time)
            # clips.append(cta_clip)
            # total_duration += 5  # Increase total duration by 5 seconds

            cta_image = create_cta_text_overlay(cta_text, video_size)
            cta_clip = mp.ImageClip(cta_image)
            cta_clip = cta_clip.set_start(cta_start_time).set_duration(total_duration - cta_start_time)
            clips.append(cta_clip)
        except Exception as e:
            print("Error adding CTA text:", str(e))

        # Add optional CTA audio
        if optional_cta_audio:
            print("Adding CTA audio:", optional_cta_audio)
            try:
                cta_audio_clip = mp.AudioFileClip(optional_cta_audio)
                audio_clip = mp.concatenate_audioclips([audio_clip, cta_audio_clip])
                # total_duration += cta_audio_clip.duration  # Increase total duration by CTA audio duration
            except Exception as e:
                print("Error adding CTA audio:", str(e))
    
    # Combine the background video, text overlays, and audio
    final_video = mp.CompositeVideoClip(clips, size=video_size)
    final_video = final_video.set_audio(audio_clip)
    final_video = final_video.set_duration(total_duration)
    
    # Write the final video file
    final_video.write_videofile(output_path, fps=24)

# Example usage
messages = [((0, 0.46), "I've been"), ((0.46, 1.1), 'feeling really'), ((1.1, 1.8), 'down lately'), ((1.8, 3.0), "It's hard"), ((3.0, 3.72), 'to talk about'), ((3.72, 4.28), 'it with anyone'), ((4.28, 5.9), "I'm sorry"), ((5.9, 6.58), 'to hear that'), ((6.58, 7.9), 'Have you'), ((7.9, 8.26), 'considered'), ((8.26, 8.58), 'trying'), ((8.58, 9.4), "friendai It's"), ((9.4, 10.9), 'this new'), ((10.9, 11.76), 'mental health'), ((11.76, 11.98), 'app that'), ((11.98, 12.4), 'lets you'), ((12.4, 12.84), 'chat with'), ((12.84, 13.2), 'an AI'), ((13.2, 13.96), 'companion An'), ((13.96, 16.54), "AI I don't"), ((16.54, 17.02), "know How's"), ((17.02, 18.76), 'that supposed'), ((18.76, 18.76), 'to help'), ((18.76, 20.62), "It's designed"), ((20.62, 21.12), 'to listen'), ((21.12, 21.36), 'without'), ((21.36, 22.1), 'judgment and'), ((22.1, 22.62), 'offer support'), ((22.62, 22.98), 'Might be'), ((22.98, 24.8), 'a good first'), ((24.8, 25.38), "step if you're"), ((25.38, 25.76), 'not ready'), ((25.76, 26.24), 'to open up'), ((26.24, 26.64), 'to people'), ((26.64, 27.3), 'yet HM maybe'), ((27.3, 29.12), "I'll check"), ((29.12, 29.72), 'it out Thanks'), ((29.72, 30.86), 'for the'), ((30.86, 31.58), 'suggestion No'), ((31.58, 31.58), 'problem I'), ((31.58, 34.62), 'hope it helps')]


conversation =  [ 
    { "person1": "I've been feeling really down lately. It's hard to talk about it with anyone." },
    { "person2": "I'm sorry to hear that. Have you considered trying Friend.AI? It's this new mental health app that lets you chat with an AI companion." },
    { "person1": "An AI? I don't know... How's that supposed to help?" },
    { "person2": "It's designed to listen without judgment and offer support. Might be a good first step if you're not ready to open up to people yet." },
    { "person1": "Hm, maybe I'll check it out. Thanks for the suggestion." },
    { "person2": "No problem. I hope it helps!" }
]



audio_file_path = "audio_tts1.wav"
background_video_path = "video1.mp4"
output_path = "tiktok_imessage_conversation.mp4"
optional_cta_audio= "cta_tts.mp3"
cta_text="Visit friendai.com"
# create_tiktok_conversation_video(messages,conversation, audio_file_path, background_video_path, output_path,optional_cta_audio="cta_tts.mp3", cta_text="Visit friendai.com")