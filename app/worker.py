"""Local queue runner. No model, API key, or AI service is involved."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent.parent


def emit(kind, **data):
    print(json.dumps(dict(kind=kind, **data), ensure_ascii=False), flush=True)


def links(text):
    result = []
    for raw in re.findall(r'https?://[^\s；;<>"\]\)]+', text):
        parsed = urlparse(raw.rstrip('。，,'))
        host = (parsed.hostname or '').lower()
        if host == 'youtu.be':
            video_id = parsed.path.strip('/').split('/')[0]
        elif host == 'youtube.com' or host.endswith('.youtube.com'):
            parts = parsed.path.strip('/').split('/')
            video_id = parse_qs(parsed.query).get('v', [''])[0]
            if not video_id and len(parts) == 2 and parts[0] in ('shorts', 'live', 'embed'):
                video_id = parts[1]
        else:
            continue
        if re.fullmatch(r'[A-Za-z0-9_-]{11}', video_id):
            url = 'https://www.youtube.com/watch?v=' + video_id
            if url not in result:
                result.append(url)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=str(Path.home() / "Movies" / "YouTube Downloads"))
    parser.add_argument('--proxy', default='')
    parser.add_argument('--thumbnail-only', action='store_true')
    parser.add_argument('--update', action='store_true')
    args = parser.parse_args()
    try:
        os.setsid()  # A dedicated group lets the app stop the entire download tree.
    except PermissionError:
        if os.getpgrp() != os.getpid():
            raise
    env = dict(os.environ, PYTHONUNBUFFERED='1')
    env['PATH'] = '/opt/homebrew/bin:/usr/local/bin:' + env.get('PATH', '')
    if args.update:
        commands = [[str(ROOT / '.venv/bin/python'), '-m', 'pip', 'install', '--upgrade', 'yt-dlp[default]']]
    else:
        urls = links(sys.stdin.read())
        if not urls:
            emit('error', message='没有找到有效的 YouTube 视频链接。请粘贴完整视频链接。')
            return 1
        commands = []
        for url in urls:
            cmd = [str(ROOT / '.venv/bin/python'), str(ROOT / 'download_youtube.py'), '--output', args.output]
            if args.proxy.strip():
                cmd += ['--proxy', args.proxy.strip()]
            if args.thumbnail_only:
                cmd += ['--thumbnail-only']
            commands.append(cmd + [url])
    succeeded = 0
    for index, cmd in enumerate(commands, 1):
        emit('start', index=index, total=len(commands), message='更新下载组件' if args.update else cmd[-1])
        try:
            child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace', env=env)
            for line in child.stdout:
                if line.strip():
                    emit('log', message=line.strip())
            code = child.wait()
            if code == 0 and not args.update:
                video_id = parse_qs(urlparse(cmd[-1]).query)['v'][0]
                output = Path(args.output).expanduser()
                matches = [p for p in output.glob('*.jpg') if f'[{video_id}] [max1080p-en]' in p.name]
                if not matches:
                    raise RuntimeError('未找到已保存的 JPG 封面')
                if not args.thumbnail_only:
                    videos = [p for p in output.glob('*.mp4') if f'[{video_id}] [max1080p-en]' in p.name and '.f' not in p.stem.split(f'[{video_id}]')[-1]]
                    if not videos:
                        raise RuntimeError('未找到已合并的 MP4 视频')
                    probe = shutil.which('ffprobe', path=env['PATH'])
                    meta = json.loads(subprocess.check_output([probe, '-v', 'error', '-show_streams', '-of', 'json', str(videos[0])]))
                    streams = meta['streams']
                    if not any(s.get('codec_type') == 'video' and 0 < s.get('height', 0) <= 1080 for s in streams) or not any(s.get('codec_type') == 'audio' and s.get('tags', {}).get('language') in ('eng', 'en') for s in streams):
                        raise RuntimeError('文件画质或英文音轨核验未通过')
                    emit('log', message='已核验 MP4 画质、英文音轨及 JPG 封面。')
            if code == 0:
                succeeded += 1
            emit('item', success=code == 0, index=index)
        except Exception as exc:
            emit('log', message=str(exc))
            emit('item', success=False, index=index)
    emit('done', succeeded=succeeded, failed=len(commands)-succeeded, update=args.update)
    return 0 if succeeded == len(commands) else 1


if __name__ == '__main__':
    raise SystemExit(main())
