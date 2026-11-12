"""Build a local macOS app after installing requirements into .venv."""
from pathlib import Path
import plistlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    if sys.platform != 'darwin':
        raise SystemExit('The desktop app requires macOS. The CLI also supports Linux.')
    if not (ROOT / '.venv/bin/python').exists():
        raise SystemExit('Create .venv and install requirements.txt first; see README.md.')
    bundle = ROOT / 'dist/YouTube Download Helper.app'
    executable = bundle / 'Contents/MacOS/YouTubeDownloader'
    executable.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['swiftc', '-swift-version', '5', '-module-cache-path', str(ROOT / 'build/swift-cache'), str(ROOT / 'app/YouTubeDownloader.swift'), '-o', str(executable), '-framework', 'Cocoa'], check=True)
    (bundle / 'Contents/Info.plist').write_bytes(plistlib.dumps({
        'CFBundleExecutable': 'YouTubeDownloader',
        'CFBundleIdentifier': 'local.youtube.download-helper',
        'CFBundleName': 'YouTube Download Helper',
        'CFBundlePackageType': 'APPL',
        'CFBundleVersion': '1',
        'CFBundleShortVersionString': '1.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '12.0',
        'WorkspaceRoot': str(ROOT),
    }))
    subprocess.run(['codesign', '--force', '--sign', '-', str(bundle)], check=True)
    print(f'Built: {bundle}')
    print('Keep this project folder and .venv in place: the app uses them at runtime.')


if __name__ == '__main__':
    main()
