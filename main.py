import yt_dlp
import sys
import os
import shutil


class YouTubeDownloader:
    def __init__(self, download_path='downloads'):
        self.download_path = download_path
        self._ensure_directories()
        self.ffmpeg_path = self._get_ffmpeg_path()

    def _ensure_directories(self):
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

    def _get_ffmpeg_path(self):
        """
         robustly finds FFmpeg. Checks:
         1. System PATH
         2. Current Directory
         3. Common Windows Install Locations (Winget)
        """
        # 1. Check System/Venv PATH
        ffmpeg_in_env = shutil.which("ffmpeg")
        if ffmpeg_in_env:
            return ffmpeg_in_env

        # 2. Check current directory (where script is running)
        if os.path.exists("ffmpeg.exe"):
            return os.path.abspath("ffmpeg.exe")

        # 3. Check standard Windows Winget location (Fallback based on your logs)
        # Note: The version number folder might change, so we look for the general pattern if needed,
        # but here is the specific path you found working:
        winget_path = r"C:\Users\Manoj_Upadhye\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.EXE"
        if os.path.exists(winget_path):
            return winget_path

        print("\n[CRITICAL ERROR] FFmpeg binary not found.")
        print("Please ensure FFmpeg is installed and added to your PATH.")
        sys.exit(1)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            sys.stdout.write(f"\r[Downloading] {percent} | ETA: {d.get('_eta_str', 'N/A')}   ")
            sys.stdout.flush()
        elif d['status'] == 'finished':
            sys.stdout.write("\n[Download Complete] Converting Audio to AAC for compatibility...\n")

    def download_video(self, url):

        ydl_opts = {
            # --- File Naming ---
            'outtmpl': f'{self.download_path}/%(title)s [%(id)s].%(ext)s',
            'restrictfilenames': True,  # Removes emojis/special chars to prevent file errors

            # --- FFmpeg Location ---
            'ffmpeg_location': self.ffmpeg_path,

            # --- Quality Selection ---
            # Download Best Video (any codec) + Best Audio
            'format': 'bestvideo+bestaudio/best',

            # --- Final Container ---
            'merge_output_format': 'mp4',

            # --- COMPATIBILITY ENGINE (The Magic Part) ---
            # This passes arguments to FFmpeg during the merge process.
            # -c:v copy  -> Keep video as-is (Fast, Lossless)
            # -c:a aac   -> Convert audio to AAC (Fixes "No Audio" on standard players)
            'postprocessor_args': {
                'merger': ['-c:v', 'copy', '-c:a', 'aac']
            },

            # --- Post Processing (Metadata/Thumbnails) ---
            'writethumbnail': True,
            'postprocessors': [
                # Embed Metadata (Title, Artist)
                {'key': 'FFmpegMetadata'},
                # Embed Thumbnail (Cover Art)
                {'key': 'EmbedThumbnail'},
            ],

            # --- Output Settings ---
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [self.progress_hook],
            'retries': 10,
        }

        try:
            print(f"Using FFmpeg at: {self.ffmpeg_path}")
            print(f"Initializing download for: {url}")
            print("-" * 50)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 1. Get Info
                info = ydl.extract_info(url, download=False)
                print(f"Title: {info.get('title')}")
                print(f"Quality: {info.get('resolution')} (Best Available)")
                print("-" * 50)

                # 2. Download
                ydl.download([url])

            print(f"\n[Success] Video saved to: {os.path.abspath(self.download_path)}")
            return True

        except Exception as e:
            print(f"\n[Error] {e}")
            return False


if __name__ == "__main__":
    downloader = YouTubeDownloader(download_path="my_videos")
    video_url = input("Enter YouTube URL: ").strip()

    if video_url:
        downloader.download_video(video_url)
    else:
        print("No URL entered.")
