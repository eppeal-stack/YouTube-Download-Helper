#!/usr/bin/env python3
"""Download YouTube video and JPG thumbnail using the local yt-dlp install."""
import argparse
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent


def format_selector(height):
    limit = f"[height<={height}]"
    return f"bv{limit}+ba[language^=en]/b{limit}[language^=en]"


def main():
    parser = argparse.ArgumentParser(description="下载 YouTube 视频和 JPG 封面")
    parser.add_argument("urls", nargs="+", help="YouTube 视频链接")
    parser.add_argument("--thumbnail-only", action="store_true", help="只下载封面")
    parser.add_argument("--playlist", action="store_true", help="下载整个播放列表")
    parser.add_argument("--height", type=int, default=1080, help="最高分辨率（默认 1080），不足时选更低画质")
    parser.add_argument("--output", type=Path, default=Path.home() / "Movies" / "YouTube Downloads", help="保存目录（默认：~/Movies/YouTube Downloads）")
    parser.add_argument("--proxy", help="代理地址，例如 http://127.0.0.1:7890")
    parser.add_argument("--downloader", choices=["native", "aria2c"], default="native", help="下载器；慢速连接可选 aria2c")
    parser.add_argument("--ipv4", action="store_true", help="使用 IPv4 连接")
    parser.add_argument("--http-chunk-size", help="HTTP 分块大小，例如 256K")
    parser.add_argument("--cookies-from-browser", choices=["chrome", "edge", "firefox", "safari", "brave"], help="按需使用浏览器登录状态")
    parser.add_argument("--simulate", action="store_true", help="检查视频信息，不下载文件")
    args = parser.parse_args()
    for url in args.urls:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in ("http", "https") or not (host in ("youtube.com", "youtu.be", "youtube-nocookie.com") or host.endswith((".youtube.com", ".youtube-nocookie.com"))):
            parser.error("请输入完整的 YouTube 视频链接")
    if args.height is not None and args.height <= 0:
        parser.error("--height 必须为正数")
    ytdlp = ROOT / ".venv/bin/yt-dlp"
    if not ytdlp.exists():
        parser.error("缺少本地 yt-dlp，请参考 README.md 安装")
    ffmpeg = shutil.which("ffmpeg") or ("/opt/homebrew/bin/ffmpeg" if Path("/opt/homebrew/bin/ffmpeg").exists() else None)
    node = shutil.which("node")
    if not ffmpeg or not node:
        parser.error("需要安装 FFmpeg 和 Node.js 22+，请参考 README.md")
    output = args.output.expanduser().resolve()
    command = [str(ytdlp), "--ignore-config", "--no-cache-dir", "--js-runtimes", "node:" + node,
               "--ffmpeg-location", str(Path(ffmpeg).parent), "--yes-playlist" if args.playlist else "--no-playlist",
               "--socket-timeout", "15", "--retries", "2", "--extractor-retries", "1",
               "--no-overwrites", "--write-thumbnail", "--convert-thumbnails", "jpg",
               "-P", str(output), "-o", f"%(title).160B [%(id)s] [max{args.height}p-en].%(ext)s"]
    if args.thumbnail_only:
        command += ["--skip-download"]
    else:
        command += ["-f", format_selector(args.height),
                    "--merge-output-format", "mp4", "--remux-video", "mp4"]
    if args.proxy:
        command += ["--proxy", args.proxy]
    if args.ipv4:
        command += ["--force-ipv4"]
    if args.http_chunk_size:
        command += ["--http-chunk-size", args.http_chunk_size]
    if args.downloader == "aria2c" and not args.thumbnail_only:
        if not shutil.which("aria2c"):
            parser.error("未安装 aria2c")
        command += ["--downloader", "aria2c", "--downloader-args", "aria2c:-x 8 -s 8 -k 1M --connect-timeout=15 --timeout=20 --max-tries=2 --summary-interval=10 --console-log-level=warn" + (" --disable-ipv6=true" if args.ipv4 else "")]
    if args.cookies_from_browser:
        command += ["--cookies-from-browser", args.cookies_from_browser]
    if args.simulate:
        command += ["--simulate", "--print", "%(title)s [%(id)s] | %(format)s | audio language: %(language)s"]
    else:
        output.mkdir(parents=True, exist_ok=True)
    command += ["--", *args.urls]
    print(f"保存目录：{output}", flush=True)
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
