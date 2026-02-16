# 🚀 Ultimate YouTube & Playlist Downloader

A robust, Python-based CLI tool powered by `yt-dlp` to download YouTube videos and entire playlists with high-quality merging, metadata embedding, and smart authentication handling.

## ✨ Features

* **High Quality:** Automatically fetches the best video and audio streams and merges them into an `.mp4` container.
* **Playlist Support:** Download entire playlists with organized folder structures and indexed filenames.
* **Smart Authentication:** Supports `cookies.txt` or automatic extraction from Chrome/Edge browsers to bypass age restrictions or private video blocks.
* **Metadata & Thumbnails:** Automatically embeds video thumbnails and metadata (title, author, date) into the final file.
* **Resilience:** Built-in retry logic (10 retries) and resume capability for interrupted downloads.
* **FFmpeg Integration:** Uses FFmpeg for professional-grade post-processing and conversion.

---

## 🛠 Prerequisites: Installing FFmpeg

FFmpeg is the "engine" that merges high-quality video and audio together. You **must** have it installed for this script to work.

### **1. Windows**

* **Manual:** Download the "release full" build from [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/). Extract the `.zip`, rename the folder to `ffmpeg`, and move it to `C:\`.
* **Package Manager (Recommended):** Open PowerShell as Admin and run:
```powershell
winget install ffmpeg
# OR if you use Chocolatey
choco install ffmpeg

```



### **2. macOS**

* Install via [Homebrew](https://brew.sh/):
```bash
brew install ffmpeg

```



### **3. Linux**

* **Debian/Ubuntu/Mint:** `sudo apt update && sudo apt install ffmpeg`
* **Fedora:** `sudo dnf install ffmpeg`
* **Arch Linux:** `sudo pacman -S ffmpeg`

---

## ⚙️ Setup & Installation

### **Step 1: Configure FFmpeg Path**

In the code (`YouTubeDownloader` class), the script looks for `ffmpeg` in your system's PATH or a local `ffmpeg.exe`.
If you installed FFmpeg manually to a specific folder, update this section in the script:

```python
# If ffmpeg is NOT in your system environment variables, 
# ensure 'ffmpeg.exe' is placed in the project root folder 
# OR change the logic in _get_ffmpeg_path() to point to your path.

```

### **Step 2: Install Dependencies**

Open your terminal/command prompt in the project folder and run:

```bash
pip install -r requirements.txt

```

> **Note:** Your `requirements.txt` should contain at least:
> `yt-dlp`

---

## 🍪 Setting Up Cookies (Authentication)

YouTube often blocks "bot" downloads or requires login for age-restricted/private content. This script handles this via a `cookies.txt` file.

1. **Install a Browser Extension:** * Chrome: [Get cookies.txt LOCALLY](https://www.google.com/search?q=https://chrome.google.com/webstore/detail/get-cookiestxt-locally/ccmclkhjbdinkpjtodnehddeackebmde)
* Firefox: [Get cookies.txt LOCALLY](https://addons.mozilla.org/en-US/firefox/addon/get-cookies-txt-locally/)


2. **Export:** Log into YouTube in your browser, click the extension, and select **"Export to Netscape format"**.
3. **Placement:** Create a folder named `cookies` in the project directory and save the file as `cookies.txt`.
* *Path should look like:* `./cookies/cookies.txt`



---

## 🚀 How to Run

1. Run the script:
```bash
python main.py

```


2. **Enter a valid URL** when prompted.

### **Supported Link Formats**

The script is highly flexible. You can paste:

* **Standard Video:** `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
* **Shorts:** `https://www.youtube.com/shorts/xxxxxxx`
* **Playlists:** `https://www.youtube.com/playlist?list=PLxxxxxxx`
* **Shared Links:** `https://youtu.be/xxxxxxx`

### **⚠️ Important Tips for Users**

* **Avoid Mobile App "Share" Links:** Sometimes mobile URLs have extra tracking parameters that can cause issues. Use the standard browser URL for best results.
* **Check Folder Permissions:** Ensure the script has permission to create the `my_videos` (or your custom `download_path`) folder.

---

## 📂 Output Structure

The script will organize your files like this:

```text
project_folder/
├── my_videos/
│   └── Playlist_Name/
│       ├── 01 - Video_Title [ID].mp4
│       └── 02 - Another_Video [ID].mp4
├── cookies/
│   └── cookies.txt
└── main.py

```

Would you like me to generate a sample `requirements.txt` file or a `.gitignore` to keep your downloads out of your git history?
