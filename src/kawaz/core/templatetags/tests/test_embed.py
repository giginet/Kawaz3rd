#! -*- coding: utf-8 -*-
#
# created by giginet on 2014/6/9
#
__author__ = 'giginet'

from unittest.mock import MagicMock
from django.test import TestCase
from django.template import Template, Context

class BaseViewerTemplateTagTestCase(TestCase):

    def _test_template(self, before, after, filter_name=None):
        if not filter_name:
            filter_name = self.filter_name
        c = Context({
            'body' : before
        })
        t = Template(
            """{%% load embed %%}"""
            """{{ body | %(filter_name)s }}""" % {
                'filter_name': filter_name
            }
        )
        r = t.render(c)
        self.assertEqual(r, after)

class YouTubeTemplateTagTestCase(BaseViewerTemplateTagTestCase):
    filter_name = 'youtube'

    def test_youtube(self):
        """
        YoutubeのURLからプレイヤーをembedします
        """
        body = ("オススメの動画です\n"
                "https://www.youtube.com/watch?v=r-j9FZ2TQd0")
        expected = ("オススメの動画です\n"
                    """<iframe width="640" height="360" src="//www.youtube.com/embed/r-j9FZ2TQd0" frameborder="0" allowfullscreen></iframe>""")
        self._test_template(body, expected)

    def test_youtube_multitimes(self):
        """
        YouTubeのURLが複数含まれたテキストを正しく展開します
        """
        body = ("オススメの動画です\n"
                "https://www.youtube.com/watch?v=r-j9FZ2TQd0\n"
                "\n"
                "ついでにこっちもおもしろいです\n"
                "https://www.youtube.com/watch?v=LoH0dOyyGx8")
        expected = ("オススメの動画です\n"
                    """<iframe width="640" height="360" src="//www.youtube.com/embed/r-j9FZ2TQd0" frameborder="0" allowfullscreen></iframe>\n"""
                    "\n"
                    "ついでにこっちもおもしろいです\n"
                    """<iframe width="640" height="360" src="//www.youtube.com/embed/LoH0dOyyGx8" frameborder="0" allowfullscreen></iframe>""")
        self._test_template(body, expected)

    def test_youtube_with_width_and_height(self):
        body = ("オススメの動画です\n"
                "https://www.youtube.com/watch?v=r-j9FZ2TQd0")
        expected = ("オススメの動画です\n"
                    """<iframe width="1600" height="900" src="//www.youtube.com/embed/r-j9FZ2TQd0" frameborder="0" allowfullscreen></iframe>""")
        self._test_template(body, expected, filter_name="youtube:'1600,900'")

    def test_youtube_with_width(self):
        body = ("オススメの動画です\n"
                "https://www.youtube.com/watch?v=r-j9FZ2TQd0")
        expected = ("オススメの動画です\n"
                    """<iframe width="800" height="450" src="//www.youtube.com/embed/r-j9FZ2TQd0" frameborder="0" allowfullscreen></iframe>""")
        self._test_template(body, expected, filter_name="youtube:'800'")

    def test_youtube_with_responsive(self):
        body = ("オススメの動画です\n"
                "https://www.youtube.com/watch?v=r-j9FZ2TQd0")
        expected = ("オススメの動画です\n"
                    """<iframe class="embed-responsive-item" src="//www.youtube.com/embed/r-j9FZ2TQd0" frameborder="0" allowfullscreen></iframe>""")
        self._test_template(body, expected, filter_name="youtube:'responsive'")

    def test_youtube_with_link_fail(self):
        """
        HTMLタグに含まれていた場合は展開しませんが、
        行末、行頭にURLが含まれていた場合は、プレイヤーが展開されます
        """
        body = ("オススメの動画です\n"
                """<a href="https://www.youtube.com/watch?v=r-j9FZ2TQd0">オススメ</a>\n"""
                "\n"
                "ついでにこっちもおもしろいです https://www.youtube.com/watch?v=LoH0dOyyGx8\n"
                "https://www.youtube.com/watch?v=LoH0dOyyGx8 これも")
        expected = ("オススメの動画です\n"
                    """<a href="https://www.youtube.com/watch?v=r-j9FZ2TQd0">オススメ</a>\n"""
                    "\n"
                    """ついでにこっちもおもしろいです <iframe width="640" height="360" src="//www.youtube.com/embed/LoH0dOyyGx8" frameborder="0" allowfullscreen></iframe>\n"""
                    """<iframe width="640" height="360" src="//www.youtube.com/embed/LoH0dOyyGx8" frameborder="0" allowfullscreen></iframe> これも""")
        self._test_template(body, expected)


class NicoVideoTemplateTagTestCase(BaseViewerTemplateTagTestCase):
    filter_name = 'nicovideo'

    def test_nicoviceo(self):
        """
        ニコニコ動画の動画URLからプレーヤーをembedします
        """
        body =("全てはここから始まった\n"
               "http://www.nicovideo.jp/watch/sm10805698")
        expect = ("全てはここから始まった\n"
                  """<script type="text/javascript" src="http://ext.nicovideo.jp/thumb_watch/sm10805698"></script>""")
        self._test_template(body, expect)

    def test_nicovideo_multiple(self):
        """
        文章中に複数のニコニコ動画URLが含まれていたとき、全てembedします
        """
        body = ("全てはここから始まった\n"
        "http://www.nicovideo.jp/watch/sm10805698\n"
        "\n"
        "レッツゴー\n"
        "http://www.nicovideo.jp/watch/sm9\n")
        expect = ("全てはここから始まった\n"
                  """<script type="text/javascript" src="http://ext.nicovideo.jp/thumb_watch/sm10805698"></script>\n"""
                  "\n"
                  "レッツゴー\n"
                  """<script type="text/javascript" src="http://ext.nicovideo.jp/thumb_watch/sm9"></script>\n""")
        self._test_template(body, expect)

    def test_nicoviceo_with_link_fail(self):
        """
        HTMLタグや、行末、行頭にURLが含まれていた場合は、プレイヤーが展開されません
        """
        body = ("全てはここから始まった\n"
                """<a href="http://www.nicovideo.jp/watch/sm10805698">音楽マインスイーパー</a>\n"""
                "\n"
                "http://www.nicovideo.jp/watch/sm9 レッツゴー\n"
                "行頭 http://www.nicovideo.jp/watch/sm9")
        expect = ("全てはここから始まった\n"
                """<a href="http://www.nicovideo.jp/watch/sm10805698">音楽マインスイーパー</a>\n"""
                "\n"
                """<script type="text/javascript" src="http://ext.nicovideo.jp/thumb_watch/sm9"></script> レッツゴー\n"""
                """行頭 <script type="text/javascript" src="http://ext.nicovideo.jp/thumb_watch/sm9"></script>""")
        self._test_template(body, expect)