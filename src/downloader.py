import yt_dlp
import os

def download_facebook_video(video_url, output_folder="data/videos"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ydl_opts = {
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'format': 'best'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

if __name__ == "__main__":
    video_link = "PASTE_FACEBOOK_VIDEO_URL_HERE"  # Replace with an actual Facebook video link
    download_facebook_video(video_link)