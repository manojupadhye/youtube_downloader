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
        Robustly finds FFmpeg.
        Checks:
        1. System PATH
        2. Current Directory
        3. Common Windows Winget Install
        """
        ffmpeg_in_env = shutil.which("ffmpeg")
        if ffmpeg_in_env:
            return ffmpeg_in_env

        if os.path.exists("ffmpeg.exe"):
            return os.path.abspath("ffmpeg.exe")

        winget_path = r"C:\Users\Manoj_Upadhye\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.EXE"
        if os.path.exists(winget_path):
            return winget_path

        print("\n[CRITICAL ERROR] FFmpeg binary not found.")
        sys.exit(1)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            sys.stdout.write(
                f"\r[Downloading] {percent} | ETA: {d.get('_eta_str', 'N/A')}   "
            )
            sys.stdout.flush()
        elif d['status'] == 'finished':
            sys.stdout.write(
                "\n[Download Complete] Converting Audio to AAC for compatibility...\n"
            )

    def download(self, url):
        """
        Supports both:
        - Single videos
        - Playlists
        """

        ydl_opts = {
            # --- File Naming ---
            # If playlist → creates subfolder per playlist
            'outtmpl': os.path.join(
                self.download_path,
                '%(playlist_title)s/%(playlist_index)s - %(title)s [%(id)s].%(ext)s'
            ),

            'restrictfilenames': True,

            # --- Playlist Handling ---
            'noplaylist': False,          # Allow playlists
            'ignoreerrors': True,         # Continue if one video fails
            'playlistreverse': False,
            'playlist_items': None,       # Can limit like "1-10"

            # --- FFmpeg ---
            'ffmpeg_location': self.ffmpeg_path,

            # --- Quality ---
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',

            'postprocessor_args': {
                'merger': ['-c:v', 'copy', '-c:a', 'aac']
            },

            # --- Metadata & Thumbnail ---
            'writethumbnail': True,
            'postprocessors': [
                {'key': 'FFmpegMetadata'},
                {'key': 'EmbedThumbnail'},
            ],

            # --- Logging ---
            'progress_hooks': [self.progress_hook],
            'retries': 10,
        }

        try:
            print(f"Using FFmpeg at: {self.ffmpeg_path}")
            print(f"Initializing download for: {url}")
            print("-" * 60)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                info = ydl.extract_info(url, download=False)

                # Detect playlist
                if 'entries' in info:
                    print(f"Playlist Title: {info.get('title')}")
                    print(f"Total Videos: {len(info.get('entries', []))}")
                else:
                    print(f"Title: {info.get('title')}")
                    print(f"Resolution: {info.get('resolution')}")

                print("-" * 60)

                ydl.download([url])

            print(f"\n[Success] Content saved to: {os.path.abspath(self.download_path)}")
            return True

        except Exception as e:
            print(f"\n[Error] {e}")
            return False


if __name__ == "__main__":
    downloader = YouTubeDownloader(download_path="my_videos")
    input_url = input("Enter YouTube Video or Playlist URL: ").strip()

    if input_url:
        downloader.download(input_url)
    else:
        print("No URL entered.")
