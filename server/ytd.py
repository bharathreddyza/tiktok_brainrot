from pytubefix import YouTube
from pytubefix.cli import on_progress
import os

output_path = os.path.join(os.getcwd(), 'videos')
os.makedirs(output_path, exist_ok=True)

# url = "https://www.youtube.com/watch?v=BbFfpC6ncdo"
 
# yt = YouTube(url, on_progress_callback = on_progress)
# print(yt.title)
 
# ys = yt.streams.get_highest_resolution()
# ys.download()


# Function to download YouTube video to /videos folder
def download_video(url):
    yt = YouTube(url, on_progress_callback=on_progress)
    print(yt.title)
    ys = yt.streams.get_highest_resolution()
    ys.download(output_path=output_path)


# Function to download a list of pre-specified video URLs
def download_video_list():
    video_urls = [
        "https://www.youtube.com/watch?v=i0M4ARe9v0Y",
        "https://www.youtube.com/watch?v=u7kdVe8q5zs",
        "https://www.youtube.com/watch?v=VS3D8bgYhf4",
        "https://www.youtube.com/watch?v=BbFfpC6ncdo"
        # "https://www.youtube.com/watch?v=ZCPt78a1eLc"
        # Add more video URLs here
    ]
    for url in video_urls:
        download_video(url)

download_video_list()
 
 # run this command to download demo videos into /videos folder
 # python ytd.py