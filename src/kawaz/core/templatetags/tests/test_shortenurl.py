from unittest.mock import MagicMock
from django.test import TestCase
from django.template import Template, Context
from ..templatetags import shortenurl

__author__ = 'giginet'

URL = "http://www.kawaz.org"

class ShortenURLTestCase(TestCase):
    def test_shortenurl_templatetag(self):
        t = Template((
            "{% load shortenurl %}"
            "{% shortenurl %}"
            "かわずたんが「けろ〜ん」を書きました http://www.kawaz.org/blogs/hoge/"
            "{% endshortenurl %}"
        ))

        mock = MagicMock()
        mock.return_value = 'http://goo.gl/testurl'
        shortenurl.shorten = mock

        rendered = t.render(Context())

        self.assertRegex(rendered, r'http:\/\/goo.\gl\/.+')
