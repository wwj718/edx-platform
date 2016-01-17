"""
Tests for js_utils.py
"""
import json
from unittest import TestCase

from openedx.core.lib.js_utils import (
    escape_jsoon_for_js, escape_string_for_js
)


class TestJSUtils(TestCase):
    """
    Test JS utils
    """

    class NoDefaultEncoding(object):
        """
        Helper class that has no default JSON encoding
        """
        def __init__(self, value):
            self.value = value

    class SampleJSONEncoder(json.JSONEncoder):
        """
        A test encoder that is used to prove that the encoder does its job before the escaping.
        """
        # pylint: disable=method-hidden
        def default(self, noDefaultEncodingObj):
            return noDefaultEncodingObj.value.replace("<script>", "sample-encoder-was-here")

    def test_escape_jsoon_for_js_escapes_unsafe_html(self):
        """
        Test escape_jsoon_for_js properly escapes &, <, and >.
        """
        malicious_json = {"</script><script>alert('hello, ');</script>": "</script><script>alert('&world!');</script>"}
        expected_escaped_json = (
            r'''{"\u003c/script\u003e\u003cscript\u003ealert('hello, ');\u003c/script\u003e": '''
            r'''"\u003c/script\u003e\u003cscript\u003ealert('\u0026world!');\u003c/script\u003e"}'''
        )

        escaped_json = escape_jsoon_for_js(malicious_json)
        self.assertEquals(expected_escaped_json, escaped_json)

    def test_escape_jsoon_for_js_with_custom_encoder_escapes_unsafe_html(self):
        """
        Test escape_jsoon_for_js first encodes with custom JSNOEncoder before escaping &, <, and >

        The test encoder class should first perform the replacement of "<script>" with
        "sample-encoder-was-here", and then should escape the remaining &, <, and >.

        """
        malicious_json = {
            "</script><script>alert('hello, ');</script>":
            self.NoDefaultEncoding("</script><script>alert('&world!');</script>")
        }
        expected_custom_escaped_json = (
            r'''{"\u003c/script\u003e\u003cscript\u003ealert('hello, ');\u003c/script\u003e": '''
            r'''"\u003c/script\u003esample-encoder-was-herealert('\u0026world!');\u003c/script\u003e"}'''
        )

        escaped_json = escape_jsoon_for_js(malicious_json, cls=self.SampleJSONEncoder)
        self.assertEquals(expected_custom_escaped_json, escaped_json)

    def validate_js_method_escapes_unsafe_html(self, escape_js_method):
        """
        Test passed escape_js_method escapes &, <, and >, as well as returns a
        unicode type
        """

    def test_escape_string_for_js_escapes_unsafe_html(self):
        """
        Test escape_string_for_js escapes &, <, and >, as well as returns a unicode type
        """
        malicious_js_string = "</script><script>alert('hello, ');</script>"

        expected_escaped_string_for_js = unicode(
            r"\u003C/script\u003E\u003Cscript\u003Ealert(\u0027hello, \u0027)\u003B\u003C/script\u003E"
        )
        escaped_string_for_js = escape_string_for_js(malicious_js_string)
        self.assertEquals(expected_escaped_string_for_js, escaped_string_for_js)
