# Contributing / 参与贡献

欢迎报告可复现的问题、改进安装说明、补充测试和贡献翻译。English issues and pull requests are welcome.

## Report a bug / 反馈问题

Please include your macOS version, Apple Silicon / Intel architecture, Python / yt-dlp / FFmpeg versions, steps to reproduce and the relevant error message.

请提供系统和芯片类型、组件版本、操作步骤及相关错误信息。仅在愿意公开时分享视频链接；移除日志中的用户名、本地路径、Cookie、代理密码和 token。不要上传浏览器资料、私有配置或下载的视频。

Remove credentials, cookies, proxy passwords, usernames and local paths before sharing logs. Only share video links you are comfortable making public.

## Submit a change / 提交修改

Discuss larger changes in an Issue first. Keep each PR focused and describe the behavior and validation. Update both READMEs when documented behavior changes.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

For UI changes, build with `python3 build_app.py` on macOS and inspect the app. Do not commit generated bundles, virtual environments, logs or media files.

界面修改请在 macOS 上构建检查；不要提交构建产物、虚拟环境、日志或媒体文件。
