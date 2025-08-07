# test_email_utils.py

import pytest
import email
from datetime import datetime, timedelta
from src.utils.email_utils import (
    decode_mime_header,
    get_since_date,
    strip_html_tags,
    get_body_preview
)

@pytest.mark.parametrize("header,expected", [
    ("=?utf-8?b?VGVzdCBFbWFpbA==?=", "Test Email"),
    (None, "(No Value)"),
    ("Simple Header", "Simple Header")
])
def test_decode_mime_header(header, expected):
    assert decode_mime_header(header) == expected

def test_get_since_date_format():
    expected_date = (datetime.today() - timedelta(days=7)).strftime("%d-%b-%Y")
    assert get_since_date(7) == expected_date

def test_strip_html_tags_basic():
    html = "<div><p>Hello <b>World</b></p><p>Second Line</p></div>"
    result = strip_html_tags(html)
    assert result == "Hello\nWorld\nSecond Line"

def test_get_body_preview_text():
    raw_email = "Subject: Preview Test\n\nLine One\nLine Two\nLine Three"
    msg = email.message_from_string(raw_email)
    preview = get_body_preview(msg, max_lines=2)
    assert preview == "Line One Line Two..."

def test_get_body_preview_html():
    raw_html = """Content-Type: text/html\n\n<html><body><p>One</p><p>Two</p><p>Three</p></body></html>"""
    msg = email.message_from_string(raw_html)
    preview = get_body_preview(msg, max_lines=2)
    assert preview == "One Two..."
