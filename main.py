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

        print("\n[CRITICAL ERROR] FFmpeg binary not found in PATH.")
        sys.exit(1)

    # ---------------------------------------------------------
    # Authentication Resolution
    # ---------------------------------------------------------
    def _resolve_authentication(self):
        """
        Priority:
        1. cookies.txt file
        2. Chrome browser cookies
        3. Edge browser cookies
        4. None (unauthenticated)
        """

        # 1️⃣ Check cookies.txt
        if os.path.exists(self.cookies_path) and os.path.getsize(self.cookies_path) > 0:
            print(f"[Auth] Using cookies file: {os.path.abspath(self.cookies_path)}")
            return {"cookiefile": self.cookies_path}

        print("[Auth] cookies.txt not found or empty.")

        # 2️⃣ Try Chrome
        print("[Auth] Attempting Chrome cookie extraction...")
        return {"cookiesfrombrowser": ("chrome",)}

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

        # Resolve Authentication
        auth_config = self._resolve_authentication()

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

            # FFmpeg
            'ffmpeg_location': self.ffmpeg_path,

            # Quality
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'postprocessor_args': {
                'merger': ['-c:v', 'copy', '-c:a', 'aac']
            },

            # JS Engine
            'jsengine': 'node',

            # Metadata
            'writethumbnail': True,
            'postprocessors': [
                {'key': 'FFmpegMetadata'},
                {'key': 'EmbedThumbnail'},
            ],

            # Stability
            'retries': 10,
            'continuedl': True,

            # Progress
            'progress_hooks': [self.progress_hook]
        }

        # Inject authentication strategy
        ydl_opts.update(auth_config)

        try:
            print(f"Using FFmpeg at: {self.ffmpeg_path}")
            print(f"Initializing download for: {url}")
            print("-" * 60)

            # First attempt (cookies.txt OR Chrome)
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                    if 'entries' in info:
                        print(f"Playlist: {info.get('title')}")
                        print(f"Total Videos: {len(info.get('entries', []))}")
                    else:
                        print(f"Title: {info.get('title')}")
                        print(f"Availability: {info.get('availability')}")

                    print("-" * 60)

                    ydl.download([url])

            except yt_dlp.utils.DownloadError as chrome_error:
                # If Chrome was used and failed, try Edge fallback
                if auth_config.get("cookiesfrombrowser") == ("chrome",):
                    print("[Auth] Chrome authentication failed. Trying Edge...")
                    ydl_opts.pop("cookiesfrombrowser", None)
                    ydl_opts["cookiesfrombrowser"] = ("edge",)

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                else:
                    raise chrome_error

            print(f"\n[Success] Saved to: {os.path.abspath(self.download_path)}")
            return True

        except yt_dlp.utils.DownloadError as e:
            print("\n[DownloadError] Authentication or access issue.")
            print("Possible causes:")
            print("- Not logged into YouTube in browser")
            print("- Expired cookies")
            print("- Members-only content without membership")
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
