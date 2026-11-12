# YouTube Download Helper — Batch Video & Thumbnail Downloader for Mac

A local macOS downloader built on [yt-dlp](https://github.com/yt-dlp/yt-dlp), with a native Swift/AppKit window and a Python queue runner. No AI service, API key, or token usage.

[简体中文](README.md) | **English**

Save batches of YouTube videos and matching thumbnails as **MP4 + JPG**. Defaults to **up to 1080p and explicitly labeled English audio**. Paste multiple links, choose a folder and download.

[Install](#install-and-build) · [Use](#use) · [Report a bug](https://github.com/eppeal-stack/youtube-downloader-formac/issues) · [MIT](LICENSE)

> Source installation is currently required. There is no standalone DMG installer. The desktop UI is Chinese; see the button guide below or use the CLI. Audio selection currently requires an English label.

## What it does

- Accepts multiple lines, semicolon-separated lists, Markdown links, Shorts and youtu.be URLs; removes duplicates.
- Downloads matching JPG thumbnails, with a thumbnails-only option.
- Uses a sequential queue, continues after failed items, and keeps partial files for retries.
- Supports an optional proxy and component updates from the app.

Only YouTube links are accepted. Other sites, a Windows desktop app, an English UI and a graphical audio-language picker are not currently implemented. This project is independent of yt-dlp and YouTube; it is not an official client.

## Requirements

- macOS 12+ for the desktop app; the Python CLI can also run on Linux.
- Python 3.10+, FFmpeg (including ffprobe), Node.js 22+.
- Xcode Command Line Tools (`xcode-select --install`) to build the macOS app.

Install Python, FFmpeg and Node through your preferred package manager. For example, with Homebrew: `brew install python ffmpeg node`.

## Install and build

Get the project and build the app:

```sh
git clone https://github.com/eppeal-stack/youtube-downloader-formac.git
cd youtube-downloader-formac
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
python3 build_app.py
open 'dist/YouTube Download Helper.app'
```

Keep the project directory and `.venv` in place. The locally built app stores that directory in its generated Info.plist; rebuild if you move the project. This is a source distribution, not a notarized, standalone app installer. Do not publish generated app bundles containing your local paths.

## Desktop button guide

| Chinese label | Action |
| --- | --- |
| 视频链接 | Paste video URLs |
| 保存目录 / 选择目录 | Output folder / choose folder |
| 下载视频和封面 | Download videos and thumbnails |
| 只下载封面 | Download thumbnails only |
| 打开保存目录 | Open output folder |
| 代理地址 | Optional proxy URL |
| 停止 | Stop and keep partial files |
| 更新下载组件 | Update yt-dlp and dependencies |

## Use

Paste one or more YouTube video URLs and click **下载视频和封面**. Semicolon-separated lists, Markdown links, Shorts URLs and youtu.be links are supported and deduplicated. Playlists are not downloaded automatically.

- Default output: `~/Movies/YouTube Downloads`; change it in the window.
- Video: best available resolution up to 1080p, merged into MP4.
- Audio: explicitly labeled English tracks only; missing or unknown language fails rather than silently selecting another language. An English label can include dubbed audio.
- Thumbnail: separate JPG.
- Individual failures do not stop the rest of the queue. Logs show the reason. Stop/quit terminates the queue's process group and leaves partial files for retries.
- An optional proxy field uses your actual HTTP/SOCKS proxy address; no ports are guessed or system proxy settings changed.
- **更新下载组件** updates yt-dlp and its official dependencies from PyPI.

```sh
.venv/bin/python download_youtube.py 'https://www.youtube.com/watch?v=VIDEO_ID'
.venv/bin/python download_youtube.py --thumbnail-only 'https://youtu.be/VIDEO_ID'
.venv/bin/python download_youtube.py --height 720 --output '/path/to/folder' 'VIDEO_URL'
.venv/bin/python download_youtube.py --simulate 'VIDEO_URL'
.venv/bin/python download_youtube.py --playlist 'PLAYLIST_URL'
```

The default output may contain AV1/Opus in MP4; editor support depends on your software. If a source changes between attempts, old partial data may no longer match it: move the corresponding partial files out of the output directory before retrying. Downloads may fail because of network, region, login requirements or YouTube changes; update the components and inspect the log.

## Privacy and safety

The app runs locally and does not start a web server or provide remote access. Download requests go to YouTube and its media hosts; updates contact PyPI. It does not automatically read browser cookies. The CLI can read browser cookies only when explicitly supplied `--cookies-from-browser`.

The app stores the output folder and optional proxy in macOS UserDefaults, unencrypted. Avoid embedding proxy passwords there. Logs can contain video titles, URLs and local paths; review/redact logs before sharing. Never commit cookies, credentials, private settings, downloaded media, logs or generated app bundles. Download only content you are entitled to save and follow applicable platform terms.

## Contribute

If this saves you time, a **Star** makes it easier to find again. Bugs and practical improvement ideas are welcome in [Issues](https://github.com/eppeal-stack/youtube-downloader-formac/issues). See [CONTRIBUTING.md](CONTRIBUTING.md) for reporting details and log redaction. Contributions to localization, installation and tests are welcome.

## Development

```sh
.venv/bin/python -m unittest discover -s tests -v
```

`download_youtube.py` wraps yt-dlp; `app/worker.py` parses links, runs a sequential queue and verifies output metadata; `app/YouTubeDownloader.swift` provides the desktop UI. Cancellation requires a POSIX platform. Dependencies retain their own licenses; only the wrapper code in this repository is MIT-licensed.
