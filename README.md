# YouTube Download Helper · 油管视频下载助手

**给 Mac 用户的视频与封面批量下载工具：粘贴链接，保存 MP4 + JPG。**

原生 macOS 窗口，基于 [yt-dlp](https://github.com/yt-dlp/yt-dlp)。默认最高 **1080p + 英文音轨**，适合保存英文学习素材、整理视频参考和收集封面。安装完成后，日常下载在窗口里完成。

**简体中文** | [English](README.en.md)

[快速安装](#快速安装) · [使用方法](#使用方法) · [常见问题](#常见问题) · [反馈问题](https://github.com/eppeal-stack/youtube-downloader-formac/issues) · [MIT](LICENSE)

> 当前提供源码安装，尚无独立 DMG 安装包。桌面界面为中文，英文用户可参考 [按钮对照表](README.en.md#desktop-button-guide)。默认只接受标注为英文的音轨。

## 为什么做这个工具

收集视频素材时，往往既要视频，也要封面。这个工具把重复操作放到一个窗口里：粘贴一组链接，自动去重，依次下载，分别保存视频和封面。不调用 AI、不需要 API Key，不消耗 AI token。

```text
一组 YouTube 链接 → 自动去重 → 下载队列 → MP4 视频 + JPG 封面
```

## 已有功能

| 功能 | 当前支持 |
| --- | --- |
| 桌面窗口 | 原生 macOS AppKit 界面 |
| 批量输入 | 多行、分号分隔、Markdown 链接；自动去重 |
| 视频链接 | YouTube 标准链接、youtu.be、Shorts、Live 链接 |
| 画质 | 默认最高 1080p；源视频不足时使用较低画质 |
| 音轨 | 明确标注的英文音轨，下载后核验语言 |
| 封面 | 随视频保存 JPG，也可单独下载 |
| 队列 | 单项失败后继续，显示日志，失败链接可重试 |
| 停止 | 结束下载进程，保留部分文件供断点重试 |
| 网络 | 可选 HTTP/SOCKS 代理，使用你填写的地址 |
| 更新 | 窗口内更新 yt-dlp 及官方依赖 |

## 快速安装

需要 **macOS 12+、Python 3.10+、FFmpeg/ffprobe、Node.js 22+**。构建窗口还需要 Xcode Command Line Tools。

### 1. 安装依赖

已安装 [Homebrew](https://brew.sh/) 的用户可以运行：

```sh
brew install python ffmpeg node
xcode-select --install
```

如果 Command Line Tools 已安装，跳过第二条命令。

### 2. 获取项目并构建

```sh
git clone https://github.com/eppeal-stack/youtube-downloader-formac.git
cd youtube-downloader-formac
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
python3 build_app.py
open 'dist/YouTube Download Helper.app'
```

以后可双击 `dist/YouTube Download Helper.app` 打开。**请保留项目文件夹和 `.venv` 的位置**，应用运行时会使用它们；移动项目后需重新构建。当前为本机签名，未进行 Apple 公证，不是独立安装包。

命令行可用于 Linux；目前没有 Windows 桌面版。下载需要能够访问 YouTube 的网络环境。

## 使用方法

1. 粘贴一个或多个视频链接，支持从聊天中复制的 Markdown 链接。
2. 确认保存目录；默认 `~/Movies/YouTube Downloads`。
3. 点击 **下载视频和封面**，查看日志中的结果。
4. 点击 **打开保存目录** 查看 MP4 和 JPG。

只要图片时勾选 **只下载封面**。需要代理时填写代理软件提供的实际地址。工具不会自动更改系统代理，也不会自动读取浏览器 Cookie。

### 命令行

```sh
# 视频 + 封面，默认最高 1080p、英文音轨
.venv/bin/python download_youtube.py 'https://www.youtube.com/watch?v=VIDEO_ID'

# 只下载封面
.venv/bin/python download_youtube.py --thumbnail-only 'https://youtu.be/VIDEO_ID'

# 指定画质上限与保存目录
.venv/bin/python download_youtube.py --height 720 --output '/path/to/folder' 'VIDEO_URL'

# 检查格式，不下载文件
.venv/bin/python download_youtube.py --simulate 'VIDEO_URL'

# 明确下载整个播放列表（窗口默认仅处理视频）
.venv/bin/python download_youtube.py --playlist 'PLAYLIST_URL'
```

## 常见问题

**支持 B 站、抖音或其他网站吗？** 目前入口仅接收 YouTube 链接。yt-dlp 的全部站点能力不等于本项目已经支持的功能。

**支持 4K 和其他语言吗？** 窗口固定最高 1080p、英文音轨。CLI 可用 `--height` 调整分辨率上限；当前没有图形化音轨选择器。英文标签可能包含英语配音，不保证为原声。

**为什么有些视频失败？** 常见原因是网络、区域、登录限制或缺少标注为英文的音轨。请查看日志；YouTube 接口变化时可点 **更新下载组件**。没有 1080p 时会使用较低画质。

**停止后能继续吗？** 重新提交链接可复用断点。如果源视频在两次下载之间重新编码，旧断点可能失效；将对应部分文件移出保存目录后再完整下载。

**所有剪辑软件都能打开吗？** 不保证。MP4 可能使用 AV1/Opus 编码，兼容性取决于播放器或剪辑软件。

## 隐私与安全

工具不启动网页服务器，不提供远程访问入口。下载请求发往 YouTube 和媒体服务器；依赖更新连接 PyPI。只有在 CLI 中明确指定 `--cookies-from-browser` 时才读取浏览器登录状态。

保存目录和代理地址存入本机 macOS UserDefaults，未加密，请避免在代理地址中嵌入密码。日志可能含标题、链接和本地路径，提交 Issue 前请脱敏。不要公开 Cookie、凭据、下载文件、日志或含本地路径的构建产物。仅下载你有权保存的内容，并遵守适用的平台条款。

## 一起改进

如果它帮你省了时间，欢迎点一个 **Star**，方便以后找到它。遇到问题请[提交 Issue](https://github.com/eppeal-stack/youtube-downloader-formac/issues)，附系统版本、操作步骤和脱敏日志。

欢迎贡献英文界面、安装体验、测试和文档改进，参见 [贡献指南](CONTRIBUTING.md)。这些是欢迎参与的方向，不是已经实现的功能。

```sh
.venv/bin/python -m unittest discover -s tests -v
```

## 致谢与许可证

下载由 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 完成，合并与封面转换使用 [FFmpeg](https://ffmpeg.org/)。本项目是独立的界面与流程封装，与 YouTube、yt-dlp 无官方关联。

本仓库封装代码采用 [MIT](LICENSE) 许可证，依赖各自遵循原有许可证。
