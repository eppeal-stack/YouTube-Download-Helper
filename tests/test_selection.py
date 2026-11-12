import unittest
from app.worker import links
from download_youtube import format_selector
from yt_dlp import YoutubeDL


class DownloadTests(unittest.TestCase):
    def test_markdown_lists_and_duplicates(self):
        url = 'https://youtu.be/abcdefghijk'
        self.assertEqual(links(f'[{url}]({url})；https://www.youtube.com/shorts/12345678901'), ['https://www.youtube.com/watch?v=abcdefghijk', 'https://www.youtube.com/watch?v=12345678901'])
        self.assertEqual(links('https://youtube.com.evil.example/watch?v=abcdefghijk'), [])

    def test_resolution_and_language(self):
        def fmt(i, height=None, language=None):
            return dict(format_id=i, url='https://example.com/'+i, ext='mp4' if height else 'm4a', vcodec='avc1' if height else 'none', acodec='none' if height else 'aac', height=height, language=language)
        with YoutubeDL({'quiet': True}) as ydl:
            select = ydl.build_format_selector(format_selector(1080))
            def choose(formats):
                return list(select(dict(formats=formats, has_merged_format=False, incomplete_formats=False)))
            self.assertEqual(choose([fmt('en', language='en-US'), fmt('zh', language='zh'), fmt('720', 720), fmt('1080', 1080), fmt('4k', 2160)])[0]['format_id'], '1080+en')
            self.assertEqual(choose([fmt('en', language='en'), fmt('720', 720), fmt('4k', 2160)])[0]['format_id'], '720+en')
            self.assertEqual(choose([fmt('zh', language='zh'), fmt('unknown'), fmt('1080',1080)]), [])


if __name__ == '__main__':
    unittest.main()
