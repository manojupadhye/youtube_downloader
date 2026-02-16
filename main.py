import yt_dlp
import sys
import os
import shutil


class YouTubeDownloader:
    def __init__(self, download_path='downloads', cookies_path='./cookies/cookies.txt'):
        self.download_path = download_path
        self.cookies_path = cookies_path

        self._ensure_directories()
        self.ffmpeg_path = self._get_ffmpeg_path()
        self._validate_cookies_file()

    # ---------------------------------------------------------
    # Directory Handling
    # ---------------------------------------------------------
    def _ensure_directories(self):
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

    # ---------------------------------------------------------
    # FFmpeg Detection
    # ---------------------------------------------------------
    def _get_ffmpeg_path(self):
        ffmpeg_in_env = shutil.which("ffmpeg")
        if ffmpeg_in_env:
            return ffmpeg_in_env

        if os.path.exists("ffmpeg.exe"):
            return os.path.abspath("ffmpeg.exe")

        print("\n[CRITICAL ERROR] FFmpeg binary not found.")
        sys.exit(1)

    # ---------------------------------------------------------
    # Cookie Validation
    # ---------------------------------------------------------
    def _validate_cookies_file(self):
        """
        Validates existence and readability of cookies file.
        Required for members-only content.
        """
        if not os.path.exists(self.cookies_path):
            print(f"[Warning] Cookies file not found at: {self.cookies_path}")
            print("Members-only videos will NOT be accessible.")
            self.cookies_available = False
        else:
            if os.path.getsize(self.cookies_path) == 0:
                print("[Warning] Cookies file is empty.")
                self.cookies_available = False
            else:
                print(f"[Info] Using cookies file: {os.path.abspath(self.cookies_path)}")
                self.cookies_available = True

    # ---------------------------------------------------------
    # Progress Hook
    # ---------------------------------------------------------
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            sys.stdout.write(
                f"\r[Downloading] {percent} | ETA: {d.get('_eta_str', 'N/A')}   "
            )
            sys.stdout.flush()

        elif d['status'] == 'finished':
            sys.stdout.write(
                "\n[Download Complete] Processing & Converting Audio...\n"
            )

    # ---------------------------------------------------------
    # Core Download Method
    # ---------------------------------------------------------
    def download(self, url):

        ydl_opts = {
            # File Naming
            'outtmpl': os.path.join(
                self.download_path,
                '%(playlist_title)s/%(playlist_index)s - %(title)s [%(id)s].%(ext)s'
            ),

            'restrictfilenames': True,

            # Playlist Handling
            'noplaylist': False,
            'ignoreerrors': True,
            'playlistreverse': False,

            # FFmpeg
            'ffmpeg_location': self.ffmpeg_path,

            # Format Selection
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',

            'postprocessor_args': {
                'merger': ['-c:v', 'copy', '-c:a', 'aac']
            },

            # Metadata
            'writethumbnail': True,
            'postprocessors': [
                {'key': 'FFmpegMetadata'},
                {'key': 'EmbedThumbnail'},
            ],

            # Stability
            'retries': 10,
            'continuedl': True,

            # Hooks
            'progress_hooks': [self.progress_hook],
        }

        # ---------------------------------------------------------
        # Add Cookies (Critical for Members-Only)
        # ---------------------------------------------------------
        if self.cookies_available:
            ydl_opts['cookiefile'] = self.cookies_path
        else:
            print("[Info] Proceeding without authentication.")

        try:
            print(f"Using FFmpeg at: {self.ffmpeg_path}")
            print(f"Initializing download for: {url}")
            print("-" * 60)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                info = ydl.extract_info(url, download=False)

                # Detect login requirement
                if info.get('availability') == 'needs_auth':
                    if not self.cookies_available:
                        raise Exception(
                            "This video requires login (Members-Only). "
                            "Cookies file is missing or invalid."
                        )

                # Playlist Detection
                if 'entries' in info:
                    print(f"Playlist Title: {info.get('title')}")
                    print(f"Total Videos: {len(info.get('entries', []))}")
                else:
                    print(f"Title: {info.get('title')}")
                    print(f"Uploader: {info.get('uploader')}")
                    print(f"Availability: {info.get('availability')}")

                print("-" * 60)

                ydl.download([url])

            print(f"\n[Success] Content saved to: {os.path.abspath(self.download_path)}")
            return True

        except yt_dlp.utils.DownloadError as e:
            print("\n[DownloadError] Possible authentication failure.")
            print("Ensure cookies are exported correctly from the same browser where you are logged in.")
            print(f"Details: {e}")
            return False

        except Exception as e:
            print(f"\n[Error] {e}")
            return False


# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    downloader = YouTubeDownloader(
        download_path="my_videos",
        cookies_path="./cookies/cookies.txt"
    )

    input_url = input("Enter YouTube Video or Playlist URL: ").strip()

    if input_url:
        downloader.download(input_url)
    else:
        print("No URL entered.")
