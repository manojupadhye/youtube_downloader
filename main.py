import yt_dlp
import sys
import os
import shutil


class YouTubeDownloader:
    def __init__(self, download_path='downloads'):
        self.download_path = download_path
        self._ensure_directories()
        # We now store the path to ffmpeg to pass it directly to yt-dlp
        self.ffmpeg_path = self._get_ffmpeg_path()

    def _ensure_directories(self):
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

    def _get_ffmpeg_path(self):
        """
        Locates FFmpeg. Checks venv, current dir, and system PATH.
        Returns the absolute path to the executable.
        """
        # 1. Check if it's in the current Python environment (venv/Scripts or venv/bin)
        ffmpeg_in_env = shutil.which("ffmpeg")
        if ffmpeg_in_env:
            return ffmpeg_in_env

        # 2. Check current working directory
        if os.path.exists("ffmpeg.exe"):
            return os.path.abspath("ffmpeg.exe")

        # 3. Fail if not found
        print("\n[CRITICAL ERROR] FFmpeg binary not found.")
        print("Please copy 'ffmpeg.exe' into your 'venv/Scripts' folder.")
        sys.exit(1)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            sys.stdout.write(f"\r[Downloading] {percent} | ETA: {d.get('_eta_str', 'N/A')}   ")
            sys.stdout.flush()
        elif d['status'] == 'finished':
            sys.stdout.write("\n[Download Complete] Starting Merge/Conversion (This may take a moment)...\n")

    def download_video(self, url, format_type='best'):

        ydl_opts = {
            # Filesystem
            'outtmpl': f'{self.download_path}/%(title)s [%(id)s].%(ext)s',
            'restrictfilenames': True,

            # --- CRITICAL FIX: Explicitly tell yt-dlp where FFmpeg is ---
            'ffmpeg_location': self.ffmpeg_path,

            # Formats: Download best Video and best Audio separately
            'format': 'bestvideo+bestaudio/best',

            # Merge: Force them into an MP4 container
            'merge_output_format': 'mp4',

            # Post-processing
            'writethumbnail': True,
            'postprocessors': [
                # We REMOVED 'FFmpegVideoConvertor' because 'merge_output_format' handles this.
                # Adding both often causes conflicts.
                {'key': 'FFmpegMetadata'},
                {'key': 'EmbedThumbnail'},
            ],

            # --- DEBUGGING: Enabled output to see Merger errors ---
            'quiet': False,  # Changed to False to see FFmpeg output
            'no_warnings': False,  # Changed to False to see warnings
            'progress_hooks': [self.progress_hook],

            # Network
            'retries': 10,
            'fragment_retries': 10,
        }

        if format_type == '1080':
            ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'

        try:
            print(f"Using FFmpeg at: {self.ffmpeg_path}")
            print(f"Initializing download for: {url}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            print(f"\n[Done] Video saved successfully to: {self.download_path}")
            return True

        except Exception as e:
            print(f"\n[Error] {e}")
            return False


if __name__ == "__main__":
    downloader = YouTubeDownloader(download_path="my_videos")
    video_url = input("Enter YouTube URL: ").strip()
    if video_url:
        downloader.download_video(video_url)
